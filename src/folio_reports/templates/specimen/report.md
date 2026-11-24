---
title: An extra hour after six
subtitle: A working specimen for reports on the East Room pilot
author: Library planning office
date: November 2026
bibliography: references.bib
reference-section-title: Method reference
---

::: {.summary}
Test a later closing time at the East Room on Tuesdays and Thursdays. The current evidence describes when readers arrive. A trial can tell the library whether the extra hour is worth staffing.
:::

::: {.metric value="36%"}
**Evening arrivals** among 200 visits in the illustrative count. Seventy-two visits began after 18:00.
:::

::::: {.scorecard}
::: {.measure value="200" label="Observed visits"}
Four weeks of desk logs.
:::
::: {.measure value="72" label="Evening visits"}
Arrivals after 18:00.
:::
::: {.measure value="8" label="Pilot shifts"}
Two late closes each week.
:::
:::::

::: {.finding title="What the desk recorded"}
Most evening arrivals came in the final half hour. Several readers asked to finish a task when the closing announcement began.
:::

::: {.recommendation}
Pilot a 19:30 close twice a week for one month. Use the west entrance so one desk can cover entry and returns.
:::

::: {.source}
Source: synthetic desk counts and illustrative staff notes. Every page uses the same fictional pilot.
:::

::: {.pagebreak}
:::

# Reading the evening count

The distribution below uses all 200 visits. The three bars share a zero baseline and a 100% scale.

::: {.bar label="Before 17:00" value="40"}
:::
::: {.bar label="17:00 to 18:00" value="24"}
:::
::: {.bar label="After 18:00" value="36"}
:::

## How precise is the evening share?

::: {.interval label="Evening arrivals · 95% Wilson interval" low="29.7" value="36" high="42.9"}
:::

## How did the evening count change?

::: {.trend label="Evening visits per week" min="0" max="30" start="Week 1" end="Week 4" values="12,16,20,24"}
:::

| Week | All visits | Evening visits |
|:-----|-----------:|---------------:|
| 1    | 50         | 12             |
| 2    | 50         | 16             |
| 3    | 50         | 20             |
| 4    | 50         | 24             |

::: {.source}
The four values in the line chart sum to 72. The table preserves each count for readers who need the exact value.
:::

::: {.pagebreak}
:::

# Comparing the operating choices

Approval is [Pending review]{.status} until the branch manager signs the shift plan.

::::: {.comparison}
::: {.column title="Keep the current hours"}
Close at 18:30 every day. Staffing stays predictable. Readers who arrive late have little time to use the desks.
:::
::: {.column title="Try two late evenings"}
Keep the East Room open until 19:30 on two days. Measure additional seat use and the work required to close.
:::
:::::

::: {.decision title="Decision for the branch manager"}
Authorize four weeks of the two-evening pilot. Retain ordinary closing times on the other weekdays.
:::

::: {.divider title="Pilot calendar"}
:::

::: {.milestone when="Week 0 · Prepare"}
Brief the evening team and record usual closing workloads.
:::
::: {.milestone when="Weeks 1–4 · Operate"}
Record entries, occupied seats at 19:00, and paid staff time.
:::
::: {.milestone when="Week 5 · Review"}
Compare late-day usage, staffing cost, and any adverse incidents.
:::

::: {.risk title="Watch the closing shift"}
A later finish may disrupt the next morning's opening. Check actual clock-out time alongside scheduled hours.
:::

::: {.pagebreak}
:::

# Documenting the method

::: {.definition title="Evening arrival"}
A visit beginning after 18:00. Count a returning visitor as a second visit only if a new entry is registered.
:::

::: {.method title="Estimate the evening share"}
Divide evening arrivals by registered visits for the same observation window. Report the counts with the estimate.
:::

$$
\hat p=\frac{\sum_w e_w}{\sum_w n_w}=\frac{72}{200}=0.36
$$

~~~python
evening = [12, 16, 20, 24]
observed = [50, 50, 50, 50]
share = sum(evening) / sum(observed)
~~~

::: {.assumption}
The example interval uses independent visits. A real study should retain day identifiers so the analyst can assess clustering.
:::

::: {.limitation}
Four weeks of baseline data cannot establish whether longer hours cause more visits. Weather, events, and exam schedules may change demand.[^window]
:::

[^window]: Keep the same weekday composition when comparing observation windows.

The interval on the preceding data page uses Wilson's score method [@wilson1927].

::: {.pagebreak}
:::

# Handing the pilot to the evening team

![Evening route through the East Room. One desk can see both the west entrance and the study tables. The diagram is illustrative.](east-room.pdf){width=90%}

::: {.pullquote by="Evening desk lead · illustrative interview"}
The last readers tend to need a quiet place to finish, even after the returns desk has emptied.
:::

::: {.action owner="Evening supervisor · Before the first shift"}
Confirm the exit route, assign a relief contact, and post the two pilot evenings at the entrance.
:::

::: {.flow}
1. **Open** the desk log.
2. **Count** occupied seats at 19:00.
3. **Close** the room and record paid time.
:::

::: {.check state="done"}
The desk log records the arrival time and the day.
:::
::: {.check state="open"}
A relief contact has acknowledged the new closing time.
:::

::: {.note title="Where to file the records"}
Put each completed shift sheet with the corresponding opening log.
:::

::: {.signature name="Branch manager"}
Pilot authorization and date
:::

::: {.appendix}
:::

# Counts behind the pilot

This matrix breaks the same 72 evening visits down by weekday. Each week's six counts add up to the corresponding total in the line chart. Darker cells indicate more visits on a common scale from zero to eight.

::::: {.heatmap label="Evening arrivals by day" stub="Week" columns="Mon|Tue|Wed|Thu|Fri|Sat" min="0" max="8"}
::: {.row label="Week 1" values="1,3,1,3,2,2"}
:::
::: {.row label="Week 2" values="2,4,2,4,2,2"}
:::
::: {.row label="Week 3" values="2,5,3,6,2,2"}
:::
::: {.row label="Week 4" values="3,7,3,7,2,2"}
:::
:::::

## How long did a visit last?

::: {.distribution label="Visit duration in minutes" min="0" max="90" summary="4,12,23,38,76"}
:::

The five numbers are the minimum, first quartile, median, third quartile and maximum of an illustrative duration distribution. The box spans the middle half of visits. The central line marks the median.

## What the desk log needs

Arrival
: Local time when a visitor enters the room.

Departure
: Local time when that visit ends.

Shift identifier
: The date and scheduled closing time, retained for comparisons between days.
