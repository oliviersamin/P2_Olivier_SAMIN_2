
""" Projet 2 de formation OpenClassRooms
 Mars 2021
 Olivier SAMIN
 """


import requests
from bs4 import BeautifulSoup
import os
import time as t


class scraping():
    """ classe pour le scrapping du site BooksToScrap """
    def __init__(self):
        self.urlsCategories=[]
        self.categorie={'nbLivres':'','nbPages':'','urlsLivres':[],'urlsPages':[]}
        self.fichierCSV='resultats.csv'
        self.urlBase='http://books.toscrape.com/index.html'
        self.urlCatalogue='http://books.toscrape.com/catalogue/'
        self.urlCourante='http://books.toscrape.com/catalogue/category/books/fiction_10/page-1.html'
        self.livres=[]
        self.livre={'product_page_url':'','upc':'','title':'','price_including_tax':'',
                    'price_excluding_tax':'','number_available':'','product_description':'',
                    'category':'','review_rating':'','image_url':''}

    def initialiseLivre(self):
        self.livre={'product_page_url':'','upc':'','title':'','price_including_tax':'',
                    'price_excluding_tax':'','number_available':'','product_description':'',
                    'category':'','review_rating':'','image_url':''}

    def creerObjetSoup(self,url): # OK
        self.urlCourante=url
        self.reponse=requests.get(self.urlCourante)
        self.soup=BeautifulSoup(self.reponse.text,features="html.parser")
        print (self.reponse.text)

    def categoryTitle(self): # OK
        """ trouve et sauvegarde la catégorie et le titre du livre """
        lis=self.soup.findAll('li')
        # print (len(lis))
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

    def image(self): # OK
        """ trouve et sauvegarde l'url de l'image du livre """
        divs=self.soup.findAll('div')
        for elem in divs:
            try:
                if (elem['class'] == ['item', 'active']):
                    image=elem
                    self.livre['image_url']=self.urlBase[:-10]+elem.find('img')['src'][9:]
                    # print (self.livre['image_url'])
            except:
                pass

    def description(self): # OK
        """ trouve et sauvegarde la description du livre """
        ps=self.soup.findAll('p')
        for p in ps:
            if (len(p.contents[0]) >= 50):
                self.livre['product_description']='"'+p.contents[0]+'"'
        # print ('description : ',self.livre['product_description'])

    def autres(self): # OK
        """ trouve et sauvegarde les autres caracteristiques du livre """
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

    def creationCSV1livre(self): # PB encodage string
        """ crée un CSV avec séparateur ';' """
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

    def unLivre(self,urlLivre,csv=False): # OK
        """ execute toutes les methodes pour obtenir toutes les infos cherchees
         si csv == True on génère un fichier CSV pour un seul livre"""
        self.creerObjetSoup(urlLivre)
        self.livre['product_page_url']=urlLivre
        self.categoryTitle()
        self.image()
        self.description()
        self.autres()
        # print ('unLivre : ',self.livre)
        if csv:
            self.creationCSV1livre()

    def liens1pageCategorie(self): # OK
        """ recupere tous les liens de livre pour une seule page de categorie """
        ol=self.soup.find('ol') # recupere tous les liens de livres pour 1 page de categorie
        divs=ol.findAll('div')
        self.categorie['urlsLivres'].append([])
        for elem in divs:
            try:
                self.categorie['urlsLivres'][-1].append(self.urlCatalogue+elem.find('a')['href'][9:])
            except:
                pass

    def infosCategorie(self,urlCategorie): # OK
        """ recupere toutes les infos necessaires à une catégorie """
        self.creerObjetSoup(urlCategorie)
        strongs=self.soup.findAll('strong')
        self.categorie['nbLivres']=int(strongs[1].contents[0])
        self.categorie['nbPages']=int(self.categorie['nbLivres']/20)+1
        # print ('nb Pages = ',self.categorie['nbPages'])
        if (self.categorie['nbPages'] > 1):
            urlUtilisee= urlCategorie[:-10]+'page-1.html'
            # print ('urlCategorie = ',urlCategorie)
            # print ('urlUtilisee = ',urlUtilisee)
            for elem in range(self.categorie['nbPages']): # urls de toutes les pages pour obtenir tous les livres
                self.categorie['urlsPages'].append(urlUtilisee[:-6]+str(elem+1)+'.html')
                # print ('test = ',self.categorie['urlsPages'][-1])
        else:
            self.categorie['urlsPages'].append(urlCategorie)
        # print (self.categorie['urlsPages'])

        for elem in self.categorie['urlsPages']: # recupere toutes les urls des livres dans toutes les pages de la catégorie
            self.creerObjetSoup(elem)
            self.liens1pageCategorie()
        # print (self.categorie)

    def uneCategorie(self,url,nomCSV='None'): # Test nom automatique CSV
        """ execute toutes les methodes pour obtenir le CSV d'une catégorie """
        self.infosCategorie(urlCategorie=url)
        print('Il y a {} page(s) dans cette catégorie....'.format(len(self.categorie['urlsLivres'])))
        for index,elem in enumerate(self.categorie['urlsLivres']): # recupere toutes les infos de livre de chaque url
                print ('scraping de la page ',index)
                for el in elem:
                    # print (el)
                    self.initialiseLivre()
                    self.unLivre(el)
                    # print (self.livre)
                    self.livres.append(self.livre)
        if (nomCSV != 'None'):
            self.fichierCSV=nomCSV
        courant=os.path.abspath(os.path.curdir)
        if (not os.path.isdir('dossierTest')):
            os.mkdir('dossierTest')
        os.chdir('dossierTest')
        self.creationCSVLivresCategorie()
        try:
            os.chdir(courant)
        except:
            pass
        print ('Ctégorie terminée!')

    def creationCSVLivresCategorie(self): # Pb encodage string
        """ crée un CSV contenant tous les livres d'une meme categorie depuis self.livres"""
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

    def toutesCategories(self): # en test
        """ crée un fichier CSV par catgorie contenant les détails de chaque livre """
        self.infosToutesCategories()
        for elem in self.urlsCategories:
            print ('Scrapping de la catégorie {} en cours....'.format(elem['csv'][:-4]))
            self.uneCategorie(url=elem['url'],nomCSV=elem['csv'])
        print ('\nScrapping de toutes les catégories terminé\n')

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
    scraping().toutesCategories()