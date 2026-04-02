#!/usr/bin/env python3
"""Generate paper-ready MacBook Pro hardware-context diagrams for DICE."""

from __future__ import annotations

import argparse
from pathlib import Path
from textwrap import fill

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = (
    REPO_ROOT
    / "data generation"
    / "dataset"
    / "ITC_M2Pro_DATA"
    / "results_itc_appendix"
    / "analysis"
    / "hardware_context"
)
DEFAULT_BASIC_NAME = "macbook_pro_2023_m2pro_hardware_context"
DEFAULT_TIERED_NAME = "macbook_pro_2023_m2pro_tiered_observability"


COLORS = {
    "bg": "#f7f8fb",
    "outer_fc": "#fbfcfe",
    "outer_ec": "#cbd5e1",
    "title_fc": "#17324d",
    "title_ec": "#17324d",
    "title_text": "#ffffff",
    "soc_fc": "#dceeff",
    "soc_ec": "#4479aa",
    "tile_fc": "#eef3f8",
    "tile_ec": "#93a6bb",
    "footer_fc": "#eef7f3",
    "footer_ec": "#84b89a",
    "tier0_fc": "#fff0df",
    "tier0_ec": "#d5893e",
    "tier1_fc": "#e7f6ef",
    "tier1_ec": "#4d9a73",
    "tier2_fc": "#e8f0ff",
    "tier2_ec": "#5e83cf",
    "text": "#16202a",
    "muted": "#4b5b6b",
    "wire": "#8a9aab",
}


def add_round_box(
    ax,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    title: str | None = None,
    lines: list[str] | None = None,
    fc: str,
    ec: str,
    title_color: str = COLORS["text"],
    text_color: str = COLORS["text"],
    title_size: float = 10.6,
    body_size: float = 9.1,
    align: str = "left",
    rounding: float = 0.18,
    lw: float = 1.5,
    wrap_width: int = 28,
) -> FancyBboxPatch:
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.02,rounding_size={rounding}",
        linewidth=lw,
        edgecolor=ec,
        facecolor=fc,
    )
    ax.add_patch(patch)

    if title:
        tx = x + 0.18 if align == "left" else x + w / 2
        ha = "left" if align == "left" else "center"
        ax.text(
            tx,
            y + h - 0.18,
            title,
            ha=ha,
            va="top",
            fontsize=title_size,
            fontweight="bold",
            color=title_color,
        )

    if lines:
        wrapped = "\n".join(fill(line, width=wrap_width) for line in lines)
        tx = x + 0.18 if align == "left" else x + w / 2
        ha = "left" if align == "left" else "center"
        top_pad = 0.56 if title else 0.20
        ax.text(
            tx,
            y + h - top_pad,
            wrapped,
            ha=ha,
            va="top",
            fontsize=body_size,
            color=text_color,
            linespacing=1.22,
        )

    return patch


def connect(
    ax,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    *,
    color: str | None = None,
    lw: float = 1.2,
    arrowstyle: str = "-",
) -> None:
    arrow = FancyArrowPatch(
        (x0, y0),
        (x1, y1),
        arrowstyle=arrowstyle,
        mutation_scale=10,
        linewidth=lw,
        color=color or COLORS["wire"],
        shrinkA=4,
        shrinkB=4,
    )
    ax.add_patch(arrow)


def build_canvas() -> tuple[plt.Figure, plt.Axes]:
    fig = plt.figure(figsize=(4.75, 6.55), facecolor=COLORS["bg"])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 13)
    ax.axis("off")
    return fig, ax


