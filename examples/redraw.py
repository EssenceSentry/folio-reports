# /// script
# dependencies = ["matplotlib>=3.9,<4"]
# ///
"""Rebuild the research starter's vector figure from its adjacent CSV."""

import csv
import sys
from math import sqrt
from pathlib import Path
from statistics import NormalDist

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

directory = Path(sys.argv[1])
with (directory / "transfers.csv").open() as source:
    observations = list(csv.DictReader(source))
ink, accent, muted = "#213639", "#8C492F", "#54686A"
fig, ax = plt.subplots(figsize=(6.1, 2.3))
fig.subplots_adjust(left=0.13, right=0.88, bottom=0.14, top=0.82)
z = NormalDist().inv_cdf(0.975)
ax.set_axisbelow(True)
ax.grid(axis="x", color="#DAE0DE", linewidth=0.65)
for row, item in enumerate(observations):
    n, missed = int(item["observed"]), int(item["missed"])
    p = missed / n
    d = 1 + z**2 / n
    middle = (p + z**2 / (2 * n)) / d
    radius = z * sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
    color = accent if item["departure"] == "08:10" else muted
    ax.plot([middle - radius, middle + radius], [row, row], color=color, lw=1.6)
    ax.scatter(p, row, color=color, s=43, zorder=3, edgecolor="white", linewidth=0.6)
    ax.text(
        0.435,
        row,
        f"{p:.0%}",
        ha="right",
        va="center",
        size=10,
        color=color,
        weight="bold" if item["departure"] == "08:10" else "normal",
    )
ax.set_yticks(range(len(observations)), [item["departure"] for item in observations])
ax.set_ylim(len(observations) - 0.45, -0.55)
ax.set_xlim(0, 0.4)
ax.set_xticks([0, 0.1, 0.2, 0.3, 0.4])
ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
ax.tick_params(axis="both", length=0, labelsize=9, colors=ink, pad=7)
ax.spines[:].set_visible(False)
fig.text(
    0.13,
    0.92,
    "Share of riders missing the connector",
    size=11,
    color=ink,
    weight="bold",
    va="top",
)
plt.rcParams["pdf.fonttype"] = 42
fig.savefig(directory / "missed-transfers.pdf", metadata={"CreationDate": None})
