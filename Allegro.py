from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import numpy as np

p = re.compile('https://allegro.pl/oferta/.+?(?=")') #pattern to later extract link of a given offer
global_df = pd.DataFrame()
counter = 0              #used to display which paged is being processed, because I am impatient
for page in range(1, 100):
    response = requests.get(
        'https://allegro.pl/kategoria/podzespoly-komputerowe-karty-graficzne-260019?p={}'.format(page)) #create link for pages filled with offers
    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.find_all(class_='_8d855a8')   #this class contains a single offer,

    print('page: {}'.format(page))

    for post in posts:
        df = pd.DataFrame(np.empty((1, 1)))
        link = p.search(str(post)).group()                          #find link for full page of the offer
        offer = BeautifulSoup(requests.get(link).text, 'html.parser')
        parameters = offer.find_all(class_='e70c44ee')              #class containing parameters of GPU
        values = offer.find_all(class_='_2036b558')                 #and corresponding values of parameters
        name = offer.find('meta', itemprop='name')['content']       #get name
        price = offer.find('meta', itemprop='price')['content']     #get price
        kupione = offer.find(class_="_7e747be3 f9f11a08")           #get information about how many units of such offer
                                                                    # have been bought

        #create columns in dataframe for all these things
        df['Nazwa'] = name
        df['Cena'] = int(float(price))
        df['Link'] = link
        df['Kupione'] = kupione

        df.drop(0, axis=1, inplace=True)

        # for each parameter create separate column
        for i in range(0, len(parameters)):
            df[parameters[i].text] = values[i].text

        global_df = global_df.append(df, ignore_index=True) #append one row (1 offer -> 1 row) to global dataframe
        counter += 1
        print('post: {}'.format(counter))
        print(link)

del post, posts, values, soup, parameters, page, response, p, offer, name, link, kupione, price
###

"""
Now in column "Kupione" we have a full sentence "60 osób kupiło 65 sztuk" which means "60 people bought 65 units".
I will extract the digit before "sz" to get only how many units were bought. This will later provide information
for calculation of weighted mean which will be more relevant than simple mean of price of all observation for a
given GPU model. Weighted mean will ignore the prices at which people did not buy, and promote prices that made
the offer popular, which is crucial as the project goal is to advise the real price of given GPU on current market.
"""
global_df['Kupione'] = global_df['Kupione'].str.extract('(\d+) sz',expand=False)
global_df.loc[global_df['Kupione'].isnull(), 'Kupione'] = 0
global_df = global_df[global_df['Producent chipsetu:'].isin(values=['AMD', 'NVIDIA'])]
global_df = global_df[global_df['Cena']>400]
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
        model = [model for model in models if model in global_df['Seria:'][i]]
        if model != []:
            model = model[0]
            global_df.loc[i, 'Model'] = model.upper()
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

for i in range(0,len(global_df)):
    if global_df.loc[i, 'Producent:'] == "Inny producent":

        producer = [producer for producer in producers_list if producer in global_df['Nazwa'][i]]
        if producer != []:
            producer = producer[0]
            global_df.loc[i, 'Producent:'] = producer
            global_df.loc[i, 'Nazwa'] = global_df['Nazwa'][i].replace(producer, '')


        else:
            global_df.loc[i,'Producent:'] = global_df['Producent chipsetu:'][i]
    else:
        for word in producers_list:
            global_df.loc[i,'Nazwa']= global_df['Nazwa'][i].replace(word, '')

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
global_df.rename(columns = {'Unnamed: 0':'Index'}, inplace=True)

global_df = global_df[['Cena','Kupione', 'Chłodzenie:', 'Faktura:',
       'Interfejs złącza karty:', 'Pamięć:',
       'Producent chipsetu:', 'Producent:', 'Rodzaj pamięci:',
       'Stan:', 'Szyna pamięci:', 'Model', 'Nr model']]

global_df['Model'] = global_df['Model']+global_df['Nr model']
global_df.drop('Nr model', axis=1, inplace=True, )

for i in range(0,len(global_df)):
    if 'GB' in global_df['Pamięć:'][i]:
        global_df.loc[i, 'Pamięć:'] = global_df['Pamięć:'][i].replace(' GB', '')
    else:
        global_df.drop(i, axis=0, inplace=True)

global_df['Pamięć:'] = global_df['Pamięć:'].astype(int)
global_df['Szyna pamięci:'] = global_df['Szyna pamięci:'].str.replace('-bit', '').astype(int)

global_df.to_csv('global_df_2.csv')

global_df_dummy = pd.get_dummies(global_df)
global_df_dummy.to_csv('global_df_dummy_2.csv')

global_df = pd.read_csv('global_df_2.csv')
