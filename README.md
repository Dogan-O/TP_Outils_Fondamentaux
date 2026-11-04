# TP_Outils_Fondamentaux

```text
README.md
├── tp
│   ├── tp1
│   ├── tp2
│   ├── tp3
│   ├── tp4
│   ├── tp5
│   └── tp6
└── projet
    └── ...
```


Calculateur de tir à l'arc pour Minecraft (Java Edition) - mode console.

Entrées : position du joueur (X, Y, Z) et position de la cible (X, Y, Z).
Sorties : Yaw et Pitch (comme sur l'écran F3) et niveau de charge de l'arc (1 à 3).

Le cœur (simulation de la flèche + recherche de l'angle) est codé à la main :
on n'utilise que `math` pour sin, cos, atan2, radians, degrees, sqrt.
Aucune fonction "boîte noire" ne résout la physique à notre place.

LIMITES DU MODÈLE (à connaître et à dire à l'oral) :
  - Les angles calculés sont THÉORIQUES : ils correspondent à une flèche idéale.
  - La DISPERSION ALÉATOIRE du jeu (la flèche part toujours avec un petit écart
    aléatoire) n'est PAS simulée.
  - Les OBSTACLES et COLLISIONS (blocs sur le trajet, entités, eau, hitbox de la
    flèche) ne sont PAS pris en compte.
  - La vitesse propre du joueur (marche, saut, chute) est ignorée : on suppose
    qu'il est immobile et debout (yeux à 1,62 bloc).
  - Le résultat ne garantit donc PAS un impact parfait à chaque tir.

NIVEAUX DE CHARGE : dans Minecraft la charge de l'arc est CONTINUE (0 à 20 ticks).
Les niveaux 1, 2 et 3 de ce programme sont trois PALIERS PERSONNALISÉS choisis
par nous (voir NIVEAUX_CHARGE), pas des niveaux existant dans le jeu.

Utilisation :
    python calculateur_arc.py          -> mode interactif
    python calculateur_arc.py --test   -> lance les tests automatiques
