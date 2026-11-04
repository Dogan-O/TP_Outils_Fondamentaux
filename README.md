# CALCULATEUR — assistant de visée à l'arc (Minecraft)

| Dossier | Contenu |
|---|---|
| `tp/` | Mes solutions aux TP (tp1-6) |
| `projet/` | Mon projet personnel (`calculateur_arc.py`) |

## But
Je donne la position du joueur et celle du bloc visé ; le programme indique, pour chaque **force** (1, 2 ou 3 : vitesse initiale de la flèche en blocs/tick), le **yaw** et le **pitch** à afficher pour toucher le bloc.

## Lancer
Python 3.10+, aucune bibliothèque externe.
```
cd projet
python calculateur_arc.py     # puis, par exemple :  0 64 0 20 74 40
```
Saisie : `x y z` du joueur (pieds), puis `x y z` du bloc. Ligne vide pour quitter.

Exemple : `0 64 0 20 74 40` → yaw −26,8° ; force 3 : pitch −19,00° (tendu) ou −75,88° (cloche) ; force 2 : pitch −34,95° ; force 1 : impossible.

## Méthode
1. **Géométrie** : la 3D est ramenée à un plan vertical (distance horizontale `d`, dénivelé `dy`, yaw par `atan2`).
2. **Simulation** : la flèche est avancée tick par tick (gravité 0,05, traînée 0,99), avec interpolation entre deux ticks.
3. **Équation** : `hauteur_à_la_distance_d(angle) − dy = 0`. Un balayage des angles repère les changements de signe, puis ma **dichotomie** affine. Il y a 0, 1 ou 2 solutions (tir tendu / cloche).
4. **Choix** : l'erreur par degré (décalage en blocs pour 1° d'erreur) sert à conseiller un tir. Les tirs en cloche sont de 10 à 40 fois plus sensibles.

Pourquoi la dichotomie et pas Newton : la fonction vient d'une simulation (pas de dérivée exacte) et le balayage fournit déjà des intervalles avec changement de signe, donc la dichotomie converge toujours.

## Limites
- Constantes (gravité, traînée, hauteur des yeux, vitesse max 3, convention de yaw) tirées de ma mémoire : **à vérifier dans le jeu** `[source : à compléter]`.
- Pas de dispersion aléatoire, pas de blocs intermédiaires, pas de vent.
- Le balayage (pas de 0,5°) peut manquer deux angles très proches (portée maximale).
- Bloc à la verticale exacte du joueur : non géré.

## Validation dans le jeu
> À compléter après essais : scénario, force et angles utilisés, résultat, écart observé.

## Utilisation de l'IA
> À compléter honnêtement : ce que Claude a fait, ce que j'ai relu, testé, modifié et compris moi-même.
