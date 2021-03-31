
""" Projet 2 de formation OpenClassRooms
 Mars 2021
 Olivier SAMIN
 """


import requests
from bs4 import BeautifulSoup
import os
from progress.bar import IncrementalBar


class scraping():
    """ classe pour le scrapping du site BooksToScrap """
    def __init__(self):
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
        # stocke les variables self.livre pour toute une catégorie
        self.livres=[]
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

    def initialiseLivres(self):
        """ remet la liste self.livres = [] """
        self.livres=[]

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
                    # print('title : ', self.livre['title'])
                    break
            except: # pour catégorie
                if ('category' in elem.find('a')['href']):
                    cat=elem.find('a')
                    if (cat.contents[0] != 'Books'):
                        self.livre['category']=cat.contents[0]
        # print (self.livre)

    def recupereUrlImageLivre(self):
        """ recupere et sauvegarde l'url de l'image du livre dans self.livre """
        divs=self.soup.findAll('div')
        for elem in divs:
            try:
                if (elem['class'] == ['item', 'active']):
                    image=elem
                    self.livre['image_url']=self.urlBase[:-10]+elem.find('img')['src'][9:]
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
                self.livre['number_available'] = elem.find('td').contents[0]
            elif (elem.find('th').contents[0]== 'Number of reviews'):
                self.livre['review_rating'] = elem.find('td').contents[0]

    def creeCSVunLivre(self):
        """ crée un CSV avec séparateur ';' et sauvegrde les caracteristiques
        présentes dans self.livre dans le fichier self.fichierCSV"""

        headers=''
        values=''
        for key,value in zip(self.livre.keys(),self.livre.values()):
            # print ('k = {}, v= {}'.format(key,value))
            headers+=key+';'
            values+=value+';'
        headers=headers[:-1]
        values=values[:-1]
        with open(self.fichierCSV,'w') as f:
            f.write(headers)
            f.write('\n')
            f.write(values)

    def scrapUnLivre(self,urlLivre,csv=False):
        """ scrap les paramètres pour un livre donné
         si csv == True génèration d'un fichier CSV pour ce livre uniquement"""
        self.creerObjetSoup(urlLivre)
        self.initialiseLivre()
        self.livre['product_page_url']=urlLivre
        self.recupereCategorieEtTitreLivre()
        self.recupereUrlImageLivre()
        self.recupereDescriptionLivre()
        self.recupereAutresParametresLivre()
        # print ('unLivre : ',self.livre)
        if csv:
            self.creeCSVunLivre()

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
        # print (self.categorie)

    def scrapUneCategorie(self,url,nomCSV='None'):
        """ scrap une catégorie entière de livres et la sauvegarde
         dans un CSV  """
        self.recupereInfosUneCategorie(urlCategorie=url)
        self.initialiseLivres()
        print('Il y a {} page(s) dans cette catégorie'.format(len(self.categorie['urlsLivres'])))
        self.barre=IncrementalBar('pages scrapées : ',max = len(self.categorie['urlsLivres']))
        for index,elem in enumerate(self.categorie['urlsLivres']): # recupere toutes les infos de livre de chaque url
                for el in elem:
                    self.initialiseLivre()
                    self.scrapUnLivre(el)
                    self.livres.append(self.livre)
                self.barre.next()
        self.barre.finish()
        if (nomCSV != 'None'):
            self.fichierCSV=nomCSV
        courant=os.path.abspath(os.path.curdir)
        if (not os.path.isdir(self.dossierScrap)):
            os.mkdir(self.dossierScrap)
        os.chdir(self.dossierScrap)
        self.creeCSVLivresUneCategorie()
        try:
            os.chdir(courant)
        except:
            pass
        print ('Catégorie sauvegardée dans {}'.format('./'+self.dossierScrap+'/'+self.fichierCSV))

    def creeCSVLivresUneCategorie(self):
        """ crée un CSV contenant tous les livres d'une meme categorie
        depuis self.livres"""

        headers = ''
        values = ''
        # print (len(self.livres),self.livres[0])
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
         ces csv sont stockés dans un dossier"""

        self.infosToutesCategories()
        print ('Il y a {} categories'.format(len(self.urlsCategories)))
        for index,elem in enumerate(self.urlsCategories):
            print ('Catégorie {}/{} : {}'.format(index+1,len(self.urlsCategories),elem['csv'][:-4]))
            self.scrapUneCategorie(url=elem['url'],nomCSV=elem['csv'])
        print ('\nSite Web scrapé intégralement\n')

    def trouverNomCategorie(self,url): # OK
        csv = url[::-1]
        csv = csv[csv.find('/') + 1:]
        csv = csv[:csv.find('/')]
        csv = csv[csv.find('_')+1:]
        csv=csv[::-1]
        return( csv)

    def infosToutesCategories(self): # erreur URL
        self.creerObjetSoup(self.urlBase)
        uls=self.soup.findAll('ul')
        # print (len(uls))
        for ul in uls:
            try:
                if (ul['class'] == ['nav', 'nav-list']):
                    lis=ul.find('ul').findAll('li')
                    # print (len(lis))
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
        # print (self.urlsCategories)

if __name__ == '__main__':
    scraping().scrapSiteInternet()