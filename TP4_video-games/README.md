# Atlas Pokémon — DataViz

Projet individuel sur les jeux vidéo. J'ai choisi d'explorer les statistiques des Pokémon : les types, les générations et les profils de combat.

**Question :** Quels profils de Pokémon se distinguent selon les types et les générations ?

L'application permet de filtrer les générations, les types et les statuts, de comparer les moyennes et les distributions, puis de confronter deux Pokémon dans un face-à-face.

## Capture du tableau de bord

![Capture du dashboard](dashboard.png)

## Lancement

Installer les dépendances avec `pip install -r requirements.txt`, puis lancer `streamlit run app.py`.

Les différentes formes d'un Pokémon sont conservées : une ligne représente une forme et non forcément une espèce unique. Les statistiques manquantes ne sont pas inventées.

Outils : Python, pandas, Plotly, Streamlit. Données : `pokedex.csv`.

## Aperçu du dashboard

### Vue d'ensemble
![Vue d'ensemble 1](vue-ensemble1.png)
![Vue d'ensemble 2](vue-ensemble2.png)

### Analyse des combats
![Combat 1](COMBAT1.png)
![Combat 2](combat2.png)

### Comparateur Pokémon
![Duel 1](duel1.png)
![Duel 2](DUEL2.png)