def draw_basic_context(ax) -> None:
    add_round_box(
        ax,
        0.35,
        1.05,
        9.3,
        11.45,
        fc=COLORS["outer_fc"],
        ec=COLORS["outer_ec"],
        rounding=0.28,
        lw=1.8,
    )

    add_round_box(
        ax,
        0.7,
        11.55,
        8.6,
        0.95,
        title="MacBook Pro (16-inch, 2023)",
        lines=["Collection platform used in DICE experiments"],
        fc=COLORS["title_fc"],
        ec=COLORS["title_ec"],
        title_color=COLORS["title_text"],
        text_color=COLORS["title_text"],
        title_size=12.0,
        body_size=9.0,
        align="center",
        rounding=0.20,
    )

    add_round_box(
        ax,
        0.95,
        10.15,
        8.1,
        1.15,
        title="Display",
        lines=[
            '16.2" Liquid Retina XDR',
            "3456 x 2234 native resolution",
            "ProMotion up to 120 Hz",
        ],
        fc=COLORS["tile_fc"],
        ec=COLORS["tile_ec"],
        title_size=10.1,
        body_size=8.7,
        align="center",
    )

    add_round_box(
        ax,
        0.95,
        8.35,
        2.55,
        1.55,
        title="Battery + Power",
        lines=[
            "100 Wh battery",
            "140 W USB-C adapter",
            "MagSafe 3 fast charge",
        ],
        fc=COLORS["tile_fc"],
        ec=COLORS["tile_ec"],
        title_size=9.8,
        body_size=8.6,
    )

    add_round_box(
        ax,
        6.5,
        8.35,
        2.55,
        1.55,
        title="Unified Memory",
        lines=[
            "16 GB shared memory",
            "CPU / GPU / ANE",
            "200 GB/s fabric",
        ],
        fc=COLORS["tile_fc"],
        ec=COLORS["tile_ec"],
        title_size=9.8,
        body_size=8.6,
    )

    add_round_box(
        ax,
        2.95,
        5.35,
        4.1,
        3.35,
        title="Apple M2 Pro SoC",
        lines=[
            "12-core CPU (8P + 4E)",
            "19-core integrated GPU",
            "16-core Neural Engine",
            "Media encode / decode engines",
            "Host-visible compute hub for DICE",
        ],
        fc=COLORS["soc_fc"],
        ec=COLORS["soc_ec"],
        title_size=11.0,
        body_size=8.95,
        align="center",
        rounding=0.22,
        lw=1.7,
    )

    add_round_box(
        ax,
        0.95,
        5.55,
        2.55,
        1.55,
        title="I/O + Expansion",
        lines=[
            "3x Thunderbolt 4",
            "HDMI, SDXC",
            "3.5 mm, MagSafe 3",
        ],
        fc=COLORS["tile_fc"],
        ec=COLORS["tile_ec"],
        title_size=9.8,
        body_size=8.55,
    )

    add_round_box(
        ax,
        6.5,
        5.55,
        2.55,
        1.55,
        title="Storage",
        lines=[
            "512 GB SSD",
            "Local telemetry logs",
            "Swap / file activity",
        ],
        fc=COLORS["tile_fc"],
        ec=COLORS["tile_ec"],
        title_size=9.8,
        body_size=8.55,
    )

    add_round_box(
        ax,
        0.95,
        3.65,
        8.1,
        1.2,
        title="Connectivity + Sensing",
        lines=[
            "Wi-Fi 6E, Bluetooth 5.3, 1080p camera, six-speaker audio, and three-mic array"
        ],
        fc=COLORS["tile_fc"],
        ec=COLORS["tile_ec"],
        title_size=10.0,
        body_size=8.7,
        align="center",
    )

    add_round_box(
        ax,
        0.95,
        1.65,
        8.1,
        1.35,
        title="DICE-visible subsystem scope",
        lines=[
            "CPU complex, GPU / display path, Neural Engine, unified memory, SSD / storage, power / thermal behavior, and I/O / network activity"
        ],
        fc=COLORS["footer_fc"],
        ec=COLORS["footer_ec"],
        title_size=10.1,
        body_size=8.55,
        align="center",
    )

    connect(ax, 5.0, 10.15, 5.0, 8.70)
    connect(ax, 3.50, 9.10, 2.95, 8.60)
    connect(ax, 6.50, 9.10, 7.05, 8.60)
    connect(ax, 2.95, 6.32, 3.50, 6.32)
    connect(ax, 7.05, 6.32, 6.50, 6.32)
    connect(ax, 5.0, 5.35, 5.0, 4.85)
    connect(ax, 5.0, 3.65, 5.0, 3.00)

    ax.text(
        5.0,
        0.65,
        "Paper test configuration: M2 Pro / 16 GB unified memory / 512 GB SSD",
        ha="center",
        va="center",
        fontsize=8.65,
        color=COLORS["muted"],
        fontweight="bold",
    )

