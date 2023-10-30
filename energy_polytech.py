import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
from datetime import datetime


#----------------------------------------------------------------------------------------------------
#--------------------------------------IMPORTER LES FICHIERS EXCELS----------------------------------
#----------------------------------------------------------------------------------------------------


link_data_template_polytech = "C:\\Users\\Cron\Desktop\\topush2\\Energy-Challenge\\polytech_data\\Building_Data_Template_Polytech.xlsx"
link_power_polytech_buildings = "C:\\Users\\Cron\\Desktop\\topush2\\Energy-Challenge\\power_polytech_data\\"

#available_buildings = [ 'B26', 'B28', 'B37', 'B48', 'B48_2', 'B49', 'B52_3', 'B52_4', 'B52_6-7-8', 'B52_9','B53', 'B56', 'B57', 'B65']
buildings_selected = ['B28']

#available_excel_files (working) : ['B37_c.csv', 'B28_CHA_CC.csv','B52_CHA_CC.csv','B52_CHA_RC_BUR.csv','B52_CHA_RC_HALL.csv','B37_c.csv','B48_c.csv']
buildings_excel_selected = ['B28_CHA_CC.csv']

#----------------------------------------------------------------------------------------------------
#-------------------------------------------FONCTIONS------------------------------------------------
#----------------------------------------------------------------------------------------------------

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
    power_df_original = df.groupby(['Date', 'Hour'])['P'].mean().reset_index()
    
    power_df = search_error_and_solve(power_df_original)
    
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

def human_heat(active, T_base_inside, K, A_ground, occup_building, h):
    if(active == 'False'):
        return 0
    elif(active == 'True'):
        o=4
        val = occup_building[0] #valeur multiplicative
        
        val = val * occup_building[o+h]

        P_people = val * A_ground

        return P_people
    else:
        print('ERROR IN THE INPUT PARAMETERS OF THE FUNCTION human_heat()')

