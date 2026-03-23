#!/usr/bin/env python3
"""
Portable local grounded-LLM runner for DICE case cards.

This script is intentionally lightweight and deterministic:
- it regenerates the case cards and prompt bundle from the released DICE outputs;
- it runs a single local MLX-backed model over a chosen prompt type;
- it writes raw generations, runtime metadata, and grounding scores.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path
import sys
from time import perf_counter

import pandas as pd

from grounded_llm_triage import (
    evaluate_llm_grounding_outputs,
    export_llm_case_cards,
    export_llm_diagnostic_model_catalog,
    export_llm_diagnostic_prompt_bundle,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_ROOT = PROJECT_ROOT / "data generation" / "dataset" / "ITC_M2Pro_DATA"
DEFAULT_MODEL_ID = "mlx-community/Qwen2.5-0.5B-Instruct-4bit"
HF_CACHE_ROOT = Path.home() / ".cache" / "huggingface" / "hub"


def profile_global_dir(root: Path, profile: str) -> Path:
    if profile == "mixed":
        return root / "results_dice_full"
    return root / f"results_dice_full_{profile}"


def profile_appendix_dir(root: Path, profile: str) -> Path:
    out = root / "results_itc_appendix" / profile
    out.mkdir(parents=True, exist_ok=True)
    return out


def slugify_model_id(model_id: str) -> str:
    return model_id.replace("/", "__").replace("-", "_").replace(".", "_")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_cached_hf_revision(model_id: str) -> str:
    cache_dir = HF_CACHE_ROOT / ("models--" + model_id.replace("/", "--"))
    ref_main = cache_dir / "refs" / "main"
    if ref_main.exists():
        return ref_main.read_text().strip()
    return ""


def build_prompt(system_prompt: str, user_prompt: str, tokenizer) -> str:
    if hasattr(tokenizer, "apply_chat_template"):
        try:
            return tokenizer.apply_chat_template(
                [
                    {"role": "system", "content": str(system_prompt)},
                    {"role": "user", "content": str(user_prompt)},
                ],
                tokenize=False,
                add_generation_prompt=True,
            )
        except Exception:
            pass
    return f"System: {system_prompt}\n\nUser: {user_prompt}\n\nAssistant:"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset_root", type=Path, default=DEFAULT_DATASET_ROOT)
    ap.add_argument("--feature_profile", choices=["mixed", "full"], required=True)
    ap.add_argument("--model_id", default=DEFAULT_MODEL_ID)
    ap.add_argument("--revision", default="")
    ap.add_argument(
        "--prompt_types",
        nargs="+",
        default=["reviewer_summary"],
        choices=["reviewer_summary", "triage", "followup"],
    )
    ap.add_argument("--max_tokens", type=int, default=160)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--limit_cases", type=int, default=0)
    args = ap.parse_args()

    dataset_root = args.dataset_root.expanduser().resolve()
    global_dir = profile_global_dir(dataset_root, args.feature_profile)
    appendix_dir = profile_appendix_dir(dataset_root, args.feature_profile)
    appendix_dir.mkdir(parents=True, exist_ok=True)

    cards = export_llm_case_cards(global_dir, appendix_dir)
    models = export_llm_diagnostic_model_catalog(appendix_dir)
    prompt_bundle = export_llm_diagnostic_prompt_bundle(cards, models, appendix_dir)
    cards_csv = appendix_dir / "llm_case_cards.csv"
    prompt_bundle_csv = appendix_dir / "llm_diagnostic_prompt_bundle.csv"
    prompt_rows = prompt_bundle[
        (prompt_bundle["prompt_type"].isin(args.prompt_types))
        & (prompt_bundle["model_id"].astype(str) == str(args.model_id))
    ].copy()
    prompt_rows = prompt_rows.sort_values(["case_id", "prompt_type"]).reset_index(drop=True)
    if args.limit_cases > 0:
        keep_cases = prompt_rows["case_id"].drop_duplicates().iloc[: args.limit_cases].tolist()
        prompt_rows = prompt_rows[prompt_rows["case_id"].isin(keep_cases)].reset_index(drop=True)

    if prompt_rows.empty:
        raise RuntimeError("No prompt rows matched the requested prompt types.")

    import mlx.core as mx
    from mlx_lm import generate, load
    from mlx_lm.sample_utils import make_sampler

    mx.random.seed(args.seed)

    t0 = perf_counter()
    load_out = load(args.model_id, revision=(args.revision or None), return_config=True)
    if len(load_out) == 3:
        model, tokenizer, model_config = load_out
    else:
        model, tokenizer = load_out
        model_config = {}
    sampler = make_sampler(temp=0.0)
    generations = []
    for row in prompt_rows.itertuples(index=False):
        prompt = build_prompt(row.system_prompt, row.user_prompt, tokenizer)
        response_text = generate(
            model,
            tokenizer,
            prompt=prompt,
            verbose=False,
            max_tokens=int(args.max_tokens),
            sampler=sampler,
        )
        generations.append(
            {
                "case_id": str(row.case_id),
                "prompt_type": str(row.prompt_type),
                "model_id": str(args.model_id),
                "revision": str(args.revision or ""),
                "backend": "mlx_lm",
                "seed": int(args.seed),
                "max_tokens": int(args.max_tokens),
                "response_text": str(response_text).strip(),
            }
        )

    outputs_df = pd.DataFrame(generations)
    stem = f"{slugify_model_id(args.model_id)}_{'_'.join(args.prompt_types)}"
    outputs_csv = appendix_dir / f"llm_outputs_{stem}.csv"
    outputs_df.to_csv(outputs_csv, index=False)
    summary_df, detail_df = evaluate_llm_grounding_outputs(outputs_df, cards, appendix_dir, stem=stem)

    runtime_json = appendix_dir / f"llm_runtime_{stem}.json"
    runtime_json.write_text(
        json.dumps(
            {
                "feature_profile": args.feature_profile,
                "global_dir": str(global_dir),
                "appendix_dir": str(appendix_dir),
                "model_id": args.model_id,
                "revision": args.revision,
                "resolved_cached_revision": resolve_cached_hf_revision(args.model_id),
                "backend": "mlx_lm",
                "prompt_types": list(args.prompt_types),
                "max_tokens": int(args.max_tokens),
                "seed": int(args.seed),
                "n_outputs": int(len(outputs_df)),
                "mlx_lm_version": importlib.metadata.version("mlx-lm"),
                "prompt_bundle_sha256": file_sha256(prompt_bundle_csv),
                "case_cards_sha256": file_sha256(cards_csv),
                "python_version": sys.version,
                "platform": platform.platform(),
                "sampler": "greedy(temp=0.0)",
                "model_config": model_config,
                "elapsed_s": round(perf_counter() - t0, 3),
            },
            indent=2,
        )
        + "\n"
    )

    print("[OK] wrote:", outputs_csv)
    print("[OK] wrote:", appendix_dir / f"llm_grounding_summary_{stem}.csv")
    print("[OK] wrote:", appendix_dir / f"llm_grounding_detail_{stem}.csv")
    print("[OK] wrote:", runtime_json)
    if not summary_df.empty:
        print(summary_df.to_string(index=False))
    else:
        print("[WARN] No scored grounding rows were produced.")


if __name__ == "__main__":
    main()
