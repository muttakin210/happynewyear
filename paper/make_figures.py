"""Build the paper's figures from the RoadWatch BD repository's data and results.

    python paper/make_figures.py --ml "D:/Traffic AI model project/ml"

Needs the converted BadODD (`data/processed/badodd`), the paired split (`data/processed/badodd_paired`,
from `scripts/make_group_split.py paired`) and the result JSONs in `ml/eval/results/`. Writes PDFs (for
LaTeX) and PNGs (for a quick look) to paper/figs/.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

COL = 3.45  # IEEE column width, inches
C = {"train": "#0072B2", "val": "#999999", "test": "#E69F00", "unused": "#DDDDDD", "zs": "#999999", "ft": "#0072B2"}
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["STIXGeneral", "DejaVu Serif"], "mathtext.fontset": "stix",
    "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "legend.fontsize": 7, "xtick.labelsize": 7,
    "ytick.labelsize": 7, "pdf.fonttype": 42, "ps.fonttype": 42, "axes.spines.top": False, "axes.spines.right": False,
})


def load_split_module(ml: Path):
    spec = importlib.util.spec_from_file_location("make_group_split", ml / "scripts" / "make_group_split.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["make_group_split"] = mod
    spec.loader.exec_module(mod)
    return mod


def fig_timeline(gs, ml: Path, out: Path, video: str, n_frames: int) -> None:
    """Fig. 1a: the labelled frames of one test video and the split each protocol puts them in."""
    items = sorted((it for it in gs.scan(ml.parent / "data" / "processed" / "badodd") if it.video == video),
                   key=lambda it: it.frame)[:n_frames]
    paired_test = {p.stem for p in (ml.parent / "data" / "processed" / "badodd_paired" / "clean" / "test" / "images").iterdir()}
    rows = [
        ("Official split", [it.official for it in items]),
        ("Paired: leaky", ["test" if it.stem in paired_test else "train" for it in items]),
        ("Paired: clean", ["test" if it.stem in paired_test else "unused" for it in items]),
    ]
    fig, ax = plt.subplots(figsize=(COL, 1.05))
    x = np.arange(len(items))
    for r, (_, roles) in enumerate(rows):
        ax.bar(x, 0.8, bottom=len(rows) - 1 - r - 0.4, width=0.85, color=[C[s] for s in roles], linewidth=0)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([name for name, _ in rows][::-1])
    ax.set_xlim(-0.6, len(items) - 0.4)
    ax.set_xlabel(f"first {len(items)} labelled frames of test video {video}, in time order")
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=C[k]) for k in ("train", "val", "test", "unused")]
    ax.legend(handles, ["train", "val", "test", "not used"], ncol=4, frameon=False, loc="lower center",
              bbox_to_anchor=(0.42, 1.0), handlelength=1.0, columnspacing=1.0)
    fig.savefig(out.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.02)
    fig.savefig(out.with_suffix(".png"), dpi=200, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def fig_gaps(gs, ml: Path, out: Path) -> dict:
    """Fig. 1b: for every official test image, source-video frames to the nearest train/val frame."""
    items = gs.scan(ml.parent / "data" / "processed" / "badodd")
    seen: dict[str, list[int]] = {}
    for it in items:
        if it.official != "test":
            seen.setdefault(it.video, []).append(it.frame)
    gaps = np.array([min(abs(it.frame - f) for f in seen[it.video]) for it in items if it.official == "test"])
    fig, ax = plt.subplots(figsize=(COL, 1.25))
    ax.hist(np.clip(gaps, 0, 300), bins=np.arange(0, 306, 6), color=C["train"], linewidth=0)
    med = float(np.median(gaps))
    ax.axvline(med, color="black", linewidth=0.8, linestyle="--")
    ax.text(med + 5, ax.get_ylim()[1] * 0.85, f"median {med:.0f}", fontsize=7)
    ax.set_xlabel("frames to the nearest train/val frame of the same video")
    ax.set_ylabel("test images")
    fig.savefig(out.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.02)
    fig.savefig(out.with_suffix(".png"), dpi=200, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    return {"n": int(len(gaps)), "median": med, "share_le_30": float(np.mean(gaps <= 30)),
            "share_le_60": float(np.mean(gaps <= 60)), "max": int(gaps.max())}


def fig_per_class(ml: Path, out: Path) -> None:
    """Fig. 2: per-class AP@50 on the official test split, COCO zero-shot vs fine-tuned on BadODD."""
    res = ml / "eval" / "results"
    zs = json.loads((res / "coco_rtdetr_r18_badodd_test.json").read_text())["per_class"]
    ft = json.loads((res / "bd_rtdetr_r18_badodd_test.json").read_text())["per_class"]
    classes = sorted(zs, key=lambda c: -zs[c]["n_gt"])
    label = {"cng_autorickshaw": "CNG/auto", "motorcycle": "motorbike"}
    x = np.arange(len(classes))
    fig, ax = plt.subplots(figsize=(COL, 1.55))
    ax.bar(x - 0.2, [zs[c]["ap50"] for c in classes], 0.4, color=C["zs"], label="COCO, zero-shot")
    ax.bar(x + 0.2, [ft[c]["ap50"] for c in classes], 0.4, color=C["ft"], label="fine-tuned on BadODD")
    for i, c in enumerate(classes):
        if not zs[c]["model_can_predict"]:
            ax.text(i - 0.2, 0.02, "×", ha="center", va="bottom", fontsize=7, color="#555555")
    ax.set_xticks(x)
    ax.set_xticklabels([label.get(c, c) for c in classes], rotation=35, ha="right")
    ax.set_ylabel("AP@50")
    ax.set_ylim(0, 1)
    ax.legend(frameon=False, ncol=2, loc="lower center", bbox_to_anchor=(0.5, 1.0))
    fig.savefig(out.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.02)
    fig.savefig(out.with_suffix(".png"), dpi=200, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ml", type=Path, required=True, help="the repository's ml/ folder")
    ap.add_argument("--video", default="mymensingh3", help="test video shown in the timeline")
    ap.add_argument("--frames", type=int, default=40, help="how many of its labelled frames to show")
    a = ap.parse_args()
    out = Path(__file__).resolve().parent / "figs"
    out.mkdir(exist_ok=True)
    gs = load_split_module(a.ml)
    fig_timeline(gs, a.ml, out / "split_timeline", a.video, a.frames)
    stats = fig_gaps(gs, a.ml, out / "leak_gaps")
    fig_per_class(a.ml, out / "per_class_ap")
    print("gap statistics:", stats)
    print("written", sorted(p.name for p in out.iterdir()))


if __name__ == "__main__":
    main()
