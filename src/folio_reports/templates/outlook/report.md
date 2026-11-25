---
title: Classification under a review budget
subtitle: A held-out evaluation of a binary review queue
author: Model Evaluation · Folio
date: November 2026
folio-cover-image: cover.jpg
---

# A threshold for a limited trial

The operating question is whether a classifier can bring enough relevant items into a manual review queue without exceeding the team's capacity.

## What the holdout supports

At the preselected threshold of 0.72, the classifier sends 480 of 8,000 items to review. Of those, 384 have a positive reference label. That gives 80% precision at a review rate of 6%, below the illustrative capacity of 600 items per batch.

The holdout contains 600 positives. The queue captures 384 and leaves 216 outside it, for a recall of 64%. Reviewers would see a higher concentration of positives than in the full batch, but a substantial share would still go unreviewed.

\columnbreak

## What the trial would measure

Run the queue beside the existing review process for a fixed period. Log actual queue size, reviewer agreement, and the time spent per item. Sample from below the threshold to check what the queue misses.

Keep the score cutoff fixed for that period. A decision about expanding review should use the observed workload and a separate evaluation sample. The holdout gives a starting point for the trial.

::: {.full-width}
## Trial design
:::

**Track the queue by batch.** Record the total scored, the number routed, and the number actually reviewed. Report disagreements between reviewers separately from classifier errors. Track review time alongside count so a change in the mix of items does not look like a change in staffing capacity.

**Follow up below the cutoff.** Draw a random sample from the unflagged pool each week and record its sampling fraction. Use that fraction when estimating missed positives, and report uncertainty separately from reviewer agreement.

::: {.recommendation title="Proposed operating decision"}
Trial the 0.72 cutoff with a 600-item review budget per 8,000 scored items. Route every flagged item to human review and sample below the cutoff to estimate missed positives.
:::

::: {.source}
Illustrative model audit. All counts and thresholds in this report are synthetic.
:::

::: {.pagebreak}
:::

# What 0.72 buys

::::::: {.metric-rail}
::::: {.rail}
::: {.metric value="80%"}
**Precision.** 384 of 480 flagged items have a positive reference label.
:::

::: {.metric value="64%"}
**Recall.** The queue captures 384 of 600 positives.
:::

::: {.metric value="6%"}
**Review rate.** 480 of 8,000 items enter the queue.
:::
:::::

::: {.reading-columns}
## Where the errors go

The 480 flagged items contain 96 false positives. They add work to the queue without yielding a positive finding. The 216 false negatives remain in the unflagged pool, so the queue cannot replace an occasional audit of that pool.

The two error types have different consequences. A false positive uses reviewer time. A false negative delays review. The decision depends on what happens after review and on the cost of leaving a positive item in the unflagged pool.

Reviewing all 8,000 items would find all 600 positives if the reference labels were reproduced perfectly. The classifier instead prioritizes a small fraction of the batch. That trade-off is appropriate only when the unflagged pool remains eligible for follow-up.

\columnbreak

## How much room is left

The 0.72 cutoff leaves space for 120 more reviews within the assumed capacity. The lower cutoff would flag 720 items and exceed that budget. The higher cutoff would save another 180 reviews but miss 120 more positives.

Use the remaining capacity for an independent sample of unflagged items. Track queue size by batch so a shift in the score distribution can trigger a review of the operating point.

If the 6% review rate held in a batch of 10,000 items, the queue would reach 600 and use the entire budget. The trial should record batch sizes as well as review rates. A larger batch can strain staffing even when the classifier behaves the same way.
:::
:::::::

::::: {.exhibit label="Queue accounting" title="Review assignments at 0.72" units="Items by reference label and review assignment"}

::: {.table-layout widths="40,20,20,20"}

| Reference label | Flagged | Not flagged | Total |
|:----------------|--------:|------------:|------:|
| Positive        |     384 |         216 |   600 |
| Negative        |      96 |       7,304 | 7,400 |
| **Total**       | **480** |   **7,520** | **8,000** |

:::
:::::

::: {.pagebreak}
:::

# Threshold sensitivity

::::: {.exhibit label="Exhibit 1" title="The middle cutoff fits the review budget and captures 384 positives" units="8,000 held-out items · thresholds and rates"}

::: {.table-layout widths="20,15,17,16,15,17"}

| Score cutoff | Flagged | True positives | Precision | Recall | Review rate |
|:-------------|--------:|---------------:|----------:|-------:|------------:|
| 0.62         |     720 |            486 |     67.5% |  81.0% |        9.0% |
| **0.72**     | **480** |        **384** | **80.0%** | **64.0%** |    **6.0%** |
| 0.82         |     300 |            264 |     88.0% |  44.0% |        3.8% |

