import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from app.isotope_data import IsotopeData
from app.site_data import SiteData
from app.utils.comparison_functions import compare_pearsonr
from matplotlib.figure import Figure, Axes
from os import listdir
from typing import Dict, Optional, List, Tuple, Callable
from zhutils.common import ComparisonFunction, OutputFunction, Months
from zhutils.dataframes import MonthlyDataFrame, SuperbDataFrame
from zhutils.stats import dropna_mannwhitneyu


class TRSIsotopesAnalyser:
    sites: List[SiteData]
    isotopes: List[IsotopeData]
    climate_data = Dict[str, MonthlyDataFrame]
    
    def __init__(
            self,
            sites_path: str,
            isotopes_path: str,
            climate_path: str
        ) -> None:
        self.sites = self._load_sites_(sites_path)
        self.isotopes = self._load_isotopes_(isotopes_path)
        self.climate_data = self._load_climate_(climate_path)
    
    def _load_sites_(self, path: str) -> List[SiteData]:
        result = []
        sites = self._load_dataframe_(path)
        if len(pd.unique(sites['Site code'])) != len(sites):
            raise Exception("Not every site codes are unique!")
        for _, row in sites.iterrows():
            result.append(SiteData(*row))
        return result
    
    def _load_isotopes_(self, path: str) -> List[IsotopeData]:
        result = []
        data =  self._load_dataframe_(path)
        for column in data.columns:
            try:
                site = self.__get_sites_by_pattern__({'code': column.split('_')[0]})[0]
                result.append(IsotopeData(data, column, site))
            except IndexError:
                continue
        return result
    
    @staticmethod
    def _load_dataframe_(path) -> pd.DataFrame:
        if path.lower().endswith('.xlsx') or path.lower().endswith('.xls'):
            return pd.read_excel(path)
        elif path.lower().endswith('.csv'):
            return pd.read_csv(path)
        else:
            raise Exception(f"Wrong spreadsheet format: {path}")
    
    def _load_climate_(
            self,
            path: str
        ) -> Dict[str, Dict[str, MonthlyDataFrame]]:
        result = {}
        for file in listdir(path):
            df = self._load_dataframe_(f'{path}/{file}')
            df = MonthlyDataFrame(df)
            result[file.split('.')[0]] = df
        return result
    
    def __get_sites_by_pattern__(self, pattern: Dict) -> List[SiteData]:
        return list(filter(lambda s: s.match(pattern), self.sites))
    
    def __get_isotopes_by_pattern__(self, isotope, site_pattern: Optional[Dict]=None) -> List[IsotopeData]:
        return list(filter(lambda i: i.match(isotope, site_pattern), self.isotopes))
    
    def boxplot(
            self,
            isotope: str,
            sort_by: Callable[[IsotopeData], int] = None,
            ylabel: Optional[str] = None,
            subplots_kws: Optional[Dict] = None,
            site_to_color: Optional[Dict[str, str]] = None,
        ) -> Tuple[Figure, Axes]:

        subplots_kws = subplots_kws or {}
        isotopes = self.__get_isotopes_by_pattern__(isotope)
        
        if sort_by:
            isotopes = sorted(isotopes, key=sort_by)
        
        data = [list(i.data['Value'].dropna()) for i in isotopes]
        labels = [i.site.code for i in isotopes]

        fig, axes = plt.subplots(**subplots_kws)
        bp = axes.boxplot(
            data
        )

        if site_to_color:
            
            colors = [site_to_color[code] for code in labels]

            for el in ['boxes']:
                for patch, color in zip(bp[el], colors):
                    patch.set_color(color)
        
        axes.set_xticklabels(labels, rotation=90)
        axes.set_ylabel(ylabel or isotope)
        axes.set_xlabel('Site')

        return fig, axes
    
    def mannwhitneyu(
            self,
            isotope: str,
            output_function: OutputFunction,
            highlight_from: Optional[float] = None,
            sort_by: Callable[[IsotopeData], int] = None,
        ) -> pd.DataFrame:

        isotopes = self.__get_isotopes_by_pattern__(isotope)
        
        if sort_by:
            isotopes = sorted(isotopes, key=sort_by)
        
        df = pd.concat(
            [
                i.data.rename(columns={'Value': i.site.code}).set_index('Year') 
                for i in isotopes
            ], 
            axis=1
        ).reset_index()

        return SuperbDataFrame(
                df.
                drop(columns=['Year'])
            ).\
            corr_and_p_values(
                highlight_from=highlight_from,
                corr_function=dropna_mannwhitneyu,
                output_function=output_function
            )
    
    def mannwhitneyu_heatmap(
            self,
            isotope,
            isotope_title: str,
            sort_by: Callable[[IsotopeData], int] = None,
            site_to_color: Optional[Dict[str, str]] = None,
            clustermap_kwargs: Optional[Dict] = None
        ) -> sns.matrix.ClusterGrid:

        def print_p_values(r, p, *args, **kwargs):
            return p
        
        df = self.mannwhitneyu(isotope, print_p_values, sort_by=sort_by)

        clustermap_kwargs = {
            'yticklabels': df.index,
            'xticklabels': df.index,
            'cmap': 'Greens_r',
            'linewidths': 1,
            'linecolor': 'gray',
            'cbar_pos': (0.08, .7, .05, .18),
            'dendrogram_ratio': (0.15, 0.05),
            'vmin': 0.0, 'vmax': 0.01,
            'col_cluster': False,
            'row_cluster': False,
        } or clustermap_kwargs

        hm = sns.clustermap(
            data=df.astype(float),
            mask=df.astype(float) > 0.01,
            **clustermap_kwargs
        )

        if site_to_color:
            for yticklabel in hm.ax_heatmap.get_yticklabels():
                yticklabel.set_color(site_to_color[yticklabel.get_text()])

            for xticklabel in hm.ax_heatmap.get_xticklabels():
                xticklabel.set_color(site_to_color[xticklabel.get_text()])

        hm.ax_heatmap.set_title('Mann-Whitneyu for ' + isotope_title, fontsize=20)
        hm.ax_heatmap.set_xlabel('Site code', fontsize=16)
        hm.ax_heatmap.xaxis.set_tick_params(labelsize=16, rotation=45)
        hm.ax_heatmap.yaxis.set_tick_params(labelsize=16, rotation=0)

        hm.ax_heatmap.set_ylabel('Site code', fontsize=16)
        hm.ax_cbar.set_ylabel('P-value')
        hm.ax_cbar.yaxis.tick_left()
        hm.ax_cbar.yaxis.set_label_position("left")

        return hm
    
    def compare_with_climate(
            self,
            isotope: str,
            climate_index: str,
            compare_by: ComparisonFunction = compare_pearsonr,
            sort_by: Callable[[IsotopeData], int] = None,
            start_year: Optional[int] = None,
            end_year: Optional[int] = None
        ) -> pd.DataFrame:
        """
        Params:
            isotope: isotope name (13C, 2H, 18O, etc.)
            climate_index: climate index name (Temperature, Precipitation, VPD, etc.)
            compare_by: comparison function (default: pearson correlation)
            sort_by: sort function for isotopes (by lat \ lon, name etc.)
            start_year: beginning of comparison period
            end_year: ending of comparison period
        Returns:
            pd.Dataframe with columns:
                Site Code: str
                Month: str
                Stat: float
                P-value: float
        """

        isotopes = self.__get_isotopes_by_pattern__(isotope)
        
        if sort_by:
            isotopes = sorted(isotopes, key=sort_by)
        
        dfs = []

        for i in isotopes:
            
            i_data = i.data
            clim_data = self.climate_data.get(i.site.station_name)

            if clim_data is None:
                continue

            if climate_index not in clim_data.columns:
                continue

            if start_year and end_year:
                i_data = i_data[
                    (start_year <= i_data['Year']) & (i_data['Year'] <= end_year)
                ]
            
            prev_year = clim_data.compare_with(
                other=i_data,
                using=compare_by,
                clim_index=climate_index,
                previous_year=True
            )
            curr_year = clim_data.compare_with(
                other=i_data,
                using=compare_by,
                clim_index=climate_index,
                previous_year=False
            )

            prev_year['Month'] = prev_year['Month'].apply(lambda x: f'{Months(x).name} prev')
            curr_year['Month'] = curr_year['Month'].apply(lambda x: Months(x).name)

            df = pd.concat([prev_year, curr_year])
            df['Site Code'] = i.site.code
            dfs.append(df)
        
        result = pd.concat(dfs).reset_index(drop=True)
        result.insert(0, 'Site Code', result.pop('Site Code'))

        return result
    
    def _get_wide_comparison_(
            self,
            isotopes: List[str],
            climate_index: str,
            prev_months: List[int],
            curr_months: List[int],
            compare_by: ComparisonFunction = compare_pearsonr,
            sort_by: Callable[[IsotopeData], int] = None,
            start_year: Optional[int] = None,
            end_year: Optional[int] = None
        ) -> Tuple[pd.DataFrame, pd.DataFrame]:

        months = [f'{Months(i).name} prev' for i in prev_months] \
               + [Months(i).name for i in curr_months]

        stats = []
        p_vals = []

        for isotope in isotopes:

            df = self.compare_with_climate(
                isotope,
                climate_index,
                compare_by=compare_by,
                sort_by=sort_by,
                start_year=start_year,
                end_year=end_year
            )

            stats_wide = df.pivot(index='Site Code', values='Stat', columns='Month')[months]
            p_values_wide = df.pivot(index='Site Code', values='P-value', columns='Month')[months]

            isotopes_data = self.__get_isotopes_by_pattern__(isotope)

            if sort_by:
                isotopes_data = sorted(isotopes_data, key=sort_by)
            
            site_codes = [i.site.code for i in isotopes_data if i.site.code in stats_wide.index]

            stats_wide = stats_wide.loc[site_codes]
            p_values_wide = p_values_wide.loc[site_codes]
            
            stats_wide.index = [f'{isotope}_{el}' for el in stats_wide.index]
            p_values_wide.index = [f'{isotope}_{el}' for el in p_values_wide.index]

            stats.append(stats_wide)
            p_vals.append(p_values_wide)

        stats = (
            pd.
            concat(stats).
            rename(columns={f'{Months(i).name} prev': Months(i).name for i in prev_months})
        )

        p_vals = (
            pd.
            concat(p_vals).
            rename(columns={f'{Months(i).name} prev': Months(i).name for i in prev_months})
        )

        return stats, p_vals
    
    def heatmap(
            self,
            isotopes: List[str],
            climate_index: str,
            prev_months: List[int],
            curr_months: List[int],
            isotope_to_color: Dict[str, str],
            compare_by: ComparisonFunction = compare_pearsonr,
            sort_by: Callable[[IsotopeData], int] = None,
            start_year: Optional[int] = None,
            end_year: Optional[int] = None,
            min_p_value: float = 0.05,
            clustermap_kwargs: Optional[Dict] = None
        ) -> sns.matrix.ClusterGrid:

        stats, mask = self._get_wide_comparison_(
            isotopes,
            climate_index,
            prev_months,
            curr_months,
            compare_by,
            sort_by,
            start_year,
            end_year
        )

        row_colors = [isotope_to_color[i.split('_')[0]] for i in stats.index]

        clustermap_kwargs = {
            'row_colors': row_colors,
            'cmap': "seismic",
            'col_cluster': False,
            'row_cluster': False,
            'linewidths': 1,
            'linecolor': 'gray',
            'cbar_pos': (0.12, .7, .05, .18),
            'cbar_kws': dict(ticks=[-.6, -.3, 0, .3, .6]),
            'vmin': -0.7, 'vmax': 0.7,
            'dendrogram_ratio': (0.2, 0.05)
        } or clustermap_kwargs

        hm = sns.clustermap(
            data=stats.fillna(0),
            mask=mask.fillna(1) > min_p_value,
            yticklabels=stats.index,
            **clustermap_kwargs
        )
        hm.ax_heatmap.set_title(climate_index, fontsize = 20)
        hm.ax_heatmap.set_xlabel('Month', fontsize = 16)
        hm.ax_heatmap.set_xticklabels(hm.ax_heatmap.get_xticklabels(), rotation = 45)
        hm.ax_heatmap.yaxis.set_tick_params(labelsize=10)

        hm.ax_heatmap.set_ylabel('Site code', fontsize = 16)
        hm.ax_cbar.set_ylabel('Pearson R')
        hm.ax_cbar.yaxis.tick_left()
        hm.ax_cbar.yaxis.set_label_position("left")

        # TODO: get rid of the hard-coded values

        text_pos = max(hm.ax_row_colors.get_ylim())/2
        hm.ax_row_colors.text(-3.7, text_pos-2, '$-$ $\delta^{2}H$', fontsize = 16)
        hm.ax_row_colors.text(-3.7, text_pos, '$-$ $\delta^{13}C$', fontsize = 16)
        hm.ax_row_colors.text(-3.7, text_pos+2, '$-$ $\delta^{18}O$', fontsize = 16)
        hm.ax_row_colors.add_patch(plt.Rectangle((-5, text_pos-2-1+.15), 1, 1,facecolor='#2DFAA5', clip_on=False,linewidth = 1))
        hm.ax_row_colors.add_patch(plt.Rectangle((-5, text_pos-1+.15), 1, 1,facecolor='#E3D41E', clip_on=False,linewidth = 1))
        hm.ax_row_colors.add_patch(plt.Rectangle((-5, text_pos+2-1+.15), 1, 1,facecolor='#FA5D2A', clip_on=False,linewidth = 1))

        return hm
