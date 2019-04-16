from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import numpy as np


# ----THE SAME AS ALLEGRO SCRAPPER BUT ADJUSTED TO ARCHIVE OF ALLEGRO, DIFFERENT CLASSES, LESS PARAMETERS, INFROMATION IN OTHER PLACES-----

p = re.compile('/oferta/.+?(?=")')
global_df = pd.DataFrame()
counter = 0
for page in range(1, 160):
    response = requests.get(
        'https://archiwum.allegro.pl/kategoria/obraz-i-grafika-karty-graficzne-257236?p={}'.format(page)) #other link
    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.find_all(class_='_8d855a8')
    print('page: {}'.format(page))

    for post in posts:
        df = pd.DataFrame(np.empty((1, 1)))
        link = p.search(str(post)).group()
        link = 'https://archiwum.allegro.pl/' + link
        offer = BeautifulSoup(requests.get(link).text, 'html.parser')
        parameters = str(offer.find_all(class_="asi-attributes__item-list__value"))
        stan = re.search('(Nowy|Używany)',str(parameters))
        if stan is not None:
            stan = stan.group(1)
        name = offer.find('meta', itemprop='name')#['content']
        if name is not None:

            name = name['content']
            offer_id = str(offer.find(class_="asi-offer__offer-id"))
            offer_id = re.search('(\d+)', offer_id).group(1)
            parameters = offer.find_all(class_='e70c44ee')
            values = offer.find_all(class_='_2036b558')
            price = str(offer.find(class_="asi-offer__price m-price m-price--primary"))
            price = re.search('(\d+ ?\d*|Nie było ofert kupna)', price).group(1) # find price or 'No purchase offers'
            price_offered = re.search('fee8042">(\d\d? ?\d*)', str(post)).group(1) #find price proposed by seller(not final price)
            re.search('(\d\d? ?\d*)',str('1 700')).group(1)
            df['Nazwa'] = name.replace("Kup podobny do ", "") # in archive name there is "Buy simmiliar to" before actual name, delete it
            df['Cena kupiona'] = price.replace(" ", "")    # price bought(final) - remove spaces
            df['Cena zaoferowana'] = price_offered.replace(" ", "")   # price offered by seller - remove spaces
            df['Link'] = link
            df['offer_id'] = offer_id
            df['Stan:'] = stan # condition: new/used

            df.drop(0, axis=1, inplace=True)
            for i in range(0, len(parameters)):
                df[parameters[i].text] = values[i].text

            global_df = global_df.append(df, ignore_index=True)
        counter += 1
        print('post: {}'.format(counter))
        print(link)
        
        

        
"""#in archve there is no information about how many units were bought because these are single offers, -----------------------------
so if the price bought exists at all instead of " No offers" it means it was bought once and here I will define that"""

global_df['Kupione']=0    
global_df.loc[global_df['Cena kupiona'] != 'Niebyłoofertkupna', 'Kupione' ] = 1
global_df.loc[global_df['Cena kupiona'] == 'Niebyłoofertkupna','Cena kupiona'] = 'Brak'



"""----------------FROM NOW ON BASICALLY EVERYTHING IS ANALOGICAL TO THE ALLEGRO.PY---------------------------- """

global_df['Cena zaoferowana'] = global_df['Cena zaoferowana'].astype(int)
global_df = global_df[global_df['Cena zaoferowana']>400]
global_df.reset_index(drop=True, inplace=True)


#getting only model with RX, RTX, GTX, Quadro in the name:
global_df['Model'] = 'NA'
models= ['Rx','rx','RX', 'Rtx', 'RTX','rtx','GTX', 'gtx','Gtx', 'Quadro', 'quadro', 'QUADRO']

for i in range(0,len(global_df)):

    model = [model for model in models if model in global_df['Nazwa'][i]]
    if model != []:
        model = model[0]
        global_df.loc[i, 'Model'] = model.upper()
        #global_df.loc[i, 'Nazwa'] = global_df['Nazwa'][i].replace(model, '')

    else:
        global_df.drop(i, axis=0, inplace=True)

