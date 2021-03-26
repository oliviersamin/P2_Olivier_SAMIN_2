""" Projet 2 de formation OpenClassRooms
 Mars 2021
 Olivier SAMIN
 """

import requests
from bs4 import BeautifulSoup


class scraping():
    """ classe pour le P2 """
    def __init__(self):
        self.fichierCSV='resultats.csv'
        self.urlBase='http://books.toscrape.com/'
        self.urlTest='http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'
        self.reponse=requests.get(self.urlTest)
        self.soup=BeautifulSoup(self.reponse.text,features="html.parser")
        self.livre={'product_page_url':'','upc':'','title':'','price_including_tax':'',
                    'price_excluding_tax':'','number_available':'','product_description':'',
                    'category':'','review_rating':'','image_url':''}

    def categoryTitle(self):
        """ trouve et sauvegarde la catégorie et le titre du livre """
        lis=self.soup.findAll('li')
        for elem in lis: # boucle pour trouver le titre et la catégorie
            try: # pour trouver le titre
                elem['class']
                self.livre['title']=elem.__dict__['contents'][0]
                # print (self.livre['title'])
            except: # pour catégorie
                if ('category' in elem.find('a')['href']):
                    cat=elem.find('a')
                    if (cat.__dict__['contents'][0] != 'Books'):
                        self.livre['category']=cat.__dict__['contents'][0]

    def image(self):
        """ trouve et sauvegarde l'url de l'image du livre """
        divs=self.soup.findAll('div')
        for elem in divs:
            try:
                if (elem['class'] == ['item', 'active']):
                    image=elem
                    self.livre['image_url']=elem.find('img')['src']
                    # print (self.livre['image_url'])
            except:
                pass

    def description(self):
        """ trouve et sauvegarde la description du livre """
        ps=self.soup.findAll('p')
        self.livre['product_description']=ps[-1].__dict__['contents'][0]

    def autres(self):
        """ trouve et sauvegarde les autres caracteristiques du livre """
        trs=self.soup.findAll('tr')
        for elem in trs:
            if (elem.find('th').__dict__['contents'][0]== 'UPC'):
                self.livre['upc']= elem.find('td').__dict__['contents'][0]
            elif (elem.find('th').__dict__['contents'][0]== 'Price (excl. tax)'):
                self.livre['price_excluding_tax'] = elem.find('td').__dict__['contents'][0][1:]
            elif (elem.find('th').__dict__['contents'][0]== 'Price (incl. tax)'):
                self.livre['price_including_tax'] = elem.find('td').__dict__['contents'][0][1:]
            elif (elem.find('th').__dict__['contents'][0]== 'Availability'):
                self.livre['number_available'] = elem.find('td').__dict__['contents'][0]
            elif (elem.find('th').__dict__['contents'][0]== 'Number of reviews'):
                self.livre['review_rating'] = elem.find('td').__dict__['contents'][0]

    def creationCSV(self):
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

    def unLivre(self,urlLivre):
        """ execute toutes les methodes pour obtenir toutes les infos cherchees """
        self.livre['product_page_url']=urlLivre
        self.categoryTitle()
        self.image()
        self.description()
        self.autres()
        self.creationCSV()
        # print(self.livre)


if __name__ == '__main__':
    scraping().unLivre('http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html')
