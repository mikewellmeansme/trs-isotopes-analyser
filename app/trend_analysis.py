import argparse
import json
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymannkendall as mk
import statsmodels.api as sm

warnings.filterwarnings("ignore")


plt.rcParams['font.size'] = "20"
plt.rcParams['font.family'] = "Times New Roman"

# ============================================================
# DEFAULT SETTINGS
# ============================================================

DEFAULT_CONFIG = {
    "input_file": "data.xlsx",
    "output_dir": ".",
    "output_file": "trend_analysis.xlsx",
    "detrend_output_file": "detrended_data.csv",
    "trend_output_file": "trend_data.csv",
    "alpha": 0.05,
    "smoothing_windows": [25, 50, 100],
    "periods": {
        "Pre-industrial": [1000, 1900],
        "Post-industrial": [1901, 2020]
    },
    "time_mode": "auto",
    "year_column": "Year",
    "month_column": "Month",
    "ignore_columns": ["Day"]
}

ALPHA = DEFAULT_CONFIG["alpha"]

SMOOTHING_WINDOWS = DEFAULT_CONFIG["smoothing_windows"]

PERIODS = {
    key: tuple(value)
    for key, value in DEFAULT_CONFIG["periods"].items()
}


# ============================================================
# CONFIG AND IO HELPERS
# ============================================================


def load_config(config_path: str) -> Dict[str, Any]:
    if not Path(config_path).exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}"
        )

    with open(config_path, "r", encoding="utf-8") as f:
        user_config = json.load(f)

    cfg = DEFAULT_CONFIG.copy()
    cfg.update(user_config)

    if "periods" in user_config:
        cfg["periods"] = user_config["periods"]

    cfg["alpha"] = float(cfg["alpha"])
    cfg["smoothing_windows"] = [
        int(w) for w in cfg["smoothing_windows"]
    ]
    cfg["ignore_columns"] = [
        str(c) for c in cfg.get("ignore_columns", ["Day"])
    ]

    cfg["periods"] = {
        key: tuple(value)
        for key, value in cfg["periods"].items()
    }

    return cfg


def normalize_input_files(input_spec: Any) -> List[str]:
    if isinstance(input_spec, str):
        return [input_spec]

    if isinstance(input_spec, list):
        files = []
        for path in input_spec:
            if not isinstance(path, str):
                raise ValueError(
                    "All items in input_file list must be strings."
                )
            files.append(path)
        return files

    raise ValueError(
        "input_file must be a string or a list of strings."
    )


def read_input_table(path: str) -> pd.DataFrame:
    p = Path(path)
    suffix = p.suffix.lower()

    if suffix in [".xlsx", ".xlsm", ".xls"]:
        return pd.read_excel(path)

    if suffix == ".csv":
        return pd.read_csv(path)

    raise ValueError(
        f"Unsupported input format: {path}. Use xlsx/xls/xlsm/csv."
    )


def load_and_validate_data(
    path: str,
    year_column: str,
    month_column: Optional[str] = None
) -> pd.DataFrame:
    df = read_input_table(path)

    if year_column not in df.columns:
        raise ValueError(
            f"Column '{year_column}' not found in input file: {path}"
        )

    if month_column is not None and month_column not in df.columns:
        raise ValueError(
            f"Column '{month_column}' not found in input file: {path}"
        )

    return df


def safe_sheet_name(name: str) -> str:
    cleaned = "".join(
        ch if ch not in ["\\", "/", "*", "?", ":", "[", "]"] else "_"
        for ch in name
    )
    return cleaned[:31]


def source_name_from_path(path: str) -> str:
    return Path(path).stem