def theoritical_model(building_base, is_human_heating):
    k=0
    for k in range (len(building_base)) : 
            
        building = building_base[k]
        T_building = 15
        
        U_walls = 1.7 #coefficient de conductivité thermique du Béton [W/m²K]
        U_windows = 1.5 #coefficient de conductivité thermique du double vitrage [W/m²K]
        U_roof = 0.45 #coefficient de conductivité thermique d'une toiture isolée [W/m²K]
        
        lien_fichier_excel = link_data_template_polytech
        
        #--------------------------------------------------------------------#
        
        
        geometry = pd.read_excel(io=lien_fichier_excel, sheet_name='Geometry')
        occupation = pd.read_excel(io=lien_fichier_excel, sheet_name='Occupation')
        
        
        #récupère uniquement les données du bâtiment voulu (spécifié plus haut)
        row_building = geometry.loc[geometry['Building Geometry'] == building]
        occup_building = occupation[building]
        
            
        
        
        #récupère la hauteur du pignon (si c'est 0 on sait que le toit est plat et peut être
        #considéré comme un toit plat en béton béton)
        Pignon = row_building['Height pignon m'].values[0]
        is_roof_flat = 'False'
        
        if(Pignon == 0):
            U_roof = U_walls
            is_roof_flat = 'True'
        
        
        #récupère les surfaces des murs et du toit
        A_walls = row_building['Wall surface'].values[0]
        
        A_windows_N = row_building['north'].values[0]
        A_windows_E = row_building['east'].values[0]
        A_windows_S = row_building['south'].values[0]
        A_windows_W = row_building['west'].values[0]
        
        A_windows = A_windows_N + A_windows_E + A_windows_S + A_windows_W
        A_roof = row_building['Zone surface m^2'].values[0]
        A_ground = row_building['Zone surface m^2'].values[0]
        
        if(is_roof_flat == 'True'):
            A_roof = row_building['Zone surface m^2'].values[0]
        elif(is_roof_flat == 'False'):
            A_roof = row_building['Zone surface m^2'].values[0] #!!!à changer pour calculer la surface du toit!!!
        else:
            print("ERROR IN DEFINING THE SHAPE OF THE ROOF !")
            sys.exit()
        
        #dans la formule Q = K*(T_in-T_out), on peut déjà déterminer K
        K = (A_walls*U_walls) + (A_windows*U_windows) + (A_roof*U_roof)
        
        #En revanche pour déterminer T_out, ça dépend des jours, des heures... on va donc itérer
        #sur toute l'année.
        
        months = ['jan', 'FEB', 'mar', 'APR', 'MAY', 'jun', 'jul', 'AUG', 'sep', 'oct', 'nov', 'DEC']
        
        hours = generate_numbers_as_strings(24)
        
        T_hours = temperature_tri()
        Q_hours = np.zeros(8760) #consommation de chaque heure
        Q_hours_bis = np.zeros(8760) #consommation de chaque heure
        
        indice_hour = 0
        
        #Note pour le lecteur : Ci-dessous, le code va permettre d'itérer pour chaque jour de l'année pour calculer
        #la demande énergétique du bâtiment POUR CHAQUE JOUR (sur base de la moyenne de la température journalière)
        #grâce à la formule qui se trouve dans la partie du cours de Mr. LEMORT sur les besoins énergétiques.
        #La formule est : Q_load = K * temps * (T_building-T_out). Au fur et à mesure, la boucle remplit le 
        #tableau Q_days (une case = besoins énergétiques sur 1 jour, comme il y a 365 jours -> 365 cases).
        
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
                indice_h = 0
                for h in hours:         
                    P_people = human_heat(is_human_heating, T_building, K, A_ground, occup_building, indice_h)
                    indice_h+=1
                    
                    T_NH = T_building  - (P_people/K)
                    Q_hour = (K/1000)*(T_NH - T_hours[indice_hour]) #LA FORMULE pour calculer la puissance recquise.
                    
                    Q_hours[indice_hour] = Q_hour
                    if (is_human_heating == 'True'):
                        #-----------------------------------------------------------------------------------------------
                        #-----------------autre couleur si pas de personnes---------------------------------------------
                        P_people_bis = 0
                        T_NH = T_building  - (P_people_bis/K)
                        Q_hour_bis = (K/1000)*(T_NH - T_hours[indice_hour]) #LA FORMULE pour calculer la puissance recquise.
                        
                        Q_hours_bis[indice_hour] = Q_hour_bis
                        #-----------------------------------------------------------------------------------------------
                    indice_hour += 1
        
        
        #Ci dessous: Permet de redéfinir les puissances négatives à 0 (une puissance négative signifie
        #que l'extérieur du bâtiment est plus chaud que l'intérieur, nottament en été. Il n'y a donc
        #pas besoin de fournir un apport en chaleur, donc on définit la valeur à 0.)
        for i in range(len(Q_hours)):
            if Q_hours[i] < 0:
                Q_hours[i] = 0
        for i in range(len(Q_hours_bis)):
            if Q_hours_bis[i] < 0:
                Q_hours_bis[i] = 0
                
        #-------------------------#PLOTS#-------------------------------#
        
        #SECTION uniquement réservée au plot des graphs et à l'estétique de ces derniers.   
        heures_an = range(0, 8760)
        
        plt.plot(heures_an, (Q_hours), color='blue')
        plt.title(f"Theoritical load profile ({building})")
        plt.ylabel("Power consumed [kW]")
        plt.grid(True, alpha=0.3)
        #plt.ylim(0, 1)
        mois = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        plt.fill_between(heures_an, (Q_hours), where=Q_hours>0, color='blue')
        
        plt.xticks(heures_an[::(30*24)][:12], mois, rotation=90)
        # Spécifiez l'emplacement et le nom du fichier
        #file_path = "C:\\Users\\Romain\\Desktop\\Master 1\\Energy challenge\\Signature_Thermique\\load profile occupation\\building_a"+building_base[k]

        # Enregistrez le graphique dans le fichier spécifié
        #plt.savefig(file_path)
        plt.show()
                
        plt.scatter(T_hours, (Q_hours), color='blue', label='With people')
        if (is_human_heating == 'True'):
            plt.scatter(T_hours, (Q_hours_bis), color='orangered', label='Without people')
        plt.title(f"Theoritical thermal signature ({building})")
        plt.xlabel("θ [°C]")
        plt.ylabel("Power consumed [kW]")
        plt.grid(True, alpha=0.3)
        plt.legend()
        #plt.ylim(0, 1)
        # Spécifiez l'emplacement et le nom du fichier
        #file_path = "C:\\Users\\Romain\\Desktop\\Master 1\\Energy challenge\\Signature_Thermique\\load profile occupation\\building_b"+building_base[k]

        # Enregistrez le graphique dans le fichier spécifié
        #plt.savefig(file_path)
        plt.show()
        return Q_hours

