# Compute cost of human work

For a given task, how much compute does an AI system spend on it, and how much
active time does a human spend on the same task? This repository holds the
dataset that pairs the two, and the explorer that plots it.

This is the frozen snapshot of 2026-09-17, tagged `v1-2026-09-17`.

## What is here

| Path | What it holds |
|---|---|
| `dataset/` | 1,684 rows over 484 tasks, the model registry, the field definitions, and a derivation note per study. Start at [`dataset/README.md`](dataset/README.md). |
| `explorer/` | The scatter plot as a single self-contained HTML page, and the script that builds it from the CSVs. |

## The explorer

`explorer/index.html` needs no server, no network and no libraries. Open it in a
browser; everything it plots is embedded in the file.

To rebuild it after editing the CSVs:

```
python3 explorer/build.py
```

That reads `dataset/points.csv` and `dataset/models.csv`, substitutes them into
`explorer/template.html`, and writes `explorer/index.html`. It uses nothing
beyond the Python standard library.

## License

[CC0 1.0 Universal](LICENSE): the compilation, the derived estimates, the notes
and the explorer code are placed in the public domain. Copy, change and
redistribute any of it, with or without attribution.

The cited sources are a different matter. This dataset is derived from published
benchmarks, papers and evaluation results that remain under their own terms,
and nothing here can waive rights in them. The waiver covers this repository's
own content.
