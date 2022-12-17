import matplotlib.pyplot as plt
import pandas as pd

from app.trs_isotopes_analyser import TRSIsotopesAnalyser
from app.config import load_config
from app.isotope_data import IsotopeData

from typing import Dict, Callable
import typer


ia : TRSIsotopesAnalyser
config: Dict
sort_by: Callable[[IsotopeData], int]


def main(config_path: str):
    
    global config
    global ia
    global sort_by

    config = load_config(config_path)

    plt.rcParams['font.size'] = config['plot_font']['size']
    plt.rcParams['font.family'] = config['plot_font']['family']

    ia = TRSIsotopesAnalyser(
        config['sites_path'],
        config['isotopes_path'],
        config['climate_path']
    )

    sort_by = lambda x: config['site_to_order'][x.site.code]


cli = typer.Typer(callback=main)


def savefig(name):
    plt.savefig(
        f'{config["save_path"]}/{name}.png',
        facecolor='white',
        transparent=False,
        dpi=300,
        bbox_inches='tight'
    )
    plt.close()


@cli.command()
def save_zscore_trends():
    for isotope in config['isotopes']:
        ia.plot_zscore_trends(
            isotope,
            config['isotope_to_name'][isotope],
            config['sites_trends'],
            **config['zscore_trends_kwargs']
        )
        savefig(f'trend_{isotope}')

        r2_and_pvalues = ia.get_trends_r2(isotope, config['sites_trends'])
        r2_and_pvalues = pd.DataFrame(r2_and_pvalues)
        r2_and_pvalues.insert(0, 'Stat', ('R^2', 'p-value'))
        r2_and_pvalues.to_csv(f'{config["save_path"]}/trend_r2_{isotope}.csv', index=False)


@cli.command()
def save_heatmaps():
    for clim_index in config['clim_indexes']:

        hm = ia.heatmap(
            config['isotopes'],
            clim_index,
            range(9, 13),
            range(1, 9),
            config['isotope_to_color'],
            sort_by=sort_by,
            **config['heatmap_kwargs']
        )
        
        for yticklabel in hm.ax_heatmap.get_yticklabels():
            yticklabel.set_color(config['site_to_color'][yticklabel.get_text().split('_')[1]])
        
        savefig(f'heatmap_{clim_index}')


@cli.command()
def save_mannwhitneyu_heatmaps():
    for isotope in config['isotopes']:

        ia.mannwhitneyu_heatmap(
            isotope,
            config['isotope_to_name'][isotope],
            sort_by,
            config['site_to_color']
        )
        savefig(f'mannwhitneyu_heatmap_{isotope}')


@cli.command()
def save_boxplots():
    for isotope in config['isotopes']:
        ia.boxplot(
            isotope,
            sort_by,
            config['isotope_to_title'][isotope],
            subplots_kws={'figsize': (10, 5), 'dpi': 300},
            site_to_color=config['site_to_color']
        )
        savefig(f'boxplot_{isotope}')


@cli.command()
def save_all():
    save_zscore_trends()
    save_heatmaps()
    save_mannwhitneyu_heatmaps()
    save_boxplots()


if __name__ == '__main__':
    cli()