def draw_tier_mapping_context(ax) -> None:
    add_round_box(
        ax,
        0.35,
        0.90,
        9.3,
        11.70,
        fc=COLORS["outer_fc"],
        ec=COLORS["outer_ec"],
        rounding=0.28,
        lw=1.8,
    )

    add_round_box(
        ax,
        0.70,
        11.55,
        8.60,
        0.95,
        title="MacBook Pro (16-inch, 2023): Tier-Aware DICE View",
        lines=["Observability mapped onto subsystem-level hardware context"],
        fc=COLORS["title_fc"],
        ec=COLORS["title_ec"],
        title_color=COLORS["title_text"],
        text_color=COLORS["title_text"],
        title_size=11.5,
        body_size=8.8,
        align="center",
        rounding=0.20,
        wrap_width=42,
    )

    add_round_box(
        ax,
        0.80,
        9.85,
        8.40,
        1.25,
        title="Tier-0: Unprivileged OS telemetry",
        lines=[
            "CPU load and time mix, scheduler pressure, memory and swap, disk I/O, and network activity"
        ],
        fc=COLORS["tier0_fc"],
        ec=COLORS["tier0_ec"],
        title_size=10.1,
        body_size=8.65,
        align="center",
        wrap_width=56,
    )

    add_round_box(
        ax,
        0.80,
        8.20,
        8.40,
        1.25,
        title="Tier-1: OS-mediated hardware proxies",
        lines=[
            "CPU and GPU power, frequency, temperature, residency, and ANE-visible power or activity proxies"
        ],
        fc=COLORS["tier1_fc"],
        ec=COLORS["tier1_ec"],
        title_size=10.1,
        body_size=8.6,
        align="center",
        wrap_width=57,
    )

    add_round_box(
        ax,
        0.80,
        6.55,
        8.40,
        1.25,
        title="Tier-2: Optional profiler-derived runtime evidence",
        lines=[
            "xctrace or Instruments execution density, runtime placement, concurrency, and timing structure"
        ],
        fc=COLORS["tier2_fc"],
        ec=COLORS["tier2_ec"],
        title_size=10.0,
        body_size=8.55,
        align="center",
        wrap_width=57,
    )

    add_round_box(
        ax,
        0.80,
        3.10,
        8.40,
        2.40,
        title="Apple M2 Pro platform blocks visible to DICE",
        lines=[],
        fc=COLORS["soc_fc"],
        ec=COLORS["soc_ec"],
        title_size=10.4,
        body_size=8.8,
        align="center",
        rounding=0.22,
        lw=1.7,
    )

    add_round_box(
        ax,
        1.05,
        3.55,
        2.20,
        1.35,
        title="CPU complex",
        lines=["12-core CPU and scheduler-facing behavior"],
        fc=COLORS["tile_fc"],
        ec=COLORS["tile_ec"],
        title_size=9.5,
        body_size=8.25,
        align="center",
        wrap_width=22,
    )

    add_round_box(
        ax,
        3.90,
        3.55,
        2.20,
        1.35,
        title="GPU / display",
        lines=["19-core GPU and display path including external monitor load"],
        fc=COLORS["tile_fc"],
        ec=COLORS["tile_ec"],
        title_size=9.5,
        body_size=8.15,
        align="center",
        wrap_width=22,
    )

    add_round_box(
        ax,
        6.75,
        3.55,
        2.20,
        1.35,
        title="Neural Engine",
        lines=["16-core ANE activity when visible through software proxies"],
        fc=COLORS["tile_fc"],
        ec=COLORS["tile_ec"],
        title_size=9.5,
        body_size=8.10,
        align="center",
        wrap_width=22,
    )

    add_round_box(
        ax,
        1.05,
        1.65,
        2.65,
        1.10,
        title="Unified memory",
        lines=["16 GB shared pool and bandwidth pressure"],
        fc=COLORS["tile_fc"],
        ec=COLORS["tile_ec"],
        title_size=9.5,
        body_size=8.15,
        align="center",
        wrap_width=23,
    )

    add_round_box(
        ax,
        4.05,
        1.65,
        2.05,
        1.10,
        title="SSD / swap",
        lines=["512 GB SSD, file I/O, and swap spillover"],
        fc=COLORS["tile_fc"],
        ec=COLORS["tile_ec"],
        title_size=9.4,
        body_size=8.0,
        align="center",
        wrap_width=20,
    )

    add_round_box(
        ax,
        6.45,
        1.65,
        2.50,
        1.10,
        title="I/O and network",
        lines=["Thunderbolt, HDMI, SDXC, wireless, and external-device activity"],
        fc=COLORS["tile_fc"],
        ec=COLORS["tile_ec"],
        title_size=9.4,
        body_size=8.0,
        align="center",
        wrap_width=22,
    )

    connect(ax, 2.20, 9.85, 2.15, 4.90, color=COLORS["tier0_ec"], lw=1.7, arrowstyle="->")
    connect(ax, 3.45, 9.85, 2.35, 2.75, color=COLORS["tier0_ec"], lw=1.6, arrowstyle="->")
    connect(ax, 5.10, 9.85, 5.10, 2.75, color=COLORS["tier0_ec"], lw=1.6, arrowstyle="->")
    connect(ax, 6.90, 9.85, 7.70, 2.75, color=COLORS["tier0_ec"], lw=1.6, arrowstyle="->")

    connect(ax, 3.10, 8.20, 2.15, 4.90, color=COLORS["tier1_ec"], lw=1.7, arrowstyle="->")
    connect(ax, 5.00, 8.20, 5.00, 4.90, color=COLORS["tier1_ec"], lw=1.7, arrowstyle="->")
    connect(ax, 6.90, 8.20, 7.85, 4.90, color=COLORS["tier1_ec"], lw=1.7, arrowstyle="->")
    connect(ax, 4.30, 8.20, 2.75, 2.75, color=COLORS["tier1_ec"], lw=1.6, arrowstyle="->")

    connect(ax, 3.35, 6.55, 2.20, 4.90, color=COLORS["tier2_ec"], lw=1.7, arrowstyle="->")
    connect(ax, 5.00, 6.55, 5.00, 4.90, color=COLORS["tier2_ec"], lw=1.7, arrowstyle="->")
    connect(ax, 6.65, 6.55, 7.80, 4.90, color=COLORS["tier2_ec"], lw=1.7, arrowstyle="->")

    add_round_box(
        ax,
        0.80,
        0.40,
        8.40,
        0.80,
        title=None,
        lines=[
            "DICE localizes to visible subsystems without requiring privileged PMU or MSR access."
        ],
        fc=COLORS["footer_fc"],
        ec=COLORS["footer_ec"],
        body_size=8.55,
        align="center",
        wrap_width=70,
    )


