import math
import sys


GRAVITE = 0.05            
RESISTANCE_AIR = 0.99     
VITESSE_MAX = 3.0         
HAUTEUR_YEUX = 1.62       
DECALAGE_FLECHE = 0.1     
TICKS_MAX = 1200          

NIVEAUX_CHARGE = {1: 6, 2: 12, 3: 20}   

PAS_BALAYAGE = 0.25      
TOLERANCE_ANGLE = 1e-9   
CODE_TROP_COURT = -1e9  


def vitesse_initiale(ticks): #vitesse de base selon la charge. | Formule du jeu : f = ticks / 20 ; puissance = (f*f + 2*f) / 3 (limitée à 1) ;vitesse = puissance * 3. Pleine charge (20 ticks) -> 3.0 blocs/tick.
    f = ticks / 20
    puissance = (f * f + 2 * f) / 3
    if puissance > 1:
        puissance = 1.0
    return puissance * VITESSE_MAX


def hauteur_a_distance(angle_deg, vitesse, distance, dy): #simulation
    angle = math.radians(angle_deg)
    vh = vitesse * math.cos(angle)   
    vy = vitesse * math.sin(angle)   
    if vh <= 0:                      
        return None

    x = 0.0                          
    y = 0.0                          
    y_plancher = min(0.0, dy) - 5.0  

    for _ in range(TICKS_MAX):
        x_suivant = x + vh
        y_suivant = y + vy
        if x_suivant >= distance:
            t = (distance - x) / (x_suivant - x)   
            return y + t * (y_suivant - y)         
        x, y = x_suivant, y_suivant
        
        vh = vh * RESISTANCE_AIR
        vy = vy * RESISTANCE_AIR - GRAVITE
        
        if vy < 0 and y < y_plancher:
            return None
    return None


def erreur_hauteur(angle_deg, vitesse, distance, dy): #calcule hauteur
    h = hauteur_a_distance(angle_deg, vitesse, distance, dy)
    if h is None:
        return CODE_TROP_COURT      
    return h - dy


def dichotomie(f, a, b, tolerance): #racine de f entre a et b, f(a) et f(b) de signes opposés
    fa = f(a)
    while b - a > tolerance:
        milieu = (a + b) / 2
        fm = f(milieu)
        if fa * fm <= 0:
            b = milieu
        else:
            a, fa = milieu, fm
    return (a + b) / 2


def trouver_angle(vitesse, distance, dy): #cherche l'angle de tir
    nb_pas = int(179.8 / PAS_BALAYAGE)
    a = -89.9
    erreur_a = erreur_hauteur(a, vitesse, distance, dy)
    for i in range(1, nb_pas + 1):
        b = -89.9 + i * PAS_BALAYAGE
        erreur_b = erreur_hauteur(b, vitesse, distance, dy)
        if erreur_a < 0 and erreur_b >= 0:     # on a encadré une solution
            return dichotomie(lambda ang: erreur_hauteur(ang, vitesse, distance, dy),
                              a, b, TOLERANCE_ANGLE)
        a, erreur_a = b, erreur_b
    return None


def calculer_yaw(dx, dz): #conversion vers les angles de l'écran F3
    yaw = math.degrees(math.atan2(-dx, dz))
    if yaw == 0:
        yaw = 0.0                    
    if yaw == -180:
        yaw = 180.0
    return yaw


def pitch_depuis_elevation(angle_deg): #le pitch est positif quand on regarde vers le bas, négatif quand on regarde vers le haut.
    p = -angle_deg
    if p == 0:
        p = 0.0
    return p


def calculer_tir(joueur, cible): #résolution complte
    #la flèche part de la position des yeux du joueur
    depart = (joueur[0], joueur[1] + HAUTEUR_YEUX - DECALAGE_FLECHE, joueur[2])
    dx = cible[0] - depart[0]
    dy = cible[1] - depart[1]
    dz = cible[2] - depart[2]
    distance_h = math.sqrt(dx * dx + dz * dz)

    if distance_h < 1e-6:
        raise ValueError("La cible est à la verticale du joueur : le yaw est "
                         "indéfini et ce programme ne gère pas les tirs verticaux.")
    if distance_h < 0.5:
        raise ValueError("Cible trop proche (moins de 0,5 bloc) : tir inutile.")

    yaw = calculer_yaw(dx, dz)
    solutions = []
    for niveau in sorted(NIVEAUX_CHARGE):
        ticks = NIVEAUX_CHARGE[niveau]
        v = vitesse_initiale(ticks)
        angle = trouver_angle(v, distance_h, dy)
        if angle is not None:
            solutions.append((niveau, ticks, v, pitch_depuis_elevation(angle)))

    if not solutions:
        raise ValueError("Cible hors de portée : même à pleine charge, aucune "
                         "inclinaison ne permet à la flèche d'arriver "
                         "({:.1f} blocs à l'horizontale).".format(distance_h))
    return yaw, solutions, distance_h, dy