def monitoring_model(compteur_base, temperature_tri ):
    

    #REAL DATE PLOTS
    for i in range(len(compteur_base)) : 
        print(compteur_base[i])
        puissances_moyennes = puissance_monitoring(compteur_base[i])
    
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
            vecteur_total = puissances_moyennes
            vecteur_BUR = puissance_monitoring(compteur_base[i+1])
            vecteur_HALL = puissance_monitoring(compteur_base[i+2])
            #vecteur_c = puissance_monitoring(compteur_base[i+3]) à rajouter quand on a réglé le soucis du B52_c
            puissances_moyennes  = vecteur_total - vecteur_BUR - vecteur_HALL #-vecteur_c
    
            indices_tries_2 = np.argsort(puissances_moyennes)[::-1]
            puissances_triees = puissances_moyennes[indices_tries_2]
            
            #ici on doit soustraire les compteur B52_CHA_RC_BUR,B52_CHA_RC_HALL,B52_c du compteur B52_CHA_CC
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
    
        #-----------------------------------------------PLOTS----------------------------------------------------
        
        # Créez un graphique de la puissance moyenne en fonction de la température
        plt.plot(nombre_heure, puissances_moyennes, color='orangered')
        plt.title(f"Real load profile ({building})")
        plt.ylabel("Power consumed [kW]")
        plt.grid(True, alpha=0.3)
        mois = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        plt.fill_between(nombre_heure, puissances_moyennes, where=puissances_moyennes>0, color='orangered')  
        
        jours_an = range(1, 8760)
        plt.xticks(jours_an[::730][:12], mois, rotation=90)
        #plt.xticks(nombre_heure[::(30*24)][:12], mois, rotation=90) 
        # Spécifiez l'emplacement et le nom du fichier
        #file_path = "C:\\Users\\Romain\\Desktop\\Master 1\\Energy challenge\\Signature_Thermique\\load profile monitoring\\building_a"+building
        # Enregistrez le graphique dans le fichier spécifié
        #plt.savefig(file_path)
        plt.show()
        
        plt.scatter(temperatures_triees,puissances_triees, alpha=0.5, color='orangered')
        plt.xlabel('Temperature [°C]')
        plt.ylabel('Power consumed [kW]')
        plt.title(f"Real thermal signature ({building})")
        plt.grid(True, alpha=0.3)
        # Spécifiez l'emplacement et le nom du fichier
        #file_path = "C:\\Users\\Romain\\Desktop\\Master 1\\Energy challenge\\Signature_Thermique\\load profile monitoring\\building_b"+building
        # Enregistrez le graphique dans le fichier spécifié
        #plt.savefig(file_path)
        plt.show()
        return puissances_moyennes

