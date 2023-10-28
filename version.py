import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
from datetime import datetime

def temperature_tri() :
    lien_fichier_excel = "C:\\Users\\Romain\\Desktop\\Master 1\\Energy challenge\\Signature_Thermique\\Building_Data_Template_Polytech.xlsx"
    meteo = pd.read_excel(io=lien_fichier_excel, sheet_name='Meteo')
    
    
    months = ['jan', 'FEB', 'mar', 'APR', 'MAY', 'jun', 'jul', 'AUG', 'sep', 'oct', 'nov', 'DEC']     
    
    hours_bis = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
    
    day = 0 #on démarre au jour 0 de l'année et on va itérer
    
    #tableau regroupant les températures moyennes de CHAQUE jour de l'année (utilisé plus tard pour plot)
    Temp = np.zeros(8760)
    t = 0
    
    for m in months:
        if (m == 'FEB'):
            days = generate_numbers_as_strings(28)
        elif (m == 'jan' or m == 'mar' or m == 'MAY' or m == 'jul' or m == 'AUG' or m == 'oct' or m == 'DEC'):
            days = generate_numbers_as_strings(31)
        elif (m == 'APR' or m == 'jun' or m == 'sep' or m == 'nov'):
            days = generate_numbers_as_strings(30)
        else:
            print("ERROR IN WRITING THE MONTH !") #si jamais on recopie mal le mot dans le fichier excel...
            sys.exit()
        
        for d in days:
            if (m == 'FEB' or m == 'APR' or m == 'MAY' or m == 'AUG' or m == 'DEC'):
                lign = d+'-'+m+'-2021'
                day_lign = meteo.loc[meteo['Date'] == lign]
            else:
                lign = d+'-'+m+'-21'
                real_date = datetime.strptime(lign, '%d-%b-%y')
                day_lign = meteo.loc[meteo['Date'] == real_date]
            
            for h in hours_bis:
                temperature = day_lign['Temperature C'].values[h]          
                Temp[t] = temperature
                t+=1
            
            day += 1
    return Temp




# Chargez le fichier CSV
csv_file = "C:\\Users\\Romain\\Desktop\\Master 1\\Energy challenge\\donnee_energie\\B48_c.csv"  # Remplacez par le chemin de votre fichier CSV
df = pd.read_csv(csv_file, parse_dates=['DATETIME'], delimiter=';')

# Assurez-vous que les dates sont triées dans l'ordre croissant
df = df.sort_values(by='DATETIME')

# Créez une colonne d'heure
df['Hour'] = df['DATETIME'].dt.hour

# Créez une colonne de date
df['Date'] = df['DATETIME'].dt.date

# Groupez les données par heure et calculez la moyenne pour chaque heure
result = df.groupby(['Date', 'Hour'])['P'].mean().reset_index()

# Affichez le résultat avec les colonnes
print(result)

# Enregistrez le résultat dans un nouveau fichier CSV si nécessaire
result.to_csv('resultat.csv', index=False)
