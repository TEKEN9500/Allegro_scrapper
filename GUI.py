import sys
from qtpy import QtCore, QtGui, uic, QtWidgets
import weighted
import pandas as pd

"""-------------------THIS IS MAIN APPLICATION WITH INTERFACE-------------------"""


# -------READ CSV FILES CREATED IN ALLEGRO.PY AND ARCHIWUM_SCARP.PY-------------
global_df = pd.read_csv('global_df_2.csv')
archiwum = pd.read_csv('archiwum_1.csv')
global_df = global_df.append(archiwum, sort=False)


qtCreatorFile = "123.ui"  # load interface design created in QT DESIGNER


# -----------------Template for creating py apps out of QT DESIGNER ui files - not coded by me ---------------------
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.buttonSUBMIT.clicked.connect(self.display_stats)

        
        
""" ----------------- THE CORE OF THE PROJECT THAT TAKES MODEL FROM INPUT AND CREATES STATISTICS FOR IT -------------------------"""

    def display_stats(self):
        series = self.inputSERIES.text().upper()   # take inputs from GUI
        model = self.inputMODEL.text().upper()
        full = series + model

        loc_df = global_df.loc[global_df['Model'] == full]
        used = loc_df[loc_df['Stan:'] == 'Używany']       # create separate dataframes for used and new models
        new = loc_df[loc_df['Stan:'] == 'Nowy']

        del loc_df
        new.reset_index(drop=True, inplace=True)
        used.reset_index(drop=True, inplace=True)
        final_output = ''

        """ -------- Calculate variables needed for weighted mean, if there is no such model give such information --------
         Save all of the responses (what should be displayed) to the final_output variable. - instead of print in case of using
         terminal """
        
        s_iloczyn = 0 # sum of multiplications for weighted mean
        s_wag = 0     # sum of weights (number of bought units - ( column: Kupione:)
        if new.empty:
            final_output += "\n New:       -----------------------------"
            final_output += '\n\n No such new model'

        else:

            if new['Kupione'].sum() == 0:

                final_output += "\n \nNew:       -----------------------------"
                final_output += "\n \nWeighted mean : Null - 0 sold "
                final_output += "\n \nWeighted median : Null - 0 sold "
                final_output += "\n \nStatistics: \n "
                final_output += new["Cena"].describe()

            else:
                for i in range(0, len(new)):
                    kupione = new['Kupione'][i]
                    s_iloczyn += new['Cena'][i] * kupione
                    s_wag += kupione
                weighted_average = s_iloczyn / s_wag

                final_output += "\n \nNew:       -----------------------------"
                final_output += "\n \nWeighted mean : " + str(weighted_average)
                final_output += "\n \nWeighted median : " + str(weighted.median(new['Cena'], new['Kupione']))
                final_output += "\n \nStatistics: \n\n "
                final_output += str(new["Cena"].describe())

        ###
        s_iloczyn = 0
        s_wag = 0
        if used.empty:
            final_output += "\n\n Used:       --------------------------"
            final_output += '\n\n No such used model'
        else:

            if used['Kupione'].sum() == 0:

                final_output += "\n \nUsed:       -----------------------------"
                final_output += "\n \nWeighted mean : Null - 0 sold "
                final_output += "\n \nWeighted median : Null - 0 sold "
                final_output += "\n \nStatistics: \n "
                final_output += used["Cena"].describe()
            else:
                for i in range(0, len(used)):
                    kupione = used['Kupione'][i]
                    s_iloczyn = s_iloczyn + ((used['Cena'][i]) * kupione)
                    s_wag += kupione
                weighted_average = s_iloczyn / s_wag

                final_output += "\n\n Used:       -----------------------------"
                final_output += "\n\n Weighted mean : " + str(weighted_average)
                final_output += "\n\n Weighted median : " + str(weighted.median(used['Cena'], used['Kupione']))
                final_output += "\n\n Statistics: \n\n "
                final_output += used["Cena"].describe().to_string()

        self.textBrowser.setText(final_output) #display output in GUI display window (text browser class)
        

# end part of template - allows application to last
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