def lire_nombre(invite): #saisie, affichage
    while True:
        texte = input(invite).strip().replace(",", ".")
        try:
            valeur = float(texte)
        except ValueError:
            print("  Erreur : '{}' n'est pas un nombre. Recommencez.".format(texte))
            continue
        if valeur != valeur or abs(valeur) > 3.0e7:   # NaN ou hors du monde (±30 millions)
            print("  Erreur : coordonnée hors des limites du monde. Recommencez.")
            continue
        return valeur


def lire_oui_non(invite, defaut): #pose la question oui/non
    while True:
        rep = input(invite).strip().lower()
        if rep == "":
            return defaut
        if rep in ("o", "oui"):
            return True
        if rep in ("n", "non"):
            return False
        print("  Erreur : répondez par 'o' ou 'n'.")


def lire_point(nom):
    print("--- {} ---".format(nom))
    x = lire_nombre("  X : ")
    y = lire_nombre("  Y : ")
    z = lire_nombre("  Z : ")
    return (x, y, z)


def afficher_resultat(yaw, solutions, distance_h, dy):
    print("\n===== RÉSULTAT =====")
    print("Distance horizontale : {:.2f} blocs | écart de hauteur (départ de la flèche -> cible) : {:+.2f}".format(
        distance_h, dy))
    print("Yaw   (F3) : {:.2f}°".format(yaw))
    niveau, ticks, v, pitch = solutions[0]
    print("Pitch (F3) : {:.2f}°   [charge conseillée : niveau {}]".format(pitch, niveau))
    print("\nTous les niveaux possibles :")
    for niveau, ticks, v, pitch in solutions:
        print("  Niveau {} ({} ticks de tension, vitesse {:.2f} bl/tick) -> pitch {:.2f}°".format(
            niveau, ticks, v, pitch))
    print("(F3 affiche 1 décimale ; plus le niveau est haut, plus le tir est tendu.)")
    print("\nNiveaux de charge : Minecraft utilise une charge CONTINUE de 0 à 20 ticks.")
    print("Les niveaux 1, 2 et 3 ({}, {} et {} ticks) sont des PALIERS PERSONNALISÉS de ce programme.".format(
        NIVEAUX_CHARGE[1], NIVEAUX_CHARGE[2], NIVEAUX_CHARGE[3]))
    print("\nATTENTION : ces angles sont THÉORIQUES. La dispersion aléatoire des flèches n'est")
    print("pas simulée, et les obstacles / collisions ne sont pas pris en compte.")
    print("Le résultat ne garantit donc pas un impact parfait à chaque tir.")


def programme_principal():
    print("=== Calculateur de tir à l'arc Minecraft ===")
    print("Coordonnées de F3 (pieds du joueur). Virgule ou point acceptés.\n")
    try:
        while True:
            joueur = lire_point("Joueur")
            cible = lire_point("Cible")
            if lire_oui_non("La cible est un bloc entier (viser son centre, +0,5) ? [O/n] : ", True):
                cible = (cible[0] + 0.5, cible[1] + 0.5, cible[2] + 0.5)
            try:
                yaw, solutions, d, dy = calculer_tir(joueur, cible)
                afficher_resultat(yaw, solutions, d, dy)
            except ValueError as erreur:
                print("\nImpossible : {}".format(erreur))
            if not lire_oui_non("\nNouveau calcul ? [o/N] : ", False):
                break
    except (EOFError, KeyboardInterrupt):
        print("\nInterruption de la saisie.")
    print("À bientôt !")


def position_flechee(yaw, pitch, vitesse, depart, n_ticks): #test automatique
    """Simule la flèche en 3D à partir de (yaw, pitch) du jeu et renvoie la liste
    de ses positions. Sert de contre-vérification : on n'y réutilise pas le solveur."""
    yr, pr = math.radians(yaw), math.radians(pitch)
    vx = -math.cos(pr) * math.sin(yr) * vitesse
    vy = -math.sin(pr) * vitesse
    vz = math.cos(pr) * math.cos(yr) * vitesse
    x, y, z = depart
    chemin = [(x, y, z)]
    for _ in range(n_ticks):
        x, y, z = x + vx, y + vy, z + vz
        vx, vy, vz = vx * RESISTANCE_AIR, vy * RESISTANCE_AIR - GRAVITE, vz * RESISTANCE_AIR
        chemin.append((x, y, z))
    return chemin