Each row applies a score cutoff to the same synthetic holdout. Rates are rounded to one decimal place. The review budget is 600 items.
:::

:::::

::::: {.exhibit label="Exhibit 2" title="Newly included items have lower positive yield" units="Share with a positive label · by score band"}

::: {.bar label="0.82 and above · 264 of 300" value="88.0"}
:::
::: {.bar label="0.72 to below 0.82 · 120 of 180" value="66.7"}
:::
::: {.bar label="0.62 to below 0.72 · 102 of 240" value="42.5"}
:::
:::::

::: {.reading-columns}
## What changes at the lower cutoff

Reducing the cutoff to 0.62 catches 102 more positives. It also admits 138 more false positives, increasing the queue by 240. The queue would exceed capacity by 120 items.

## What changes at the higher cutoff

At 0.82 the queue falls to 300 items and precision rises to 88%. Recall falls to 44%, leaving 336 positives outside the queue. The smaller queue would suit a lower review budget.
:::

::: {.pagebreak}
:::

# Evaluation protocol

::: {.reading-columns}
## Cohort and labels

The fictional holdout has 8,000 scored items and 600 positive reference labels. Each eligible item appears once. A score ranks items for review. The example treats that score as an ordering, without interpreting it as a probability.[^scores]

The reference label is available for every item in the fixture. A real audit would define how disagreements are adjudicated and record which examples were sampled for review.

## What to record before scoring

Record the model version, the feature snapshot and the dates defining the cohort. Make the unit of analysis explicit. If several items come from the same publisher or source, reserve the entire group when constructing the holdout so that related examples cannot appear on both sides of the split.

Freeze a label guide before reviewers start. Use an adjudication procedure for disagreements and retain the original annotations. A consensus label can be useful for judging the classifier even when agreement is imperfect. The disagreement rate gives context for interpreting the errors.

\columnbreak

## Cutoffs and slices

The 0.72 cutoff and its two neighboring comparisons were specified before evaluating the holdout. The threshold exhibit reports the same denominator in each row. Precision uses the flagged set as its denominator, and recall uses the set of reference positives.

Diagnostic slices are mutually exclusive. Items missing metadata are assigned to that slice first. The remaining items are divided by length. The intervals describe binomial variation under independent items.[^slices]

## What to validate in a trial

Check whether the reference labels and score distribution stay comparable as new batches arrive. Report precision among reviewed items and include a below-cutoff sample for estimating recall. If the review process leaves some flagged items unread, record that difference explicitly so it is clear which part of the process affected the result.

Collect each metric with its denominator. Compare how often reviewers confirm positives, how many examples are left below the cutoff, and how long a batch takes to process. Those measurements can show where a queue rule needs revision and provide a baseline for a distinct evaluation sample.
:::

[^scores]: A score of 0.72 is a cutoff on the ranking scale. Probability calibration would require a separate check.

[^slices]: The displayed Wilson intervals are pointwise. If items come from repeated sources, a source-level analysis should account for clustering.

::::::: {.data-page}

# Performance by slice

At the 0.72 threshold, the missing-metadata slice has the lowest observed precision and recall. Its 100 flagged items also give it the least precise estimate.

::::: {.exhibit label="Exhibit 3" title="Precision is lower in the missing-metadata slice" units="True positives among flagged items · percent"}

:::: {.intervalplot label="Precision by slice" stub="Slice" interval-label="95% interval" min="55" max="95" reference="80"}
::: {.row label="Short items" low="80.3" value="85.7" high="89.8"}
:::
::: {.row label="Long items" low="70.8" value="77.6" high="83.3"}
:::
::: {.row label="Missing metadata" low="62.5" value="72.0" high="79.9"}
:::
::::

::: {.source}
Intervals are Wilson scores. The dashed line marks overall precision of 80% in the same holdout.
:::
:::::

## Recall in the same slices

::: {.bar label="Short items" value="75.0"}
:::
::: {.bar label="Long items" value="62.9"}
:::
::: {.bar label="Missing metadata" value="48.0"}
:::

::: {.reading-columns}
## What to inspect next

Review false negatives in the missing-metadata slice. Separate missing fields at scoring time from labels that depend on those fields.

## What would change the decision

If lower recall repeats on a new sample, test a routing rule that sends more missing-metadata items to manual review.
:::

:::::::
