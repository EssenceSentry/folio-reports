---
title: Where the morning transfer breaks
subtitle: Missed connections on four departures at Alder Junction
author: Service Planning
date: 24 November 2026
bibliography: references.bib
reference-section-title: References
---

# One departure accounts for nearly half the misses

::: {.prose}
The 08:10 connector left before 29 of its 100 connecting riders reached the stop. Between 8 and 12 riders missed each neighboring departure. Across the four departures, the 08:10 accounted for 29 of the 60 missed connections.
:::

![Missed transfers per 100 connecting riders. Whiskers give 95% Wilson intervals under a working assumption of independent riders.](missed-transfers.pdf){width=100%}

::: {.prose}
The pattern suggests a targeted dispatch trial. A permanent timetable change needs a different piece of evidence: how much waiting time the hold would save, after accounting for passengers already on the connector.
:::

::: {.source}
Illustrative case. All four departure groups contain synthetic observations.
:::

\newpage

# What a short hold could recover

::: {.prose}
Of the 29 riders who missed the 08:10 connector, 18 reached the stop within 90 seconds of departure. Recovering all 18 transfers would lower the miss rate across the four departures from 15% to 10.5%. That is an upper bound. The driver may already have left the bay, and a delay could cost riders their next transfer.
:::

::: {.table-layout widths="19,25,18,38"}

| **Departure** | **Observed riders** | **Missed** | **Arrived within 90 s¹** |
|:----------|----------------:|-------:|-----------------------:|
| 07:10     |             100 |      8 |                      3 |
| 07:40     |             100 |     12 |                      5 |
| 08:10     |             100 |     29 |                     18 |
| 08:40     |             100 |     11 |                      4 |
| **Total** |         **400** | **60** |                 **30** |

¹ Riders who reached the bay after the connector left, but within 90 seconds of departure. The denominator for the miss rate includes everyone attempting to transfer.
:::

# What the intervals capture

::: {.prose}
For each departure, the point estimate is $\hat p=m/n$, where $m$ is missed transfers and $n$ is observed riders. Figure 1 uses the score interval described by @wilson1927. It describes sampling variation under independence. Riders sharing a late feeder can miss together. A field study should record feeder and day identifiers so its uncertainty estimates can account for that clustering.
:::

# What to measure in the pilot

::: {.prose}
Alternate the hold policy across weekdays. Log arrivals, actual holds and the onboard passenger count. Compare passenger-minutes saved for transferring riders with passenger-minutes added for through riders. Record missed downstream connections separately because a short hold can trigger a much longer wait.
:::