def distance_min_a_la_cible(chemin, cible): #plus petite distance entre la trajectoire et la cible
    meilleur = 1e18
    for i in range(len(chemin) - 1):
        p, q = chemin[i], chemin[i + 1]
        ux, uy, uz = q[0] - p[0], q[1] - p[1], q[2] - p[2]     
        wx, wy, wz = cible[0] - p[0], cible[1] - p[1], cible[2] - p[2]  
        longueur2 = ux * ux + uy * uy + uz * uz
        if longueur2 == 0:                  
            t = 0.0
        else:
            t = (wx * ux + wy * uy + wz * uz) / longueur2
            t = max(0.0, min(1.0, t))      
        px, py, pz = p[0] + t * ux, p[1] + t * uy, p[2] + t * uz
        d = math.sqrt((px - cible[0]) ** 2 + (py - cible[1]) ** 2 + (pz - cible[2]) ** 2)
        if d < meilleur:
            meilleur = d
    return meilleur


def lancer_tests(): #lance tous les tests
    import builtins
    import contextlib
    import io

    echecs = []

    def verifier(condition, description): #enregistre le résultat d'un test sans arrêter les suivants
        if condition:
            print("  [OK]    " + description)
        else:
            print("  [ÉCHEC] " + description)
            echecs.append(description)

    def leve_valueerror(fonction): #vraie si l'appel lève une ValueError
        try:
            fonction()
        except ValueError:
            return True
        return False

    print("\n[1] Vitesse initiale")
    for ticks, attendu in [(0, 0.0), (6, 0.69), (12, 1.56), (20, 3.0), (30, 3.0)]:
        v = vitesse_initiale(ticks)
        verifier(abs(v - attendu) < 1e-9,
                 "{} ticks -> {:.4f} bl/tick (attendu {})".format(ticks, v, attendu))

    print("\n[2] Yaw (signe respecté)")
    attendus = [((0, 1), 0), ((-1, 0), 90), ((0, -1), 180), ((1, 0), -90),
                ((-1, 1), 45), ((1, 1), -45), ((-1, -1), 135), ((1, -1), -135)]
    for (dx, dz), att in attendus:
        for pas in (1, 30.0):   
            y = calculer_yaw(dx * pas, dz * pas)
            verifier(abs(y - att) < 1e-9,
                     "yaw(dx={}, dz={}) = {:.1f} (attendu {})".format(dx * pas, dz * pas, y, att))
    verifier(pitch_depuis_elevation(10) == -10 and pitch_depuis_elevation(-10) == 10,
             "pitch = -élévation (regarder en haut = pitch négatif)")

    print("\n[3] Boucle de simulation vs formule fermée")
    k, g = RESISTANCE_AIR, GRAVITE
    pire = 0.0
    for angle in (-30, 0, 10, 45):
        for v in (0.69, 1.56, 3.0):
            for n in (1, 5, 40):
                a = math.radians(angle)
                vh, vy0 = v * math.cos(a), v * math.sin(a)
                x_n = vh * (1 - k ** n) / (1 - k)
                y_n = (vy0 + g / (1 - k)) * (1 - k ** n) / (1 - k) - n * g / (1 - k)
                h = hauteur_a_distance(angle, v, x_n, -1000)
                pire = max(pire, abs(h - y_n))
    verifier(pire < 1e-6, "écart maximal boucle/formule = {:.2e} (< 1e-6)".format(pire))

    print("\n[4] Tirs complets (cohérence interne)")
    cas = [
        ("sud, 30 blocs",            (0, 64, 0),            (0, 64, 30)),
        ("ouest, 30 blocs",          (0, 64, 0),            (-30, 64, 0)),
        ("nord, 30 blocs",           (0, 64, 0),            (0, 64, -30)),
        ("est, 30 blocs",            (0, 64, 0),            (30, 64, 0)),
        ("cible plus haute",         (0, 64, 0),            (5, 80, 25)),
        ("cible plus basse",         (0, 64, 0),            (-10, 40, 20)),
        ("coordonnées négatives",    (-100.5, 70, -200.25), (-120, 75, -235.7)),
        ("Y négatif + décimales",    (-5.5, -20, -5.5),     (-40.25, -30, -60.75)),
        ("longue portée (niveau 3)", (0.5, 64, 0.5),        (60, 64, 85)),
        ("très proche",              (0, 64, 0),            (10, 64, 0)),
        ("presque à la verticale",   (0, 64, 0),            (0, 100, 15)),
    ]
    for nom, joueur, cible in cas:
        try:
            yaw, sols, d, dy = calculer_tir(joueur, cible)
        except ValueError as e:
            verifier(False, "{} : erreur inattendue : {}".format(nom, e))
            continue
        depart = (joueur[0], joueur[1] + HAUTEUR_YEUX - DECALAGE_FLECHE, joueur[2])
        pire = 0.0
        for niveau, ticks, v, pitch in sols:
            ecart = distance_min_a_la_cible(position_flechee(yaw, pitch, v, depart, 400), cible)
            pire = max(pire, ecart)
        verifier(len(sols) > 0 and pire < 0.01,
                 "{} : niveaux {} , écart max {:.4f} bloc".format(nom, [s[0] for s in sols], pire))

    for (dx, dz), att in [((0, 30), 0), ((-30, 0), 90), ((0, -30), 180), ((30, 0), -90)]:
        yaw = calculer_tir((0, 64, 0), (float(dx), 64.0, float(dz)))[0]
        verifier(abs(yaw - att) < 1e-9, "calculer_tir : cible ({}, {}) -> yaw {:.1f} (attendu {})".format(dx, dz, yaw, att))

    verifier(calculer_tir((0, 64, 0), (0, 100, 15))[1][0][3] < 0, "cible en hauteur : pitch négatif")
    verifier(calculer_tir((0, 64, 0), (0, 20, 5))[1][0][3] > 0, "cible très basse : pitch positif")

    niveaux = lambda j, c: [s[0] for s in calculer_tir(j, c)[1]]
    verifier(niveaux((0, 64, 0), (0, 64, 5)) == [1, 2, 3], "5 blocs : niveaux 1, 2 et 3")
    verifier(niveaux((0, 64, 0), (0, 64, 30)) == [2, 3], "30 blocs : niveaux 2 et 3")
    verifier(niveaux((0, 64, 0), (0, 64, 80)) == [3], "80 blocs : niveau 3 seul")

    print("\n[5] Cibles impossibles")
    verifier(leve_valueerror(lambda: calculer_tir((0, 64, 0), (0, 80, 0))), "cible à la verticale")
    verifier(leve_valueerror(lambda: calculer_tir((0, 64, 0), (0.1, 64, 0.1))), "cible trop proche")
    verifier(leve_valueerror(lambda: calculer_tir((0, 64, 0), (500, 64, 0))), "cible à 500 blocs (hors de portée)")
    verifier(leve_valueerror(lambda: calculer_tir((0, 64, 0), (150, 64, 0))), "cible à 150 blocs (hors de portée)")
    verifier(leve_valueerror(lambda: calculer_tir((0, 64, 0), (1, 320, 0))), "cible 255 blocs plus haut, à 1 bloc")
    verifier(leve_valueerror(lambda: calculer_tir((10.5, 64, -3), (10.5, 64, -3))), "cible = position du joueur")

    print("\n[6] Saisies incorrectes")
    input_origine = builtins.input
    try:
        reponses = iter(["abc", "nan", "inf", "1e9", "", "-3,5"])
        builtins.input = lambda invite="": next(reponses)
        sortie = io.StringIO()
        with contextlib.redirect_stdout(sortie):
            valeur = lire_nombre("")
        verifier(valeur == -3.5 and sortie.getvalue().count("Erreur") == 5,
                 "lire_nombre : 5 saisies refusées puis '-3,5' -> -3.5")
        reponses = iter(["peut-être", "x", "N"])
        with contextlib.redirect_stdout(io.StringIO()):
            rep = lire_oui_non("", True)
        verifier(rep is False, "lire_oui_non : réponses inconnues refusées, 'N' -> False")
        reponses = iter([""])
        verifier(lire_oui_non("", True) is True, "lire_oui_non : réponse vide -> valeur par défaut")
    finally:
        builtins.input = input_origine

    print()
    if echecs:
        print("ÉCHEC : {} test(s) en échec :".format(len(echecs)))
        for description in echecs:
            print("  - " + description)
        print("(rappel : ces tests vérifient la cohérence interne, pas la fidélité exacte à Minecraft)")
        sys.exit(1)
    print("TOUS LES TESTS PASSENT (cohérence interne ; ne prouve pas la fidélité exacte à Minecraft).")
    sys.exit(0)


if __name__ == "__main__":
    if "--test" in sys.argv:
        lancer_tests()
    else:
        programme_principal()
