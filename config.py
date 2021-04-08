""" fichier de configuration pour le programme """
import os

#dossiers de sauvegarde pour les CSV et les images
nomDossierSauvegarde='Scraping'
nomDosierImages='Images'
dossierOrigine= os.path.abspath(os.path.curdir)
dossierSauvegarde = os.path.join(dossierOrigine, nomDossierSauvegarde)
dossierImages=os.path.join(dossierSauvegarde,nomDosierImages)

#paramètres pour le fichier CSV
#le choix du délimiteur est peu commun mais dans les description et titre des livres il peut y avoir
#des ',' et ';'. J'ai donc choisi un séparateur avec une probabilité extrèmemnt faible de se retrouver
#dans un livre. Si le délimiteur est changé en ',' ou ';' il est très probable que la structure du CSV soit altérée
#et que les colonnes ne correspondent plus aux en têtes.
delimiteurCSV='|'

#pour obtenir une segmentation correcte des colonnes il faut utiliser les "'"
# pour identifier une chaîne de caractères et avoir un encodage en UTF-8