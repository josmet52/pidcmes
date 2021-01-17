# Raspberry PI : mesure d'une tension continue

## Préambule

Le Raspberry PI est un ordinateur mon-carte de petite taille qui tourne
sous Raspberry-OS (distribution de Debian). Le PI offre un bus complet
d'entrées sorties numérique mais aucune entrée analogique.

Le but de mon projet est de permettre le suivi de l'état de charge de la
batterie d'une alimentation sans coupure afin d'assurer un arrêt propre
du système en cas de coupure de courant. La batterie LIPO que j'utilise 
voit sa tension varier de 4.2 à 3.5 V.

## Introduction

Pour un projet sur Raspberry PI je dois assurer une alimentation sans interruption 
en cas de chute du réseau électrique. J'ai trouvé des solutions chez différents 
fournisseurs pour assurer proprement la transition entre le réseau et 
la batterie mais ces système ne permettent pas d'informer le PI que la batterie est
bientôt vide et qu'il faudrait arrêter proprement le système d'exploitation.

Dans ce but j'ai développé et testé plusieures variantes toutes basées
sur le même principe soit: mesure le temps que met un condensateur pour
se charger au travers d'une résistance à une tension connue et convertir ce temps en valeur de
tension. Ces différents essais m'ont amené sur la solution que je vous
propose aujourd'hui.

## Principe de base

*insérer le schéma*

La tension à mesurer est appliquée entre les bornes BBU-BAT et BBU-GND. La commande
RPI-CMD est relié sur la borne GPIO (8 dans mon cas) du PI configurée comme
une sortie et la sortie RPI-MES est reliée sur la borne GPIO (10 dans
mon cas) du PI configurée comme une entrée. Les Connexions RPI-VCC (borne 4) et
RPI-GND (borne 6) sont branchées sur le PI. La masse du signal à mesurer (BBU-GND) et 
celle du PI (RPI-GND) sont reliées.

Le principe de fonctionnement est le suivant:

Avant de lancer une mesure la sortie RPI-CMD est mise à "1" ainsi le MOSFET T1
est rendu conducteur ce qui décharge le condensateur C1. Pour lancer la mesure, le PI met l'entrée
CMD à "0" ainsi le MOSFET T1 se bloque et le condensateur peut se charger au travers de la
résistance R1 alimentée par la tension à mesurer. Lorsque la tension aux
bornes du condensateur atteint la tension VTRIG (2.5V dans mon cas), le comparateur IC1 fait passer sa
sortie de "1" à "0". Le PI mesure le temps écoulé entre le lancement
de la mesure et le moment ou un flanc descendant est détecté RPI-MES. Connaissant les caractéristiques du 
circuit R1, C1 il est possible de calculer la valeur de la tension appliquée à l'entrée
BBU-BAT par la formule:

*insérer la formule*

Où UTRIG = tension de référence (2.5V) et TMES = temps écoulé entre le
lancement de la mesure et le moment ou la sortie où un flanc descendant est détecté sur l'entrée RPI-MES.

## Limites du principe utilisé

#### Courant consommé sur le point de mesure

En branchant l'entrée sans amplificateur directement sur le point à
mesurer on consomme du courant sur cette source. Comme
la valeur de la résistance est de 100kΩ, le courant max tiré du point de
mesure, pour une tension à mesurer de 10V est de 100 μA. A l'utilisateur de déterminer si cela est
acceptable. Dans mon cas aucun problème car je mesure la tension de la
batterie de l'alimentation sans coupure.

#### Plage de tension admissible

Le principe utilisé n'autorise pas de tension mesurée en dessous de 2.8V
pour assurer que la tension aux bornes du condensateur puisse atteindre
2.5V et faire basculer la sortie du comparateur. La tension maximale qui
peut être appliquée est limitée par le comparateur LM393 et peut
atteindre 36V. Cependant comme il n'y a aucune protection entre l'entrée
de mesure et le PI, un défaut du LM393 pourrait amener la tension
d'entrée directement sur la borne RPI-MES ou, si le MOSFET devenait
défectueux, sur la borne RPI-CMD. Je recommande donc de ne pas dépasser
la tension max admissible par le port GPIO du PI soit 5V.

## Fiabilité de la mesure

Le principe de mesure dépend très fortement du temps de latence du PI.
Si le processeur est occupé à d'autres tâches prioritaires, le temps de
latence peut varier sur une ou deux mesures. Pour écarter
ces mauvaises mesures je fais un grand nombre de mesures et rejette
celles qui sont en dehors de 1.5 écarts types de l'ensemble des mesures
puis je fais la moyenne des mesures restantes.

## Software

Le software est écrit en Python est peut être téléchargé depuis GitHub
par le lien: <https://github.com/josmet52/pidcmes>

## Nomenclature

Les composants utilisés sont:

-   T1 = BS170 -- MOSFET canal N
-   D1 = LM336-2.5V - diode de référence de 2.5V
-   IC1 = LM393N - Low-Offset Voltage, Dual Comparators
-   R1 = 100kΩ -- Résistance
-   R2 = 2.5kΩ -- Résistance
-   C1 = 1μF -- Condensateur céramique

## Outils

###pidcmes_lib.py

