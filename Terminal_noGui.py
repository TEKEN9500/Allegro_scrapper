import pandas as pd
import numpy as np
import weighted

""" -------- THIS IS BASICALLY THE DISPLAY_STATS FUNCTION FROM GUI.PY FILE BUT IS ABLE TO RUN IN TERMINAL WITHOUT GUI---------"""
#and here the labels for statistics are in polish 
#instead of saving it to output variable its just using print

global_df = pd.read_csv('global_df_2.csv')
archiwum = pd.read_csv('archiwum_1.csv')
global_df = global_df.append(archiwum, sort=False)


b = input('GTX/RX/RTX/QUADRO:').upper()
a = input('Input GPU model like 2070/1650ti/k4000/vega64 :').lower()
b = b+a

loc_df = global_df.loc[global_df['Model'] == b]
used = loc_df[loc_df['Stan:']=='Używany']
new = loc_df[loc_df['Stan:']=='Nowy']

del loc_df
new.reset_index(drop=True, inplace=True)
used.reset_index(drop=True, inplace=True)

###
s_iloczyn = 0
s_wag = 0
if new.empty :
    print("\n Nowe:       -----------------------------")
    print('\n Brak takiego nowego modelu')

else:

    if new['Kupione'].sum() == 0:

        print("\n Nowe:       -----------------------------")
        print("\n Średnia ważona : Brak - 0 sprzedanych " )
        print("\n Mediana ważona : Brak - 0 sprzedanych" )
        print("\n Statystyki: \n ")
        print(new["Cena"].describe())
    else:
        for i in range(0,len(new)):
            kupione = new['Kupione'][i]
            s_iloczyn += new['Cena'][i] * kupione
            s_wag += kupione
        weighted_average = s_iloczyn/s_wag

        print("\n Nowe:       -----------------------------")
        print("\n Średnia ważona : " + str(weighted_average))
        print("\n Mediana ważona : " + str(weighted.median(new['Cena'], new['Kupione'])))
        print("\n Statystyki: \n ")
        print(new["Cena"].describe())


###
s_iloczyn = 0
s_wag = 0
if used.empty:
    print("\n Używane:       --------------------------")
    print('\nBrak takiego używanego modelu')
else:

    if used['Kupione'].sum() == 0:

        print("\n Używane:       --------------------------")
        print("\n Średnia ważona : Brak - 0 sprzedanych ")
        print("\n Mediana ważona : Brak - 0 sprzedanych")
        print("\n Statystyki: \n ")
        print(used["Cena"].describe())
    else:
        for i in range(0, len(used)):
            kupione = used['Kupione'][i]
            s_iloczyn = s_iloczyn + ((used['Cena'][i]) * kupione)
            s_wag += kupione
        weighted_average = s_iloczyn / s_wag

        print("\n Używane:       -----------------------------")
        print("\n Średnia ważona : " + str(weighted_average))
        print("\n Mediana ważona : " + str(weighted.median(used['Cena'], used['Kupione'])))
        print("\n Statystyki: \n ")
        print(used["Cena"].describe())
