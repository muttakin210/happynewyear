"""
RoadWatch BD -- thin prototype (PLAN.md Phase 1).

Runs a COCO-pretrained detector + ByteTrack on a road clip and produces, with
no training and no labelled data:

  1. annotated.mp4   -- boxes, track IDs and track trails (use a frame as a thesis Figure)
  2. congestion.png  -- vehicle count + congestion proxy over time (Results figure)
  3. stats.csv       -- per-second numbers
  4. a printed summary with the headline numbers for the thesis table

This is intentionally minimal: detection + tracking + a simple E1-style
congestion signal. E2 (bus mid-road) and E3 (wrong-way) need road geometry and
a flow field and are left for the full pipeline.

Usage:
    python prototype.py path/to/clip.mp4
    python prototype.py path/to/clip.mp4 --out results --model yolov8s.pt --stride 1
"""

import argparse
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

import cv2
import numpy as np

# COCO class ids we treat as "vehicles / road users".
# NOTE: COCO has NO class for CNG / rickshaw / leguna / easybike. That gap is
# exactly the motivation for fine-tuning on Bangladeshi data (PLAN.md 4, 5.3) --
# the prototype makes it visible rather than hiding it.
VEHICLE_COCO_IDS = {
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}


def parse_args():
    ap = argparse.ArgumentParser(description="RoadWatch BD thin prototype")
    ap.add_argument("video", help="path to the input clip (mp4/mov/webm)")
    ap.add_argument("--out", default="results", help="output folder (default: results)")
    ap.add_argument("--model", default="yolov8s.pt",
                    help="Ultralytics model weights (auto-downloaded; default yolov8s.pt)")
    ap.add_argument("--conf", type=float, default=0.25, help="detection confidence threshold")
    ap.add_argument("--stride", type=int, default=1,
                    help="process every Nth frame (raise to go faster on CPU)")
    ap.add_argument("--max-seconds", type=float, default=0,
                    help="stop after this many seconds of video (0 = whole clip)")
    return ap.parse_args()


