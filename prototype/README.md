# RoadWatch BD — thin prototype

Phase 1 of `PLAN.md`: run a COCO-pretrained detector + ByteTrack on a road clip
and get real numbers for the thesis, with **no training and no labelled data**.

## What it produces

| Output | Use in the thesis |
|---|---|
| `results/annotated.mp4` | A frame = a Figure in §5 / §7 (boxes + track IDs + trails) |
| `results/congestion.png` | Results figure: vehicle count + occupancy over time (E1 signal) |
| `results/stats.csv` | Per-second raw numbers |
| printed summary | Fills the §7 evaluation table + the baseline note |

## Setup (once)

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python prototype.py path\to\clip.mp4
```

Useful flags:

```bash
python prototype.py clip.mp4 --stride 2        # every 2nd frame (faster on CPU)
python prototype.py clip.mp4 --max-seconds 30  # only the first 30 s
python prototype.py clip.mp4 --model yolov8m.pt # bigger, more accurate, slower
```

No clip yet? A 30–120 s static footbridge/roadside landscape clip is ideal
(`PLAN.md` §4.2). A YouTube Dhaka-traffic clip also works just to show the
pipeline runs.

## How to turn the output into thesis content

1. **Detection quality** — open `annotated.mp4`, pick 3–5 frames, hand-count
   correct / missed / wrong boxes → precision & recall.
2. **Baseline (strongest result)** — note how COCO mislabels or misses
   CNG / rickshaw / leguna / easybike. This is *why* fine-tuning on Bangladeshi
   data is needed (`PLAN.md` §5.3).
3. **Tracking** — count how many track IDs flip unnecessarily (ID switches).
4. **E1 congestion** — use `congestion.png` and `stats.csv`.

## Scope

Prototype covers **detection + tracking + a basic congestion (E1) signal**.
**E2 (bus mid-road)** and **E3 (wrong-way)** need road geometry and a flow
field — present them as "rules designed, partial evaluation" until the full
pipeline is built.

## Licence note

`ultralytics` (YOLO) is **AGPL-3.0** — fine for academic / thesis use. For a
closed-source product, switch to an Apache-2.0 detector (RF-DETR, D-FINE,
YOLOX) per `PLAN.md` §5.3. `supervision` and `ByteTrack` are permissive.