global_df.reset_index(drop=True, inplace=True)
del models



remove_words = ['karta', 'Karta', 'KARTA', 'Graficzna', 'GRAFICZNA', 'graficzna',
                'wyprzedaż', 'WYPRZEDAŻ', 'Wyprzedaż', 'GRAFIKA', 'Grafika', 'grafika',
                'POTĘŻNA', 'DLA GRACZA', ' !!!', '!!!' ,'!', 'grafiki', 'kar', 'NVIDIA',
                'nvidia', 'nVidia','AMD', 'Nvidia', 'GeForce', 'GEFORCE','Radeon','RADEON','Gaming', 'GAMING',
                'OC','oc', 'Pulse','PULSE', 'PRO', 'pro', 'Pro', 'STRIX', 'Strix', 'promocja','promo','PROMO','PROMOCJA',
                'WindForce', 'WINDFORCE', 'Windforce', 'StormX']

pat = '|'.join(remove_words)
del remove_words
global_df['Nazwa'] = global_df['Nazwa'].str.replace(pat, '')
del pat

for column in list(global_df.columns):
    nan_percent = ((global_df[column].isnull().sum())/3454)*100
    print('{}  :  {}% missing'.format(column,nan_percent))

    if nan_percent >= 10:
        global_df.drop(column, axis = 1, inplace = True)
        print('\n DELETED \n')


producers_list = ['ASUS','Asus','MSI','Msi', 'msi','Gainward','GAINWARD','Gigabyte','GIGABYTE','Evga',
                  'EVGA','ZOTAC', 'Zotac','GALAX', 'Galax','Pny', 'PNY','PALIT', 'Palit','POWERCOLOR',
                  'PowerColor','SAPPHIRE', 'Sapphire', 'INNO3D','VISIONTEK', 'ASROCK', 'MANLI',
                  'Inno3D', 'XFX', 'HIS', 'VisionTek', 'ASRock', 'AFOX', 'Manli', ]
global_df.reset_index(drop=True, inplace=True)


global_df['Producent:'] = 'NA'
for i in range(0,len(global_df)):

    producer = [producer for producer in producers_list if producer in global_df['Nazwa'][i]]
    if producer != []:
        producer = producer[0]
        global_df.loc[i, 'Producent:'] = producer
        global_df.loc[i, 'Nazwa'] = global_df['Nazwa'][i].replace(producer, '')


    else:
        global_df.drop(i, axis=0, inplace=True)


del producers_list


global_df['Nr model'] = global_df['Nazwa'].str.extract('((?i)\d\d\d\d*[ -]*ti|(?i)\d\d\d\d*)', expand=False).str.replace(" ","").str.lower()




global_df['Nr model'] = global_df['Nazwa'].str.extract('((?i)\d\d\d\d*[ -]*ti|'   #GTX 1080 Ti, RTX-2080-ti
                                                       '(?i)vega[ -]*\d\d|'       #RX VEGA64
                                                       '(?i)[KMP]\d\d\d\d*|'          #Quadro K5000
                                                       '(?i)NVS[ -]*\d\d\d|'
                                                       '(?i)titan [XZ]|(?i)titan|'          #QUADRO NVS303
                                                       '(?i)\d\d\d\d*)',          #GTX 760
                                                       expand=False).str.replace(" ","").str.lower()


global_df.drop(global_df[global_df['Nr model'].isnull()].index, axis = 0, inplace = True)
global_df.reset_index(drop=True, inplace=True)


global_df['Model'] = global_df['Model']+global_df['Nr model']
global_df.drop('Nr model', axis=1, inplace=True, )

global_df['Cena'] = global_df['Cena zaoferowana'] #it turns out that actual price was always price offered so thats how system works

global_df.to_csv('archiwum_1.csv')

"""
global_df_dummy = pd.get_dummies(global_df)
global_df_dummy.to_csv('global_df_dummy_2.csv')  if necessary for modeling
global_df = pd.read_csv('global_df_2.csv')
"""
