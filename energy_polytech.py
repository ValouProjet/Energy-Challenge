import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
from datetime import datetime



#--------------------------------IMPORTER LES FICHIERS EXCELS----------------------------------

link_data_template_polytech = "C:\\Users\\Cron\\Desktop\\topush2\\Energy-Challenge\\polytech_data\\Building_Data_Template_Polytech.xlsx"
link_power_polytech_buildings = "C:\\Users\\Cron\\Desktop\\topush2\\Energy-Challenge\\power_polytech_data\\"

#----------------------------------------FONCTIONS----------------------------------------------

def generate_numbers_as_strings(n):
    
    numbers_as_strings = []

    for i in range(1, n + 1):
        number_string = str(i).zfill(2)
        numbers_as_strings.append(number_string)

    return numbers_as_strings


def temperature_tri() :
    lien_fichier_excel = link_data_template_polytech
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
 

def puissance_monitoring(batiment):
    
    # Chargez le fichier CSV
    csv_file = link_power_polytech_buildings + batiment 
    # Spécifiez le séparateur de décimal comme une virgule
    df = pd.read_csv(csv_file, parse_dates=['DATETIME'], delimiter=';', decimal=',')
    
    
    # Assurez-vous que les dates sont triées dans l'ordre croissant
    df = df.sort_values(by='DATETIME')
    
    # Créez une colonne d'heure
    df['Hour'] = df['DATETIME'].dt.hour
    
    # Créez une colonne de date
    df['Date'] = df['DATETIME'].dt.date
    
    # Groupez les données par heure et calculez la puissance moyenne pour chaque heure
    power_df = df.groupby(['Date', 'Hour'])['P'].mean().reset_index()
    
    power_df = search_error_and_solve(power_df)
    
    # Affichez le résultat
    #print(power_df)
    

    
    # Supposons que 'result' soit le DataFrame contenant les puissances moyennes
    puissances_moyennes = power_df['P'].values
    
    return puissances_moyennes


def search_error_and_solve(vecteur):
    
    tableau_tot = vecteur
    
    dernier_indice = tableau_tot.index[-1] #récupérer le dernier indice (la dernière ligne)
    
    heure_attendue = 0
    
    nombre_erreurs_attendues = 8760-dernier_indice-1
    ligne_des_erreurs = np.zeros(nombre_erreurs_attendues) #Si il y a 8760 lignes, pas d'erreur
                                                           #donc pas de tableau.
    indice_tableau = 0
    
    if(len(ligne_des_erreurs) > 0):
        for n in range(0, dernier_indice): #on itère de 2 à la fin (dernier_indice)
            y = tableau_tot['Hour'][n]
        
            if(y == heure_attendue):
              if(heure_attendue==23):
                  heure_attendue=0
              else:
                  heure_attendue+=1
            else:
              print('ERROR (SOLVED) : Ligne', n+1, '| Heure :', heure_attendue)
              ligne_des_erreurs[indice_tableau] = n+1
              indice_tableau+=1
              
              puissance_bas = tableau_tot['P'][n-1]
              puissance_haut = tableau_tot['P'][n+1]
              moyenne_puissance = (puissance_bas+puissance_haut)/2
              date = tableau_tot['Date'][n-1]
              
              ligne_a_inserer = {'Date': date, 'Hour': heure_attendue, 'P': moyenne_puissance}
              
              avant = tableau_tot.iloc[:n]
              apres = tableau_tot.iloc[n:]
              
              tableau_tot = pd.concat([avant, pd.DataFrame([ligne_a_inserer]), apres], ignore_index=True)
              #print(tableau_tot)
              
              #si il y a eu une erreur, il faut aller chercher 2 indices plus loin
              #(on passe par exemple de 4 à 6 donc +2 dans l'indice attendu).
              if(heure_attendue == 23):
                heure_attendue=0
              else:
                heure_attendue+=1
    return tableau_tot




#----------------------------------------------------------------------------------------------------
#----------------------------------------CODE PRINCIPAL----------------------------------------------
#----------------------------------------------------------------------------------------------------

