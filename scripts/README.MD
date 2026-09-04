# Data analysis scripts

The raw annual (iWUE, CI/CA, CO2) and monthly (CRU TS 4.09 climate) time series were used to perform robust trend decomposition for each site, variable and selected period (Pre-industrial: 1000-1900; Industrial: 1901-2020). For each series, a modified Mann-Kendall [1, 2] test was used to determine the presence of a trend, Sen’s slope [3,4] (with confidence interval) was estimated to quantify the trend magnitude, and linear vs quadratic trend shape was selected based on significance and Akaike's information criteria [5,6]. The selected model was then used consistently to generate fitted trend values and detrended residuals.

Afterwards, iWUE and CI/CA series were correlated with climate data using three complementary approaches: raw climate vs raw iWUE (raw CI/CA), detrended climate vs detrended iWUE (detrended CI/CA), and first-order differences of the raw series. Correlations were calculated month-by-month (1-12) for each site within the configured year window (1901-1998), producing Pearson correlation coefficients (r) and p-values (p), formatted summary tables, and heatmaps with significance masking.

All input/output paths and analysis settings (periods, ignored columns, thresholds, file names) are controlled from JSON configs (`config/correlation` and `config/trend_analysis`).

iWUE and CI/CA data are currently available only upon direct request to the authors. 

To perform trend analysis use:
```{bash}
python scripts/trend_analysis.py --config config/trend_analysis/WUE.json
python scripts/trend_analysis.py --config config/trend_analysis/CI_CA.json
python scripts/trend_analysis.py --config config/trend_analysis/CRU_TS_4.09.json
```

To perform correlation analysis use:
```{bash}
python scripts/correlation.py --config config/climateXwue.json
python scripts/correlation.py --config config/climateXci_ca.json
```

Sources:

* [1] Hamed, K.H. and Rao, A.R. (1998) A Modified Mann-Kendall Trend Test for Autocorrelated Data. Journal of Hydrology, 204, 182-196. https://doi.org/10.1016/S0022-1694(97)00125-X
* [2] Hussain et al., (2019). pyMannKendall: a python package for non parametric Mann Kendall family of trend tests.. Journal of Open Source Software, 4(39), 1556, https://doi.org/10.21105/joss.01556
* [3] Sen, P. K. (1968). Estimates of the regression coefficient based on Kendall's tau. Journal of the American statistical association, 63(324), 1379-1389. doi:10.1080/01621459.1968.10480934
* [4] Theil, H. (1950). A rank-invariant method of linear and polynominal regression analysis (parts 1-3). In Ned. Akad. Wetensch. Proc. Ser. A (Vol. 53, pp. 1397-1412).
* [5] Seabold, S. and Perktold, J., 2010. statsmodels: Econometric and statistical modeling with python. 9th Python in Science Conference.
* [6] Akaike, H. (1974). A new look at the statistical model identification. IEEE Transactions on Automatic Control, AC‐19, 716–723.