# Tree-Ring Stable Isotopes Analyser

Application for tree-ring stable isotopes data analysis:

Current features:

* Correlation between triple tree-ring stable isotopes data and monthly climate data

* Trending monthly climate data

* Trending tree-ring stable isotopes normalised data

* Boxplots and pairwise Mann-Whitneyu tests between tree-ring stable isotopes data

To simply get all plots and tables for the given configs use:

    python -m run config/config.24sites.yaml save-all

To see all options use:

    python -m run --help

Input data available in folder `data`.

Results for corresponding papers are available in folder `results`.

Used in:

* Zharkov, M.S.; Fonti, M.V.; Trushkina, T.V.; Barinov, V.V.; Taynik, A.V.; Porter, T.J.; Saurer, M.; Churakova, O.V. Mixed Temperature-Moisture Signal in δ18O Records of Boreal Conifers from the Permafrost Zone. Atmosphere 2021, 12, 1416. https://doi.org/10.3390/atmos12111416

* Churakova, O.V.; Fonti, M.V.; Barinov, V.V.; Zharkov, M.S.; Taynik, A.V.; Trushkina, T.V.; Kirdyanov, A.V.; Arzac, A.; Saurer, M. Towards the Third Millennium Changes in Siberian Triple Tree-Ring Stable Isotopes. Forests 2022, 13, 934. https://doi.org/10.3390/f13060934

* Churakova O. V.; Porter, T.J.; Zharkov, M.S.; Fonti, M.V.; Barinov, V.V.; Taynik, A.V.; Kirdyanov, A.V.; Knorre A.A.; Wegmann M.; Trushkina, T.V.; Koshurnikova N.N.; Vaganov E.A.; Myglan V.S.; Siegwolf R.T.W.; Saurer, M. Climate impacts on tree-ring stable isotopes across the Northern Hemispheric boreal zone. Science of The Total Environment 2023, 870, 161644. https://doi.org/10.1016/j.scitotenv.2023.161644