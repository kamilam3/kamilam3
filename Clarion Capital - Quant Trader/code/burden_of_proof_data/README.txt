Burden of Proof — Data
======================

30 strategy return streams. Daily net returns, ~6 years of business days.

Columns:  date, strat_001 ... strat_030
  date    ISO format (YYYY-MM-DD), business days only.
  values  daily net return in decimal (0.0123 = +1.23%).

Empty cells indicate a stream that did not exist on that date. At each date,
allocate only across the streams that exist on that date.

The streams differ in volatility. Some subsets are strongly correlated with
one another; others are close to independent. The history is not stationary
throughout. Treat the panel as your investable universe: long-only, fully
invested, weights summing to one.

See the assignment PDF (The Burden of Proof) for the task, constraints,
deliverables, and the questions your report must answer.