def main():
    args = parse_args()

    video_path = Path(args.video)
    if not video_path.exists():
        sys.exit(f"ERROR: video not found: {video_path}")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---- lazy imports so a missing package gives a clear message ----
    try:
        from ultralytics import YOLO
        import supervision as sv
    except ImportError as e:
        sys.exit(f"ERROR: missing package ({e}). Run: pip install -r requirements.txt")

    print(f"[1/4] loading model {args.model} ...")
    model = YOLO(args.model)

    # Tracking is done by Ultralytics' built-in ByteTrack (model.track) rather
    # than supervision's tracker, which was removed in supervision >= 0.30.
    box_ann = sv.BoxAnnotator(thickness=2)
    trace_ann = sv.TraceAnnotator(thickness=2, trace_length=30)
    label_ann = sv.LabelAnnotator(text_scale=0.4)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        sys.exit(f"ERROR: could not open video: {video_path}")

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    frame_area = float(w * h)

    print(f"      video: {w}x{h} @ {fps:.1f} fps, {total_frames} frames")

    out_video = out_dir / "annotated.mp4"
    writer = cv2.VideoWriter(str(out_video), cv2.VideoWriter_fourcc(*"mp4v"),
                             fps / max(args.stride, 1), (w, h))

    # ---- accumulators for the numbers ----
    per_second = defaultdict(lambda: {"counts": [], "occ": [], "classes": Counter()})
    class_totals = Counter()
    track_last_class = {}        # tracker_id -> last class, to spot class flips
    id_switch_like = 0           # a track whose class changed = likely ID confusion
    seen_ids = set()
    frames_done = 0

    print("[2/4] detecting + tracking ...")
    frame_idx = -1
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame_idx += 1
        if frame_idx % args.stride != 0:
            continue

        t_sec = int(frame_idx / fps)
        if args.max_seconds and t_sec >= args.max_seconds:
            break

        # persist=True keeps track IDs across frames; ByteTrack via ultralytics.
        result = model.track(frame, conf=args.conf, persist=True,
                             tracker="bytetrack.yaml", verbose=False)[0]
        det = sv.Detections.from_ultralytics(result)

        # keep only road-user classes
        if det.class_id is not None and len(det) > 0:
            keep = np.isin(det.class_id, list(VEHICLE_COCO_IDS))
            det = det[keep]

        n = len(det)
        # occupancy proxy: total box area / frame area (rough E1 signal; the full
        # pipeline uses union of ground footprints normalised per row -- PLAN.md 6.2)
        if n > 0 and det.xyxy is not None:
            boxes = det.xyxy
            areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
            occ = float(np.clip(areas.sum() / frame_area, 0, 1))
        else:
            occ = 0.0

        per_second[t_sec]["counts"].append(n)
        per_second[t_sec]["occ"].append(occ)

        labels = []
        if n > 0:
            tids = det.tracker_id if det.tracker_id is not None else [None] * n
            for tid, cid in zip(tids, det.class_id):
                name = VEHICLE_COCO_IDS.get(int(cid), str(cid))
                per_second[t_sec]["classes"][name] += 1
                class_totals[name] += 1
                if tid is None:
                    labels.append(name)
                    continue
                tid = int(tid)
                labels.append(f"#{tid} {name}")
                seen_ids.add(tid)
                if tid in track_last_class and track_last_class[tid] != cid:
                    id_switch_like += 1
                track_last_class[tid] = cid

        frame = trace_ann.annotate(frame, det)
        frame = box_ann.annotate(frame, det)
        if labels:
            frame = label_ann.annotate(frame, det, labels)
        writer.write(frame)

        frames_done += 1
        if frames_done % 50 == 0:
            print(f"      ...{frames_done} frames, t={t_sec}s, vehicles now={n}")

    cap.release()
    writer.release()

    # ---- condense to per-second rows ----
    seconds = sorted(per_second)
    rows = []
    for s in seconds:
        c = per_second[s]["counts"]
        o = per_second[s]["occ"]
        rows.append({
            "second": s,
            "avg_vehicles": sum(c) / len(c) if c else 0,
            "max_vehicles": max(c) if c else 0,
            "avg_occupancy": sum(o) / len(o) if o else 0,
        })

    # ---- write stats.csv ----
    csv_path = out_dir / "stats.csv"
    with open(csv_path, "w", newline="") as f:
        wri = csv.DictWriter(f, fieldnames=["second", "avg_vehicles", "max_vehicles", "avg_occupancy"])
        wri.writeheader()
        for r in rows:
            wri.writerow({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})

    # ---- congestion.png ----
    print("[3/4] plotting congestion ...")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        xs = [r["second"] for r in rows]
        veh = [r["avg_vehicles"] for r in rows]
        occ = [r["avg_occupancy"] for r in rows]

        fig, ax1 = plt.subplots(figsize=(9, 4))
        ax1.plot(xs, veh, color="#1f3864", label="avg vehicles")
        ax1.set_xlabel("time (s)")
        ax1.set_ylabel("avg vehicles in frame", color="#1f3864")
        ax2 = ax1.twinx()
        ax2.plot(xs, occ, color="#b00000", linestyle="--", label="occupancy proxy")
        ax2.set_ylabel("occupancy (box area / frame)", color="#b00000")
        fig.suptitle("RoadWatch BD prototype -- congestion over time")
        fig.tight_layout()
        fig.savefig(out_dir / "congestion.png", dpi=120)
        plt.close(fig)
    except ImportError:
        print("      (matplotlib not installed -- skipped congestion.png)")

    # ---- printed summary (copy these into the thesis Section 7 table) ----
    dur = seconds[-1] + 1 if seconds else 0
    all_counts = [n for s in seconds for n in per_second[s]["counts"]]
    avg_v = sum(all_counts) / len(all_counts) if all_counts else 0
    peak_v = max(all_counts) if all_counts else 0

    print("\n[4/4] ===== SUMMARY (for thesis Section 7) =====")
    print(f"  clip duration analysed : {dur} s ({frames_done} frames)")
    print(f"  unique track IDs        : {len(seen_ids)}")
    print(f"  avg vehicles / frame    : {avg_v:.2f}")
    print(f"  peak vehicles / frame   : {peak_v}")
    print(f"  tracks that changed class (ID-confusion proxy): {id_switch_like}")
    print("  detections by COCO class:")
    for name, cnt in class_totals.most_common():
        print(f"      {name:12s} {cnt}")
    print("\n  BASELINE NOTE for the thesis:")
    print("  COCO has no class for CNG / rickshaw / leguna / easybike, so those")
    print("  vehicles are MISSED or mislabelled (often as 'car'/'motorcycle').")
    print("  That gap is the motivation for fine-tuning on DhakaAI / Poribohon-BD")
    print("  (PLAN.md 4, 5.3) and is your strongest baseline-comparison result.")
    print("\n  outputs written to:")
    print(f"      {out_video}")
    print(f"      {out_dir / 'congestion.png'}")
    print(f"      {csv_path}")


if __name__ == "__main__":
    main()
