""" fichier de configuration pour le programme """
import os

# créé les dossiers de sauvegarde pour les CSV et les images
nomDossierSauvegarde='Scraping'
nomDosierImages='Images'
dossierOrigine= os.path.abspath(os.path.curdir)
dossierSauvegarde = os.path.join(dossierOrigine, nomDossierSauvegarde)
dossierImages=os.path.join(dossierSauvegarde,nomDosierImages)