def error_between_models(Q_hours_monitoring, Q_hours_theoritical, buildings_selected):
    Q_days_monitoring_year = np.zeros(365)
    Q_days_theoritical_year = np.zeros(365)

    id_hours = 0

    for i_d in range (0,365):
        mean_d_monitoring = 0
        mean_d_theoritical = 0
        for actual_h in range (0, 23):
            mean_d_monitoring += Q_hours_monitoring[id_hours]
            mean_d_theoritical += Q_hours_theoritical[id_hours]
            id_hours+=1
        Q_days_monitoring_year[i_d] = mean_d_monitoring/24
        Q_days_theoritical_year[i_d] = mean_d_theoritical/24
    
    days_months=[31,28,31,30,31,30,31,31,30,31,30,31]

    Q_month_monitoring = np.zeros(12)
    Q_month_theoritical = np.zeros(12)
    for m in range(0,12):
        actual_month = days_months[m]
        for i in range (0, actual_month):
            Q_month_monitoring[m]+=Q_days_monitoring_year[i]
            Q_month_theoritical[m]+=Q_days_theoritical_year[i]
        Q_month_monitoring[m] = Q_month_monitoring[m]/actual_month
        Q_month_theoritical[m] = Q_month_theoritical[m]/actual_month  
        
        
        
    error = np.zeros(12)
    for k in range(0,12):
        if(Q_month_theoritical[k] == 0 or Q_month_monitoring[k] == 0 or Q_month_theoritical[k] == Q_month_monitoring[k]):
            error[k] = 0
        else:
            if(Q_month_theoritical[k] > Q_month_monitoring[k]):
                error[k] = ((Q_month_theoritical[k]-Q_month_monitoring[k])/Q_month_monitoring[k])*100
            else:
                error[k] = ((Q_month_monitoring[k]-Q_month_theoritical[k])/Q_month_theoritical[k])*100

    mois_an = range(0, 12)
    plt.plot(mois_an,error, alpha=1, color='orchid')
    plt.ylabel('Error [%]')
    plt.title(f"Relative error ({buildings_selected[0]})")
    plt.grid(True, alpha=0.3)

    mois = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']  

    plt.xticks(mois_an[::1][:12], mois, rotation=90)
    # Spécifiez l'emplacement et le nom du fichier
    #file_path = "C:\\Users\\Romain\\Desktop\\Master 1\\Energy challenge\\Signature_Thermique\\load profile monitoring\\building_b"+building
    # Enregistrez le graphique dans le fichier spécifié
    #plt.savefig(file_path)
    plt.show()
    
#----------------------------------------------------------------------------------------------------
#----------------------------------------CODE PRINCIPAL----------------------------------------------
#----------------------------------------------------------------------------------------------------
THEORITICAL = 'True'
REAL_DATA = 'True'


"""RESOLUTION BASED ON THEORITICAL MODEL"""

if(THEORITICAL == 'True'):
    is_human_heating = 'True'
    Q_hours_theoritical = theoritical_model(buildings_selected, is_human_heating)


""""RESOLUTION BASED ON REAL DATA"""

if(REAL_DATA == 'True'):
    Temp = temperature_tri()
    
    # Les indices triés des températures (du plus froid au plus chaud)
    indices_tries = np.argsort(Temp)
    temperatures_triees = Temp[indices_tries]
    
    #ERRORS IN THE FOLLOWING BUILDINGS : ['B53_c.csv', 'B52_c.csv', 'B49_47_CHA_CC.csv']
    compteur_base = buildings_excel_selected
    Q_hours_monitoring = monitoring_model(compteur_base, temperatures_triees)


"""ANALYZING THE ERROR BETWEEN THE THEORITICAL MODEL AND THE REAL DATA"""
if(THEORITICAL == 'True' and REAL_DATA == 'True'):
    error_between_models(Q_hours_monitoring, Q_hours_theoritical, buildings_selected)



#------------------------------------A AMELIORER-----------------------------------------
# 1] Certains fichiers excels de bâtiments ont énormément de données manquantes (parfois plus de 2 mois à la suite). Améliorer la fonction
#qui repère et règle les erreurs pour prendre en compte ça. Pour le moment, ça ne marche pas.
# 2] Pour le moment, on ne peut spécidier qu'un bâtiment à la fois (en haut de page) pour que la dernière fonctionnalité 
#"ANALYZING THE ERROR BETWEEN THE THEORITICAL MODEL AND THE REAL DATA" marche.
# 3] Ajouter la génération interne des équipements.


