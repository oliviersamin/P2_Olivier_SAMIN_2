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
        #variable qui stocke les urls de chaque catégorie à scraper dans le site
        self.urlsCategories=[]
        #variable qui stocke pour une catégorie les paramètres nécessaires au scraping
        self.categorie={'nbLivres':'','nbPages':'','urlsLivres':[],'urlsPages':[]}
        # variable de nom de CSV sauvegardé (valeur par défaut donnée)
        self.fichierCSV='resultats.csv'
        # url de base du site à scrapper
        self.urlBase='http://books.toscrape.com/index.html'
        # url de base pour scrapper une image
        self.urlBaseImage='http://books.toscrape.com/'
        # url de base pour scrapper une catégorie
        self.urlCatalogue='http://books.toscrape.com/catalogue/'
        # url actuellement utilisée par le programme
        self.urlCourante=''
        # stocke tous les paramètres à scrapper pour un livre
        self.livre={'product_page_url':'','upc':'','title':'','price_including_tax':'',
                    'price_excluding_tax':'','number_available':'','product_description':'',
                    'category':'','review_rating':'','image_url':''}

    def initialiseLivre(self):
        """ lors du scrapping d'une catégorie, permet de remettre les valeurs par défaut
         de self.livre pour passer d'un livre à l'autre"""
        self.livre={'product_page_url':'','upc':'','title':'','price_including_tax':'',
                    'price_excluding_tax':'','number_available':'','product_description':'',
                    'category':'','review_rating':'','image_url':''}

    def initialiseCategorie(self):
        """ pour le scraping du site entier, remet les valeurs par defaut pour self.categorie
         quand on change de catégorie à scrapper"""
        self.categorie={'nbLivres':'','nbPages':'','urlsLivres':[],'urlsPages':[]}

    def creerObjetSoup(self,url):
        """ créé self.soup avec l'url en paramètre """
        self.urlCourante=url
        self.reponse=requests.get(self.urlCourante)
        self.reponse.encoding = 'utf-8'
        self.soup=BeautifulSoup(self.reponse.text,features="html.parser")

    def recupereCategorieEtTitreLivre(self):
        """ recupere et sauvegarde la catégorie et le titre du livre dans self.livre
        le titre est le content de la balise <li class ='active'>
        la catégorie est le content de la balise <li> qui contient <a href= urlPageCategorie>
        et dont le content est different de 'Books'"""

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
        """ recupere et sauvegarde l'url de l'image du livre dans self.livre
        l'url (chemin relatif) de l'image se trouve dans une balise <div class='item active'
        il faut compléter le chemin l'url de base pour une image pour avoir le chemin absolu
        """
        divs=self.soup.findAll('div')
        for elem in divs:
            try:
                if (elem['class'] == ['item', 'active']):
                    cheminRelatif=elem.find('img')['src'][6:]
                    self.livre['image_url']=self.urlBaseImage+cheminRelatif
            except:
                pass

    def recupererReviewRating(self):
        """ récupère le nombre d'étoiles du livre et le stocke dans self.livre
        le rating se trouve dans une balise <p class='star-rating RATING'
        Cependant d'autres livres sont suggérés en lecture à la fin de la page produit
        avec également du rating. Pour éviter la confusion, il faut choisir la balise
        <div class="col-sm-6 product_main"> qui correspond à celle du produit voulu
        """
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
        """ recupere et sauvegarde la description du livre dans self.livre
        la description est contenue dans une balise <p>, il y en a plusieurs dans une
        page produit mais la seule qui corresponde à la description
        a un content qui fait au moins 50 caractères
        Deplus dans la description des points-virgule peuvent apparaîtrent. Ce sont
        les séparateurs du fichier CSV. Aussi pour éviter des confusions lors de la création
        du fichier une solution est d'entourer cette string de guillemets
        """

        ps=self.soup.findAll('p')
        for p in ps:
            if (len(p.contents[0]) >= 50):
                self.livre['product_description']='"'+p.contents[0]+'"'

    def recupereAutresParametresLivre(self):
        """ recupere et sauvegarde les autres caracteristiques du livre dans self.livre
        Tous les autres paramètres cherchés se trouvent dans un tableau
        les balises <tr> incluent une balise <th> dont le content est le nom du paramètre
        cherché et dont la balise <td> contient la valeur du paramètre cherché
        Pour la disponibilité des livres on cherche seulement le nombre dans la chaine de caractère
        qui est du type 'In stock (19 available)' d'où le travail sur ce paramètre"""
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
        """ créé les dossiers nécessaires pour sauvegarder à partir du fichier
         config.py les livres scrappés"""

        if (not os.path.isdir(cf.dossierSauvegarde)):
            os.mkdir(cf.dossierSauvegarde)
        if (not os.path.isdir(cf.dossierImages)):
            os.mkdir(cf.dossierImages)

    def ecrireHeadersCSV(self,fichierCSV):
        """ créé les headers du fichier CSV entré en paramètre à partir de la variable
         self.livre"""

        headers=''
        for k in self.livre.keys():
                headers+=k+';'
        headers=headers[:-1]+'\n'

        with open(fichierCSV, 'w') as f:
                f.write(headers)

    def ajouterUneLigneCSV(self,fichierCSV):
        """ ajoute une ligne (qui correspond à un livre) à un fichier CSV déjà existant
        et de la variable self.livre"""

        ligne=''
        for v in self.livre.values():
            ligne+=v+';'
        ligne=ligne[:-1]+'\n'
        with open(fichierCSV,'a') as f:
            f.write(ligne)

    def creeCSVunLivre(self,fichierCSV):
        """ crée un CSV avec séparateur ';' et sauvegarde les caracteristiques
        présentes dans self.livre dans fichierCSV"""
        if (not os.path.exists(fichierCSV)):
            self.ecrireHeadersCSV(fichierCSV)
        self.ajouterUneLigneCSV(fichierCSV)

    def scrapUnLivre(self,urlLivre,unLivre=False):
        """ scrap les paramètres pour un livre donné,cette méthode est utilisée pour
        scrapper un livre mais également tout une catégorie aussi il est nécessaire de
        faire cette distinction pour pouvoir créer le bon nom de fichier CSV pour la sauvegarde
         si unLivre == True alors le nom du fichier CSV est le nom du livre, sinon c'est celui
         de sa catégorie"""

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
        """ recupere toutes les urls de livre pour une seule page d'une catégorie
        les urls (chemin relatif) sont incuses dans une balise <div> qui contient une balise <a> avec un href
        Il faut compléter l'url pour en faire un chemin absolu
        """
        ol=self.soup.find('ol')
        divs=ol.findAll('div')
        self.categorie['urlsLivres'].append([])
        for elem in divs:
            try:
                self.categorie['urlsLivres'][-1].append(self.urlCatalogue+elem.find('a')['href'][9:])
            except:
                pass

    def recupereInfosUneCategorie(self,urlCategorie):
        """ recupere toutes les infos necessaires à une catégorie dans self.categorie
        La première information à avoir est le nombre de pages à scrapper. Je cherche donc
        le nombre de livres, chaque page contenant 20 livres je connais le nombre de pages.
        Ensuite si il y a une seule page à scrapper alors j'ajoute simplement l'url de la catégorie
        à self.categorie['urlsPages']. Sinon je créé les urls des pages à scrapper à partir
        du modèle suivant : http://books.toscrape.com/catalogue/category/books/<NOMCATEGORIE>_<VALEUR>/page-1.html
        et je modifie l'url avec le bon numéro de page puis je les stocke dans self.categorie['urlsPages']
        """
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

    def scrapUneCategorie(self,url):
        """ scrap une catégorie entière de livres, cette méthode est également utilisée
        pour scrapper le site en entier"""

        # Prépare le scraping
        self.recupereInfosUneCategorie(urlCategorie=url)

        # Optimise l'affichage pour l'utilisateur
        print('Il y a {} page(s) dans cette catégorie'.format(len(self.categorie['urlsLivres'])))
        self.barre=IncrementalBar('pages scrapées : ',max = len(self.categorie['urlsLivres']))

        # recupere toutes les infos de livre de chaque url
        for index,elem in enumerate(self.categorie['urlsLivres']):
                for el in elem:
                    self.initialiseLivre()
                    self.scrapUnLivre(el) # enregistre le CSV et l'image de chaque livre à la volée
                self.barre.next()
        self.barre.finish()
        print ('CSV de la catégorie sauvegardée dans {}'.format(cf.dossierSauvegarde))
        print ('Images de la categorie sauvegardees dans {}'.format(cf.dossierImages))

    def scrapSiteInternet(self): # en test
        """ scrap tout le site internet et génère un csv par catégorie de livres
         ces csv sont stockés dans le dossier indiqué dans config.py et les images dans un sous dossier
         indiqué également dans config.py
         ATTENTION : cette méthode nécessite environ 15 minutes pour s'exécuter intégralement"""

        self.recupereInfosPourToutesCategories()
        print ('Il y a {} categories'.format(len(self.urlsCategories)))
        print ('Le scrapping va prendre environ 15 minutes...')
        for index,elem in enumerate(self.urlsCategories):
            print ('Catégorie {}/{} : {}'.format(index+1,len(self.urlsCategories),elem['csv'][:-4]))
            self.scrapUneCategorie(url=elem['url'])
        print ('\nSite Web scrapé intégralement dans {}'.format(cf.dossierSauvegarde))

    def trouverNomCategorie(self,url):
        """ Cette méthode permet de récupérer le nom des catégories quand on scrappe tout
         le site internet. Cette information est utilisée uniquement pour
         l'affichage dans la console lors de l'éxecution du programme
         pour le confort de l'utilisateur
         """
        csv = url[::-1]
        csv = csv[csv.find('/') + 1:]
        csv = csv[:csv.find('/')]
        csv = csv[csv.find('_')+1:]
        csv=csv[::-1]
        return(csv)

    def recupereInfosPourToutesCategories(self):
        """ recupere les urls de chaque categorie du site et les stocke dans
         self.urlsCategories. Elles sont incluses dans la balise <ul class='nav nav-list'>
          Elles sont contenus esuite dans la balise <ul> puis les balises <li> puis <a href=...>"""

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
        dans le dossier self.dossierImages pour les images de livre
        """
        reponse=requests.get(livre['image_url'])

        #le nom du livre peut poser des problemes lors de l'enregistrement du fichier
        #les deux problèmes rencontrés ont été: 1. avoir des slashs dans les titres ( donc remplacés par des underscores)
        # 2. avoir des noms avec trop de caractères (donc limités à 30)
        self.nomImage=livre['title'].replace('/','_')[:30]+'.png'
        # création des dossiers de sauvegardes
        self.creationDossiersSauvegarde()
        dossierImage=os.path.join(cf.dossierImages,self.livre['category'])
        if (not os.path.isdir(dossierImage)):
            os.mkdir(dossierImage)
        #écriture du fichier image
        with open(os.path.join(dossierImage,self.nomImage),'wb') as f:
            f.write(reponse.content)

    def choisirLaCibleDuScraping(self):
        """ Cette méthode sert à laisser le choix à l'utilisateur de ce qu'il veut scrapper
         sans avoir à toucher au code du programme, il peut scrapper:
         - un livre seul
         - une catégorie entière
         - tout le site (environ 15 minutes)
         """
        choix=[(1,self.scrapUnLivre),(2,self.scrapUneCategorie),(3,self.scrapSiteInternet)]
        print ('Choisir parmi les 3 options de scraping:\n1- scraper un seul livre\n'
               '2- scraper une seule catégorie\n3- scraper tout le site (environ 15 minutes)')
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