def build_output_paths(cfg: Dict[str, Any], source_name: str) -> Dict[str, Path]:
    output_dir = Path(cfg["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_name = f"{source_name}__{cfg['output_file']}"
    detrend_name = f"{source_name}__{cfg['detrend_output_file']}"
    trend_name = f"{source_name}__{cfg.get('trend_output_file', 'trend_data.csv')}"
    plots_dir = output_dir / f"{source_name}__plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    return {
        "summary": output_dir / summary_name,
        "detrend_csv": output_dir / detrend_name,
        "trend_csv": output_dir / trend_name,
        "plots_dir": plots_dir
    }


def detect_time_mode(df: pd.DataFrame, cfg: Dict[str, Any]) -> str:
    mode = str(cfg["time_mode"]).lower()

    if mode in ["annual", "yearly"]:
        return "annual"

    if mode == "monthly":
        return "monthly"

    month_column = cfg["month_column"]

    if month_column in df.columns:
        return "monthly"

    return "annual"


def build_period_mask(
    df: pd.DataFrame,
    year_column: str,
    periods: Dict[str, Tuple[int, int]]
) -> pd.Series:
    mask = pd.Series(False, index=df.index)
    for start_year, end_year in periods.values():
        mask = mask | df[year_column].between(start_year, end_year)
    return mask


def apply_period_filter(df: pd.DataFrame, cfg: Dict[str, Any]) -> pd.DataFrame:
    year_column = cfg["year_column"]
    if year_column not in df.columns:
        return df.copy()

    mask = build_period_mask(df, year_column, cfg["periods"])
    return df.loc[mask].copy()

def mann_kendall_test(series: Sequence[float]) -> Dict[str, Any]:

    x = pd.Series(series).dropna()

    if len(x) < 10:
        return {
            "n": len(x),
            "trend": "insufficient",
            "p": np.nan,
            "slope": np.nan
        }

    try:
        result = mk.hamed_rao_modification_test(x)

        return {
            "n": len(x),
            "trend": result.trend,
            "p": result.p,
            "slope": result.slope
        }

    except Exception:
        return {
            "n": len(x),
            "trend": "error",
            "p": np.nan,
            "slope": np.nan
        }


def sen_slope_ci(
    series: Sequence[float],
    confidence: float = 0.95
) -> Tuple[float, float]:
    """
    Approximate confidence interval for Sen's slope
    using bootstrap resampling.
    """

    x = pd.Series(series).dropna().values

    if len(x) < 10:
        return np.nan, np.nan

    slopes = []

    for i in range(len(x)):
        for j in range(i + 1, len(x)):
            slopes.append(
                (x[j] - x[i]) / (j - i)
            )

    slopes = np.array(slopes)

    alpha = 1 - confidence

    lower = np.quantile(
        slopes,
        alpha / 2
    )

    upper = np.quantile(
        slopes,
        1 - alpha / 2
    )

    return lower, upper

# ============================================================
# TREND MODEL SELECTION
# ============================================================

def select_trend_model(data: pd.DataFrame, column: str) -> Dict[str, Any]:
    """
    Select the trend model once.

    Returns a dictionary containing:
        - MK result
        - selected shape
        - selected model type
        - fitted values
        - AIC comparison
        - turning point

    The same selected model is later used for detrending.
    """

    valid = data[["Year", column]].dropna().copy()

    # Sen's slope confidence interval
    sen_ci_low, sen_ci_high = sen_slope_ci(
        valid[column]
    )

    # --------------------------------------------------------
    # Mann-Kendall
    # --------------------------------------------------------

    mk_result = mann_kendall_test(valid[column])

    if len(valid) < 10:
        return {
            "n": len(valid),
            "mk_trend": "insufficient",
            "mk_p": np.nan,

            "sen_slope": np.nan,
            "sen_ci_low": np.nan,
            "sen_ci_high": np.nan,

            "shape": "insufficient",
            "model": "none",

            "linear_r2": np.nan,
            "quadratic_r2": np.nan,
            "quadratic_p": np.nan,

            "delta_aic": np.nan,
            "turning_year": np.nan,

            "fitted": None
        }

    # --------------------------------------------------------
    # Prepare time variable
    # --------------------------------------------------------

    year = valid["Year"].values
    y = valid[column].values

    year_mean = year.mean()
    t = year - year_mean

    # --------------------------------------------------------
    # Linear model
    # --------------------------------------------------------

    X_linear = sm.add_constant(t)

    linear_model = sm.OLS(y, X_linear).fit()

    # --------------------------------------------------------
    # Quadratic model
    # --------------------------------------------------------

    X_quad = np.column_stack([
        np.ones(len(t)),
        t,
        t ** 2
    ])

    quadratic_model = sm.OLS(y, X_quad).fit()

    delta_aic = quadratic_model.aic - linear_model.aic

    linear_r2 = linear_model.rsquared
    quadratic_r2 = quadratic_model.rsquared

    quadratic_p = quadratic_model.pvalues[2]

    b1 = quadratic_model.params[1]
    b2 = quadratic_model.params[2]

    # --------------------------------------------------------
    # Determine shape
    # --------------------------------------------------------

    if (
        delta_aic >= -2
        or quadratic_p >= ALPHA
        or abs(b2) < 1e-12
    ):

        shape = "linear"
        selected_model = "linear"
        fitted = linear_model.fittedvalues

        turning_year = np.nan

    else:

        # Location of quadratic vertex
        vertex_t = -b1 / (2 * b2)
        turning_year = year_mean + vertex_t

        year_min = year.min()
        year_max = year.max()

        # ----------------------------------------------------
        # Vertex inside observed period
        # ----------------------------------------------------

        if year_min <= turning_year <= year_max:

            if b2 > 0:
                shape = "U-shaped"
            else:
                shape = "inverted U"

            selected_model = "quadratic"
            fitted = quadratic_model.fittedvalues

        # ----------------------------------------------------
        # Vertex outside observed period
        # ----------------------------------------------------

        else:

            derivative_start = (
                b1 + 2 * b2 * (year_min - year_mean)
            )

            derivative_end = (
                b1 + 2 * b2 * (year_max - year_mean)
            )

            if derivative_start > 0 and derivative_end > 0:

                if b2 > 0:
                    shape = "accelerating increase"
                else:
                    shape = "decelerating increase"

            elif derivative_start < 0 and derivative_end < 0:

                if b2 < 0:
                    shape = "accelerating decrease"
                else:
                    shape = "decelerating decrease"

            else:
                shape = "complex"

            selected_model = "quadratic"
            fitted = quadratic_model.fittedvalues
            turning_year = np.nan

    # --------------------------------------------------------
    # Return everything needed later
    # --------------------------------------------------------

    return {
        "n": mk_result["n"],
        "mk_trend": mk_result["trend"],
        "mk_p": mk_result["p"],

        "sen_slope": mk_result["slope"],
        "sen_ci_low": sen_ci_low,
        "sen_ci_high": sen_ci_high,

        "shape": shape,
        "model": selected_model,

        "linear_r2": linear_r2,
        "quadratic_r2": quadratic_r2,
        "quadratic_p": quadratic_p,

        "delta_aic": delta_aic,
        "turning_year": turning_year,

        "fitted": pd.Series(
            fitted,
            index=valid.index
        )
    }


# ============================================================
# SMOOTHING ANALYSIS
# ============================================================

def smoothing_analysis(data: pd.DataFrame, column: str) -> List[Dict[str, Any]]:

    valid = data[["Year", column]].dropna().copy()

    results = []

    for window in SMOOTHING_WINDOWS:

        if len(valid) < window:
            results.append({
                "Window": window,
                "trend": "insufficient",
                "p": np.nan,
                "slope": np.nan
            })
            continue

        smoothed = (
            valid[column]
            .rolling(
                window=window,
                center=True
            )
            .mean()
            .dropna()
        )

        if len(smoothed) < 10:
            results.append({
                "Window": window,
                "trend": "insufficient",
                "p": np.nan,
                "slope": np.nan
            })
            continue

        try:

            result = mk.hamed_rao_modification_test(
                smoothed
            )

            results.append({
                "Window": window,
                "trend": result.trend,
                "p": result.p,
                "slope": result.slope
            })

        except Exception:

            results.append({
                "Window": window,
                "trend": "error",
                "p": np.nan,
                "slope": np.nan
            })

    return results


# ============================================================
# SMOOTHING SUMMARY
# ============================================================

def smoothing_summary(
    mk_result: Dict[str, Any],
    smoothing_results: List[Dict[str, Any]]
) -> str:
    raw_trend = mk_result["mk_trend"]
    raw_p = mk_result["mk_p"]

    if raw_trend not in ["increasing", "decreasing"]:
        return "no significant raw trend"

    if pd.isna(raw_p) or raw_p >= ALPHA:
        return "no significant raw trend"

    stable_windows = []

    for result in smoothing_results:

        if (
            result["trend"] == raw_trend
            and pd.notna(result["p"])
            and result["p"] < ALPHA
        ):
            stable_windows.append(result["Window"])

    if len(stable_windows) == len(SMOOTHING_WINDOWS):

        return (
            "stable:"
            + "/".join(map(str, stable_windows))
            + "y"
        )

    elif len(stable_windows) > 0:

        return (
            "partial: "
            + "/".join(map(str, stable_windows))
            + "y"
        )

    else:

        return "not stable"


# ============================================================
# DETRENDING
# ============================================================

def detrend_using_selected_model(
    data: pd.DataFrame,
    column: str,
    model_result: Dict[str, Any]
) -> pd.Series:

    result = data[column].copy()

    if model_result["model"] == "none":
        return result

    fitted = model_result["fitted"]

    if fitted is None:
        return result

    valid_index = fitted.index

    # Residual = observed - fitted trend
    result.loc[valid_index] = (
        data.loc[valid_index, column] - fitted
    )

    return result


# ============================================================
# CORE ANALYSIS
# ============================================================

def run_analysis_for_dataframe(
    df: pd.DataFrame,
    cfg: Dict[str, Any],
    source_name: str,
    month_value: Optional[Any] = None
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    year_column = cfg["year_column"]

    work_df = df.copy()
    work_df = work_df.sort_values(year_column).reset_index(drop=True)
    period_mask = build_period_mask(work_df, year_column, cfg["periods"])

    summary: List[Dict[str, Any]] = []
    smoothing_details: List[Dict[str, Any]] = []

    detrended_df = work_df.copy()
    trend_df = work_df.copy()

    ignored_columns = set(cfg.get("ignore_columns", ["Day"]))

    value_columns = [
        c for c in work_df.columns
        if c not in [cfg["year_column"], cfg["month_column"]]
        and c not in ignored_columns
    ]

    for column in value_columns:
        for period_name, (start_year, end_year) in cfg["periods"].items():

            mask = work_df[year_column].between(start_year, end_year)

            data = work_df.loc[
                mask,
                [year_column, column]
            ].copy()

            data = data.rename(columns={year_column: "Year"})

            trend_result = select_trend_model(data, column)

            if trend_result["fitted"] is not None:
                trend_df.loc[
                    trend_result["fitted"].index,
                    column
                ] = trend_result["fitted"].values
            else:
                trend_df.loc[data.index, column] = np.nan

            smooth_results = smoothing_analysis(data, column)

            smooth_status = smoothing_summary(
                trend_result,
                smooth_results
            )

            detrended = detrend_using_selected_model(
                data,
                column,
                trend_result
            )

            detrended_df.loc[
                mask,
                column
            ] = detrended.values

            summary.append({
                "Source": source_name,
                "Month": month_value,
                "Variable": column,
                "Period": period_name,
                "N": trend_result["n"],
                "MK trend": trend_result["mk_trend"],
                "MK p-value": trend_result["mk_p"],
                "Sen slope": trend_result["sen_slope"],
                "Sen slope CI low": trend_result["sen_ci_low"],
                "Sen slope CI high": trend_result["sen_ci_high"],
                "Shape": trend_result["shape"],
                "Selected model": trend_result["model"],
                "Linear R²": trend_result["linear_r2"],
                "Quadratic R²": trend_result["quadratic_r2"],
                "Quadratic p-value": trend_result["quadratic_p"],
                "ΔAIC (quad-linear)": trend_result["delta_aic"],
                "Turning year": trend_result["turning_year"],
                "Smoothing": smooth_status
            })

            for result in smooth_results:
                smoothing_details.append({
                    "Source": source_name,
                    "Month": month_value,
                    "Variable": column,
                    "Period": period_name,
                    "Window": result["Window"],
                    "MK trend": result["trend"],
                    "p-value": result["p"],
                    "Sen slope": result["slope"]
                })

    summary_df = pd.DataFrame(summary)
    smoothing_df = pd.DataFrame(smoothing_details)

    detrended_df = detrended_df.loc[period_mask].copy()
    trend_df = trend_df.loc[period_mask].copy()

    return summary_df, smoothing_df, detrended_df, trend_df


# ============================================================
# CREATE DATAFRAMES
# ============================================================

def make_interpretation(row: pd.Series) -> str:

    trend = row["MK trend"]
    shape = row["Shape"]
    smoothing = row["Smoothing"]

    if trend == "increasing":
        direction = "increasing"

    elif trend == "decreasing":
        direction = "decreasing"

    elif trend == "no trend":
        direction = "no significant monotonic trend"

    else:
        direction = trend

    return (
        f"{direction}; "
        f"{shape}; "
        f"{smoothing}"
    )


def finalize_result_tables(
    summary_df: pd.DataFrame,
    smoothing_df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    if not summary_df.empty:
        summary_df["Interpretation"] = summary_df.apply(
            make_interpretation,
            axis=1
        )

        summary_df["MK p-value"] = summary_df["MK p-value"].round(4)
        summary_df["Sen slope"] = summary_df["Sen slope"].round(6)
        summary_df["ΔAIC (quad-linear)"] = summary_df[
            "ΔAIC (quad-linear)"
        ].round(2)
        summary_df["Turning year"] = summary_df["Turning year"].round(0)
        summary_df["Sen slope CI low"] = summary_df[
            "Sen slope CI low"
        ].round(6)
        summary_df["Sen slope CI high"] = summary_df[
            "Sen slope CI high"
        ].round(6)
        summary_df["Linear R²"] = summary_df["Linear R²"].round(3)
        summary_df["Quadratic R²"] = summary_df["Quadratic R²"].round(3)
        summary_df["Quadratic p-value"] = summary_df[
            "Quadratic p-value"
        ].round(4)

    if not smoothing_df.empty:
        smoothing_df["p-value"] = smoothing_df["p-value"].round(4)
        smoothing_df["Sen slope"] = smoothing_df["Sen slope"].round(6)

    return summary_df, smoothing_df


def run_for_single_source(path: str, cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    source_name = source_name_from_path(path)
    year_column = cfg["year_column"]
    month_column = cfg["month_column"]

    df = load_and_validate_data(path, year_column)
    mode = detect_time_mode(df, cfg)

    all_results: List[Dict[str, Any]] = []

    print(f"[INFO] Source: {source_name} | mode={mode}")

    if mode == "annual":
        summary_df, smoothing_df, detrended_df, trend_df = run_analysis_for_dataframe(
            df,
            cfg,
            source_name=source_name,
            month_value=np.nan
        )
        all_results.append({
            "source": source_name,
            "month": None,
            "summary": summary_df,
            "smoothing": smoothing_df,
            "raw": df.copy(),
            "detrended": detrended_df,
            "trend": trend_df
        })
        return all_results

    df = load_and_validate_data(path, year_column, month_column)

    month_values = sorted(
        pd.Series(df[month_column]).dropna().unique().tolist()
    )

    total_months = len(month_values)

    for idx, month_value in enumerate(month_values, start=1):
        print(
            f"[INFO] Source: {source_name} | month {idx}/{total_months}: {month_value}"
        )
        month_mask = df[month_column] == month_value
        month_df = df.loc[month_mask].copy()

        if month_df.empty:
            continue

        summary_df, smoothing_df, detrended_df, trend_df = run_analysis_for_dataframe(
            month_df,
            cfg,
            source_name=source_name,
            month_value=month_value
        )

        all_results.append({
            "source": source_name,
            "month": month_value,
            "summary": summary_df,
            "smoothing": smoothing_df,
            "raw": month_df.copy(),
            "detrended": detrended_df,
            "trend": trend_df
        })

    return all_results


def _trend_significance_for_column(
    summary_df: pd.DataFrame,
    column: str,
    alpha: float
) -> str:
    col_rows = summary_df[summary_df["Variable"] == column].copy()
    if col_rows.empty:
        return "trend significance: unknown"

    statuses: List[str] = []

    for _, row in col_rows.iterrows():
        period = row.get("Period", "period")
        trend = row.get("MK trend", "")
        p_val = row.get("MK p-value", np.nan)

        is_sig = (
            trend in ["increasing", "decreasing"]
            and pd.notna(p_val)
            and float(p_val) < alpha
        )
        state = "significant" if is_sig else "not significant"
        statuses.append(f"{period}: {state}")

    return " | ".join(statuses)


def plot_result_set(
    result: Dict[str, Any],
    cfg: Dict[str, Any],
    output_plots_dir: Path
) -> None:
    ignored_columns = set(cfg.get("ignore_columns", ["Day"]))

    year_column = cfg["year_column"]
    month_column = cfg["month_column"]

    raw_df = result["raw"].copy()
    detrended_df = result["detrended"].copy()
    trend_df = result["trend"].copy()
    month = result["month"]

    if year_column not in detrended_df.columns:
        return

    raw_df = apply_period_filter(raw_df, cfg)
    trend_df = apply_period_filter(trend_df, cfg)
    detrended_df = apply_period_filter(detrended_df, cfg)

    if raw_df.empty or trend_df.empty or detrended_df.empty:
        return

    value_columns = [
        c for c in detrended_df.columns
        if c not in [year_column, month_column]
        and c not in ignored_columns
    ]

    for column in value_columns:
        fig, axes = plt.subplots(
            nrows=2,
            ncols=1,
            figsize=(11, 7),
            sharex=True,
            constrained_layout=True
        )

        x = raw_df[year_column]
        y_raw = raw_df[column]
        y_trend = trend_df[column]
        y_detr = detrended_df[column]

        axes[0].plot(x, y_raw, color="tab:blue", linewidth=1.0, label="Original")
        axes[0].plot(x, y_trend, color="tab:red", linewidth=1.4, label="Trend")
        axes[0].set_ylabel(column)
        axes[0].legend(loc="best")
        axes[0].grid(alpha=0.25)

        axes[1].plot(x, y_detr, color="tab:green", linewidth=1.0, label="Detrended")
        axes[1].axhline(0.0, color="black", linewidth=0.8, alpha=0.7)
        axes[1].set_xlabel(year_column)
        axes[1].set_ylabel(f"{column} detrended")
        axes[1].legend(loc="best")
        axes[1].grid(alpha=0.25)

        significance_info = _trend_significance_for_column(
            result["summary"],
            column,
            float(cfg["alpha"])
        )

        if month is None or pd.isna(month):
            fig.suptitle(f"{column} | {significance_info}")
            png_name = f"{column}.png"
        else:
            fig.suptitle(
                f"month={month} | {column} | {significance_info}"
            )
            png_name = f"M{month}__{column}.png"

        safe_name = "".join(
            ch if ch not in ['\\', '/', '*', '?', ':', '[', ']', ' '] else '_'
            for ch in png_name
        )

        out_path = output_plots_dir / safe_name
        fig.savefig(out_path, dpi=160)
        plt.close(fig)


def write_outputs_for_source(
    all_results: List[Dict[str, Any]],
    cfg: Dict[str, Any],
    source_name: str
) -> Dict[str, Path]:
    paths = build_output_paths(cfg, source_name)

    summary_tables: List[pd.DataFrame] = []
    smoothing_tables: List[pd.DataFrame] = []

    with pd.ExcelWriter(paths["summary"], engine="openpyxl") as writer:
        for result in all_results:
            summary_df, smoothing_df = finalize_result_tables(
                result["summary"].copy(),
                result["smoothing"].copy()
            )

            summary_tables.append(summary_df)
            smoothing_tables.append(smoothing_df)

            source = result["source"]
            month = result["month"]

            if month is None or pd.isna(month):
                summary_sheet = safe_sheet_name(f"Summary_{source}")
                smoothing_sheet = safe_sheet_name(f"Smooth_{source}")
            else:
                summary_sheet = safe_sheet_name(f"S_{source}_M{month}")
                smoothing_sheet = safe_sheet_name(f"Sm_{source}_M{month}")

            summary_df.to_excel(writer, sheet_name=summary_sheet, index=False)
            smoothing_df.to_excel(writer, sheet_name=smoothing_sheet, index=False)

            plot_result_set(result, cfg, paths["plots_dir"])

        if summary_tables:
            all_summary = pd.concat(summary_tables, ignore_index=True)
            all_smoothing = pd.concat(smoothing_tables, ignore_index=True)
        else:
            all_summary = pd.DataFrame()
            all_smoothing = pd.DataFrame()

        all_summary.to_excel(writer, sheet_name="Summary_all", index=False)
        all_smoothing.to_excel(writer, sheet_name="Smoothing_all", index=False)

    detrended_tables: List[pd.DataFrame] = []
    trend_tables: List[pd.DataFrame] = []

    for result in all_results:
        month = result["month"]

        detrended_df = result["detrended"].copy()
        trend_df = result["trend"].copy()

        if month is not None and not pd.isna(month):
            if "Month" in detrended_df.columns:
                detrended_df["Month"] = month
            else:
                detrended_df.insert(1, "Month", month)

            if "Month" in trend_df.columns:
                trend_df["Month"] = month
            else:
                trend_df.insert(1, "Month", month)

        detrended_tables.append(detrended_df)
        trend_tables.append(trend_df)

    if detrended_tables:
        detrended_all = pd.concat(detrended_tables, ignore_index=True)
        trend_all = pd.concat(trend_tables, ignore_index=True)

        order_columns = [
            c for c in [cfg["year_column"], cfg["month_column"]]
            if c in detrended_all.columns
        ]
        if order_columns:
            detrended_all = detrended_all.sort_values(order_columns).reset_index(drop=True)
            trend_all = trend_all.sort_values(order_columns).reset_index(drop=True)
    else:
        detrended_all = pd.DataFrame()
        trend_all = pd.DataFrame()

    detrended_all.to_csv(paths["detrend_csv"], index=False)
    trend_all.to_csv(paths["trend_csv"], index=False)

    return paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Trend analysis for annual or monthly isotope tables "
            "using JSON parameters."
        )
    )
    parser.add_argument(
        "--config",
        default="trend_analysis_config.json",
        help="Path to JSON config file."
    )
    return parser.parse_args()


def main() -> None:
    global ALPHA, SMOOTHING_WINDOWS, PERIODS

    args = parse_args()
    cfg = load_config(args.config)

    ALPHA = cfg["alpha"]
    SMOOTHING_WINDOWS = cfg["smoothing_windows"]
    PERIODS = cfg["periods"]

    input_files = normalize_input_files(cfg["input_file"])

    total_sources = len(input_files)

    print(
        f"[INFO] Start | sources={total_sources} | output_dir={cfg['output_dir']}"
    )

    for idx, path in enumerate(input_files, start=1):
        print(f"[INFO] Processing source {idx}/{total_sources}: {path}")
        source_results = run_for_single_source(path, cfg)
        if not source_results:
            print(f"[WARN] No results for source: {path}")
            continue

        source_name = source_results[0]["source"]
        paths = write_outputs_for_source(source_results, cfg, source_name)

        print(f"[INFO] Summary saved: {paths['summary']}")
        print(f"[INFO] Detrended CSV saved: {paths['detrend_csv']}")
        print(f"[INFO] Trend CSV saved: {paths['trend_csv']}")
        print(f"[INFO] Plots dir: {paths['plots_dir']}")

    print("[INFO] Done.")


if __name__ == "__main__":
    main()