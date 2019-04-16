import sys
from qtpy import QtCore, QtGui, uic, QtWidgets
import weighted
import pandas as pd

global_df = pd.read_csv('global_df_2.csv')
archiwum = pd.read_csv('archiwum_1.csv')
global_df = global_df.append(archiwum, sort=False)


qtCreatorFile = "123.ui"  # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.buttonSUBMIT.clicked.connect(self.display_stats)

    def display_stats(self):
        series = self.inputSERIES.text().upper()
        model = self.inputMODEL.text().upper()
        full = series + model

        ########################

        loc_df = global_df.loc[global_df['Model'] == full]
        used = loc_df[loc_df['Stan:'] == 'Używany']
        new = loc_df[loc_df['Stan:'] == 'Nowy']

        del loc_df
        new.reset_index(drop=True, inplace=True)
        used.reset_index(drop=True, inplace=True)
        final_output = ''

        ###
        s_iloczyn = 0
        s_wag = 0
        if new.empty:
            final_output += "\n Nowe:       -----------------------------"
            final_output += '\n\n Brak takiego nowego modelu'

        else:

            if new['Kupione'].sum() == 0:

                final_output += "\n \nNowe:       -----------------------------"
                final_output += "\n \nŚrednia ważona : Brak - 0 sprzedanych "
                final_output += "\n \nMediana ważona : Brak - 0 sprzedanych"
                final_output += "\n \nStatystyki: \n "
                final_output += new["Cena"].describe()

            else:
                for i in range(0, len(new)):
                    kupione = new['Kupione'][i]
                    s_iloczyn += new['Cena'][i] * kupione
                    s_wag += kupione
                weighted_average = s_iloczyn / s_wag

                final_output += "\n \nNowe:       -----------------------------"
                final_output += "\n \nŚrednia ważona : " + str(weighted_average)
                final_output += "\n \nMediana ważona : " + str(weighted.median(new['Cena'], new['Kupione']))
                final_output += "\n \nStatystyki: \n\n "
                final_output += str(new["Cena"].describe())

        ###
        s_iloczyn = 0
        s_wag = 0
        if used.empty:
            final_output += "\n\n Używane:       --------------------------"
            final_output += '\n\n Brak takiego używanego modelu'
        else:

            if used['Kupione'].sum() == 0:

                final_output += "\n\n Używane:       --------------------------"
                final_output += "\n\n Średnia ważona : Brak - 0 sprzedanych "
                final_output += "\n\n Mediana ważona : Brak - 0 sprzedanych"
                final_output += "\n\n Statystyki: \n\n "
                final_output += used["Cena"].describe()
            else:
                for i in range(0, len(used)):
                    kupione = used['Kupione'][i]
                    s_iloczyn = s_iloczyn + ((used['Cena'][i]) * kupione)
                    s_wag += kupione
                weighted_average = s_iloczyn / s_wag

                final_output += "\n\n Używane:       -----------------------------"
                final_output += "\n\n Średnia ważona : " + str(weighted_average)
                final_output += "\n\n Mediana ważona : " + str(weighted.median(used['Cena'], used['Kupione']))
                final_output += "\n\n Statystyki: \n\n "
                final_output += used["Cena"].describe().to_string()

        self.textBrowser.setText(final_output)
        print(final_output)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())