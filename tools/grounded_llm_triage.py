#!/usr/bin/env python3
"""Helpers for grounded LLM triage artifacts and evaluation in DICE."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


TIER_ALIAS_MAP = {
    "tier0": ["tier0", "tier-0", "tier 0", "tier-0 evidence", "tier 0 evidence"],
    "tier1_alt": ["tier1", "tier-1", "tier 1", "tier1_alt", "tier-1 evidence", "tier 1 evidence"],
    "tier2": ["tier2", "tier-2", "tier 2", "tier-2 evidence", "tier 2 evidence"],
}

MECHANISM_ALIAS_MAP = {
    "compute": ["compute"],
    "memory_io": ["memory_io", "memory/io", "memory io"],
    "thermal_power": ["thermal_power", "thermal/power", "thermal power"],
    "scheduler_runtime": ["scheduler_runtime", "scheduler runtime"],
    "platform_pressure": ["platform_pressure", "platform pressure"],
}


def runtime_availability() -> dict[str, bool]:
    modules = {}
    for mod in ["transformers", "torch", "vllm", "llama_cpp", "ollama"]:
        if mod == "ollama":
            modules[mod] = False
            continue
        modules[mod] = importlib.util.find_spec(mod) is not None
    return modules


def export_llm_case_cards(out_full: Path, appendix_full: Path) -> pd.DataFrame:
    appendix_full.mkdir(parents=True, exist_ok=True)
    case_diag = pd.read_csv(out_full / "case_diagnosis_summary.csv")
    cards = case_diag[case_diag["config"] == "tier0_tier1_tier2"].copy()
    if "label" in cards.columns:
        cards = cards[cards["label"] == 1].copy()
    elif "stressor" in cards.columns:
        cards = cards[cards["stressor"].astype(str) != "NOMINAL"].copy()
    keep_cols = [
        "case_id",
        "workload",
        "stressor",
        "dominant_tier",
        "dominant_mechanism",
        "tier0_share",
        "tier1_alt_share",
        "tier2_share",
        "compute_share",
        "memory_io_share",
        "thermal_power_share",
        "scheduler_runtime_share",
        "platform_pressure_share",
        "top_feature_1",
        "top_feature_score_1",
        "top_feature_2",
        "top_feature_score_2",
        "top_feature_3",
        "top_feature_score_3",
        "top_feature_4",
        "top_feature_score_4",
        "top_feature_5",
        "top_feature_score_5",
        "top_mechanism_1",
        "top_mechanism_score_1",
        "top_mechanism_2",
        "top_mechanism_score_2",
        "top_mechanism_3",
        "top_mechanism_score_3",
    ]
    cards = cards[[c for c in keep_cols if c in cards.columns]].copy()

    def _case_card_json(row: pd.Series) -> str:
        payload = {
            "case_id": row.get("case_id"),
            "workload": row.get("workload"),
            "stressor": row.get("stressor"),
            "dominant_tier": row.get("dominant_tier"),
            "dominant_mechanism": row.get("dominant_mechanism"),
            "tier_share": {
                "tier0": row.get("tier0_share"),
                "tier1": row.get("tier1_alt_share"),
                "tier2": row.get("tier2_share"),
            },
            "mechanism_share": {
                "compute": row.get("compute_share"),
                "memory_io": row.get("memory_io_share"),
                "thermal_power": row.get("thermal_power_share"),
                "scheduler_runtime": row.get("scheduler_runtime_share"),
                "platform_pressure": row.get("platform_pressure_share"),
            },
            "top_features": [
                {"name": row.get(f"top_feature_{i}"), "score": row.get(f"top_feature_score_{i}")}
                for i in range(1, 6)
                if pd.notna(row.get(f"top_feature_{i}"))
            ],
            "top_mechanisms": [
                {"name": row.get(f"top_mechanism_{i}"), "score": row.get(f"top_mechanism_score_{i}")}
                for i in range(1, 4)
                if pd.notna(row.get(f"top_mechanism_{i}"))
            ],
        }
        return json.dumps(payload, sort_keys=True)

    cards["diagnostic_case_card_json"] = cards.apply(_case_card_json, axis=1)
    cards["reviewer_prompt"] = cards["diagnostic_case_card_json"].apply(
        lambda s: (
            "You are preparing a grounded DICE diagnostic note for a silicon-reliability reviewer. "
            "Use only the supplied case card. Do not invent missing evidence. "
            "Explain the dominant tier, dominant mechanism, and the top residual cues in plain English.\n\n"
            f"Case card JSON:\n{s}"
        )
    )
    cards["triage_prompt"] = cards["diagnostic_case_card_json"].apply(
        lambda s: (
            "Use only the supplied DICE case card. Write a compact triage report with five fields: "
            "severity, likely subsystem, evidence summary, two follow-up measurements, and confidence. "
            "If the evidence is weak, say so directly.\n\n"
            f"Case card JSON:\n{s}"
        )
    )
    cards["followup_prompt"] = cards["diagnostic_case_card_json"].apply(
        lambda s: (
            "Use only the supplied DICE case card. Recommend up to three next diagnostic steps. "
            "Each step must cite the specific feature or mechanism that motivated it.\n\n"
            f"Case card JSON:\n{s}"
        )
    )
    cards.to_csv(appendix_full / "llm_case_cards.csv", index=False)
    return cards


def export_llm_diagnostic_model_catalog(appendix_full: Path) -> pd.DataFrame:
    appendix_full.mkdir(parents=True, exist_ok=True)
    models = pd.DataFrame(
        [
            {
                "model_id": "Qwen/Qwen2.5-7B-Instruct",
                "deployment_role": "primary DICE baseline",
                "priority_rank": 1,
                "params_billions": 7.61,
                "context_tokens": 131072,
                "strengths": "Strong instruction following, structured output behavior, and long-context support.",
                "best_for_dice": "Primary grounded reviewer summaries and structured incident reports from exported case cards.",
                "source_url": "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct",
            },
            {
                "model_id": "microsoft/Phi-4-mini-instruct",
                "deployment_role": "lightweight comparison",
                "priority_rank": 2,
                "params_billions": 3.8,
                "context_tokens": 128000,
                "strengths": "Small footprint, strong reasoning density, and good fit for constrained local diagnostics.",
                "best_for_dice": "Fast first-pass case summaries and follow-up recommendations on a laptop or edge workstation.",
                "source_url": "https://huggingface.co/microsoft/Phi-4-mini-instruct",
            },
            {
                "model_id": "meta-llama/Meta-Llama-3.1-8B-Instruct",
                "deployment_role": "ecosystem baseline",
                "priority_rank": 3,
                "params_billions": 8.0,
                "context_tokens": 128000,
                "strengths": "Broad tooling support, stable chat behavior, and strong general-purpose instruction tuning.",
                "best_for_dice": "Fallback baseline when the deployment stack already supports Llama-family models.",
                "source_url": "https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct",
            },
            {
                "model_id": "Qwen/Qwen2.5-14B-Instruct",
                "deployment_role": "stronger offline review",
                "priority_rank": 4,
                "params_billions": 14.7,
                "context_tokens": 131072,
                "strengths": "Higher-capacity structured reasoning while remaining practical for offline workstation use.",
                "best_for_dice": "Second-pass failure analysis and richer postmortem summaries after the detector has already raised a case.",
                "source_url": "https://huggingface.co/Qwen/Qwen2.5-14B-Instruct",
            },
        ]
    ).sort_values("priority_rank").reset_index(drop=True)
    models.to_csv(appendix_full / "llm_diagnostic_model_catalog.csv", index=False)
    return models


def export_llm_diagnostic_prompt_bundle(
    cards: pd.DataFrame,
    models: pd.DataFrame,
    appendix_full: Path,
) -> pd.DataFrame:
    appendix_full.mkdir(parents=True, exist_ok=True)
    system_prompt = (
        "You are a DICE diagnostic copilot. You may use only the structured DICE evidence supplied to you. "
        "Do not claim access to raw telemetry, hidden logs, or external knowledge about the run. "
        "If the evidence is incomplete, say that the conclusion is tentative."
    )
    rows = []
    for _, model in models.iterrows():
        for _, card in cards.iterrows():
            rows.append(
                {
                    "model_id": model["model_id"],
                    "deployment_role": model["deployment_role"],
                    "case_id": card["case_id"],
                    "prompt_type": "triage",
                    "system_prompt": system_prompt,
                    "user_prompt": card["triage_prompt"],
                }
            )
            rows.append(
                {
                    "model_id": model["model_id"],
                    "deployment_role": model["deployment_role"],
                    "case_id": card["case_id"],
                    "prompt_type": "reviewer_summary",
                    "system_prompt": system_prompt,
                    "user_prompt": card["reviewer_prompt"],
                }
            )
            rows.append(
                {
                    "model_id": model["model_id"],
                    "deployment_role": model["deployment_role"],
                    "case_id": card["case_id"],
                    "prompt_type": "followup",
                    "system_prompt": system_prompt,
                    "user_prompt": card["followup_prompt"],
                }
            )

    bundle = pd.DataFrame(rows)
    bundle.to_csv(appendix_full / "llm_diagnostic_prompt_bundle.csv", index=False)
    with (appendix_full / "llm_diagnostic_prompt_bundle.jsonl").open("w") as handle:
        for row in bundle.to_dict(orient="records"):
            handle.write(json.dumps(row) + "\n")
    return bundle


def _slugify_model_id(model_id: str) -> str:
    return model_id.replace("/", "__").replace("-", "_").replace(".", "_")


def _normalize_text(text: str) -> str:
    text = str(text).lower()
    text = text.replace("_", " ")
    text = text.replace(":", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _feature_aliases(name: str | float | None) -> set[str]:
    if pd.isna(name):
        return set()
    value = str(name)
    aliases = {value.lower(), _normalize_text(value)}
    if ":" in value:
        tail = value.split(":", 1)[1]
        aliases.add(tail.lower())
        aliases.add(_normalize_text(tail))
    return {alias for alias in aliases if alias}


def _contains_any(text: str, aliases: Iterable[str]) -> bool:
    norm = _normalize_text(text)
    return any(alias and _normalize_text(alias) in norm for alias in aliases)


def discover_latest_llm_outputs(appendix_full: Path) -> list[Path]:
    appendix_full.mkdir(parents=True, exist_ok=True)
    return sorted(appendix_full.glob("llm_outputs_*.csv"))


def evaluate_llm_grounding_outputs(
    llm_outputs: pd.DataFrame,
    llm_cards: pd.DataFrame,
    appendix_full: Path,
    stem: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    appendix_full.mkdir(parents=True, exist_ok=True)
    detail = llm_outputs.merge(llm_cards, on="case_id", how="left", suffixes=("", "_card")).copy()

    supported_tier_threshold = 0.05
    supported_mech_threshold = 0.10
    global_mechanisms = list(MECHANISM_ALIAS_MAP.keys())
    global_tiers = list(TIER_ALIAS_MAP.keys())

    rows = []
    for row in detail.itertuples(index=False):
        text = str(row.response_text)
        dominant_tier = getattr(row, "dominant_tier")
        dominant_mechanism = getattr(row, "dominant_mechanism")

        tier_aliases = set(TIER_ALIAS_MAP.get(str(dominant_tier), []))
        dominant_mech_aliases = set(MECHANISM_ALIAS_MAP.get(str(dominant_mechanism), [str(dominant_mechanism)]))
        top_feature_aliases = _feature_aliases(getattr(row, "top_feature_1", None))
        top_mech_aliases = set(
            MECHANISM_ALIAS_MAP.get(str(getattr(row, "top_mechanism_1", "")), [str(getattr(row, "top_mechanism_1", ""))])
        )

        mentions_dominant_tier = _contains_any(text, tier_aliases)
        mentions_dominant_mechanism = _contains_any(text, dominant_mech_aliases)
        mentions_top_feature_1 = _contains_any(text, top_feature_aliases)
        mentions_top_mechanism_1 = _contains_any(text, top_mech_aliases)

        supported_tiers = {
            "tier0": getattr(row, "tier0_share", 0.0),
            "tier1_alt": getattr(row, "tier1_alt_share", 0.0),
            "tier2": getattr(row, "tier2_share", 0.0),
        }
        unsupported_tier_mentions = any(
            _contains_any(text, TIER_ALIAS_MAP[tier]) and supported_tiers.get(tier, 0.0) < supported_tier_threshold
            for tier in global_tiers
        )

        supported_mechs = {
            "compute": getattr(row, "compute_share", 0.0),
            "memory_io": getattr(row, "memory_io_share", 0.0),
            "thermal_power": getattr(row, "thermal_power_share", 0.0),
            "scheduler_runtime": getattr(row, "scheduler_runtime_share", 0.0),
            "platform_pressure": getattr(row, "platform_pressure_share", 0.0),
        }
        unsupported_mechanism_mentions = any(
            _contains_any(text, MECHANISM_ALIAS_MAP[mech]) and supported_mechs.get(mech, 0.0) < supported_mech_threshold
            for mech in global_mechanisms
        )

        cue_coverage = np.mean(
            [
                float(mentions_dominant_tier),
                float(mentions_dominant_mechanism),
                float(mentions_top_feature_1),
                float(mentions_top_mechanism_1),
            ]
        )

        rows.append(
            {
                "model_id": getattr(row, "model_id"),
                "case_id": getattr(row, "case_id"),
                "prompt_type": getattr(row, "prompt_type"),
                "mentions_dominant_tier": mentions_dominant_tier,
                "mentions_dominant_mechanism": mentions_dominant_mechanism,
                "mentions_top_feature_1": mentions_top_feature_1,
                "mentions_top_mechanism_1": mentions_top_mechanism_1,
                "grounded_core": bool(mentions_dominant_tier and mentions_dominant_mechanism),
                "cue_coverage": cue_coverage,
                "unsupported_tier_mentions": unsupported_tier_mentions,
                "unsupported_mechanism_mentions": unsupported_mechanism_mentions,
                "hallucination_flag": bool(unsupported_tier_mentions or unsupported_mechanism_mentions),
            }
        )

    scored = pd.DataFrame(rows)
    if scored.empty:
        summary = pd.DataFrame(
            columns=[
                "model_id",
                "prompt_type",
                "n_outputs",
                "grounded_core_rate",
                "dominant_tier_rate",
                "dominant_mechanism_rate",
                "top_feature_1_rate",
                "top_mechanism_1_rate",
                "mean_cue_coverage",
                "hallucination_rate",
            ]
        )
    else:
        summary = (
            scored.groupby(["model_id", "prompt_type"], sort=False)
            .agg(
                n_outputs=("case_id", "count"),
                grounded_core_rate=("grounded_core", "mean"),
                dominant_tier_rate=("mentions_dominant_tier", "mean"),
                dominant_mechanism_rate=("mentions_dominant_mechanism", "mean"),
                top_feature_1_rate=("mentions_top_feature_1", "mean"),
                top_mechanism_1_rate=("mentions_top_mechanism_1", "mean"),
                mean_cue_coverage=("cue_coverage", "mean"),
                hallucination_rate=("hallucination_flag", "mean"),
            )
            .reset_index()
        )

    summary.to_csv(appendix_full / f"llm_grounding_summary_{stem}.csv", index=False)
    scored.to_csv(appendix_full / f"llm_grounding_detail_{stem}.csv", index=False)
    return summary, scored
