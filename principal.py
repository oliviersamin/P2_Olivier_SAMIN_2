""" Projet 2 de formation OpenClassRooms
P2_UtilisezLesBasesDePythonPourAnalyseDeMarche
 Mars 2021
 Olivier SAMIN
 """

import requests  # utilisé pour la récupération des données depuis le site
from bs4 import BeautifulSoup # utilisé pour la récupération des données depuis le site
import os # utilisé pour la création des dossiers et la navigation dans le système
from progress.bar import IncrementalBar # utilisé pour l'information à l'utilisateur
import config as cf

class scraping():
    """ classe pour le scrapping du site BooksToScrap """
    def __init__(self):
        # nom de l'image du livre qui est sauvegardé
        self.nomImage=''
        # sous-dossier de stockage d'images de livres
        self.dossierImages='ImagesLivres'
        # dossier de stockage des données générées par le programme
        self.dossierScrap='ResultatsScrap'
        #variable qui stocke les urls de chaque catégorie à scraper dans le site
        self.urlsCategories=[]
        #variable qui stocke pour une catégorie les paramètres nécessaires au scraping
        self.categorie={'nbLivres':'','nbPages':'','urlsLivres':[],'urlsPages':[]}
        # variable de nom de CSV sauvegardé (valeur par défaut donnée)
        self.fichierCSV='resultats.csv'
        # url de base du site à scrapper
        self.urlBase='http://books.toscrape.com/index.html'
        # url de base pour scrapper une catégorie
        self.urlCatalogue='http://books.toscrape.com/catalogue/'
        # url actuellement utilisée par le programme
        self.urlCourante=''
        # stocke tous les paramètres à scrapper pour un livre
        self.livre={'product_page_url':'','upc':'','title':'','price_including_tax':'',
                    'price_excluding_tax':'','number_available':'','product_description':'',
                    'category':'','review_rating':'','image_url':''}

    def initialiseLivre(self):
        self.livre={'product_page_url':'','upc':'','title':'','price_including_tax':'',
                    'price_excluding_tax':'','number_available':'','product_description':'',
                    'category':'','review_rating':'','image_url':''}

    def initialiseCategorie(self):
        """ remet les valeurs par defaut pour self.categorie """
        self.categorie={'nbLivres':'','nbPages':'','urlsLivres':[],'urlsPages':[]}

    def creerObjetSoup(self,url):
        """ créé self.soup avec l'url en paramètre """
        self.urlCourante=url
        self.reponse=requests.get(self.urlCourante)
        self.reponse.encoding = 'utf-8'
        self.soup=BeautifulSoup(self.reponse.text,features="html.parser")

    def recupereCategorieEtTitreLivre(self):
        """ recupere et sauvegarde la catégorie et le titre du livre dans self.livre"""
        lis=self.soup.findAll('li')
        for elem in lis: # boucle pour trouver le titre et la catégorie
            try: # pour trouver le titre
                if (elem['class'][0] == 'active'):
                    self.livre['title']=elem.contents[0]
                    break
            except: # pour catégorie
                if ('category' in elem.find('a')['href']):
                    cat=elem.find('a')
                    if (cat.contents[0] != 'Books'):
                        self.livre['category']=cat.contents[0]

    def recupereUrlImageLivre(self):
        """ recupere et sauvegarde l'url de l'image du livre dans self.livre """
        divs=self.soup.findAll('div')
        for elem in divs:
            try:
                if (elem['class'] == ['item', 'active']):
                    image=elem
                    self.livre['image_url']=self.urlBase[:-10]+elem.find('img')['src'][6:]
            except:
                pass

    def recupererReviewRating(self):
        """ récupère le nombre d'étoiles du livre et le stocke dans self.livre """
        filtreStar='star-rating'
        filtreProduit='product_main'
        divs=self.soup.findAll('div')
        for d in divs:
            try:
                if (filtreProduit in d['class']):
                    ps = d.findAll('p')
                    for p in ps:
                        try:
                            if (filtreStar in p['class']):
                                self.livre['review_rating']=p['class'][1]
                                break
                        except:
                            pass
            except:
                pass

    def recupereDescriptionLivre(self):
        """ recupere et sauvegarde la description du livre dans self.livre"""
        ps=self.soup.findAll('p')
        for p in ps:
            if (len(p.contents[0]) >= 50):
                self.livre['product_description']='"'+p.contents[0]+'"'

    def recupereAutresParametresLivre(self):
        """ recupere et sauvegarde les autres caracteristiques du livre dans self.livre """
        trs=self.soup.findAll('tr')
        for elem in trs:
            if (elem.find('th').contents[0]== 'UPC'):
                self.livre['upc']= elem.find('td').contents[0]
            elif (elem.find('th').contents[0]== 'Price (excl. tax)'):
                self.livre['price_excluding_tax'] = elem.find('td').contents[0][1:]
            elif (elem.find('th').contents[0]== 'Price (incl. tax)'):
                self.livre['price_including_tax'] = elem.find('td').contents[0][1:]
            elif (elem.find('th').contents[0]== 'Availability'):
                filtre=' available'
                res=elem.find('td').contents[0]
                res=res[res.find('(')+1:res.find(filtre)]
                self.livre['number_available'] = res

    def creationDossiersSauvegarde(self):
        if (not os.path.isdir(cf.dossierSauvegarde)):
            os.mkdir(cf.dossierSauvegarde)
        if (not os.path.isdir(cf.dossierImages)):
            os.mkdir(cf.dossierImages)

    def ecrireHeadersCSV(self,fichierCSV):
        """ créé les headers du fichier CSV en parametre """
        headers=''
        for k in self.livre.keys():
                headers+=k+';'
        headers=headers[:-1]+'\n'

        with open(fichierCSV, 'w') as f:
                f.write(headers)

    def ajouterUneLigneCSV(self,fichierCSV):
        """ ajoute une ligne (qui correspond à un livre) à un fichier CSV déjà existant """
        ligne=''
        for v in self.livre.values():
            ligne+=v+';'
        ligne=ligne[:-1]+'\n'
        with open(fichierCSV,'a') as f:
            f.write(ligne)

    def creeCSVunLivre(self,fichierCSV):
        """ crée un CSV avec séparateur ';' et sauvegrde les caracteristiques
        présentes dans self.livre dans le fichier self.fichierCSV"""
        if (not os.path.exists(fichierCSV)):
            self.ecrireHeadersCSV(fichierCSV)
        self.ajouterUneLigneCSV(fichierCSV)

    def scrapUnLivre(self,urlLivre,unLivre=False):
        """ scrap les paramètres pour un livre donné
         si csv == True génération d'un fichier CSV pour ce livre uniquement"""
        self.creerObjetSoup(urlLivre)
        self.initialiseLivre()
        self.livre['product_page_url']=urlLivre
        self.recupereCategorieEtTitreLivre()
        self.recupereUrlImageLivre()
        self.recupereDescriptionLivre()
        self.recupererReviewRating()
        self.recupereAutresParametresLivre()
        self.creationDossiersSauvegarde()
        if (unLivre):
            self.fichierCSV=self.livre['title']
        else:
            self.fichierCSV = self.livre['category']
        self.creeCSVunLivre(os.path.join(cf.dossierSauvegarde,self.fichierCSV))
        self.sauvegardeImageUnLivre(self.livre)

    def recupereUrlsUnePageCategorie(self):
        """ recupere toutes les urls de livre pour une seule page d'une catégorie """
        ol=self.soup.find('ol')
        divs=ol.findAll('div')
        self.categorie['urlsLivres'].append([])
        for elem in divs:
            try:
                self.categorie['urlsLivres'][-1].append(self.urlCatalogue+elem.find('a')['href'][9:])
            except:
                pass

    def recupereInfosUneCategorie(self,urlCategorie):
        """ recupere toutes les infos necessaires à une catégorie dans self.categorie"""

        self.initialiseCategorie()
        self.creerObjetSoup(urlCategorie)
        strongs=self.soup.findAll('strong')
        self.categorie['nbLivres']=int(strongs[1].contents[0])
        self.categorie['nbPages']=int(self.categorie['nbLivres']/20)+1
        if (self.categorie['nbPages'] > 1):
            urlUtilisee= urlCategorie[:-10]+'page-1.html'
            for elem in range(self.categorie['nbPages']): # urls de toutes les pages pour obtenir tous les livres
                self.categorie['urlsPages'].append(urlUtilisee[:-6]+str(elem+1)+'.html')
        else:
            self.categorie['urlsPages'].append(urlCategorie)

        for elem in self.categorie['urlsPages']: # recupere toutes les urls des livres dans toutes les pages de la catégorie
            self.creerObjetSoup(elem)
            self.recupereUrlsUnePageCategorie()

    def scrapUneCategorie(self,url,nomCSV='None'):
        """ scrap une catégorie entière de livres et la sauvegarde
         dans un CSV  """
        # Prépare le scraping
        self.recupereInfosUneCategorie(urlCategorie=url)

        # Optimise l'affichage pour l'utilisateur
        print('Il y a {} page(s) dans cette catégorie'.format(len(self.categorie['urlsLivres'])))
        self.barre=IncrementalBar('pages scrapées : ',max = len(self.categorie['urlsLivres']))

        # recupere toutes les infos de livre de chaque url
        for index,elem in enumerate(self.categorie['urlsLivres']):
                for el in elem:
                    self.initialiseLivre()
                    self.scrapUnLivre(el)
                self.barre.next()
        self.barre.finish()
        print ('CSV de la catégorie sauvegardée dans {}'.format(cf.dossierSauvegarde))
        print ('Images de la categorie sauvegardees dans {}'.format(cf.dossierImages))

    def creeCSVLivresUneCategorie(self):
        """ crée un CSV contenant tous les livres d'une meme categorie
        depuis self.livres"""

        headers = ''
        values = ''
        for index,elem in enumerate(self.livres):
                for key, value in zip(elem.keys(), elem.values()):
                    if (index == 0):
                        headers += key + ';'
                    values += value + ';'
                values = values[:-1]
                values+='\n'
        headers = headers[:-1]
        with open(self.fichierCSV, 'w') as f:
            f.write(headers)
            f.write('\n')
            f.write(values)

    def scrapSiteInternet(self): # en test
        """ scrap tout le site internet et génère un csv par catégorie de livres
         ces csv sont stockés dans un dossier

         ATTENTION : cette méthode nécessite environ 15 minutes pour s'exécuter intégralement"""

        self.recupereInfosPourToutesCategories()
        print ('Il y a {} categories'.format(len(self.urlsCategories)))
        for index,elem in enumerate(self.urlsCategories):
            print ('Catégorie {}/{} : {}'.format(index+1,len(self.urlsCategories),elem['csv'][:-4]))
            self.scrapUneCategorie(url=elem['url'],nomCSV=elem['csv'])
        print ('\nSite Web scrapé intégralement dans {}'.format(self.dossierScrap))

    def trouverNomCategorie(self,url):
        csv = url[::-1]
        csv = csv[csv.find('/') + 1:]
        csv = csv[:csv.find('/')]
        csv = csv[csv.find('_')+1:]
        csv=csv[::-1]
        return(csv)

    def recupereInfosPourToutesCategories(self):
        """ recupere les urls de chaque categorie du site et les stocke dans
         self.urlsCategories"""

        self.creerObjetSoup(self.urlBase)
        uls=self.soup.findAll('ul')
        for ul in uls:
            try:
                if (ul['class'] == ['nav', 'nav-list']):
                    lis=ul.find('ul').findAll('li')
                    break
            except:
                pass
        for li in lis:
            try:
                url=self.urlBase[:-10]+li.find('a')['href']
                csv=self.trouverNomCategorie(url)+'.csv'
                self.urlsCategories.append({'url':url,'csv':csv})
            except:
                pass

    def sauvegardeImageUnLivre(self,livre):
        """ enregistre l'image du livre depuis son url dans self.livre
        dans le dossier self.dossierImages pour les images de livre"""
        reponse=requests.get(livre['image_url'])
        self.nomImage=livre['title'].replace('/','_')[:30]+'.png'
        self.creationDossiersSauvegarde()
        dossierImage=os.path.join(cf.dossierImages,self.livre['category'])
        if (not os.path.isdir(dossierImage)):
            os.mkdir(dossierImage)
        with open(os.path.join(dossierImage,self.nomImage),'wb') as f:
            f.write(reponse.content)

    def choisirLaCibleDuScraping(self):
        """ Cette fonction sert à laisser le choix à l'utilisateur de ce qu'il veut scrapper
         sans avoir à toucher au code du programme, il peut scrapper:
         - un livre seul
         - une catégorie entière
         - tout le site"""
        choix=[(1,self.scrapUnLivre),(2,self.scrapUneCategorie),(3,self.scrapSiteInternet)]
        print ('Choisir parmi les 3 options de scraping:\n1- scraper un seul livre\n'
               '2- scraper une seule catégorie\n3- scraper tout le site')
        entree=input('Taper 1, 2 ou 3 puis <Entree>: ')
        try:
            entree=int(entree)
        except:
            print("votre choix n'est pas un entier")
            exit()
        for elem in choix:
            if (int(entree) ==elem[0]):
                if (int(entree)==3):
                    elem[1]()
                    exit()
                elif (int(entree)==1):
                    url=input("Entrer l'url à utiliser :\n")
                    elem[1](urlLivre=url,unLivre=True)
                    exit()
                elif (int(entree)==2):
                    url = input("Entrer l'url à utiliser :\n")
                    elem[1](url)
                    exit()
                else:
                    print('Votre choix doit être compris entre 1 et 3')
                    exit()

if __name__ == '__main__':
    scraping().choisirLaCibleDuScraping()
