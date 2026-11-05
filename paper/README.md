# Conference paper draft: BadODD split leakage

*Same Video, Different Frame: Measuring Train–Test Leakage in a Bangladeshi Road Object Detection Benchmark*

IEEE conference format (`IEEEtran`). Draft 1, 2026-11-05. **Red text in the PDF** is either a number that has
not been measured yet or a decision for the authors.

## Files

| File | What it is |
|---|---|
| `main.tex` | the paper (8 sections, 3 figure panels, 4 tables) |
| `refs.bib` | 21 references; the comment at the top says which ones are verified |
| `figs/*.pdf` | figures for LaTeX (`*.png` are previews of the same) |
| `make_figures.py` | rebuilds `figs/` from the RoadWatch BD repository's data and results |

## Compile on Overleaf

1. Overleaf → **New Project → Upload Project**. Zip `main.tex`, `refs.bib` and the `figs/` folder (PDFs are
   enough) and upload the zip.
2. Menu → Compiler: **pdfLaTeX**. IEEEtran is built in, so nothing else needs installing.
3. Recompile. The references appear after BibTeX runs; Overleaf runs it automatically.

## Rebuild the figures

```bash
python paper/make_figures.py --ml "D:/Traffic AI model project/ml"
```

This needs the converted BadODD (`data/processed/badodd`), the paired split (`data/processed/badodd_paired`) and
`ml/eval/results/{coco,bd}_rtdetr_r18_badodd_test.json`. Run it with the `ml/.venv` Python.

## Still to do before submission

- [ ] **Kaggle runs** (`ml/notebooks/benchmark_kaggle.ipynb`):
  - session 1: `zeroshot`, `rtdetr_leaky`, `rtdetr_clean`;
  - session 2: `yolo_leaky`, `yolo_clean`.

  Then fill these from `bench/results/*.json` and `bench/leakage/*.json`:
  - Table `tab:main`;
  - Section VI-C;
  - the abstract, discussion and conclusion sentences marked red.
- [ ] **Authors and affiliations.** This is a placeholder, so don't publish it as it is.
- [ ] **Repository:** confirm `github.com/muttakin210/roadwatch-bd` is public, or change the link.
- [ ] **AI-use disclosure** in the Acknowledgment. IEEE requires one, so confirm the wording.
- [ ] **References not yet verified:** kaufman, kapoor, roberts, fieldwelsh, yolo11. Also check the DOIs of
  the ones taken from other papers' reference lists (see the comment at the top of `refs.bib`).
- [ ] **Venue:** choose the target conference. Check its page limit and whether review is double-blind. If it is
  double-blind, remove the names and the repository link for review.
- [ ] **Page count:** check it in the compiled PDF.
- [ ] **Images:** if dataset images are added (for example a qualitative figure), blur faces and number plates first.
