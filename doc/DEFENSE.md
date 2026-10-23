# Défense orale du TP

## Pitch d’ouverture (environ 45 secondes)

« Mon TP étudie la classification de surfaces agricoles à partir d’images Sentinel‑2. La méthode combine trois étapes : SLIC découpe l’image en régions homogènes, des caractéristiques spectrales et temporelles décrivent ces régions, puis une forêt aléatoire prédit une classe. L’étude pilote envisagée se situe autour de Mbanza‑Ngungu, au Kongo Central. Les quatre classes du cahier sont maïs, arboriculture, prairies/savane et sols nus/surfaces bâties. Les cartes ESA que j’examine pour cette zone sont des références possibles, mais elles ne fournissent pas directement toutes ces classes : leur adéquation doit être vérifiée avant de calculer des résultats. L’interface actuelle sert à montrer le parcours ; ses chiffres sont synthétiques et ne sont pas les performances du modèle. »

## 1. Présentation en 5 à 7 minutes

1. **Problème (30 s)** — distinguer les cultures à partir des réponses satellitaires, en tenant compte du fait qu’une image isolée peut confondre des couverts.
2. **Données (45 s)** — présenter le carré de cadrage d’environ 10 × 10 km autour de Mbanza‑Ngungu (Kongo Central, AEZ 4010), les images Sentinel‑2 2021 et les produits WorldCereal annuel/maïs après contrôle des pixels et de leur confiance. Préciser que les cartes ESA sont des références indirectes, pas des relevés de terrain. Le polygone est fourni dans `data/aoi/mbanza_ngungu_10km.geojson`.
3. **SLIC (60 s)** — expliquer qu’il groupe les pixels voisins par similarité spectrale et proximité spatiale ; il fournit des unités pour calculer les variables, pas la classe et pas une limite cadastrale garantie.
4. **Caractéristiques (60 s)** — montrer les réflectances par bande, NDVI et NDMI B8–B11, puis l’évolution sur plusieurs dates.
5. **Random Forest (60 s)** — expliquer plusieurs arbres construits sur des sous-échantillons et des sous-ensembles de variables, dont les votes donnent la classe finale.
6. **Évaluation (60 s)** — décrire la séparation par parcelle/bloc spatial, la matrice de confusion, F1 par classe et F1 macro ; ne pas se limiter à l’accuracy.
7. **Limites et conclusion (45 s)** — parler de la qualité des labels, nuages, segments mixtes, déséquilibre et transfert vers une autre zone/saison.

Dans le tableau de bord, la section **« Du pixel à la classe, en trois étapes »** sert à expliquer SLIC, le vecteur de caractéristiques et le vote de Random Forest avant de présenter les résultats simulés.

## 2. Questions probables

### Pourquoi combiner SLIC et Random Forest ?
SLIC regroupe les pixels en régions voisines plus homogènes pour calculer des statistiques locales. Random Forest apprend ensuite la correspondance entre les caractéristiques de ces régions et les classes connues. Les rôles sont différents : SLIC segmente, la forêt classe.

### Un superpixel est-il une parcelle ?
Pas nécessairement. Il peut couvrir une partie d’une parcelle ou chevaucher une limite réelle. Il faut comparer les segments aux polygones de référence et gérer les superpixels mixtes.

### Les cartes candidates fournissent-elles les quatre classes du cahier ?
Pas directement. WorldCereal donne des produits binaires par cible et saison ; son produit maïs peut servir à une expérience maïs/non-maïs, pas à créer seul les quatre classes. WorldCover donne des classes générales : `tree cover` ne veut pas dire spécifiquement arboriculture, `grassland` n’est pas une étiquette locale validée et `cropland` ne distingue pas le maïs. Il faut auditer ces produits et, si les quatre classes sont obligatoires, obtenir des annotations compatibles. Le tableau de bord garde les quatre classes seulement pour illustrer la matrice synthétique.

### Les scores prouvent-ils la précision terrain ?
Non, si les labels de test viennent de WorldCereal ou WorldCover : ils mesurent d’abord l’accord avec la carte choisie. Pour démontrer une précision indépendante, il faut des observations géoréférencées de terrain ou des parcelles de référence validées.

### Pourquoi plusieurs dates ?
Une culture peut ressembler à une autre à une date donnée. L’évolution des bandes et des indices au cours du cycle cultural peut aider à séparer les signatures.

### Pourquoi une séparation spatiale ?
Des superpixels voisins ou d’une même parcelle se ressemblent. Les répartir entre train et test peut donner au test des exemples trop proches de l’entraînement et gonfler artificiellement les scores. Une partition par groupe spatial mesure mieux le transfert vers des zones indépendantes.

### Pourquoi rapporter F1 par classe ?
L’accuracy globale peut être élevée si une classe est très fréquente alors qu’une classe rare est mal reconnue. F1 par classe et F1 macro exposent mieux ces déséquilibres.

### Faut-il normaliser avant Random Forest ?
Pas en général pour une Random Forest seule, qui coupe les variables à des seuils. La standardisation peut être utile si une étape telle que l’ACP ou une méthode de distance est ajoutée ; dans ce cas elle doit être ajustée sur train seulement.

### Que représentent les résultats affichés dans le prototype ?
Une simulation de démonstration calculée à partir d’une matrice fixe. Aucun raster Sentinel‑2 n’est lu et aucun modèle n’est entraîné. Ce résultat valide seulement l’interface et la cohérence des métriques ; il ne doit pas être présenté comme un résultat scientifique.

## 3. Règles de présentation des résultats

- Présenter la source, la taille du jeu, la période et la méthode de séparation avec les scores.
- Donner la matrice et l’orientation des axes.
- Distinguer les valeurs calculées sur validation des valeurs finales mesurées sur test.
- Ne pas annoncer une accuracy comme objectif ou résultat avant d’avoir exécuté l’expérience réelle.
- Signaler toute classe absente, label incertain, donnée interpolée ou région masquée.
