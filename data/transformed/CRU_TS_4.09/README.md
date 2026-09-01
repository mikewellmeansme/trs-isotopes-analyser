# CRU TS 4.09 (Transformed)

All climate data files in this folder were cleaned for missing values using Python.
In the source CRU TS data, some gaps can be filled with modal (most frequent) values,
which may introduce artificial repeats in monthly site series.
The procedure checks each climate index month by month, computes the mode for each site,
and replaces mode values with `NaN` when that mode is overrepresented (more than 5% of
available records for that site in the given month).

```python
import pandas as pd

clim_indices = ["cld", "pet", "pre", "tmp", "rhm", "vpd"]

clim_data: dict[str, pd.DataFrame] = {}
for index in clim_indices:
    clim_data[index] = pd.read_csv(f"data/raw/CRU_TS_4.09/{index}.csv")
    clim_data[index].rename(columns=rename_sites, inplace=True)

for index in clim_indices:
	for month in range(1, 13):
		month_lines = clim_data[index]["Month"] == month
		_df = clim_data[index][month_lines]
		modes = _df.mode().iloc[0]
		for site in sites:
			if (_df[_df==modes].count() / _df.count())[site] > 0.05:
				clim_data[index].loc[month_lines & (clim_data[index][site]==modes[site]), site] = np.nan
```