Temp = temperature_tri()
print('on a les 8760 températures ')
# Les indices triés des températures (du plus froid au plus chaud)
indices_tries = np.argsort(Temp)
temperatures_triees = Temp[indices_tries]
#,'B53_c.csv'
#,'B52_c.csv'
#,'B49_47_CHA_CC.csv'
compteur_base = ['B28_CHA_CC.csv','B52_CHA_CC.csv','B52_CHA_RC_BUR.csv','B52_CHA_RC_HALL.csv','B37_c.csv','B48_c.csv']
#compteur_base = ['B37_c.csv']

for i in range(len(compteur_base)) : 
    print(compteur_base[i])
    vecteur_puissances = puissance_monitoring(compteur_base[i])
    puissances_moyennes = vecteur_puissances

    #taille = len(puissances_moyennes)
    # Les indices triés des puisssances de la plus grande à la plus petite
    indices_tries_2 = np.argsort(puissances_moyennes)[::-1]
    puissances_triees = puissances_moyennes[indices_tries_2]
    
    building = compteur_base[i]
    if (compteur_base[i] == 'B28_CHA_CC.csv'):
        building = 'B28'
    if (compteur_base[i] == 'B49_47_CHA_CC.csv'):
        building = 'B49_1'
    #---------------------------------------------------------------------------------------------------------
    if (compteur_base[i] == 'B52_CHA_CC.csv'):
        building = 'B52_9'
        #ici on devrait soustraire les compteur B52_CHA_RC_BUR,B52_CHA_RC_HALL,B52_c du compteur B52_CHA_CC
    #----------------------------------------------------------------------------------------------------------
    if (compteur_base[i] == 'B52_CHA_RC_BUR.csv'):
        building = 'B52_3'
    if (compteur_base[i] == 'B52_CHA_RC_HALL.csv'):
        building = 'B52_6_7_8'
    if (compteur_base[i] == 'B52_c.csv'):
        building = 'B52_4'
    if (compteur_base[i] == 'B37_c.csv'):
        building = 'B37'
    if (compteur_base[i] == 'B53_c.csv'):
        building = 'B53'
    if (compteur_base[i] == 'B48_c.csv'):
        building = 'B48'
        
        
    nombre_heure = range(0, 8760)
    
    for k in range(8760):
        if (puissances_moyennes[k]<0):
            puissances_moyennes[k] = 0
    k=0
    for k in range(8760):
        if (puissances_triees[k]<0):
            puissances_triees[k] = 0
            
    
    # Créez un graphique de la puissance moyenne en fonction de la température
    plt.plot(nombre_heure, puissances_moyennes, color='orangered')
    plt.title(f"Load profile ({building})")
    plt.ylabel("Mean power (kW)")
    plt.grid(True, alpha=0.3)
    mois = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    plt.fill_between(nombre_heure, puissances_moyennes, where=puissances_moyennes>0, alpha=0.7, color='tomato')  
    
    jours_an = range(1, 8760)
    plt.xticks(jours_an[::730][:12], mois, rotation=90)
    #plt.xticks(nombre_heure[::(30*24)][:12], mois, rotation=90) 
    # Spécifiez l'emplacement et le nom du fichier
    #file_path = "C:\\Users\\Romain\\Desktop\\Master 1\\Energy challenge\\Signature_Thermique\\load profile monitoring\\building_a"+building
    # Enregistrez le graphique dans le fichier spécifié
    #plt.savefig(file_path)
    plt.show()
    
    plt.figure(figsize=(10, 6))
    plt.scatter(temperatures_triees,puissances_triees, alpha=0.5)
    plt.xlabel('Temperature (°C)')
    plt.ylabel('Mean power (kW)')
    plt.title(f"Thermal signature ({building})")
    plt.grid(True)
    # Spécifiez l'emplacement et le nom du fichier
    #file_path = "C:\\Users\\Romain\\Desktop\\Master 1\\Energy challenge\\Signature_Thermique\\load profile monitoring\\building_b"+building
    # Enregistrez le graphique dans le fichier spécifié
    #plt.savefig(file_path)
    plt.show()





