def save_figure(fig, stem: Path) -> None:
    for suffix in ("pdf", "png"):
        fig.savefig(
            stem.with_suffix(f".{suffix}"),
            bbox_inches="tight",
            pad_inches=0.05,
            dpi=300,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate paper-ready MacBook Pro hardware-context diagrams for DICE.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Directory where the generated figures will be written.",
    )
    parser.add_argument(
        "--basic-name",
        default=DEFAULT_BASIC_NAME,
        help="Base filename for the general hardware-context figure, without extension.",
    )
    parser.add_argument(
        "--tiered-name",
        default=DEFAULT_TIERED_NAME,
        help="Base filename for the tier-aware observability figure, without extension.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = args.out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_stem = out_dir / args.basic_name
    out_stem_tiered = out_dir / args.tiered_name

    fig, ax = build_canvas()
    draw_basic_context(ax)
    save_figure(fig, out_stem)
    plt.close(fig)

    fig, ax = build_canvas()
    draw_tier_mapping_context(ax)
    save_figure(fig, out_stem_tiered)
    plt.close(fig)

    print(f"Saved {out_stem.with_suffix('.pdf')}")
    print(f"Saved {out_stem.with_suffix('.png')}")
    print(f"Saved {out_stem_tiered.with_suffix('.pdf')}")
    print(f"Saved {out_stem_tiered.with_suffix('.png')}")


if __name__ == "__main__":
    main()
