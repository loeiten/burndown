# Burndown

A simple package to create burndown charts manually.

## Usage

### Add burndowns

This creates `data/burndown.xlsx` and adds entries to the sheet `2.5-5`

```bash
python -m burndown.create_new_sprint -r 2.5 -s 5 -p 99
python -m burndown.burndown -p 90
```

### Plot

Plot the contents of `data/burndown.xlsx`

```bash
python -m burndown.plot_sprint_burndown -r 2.5 -s 5
```

Plot the contents of `data/sprint_tasks.xlsx` and `data/capacity.xlsx`.
Note that these spreadsheets are not generated by this package, but must contain sheets corresponding to the `-r` and `-s` arguments.

`data/sprint_tasks.xlsx` must contain the following columns:

```text
- Date Closed
- Original estimate
- Points
- Created
- category
- burned
- creep
- creep_category
- creep_date
```

`data/capacity.xlsx` must contain the capacity in cell `F11`.

Plotting can be done by

```bash
python -m burndown.plot_sprint -r 2.5 -s 5
python -m burndown.plot_sprint_trends
python -m burndown.plot_sprint_double_burndown -r 2.5 -s 6 -u 2022-02-18
```
