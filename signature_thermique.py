import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
from datetime import datetime


def generate_numbers_as_strings(n):
    
    numbers_as_strings = []

    for i in range(1, n + 1):
        number_string = str(i).zfill(2)
        numbers_as_strings.append(number_string)

    return numbers_as_strings




# HYPOTHESES :
    
#⭐ Dans ce script, toutes les fenêtres sont considérées comme étant du double vitrage (au niveau
#du coefficient de confuctivité thermique U). Ce qui n'est évidemment pas le cas. La consommation
#devrait donc être revue légèrement à la hausse.

#⭐ La température journalière est la moyenne des 24 températures horaires de la journée, ce qui
#est en réalité une hypothèse plus que correcte et acceptable.

#⭐ L'aire totale utilisée est composée de la surface des murs, la surface des fenêtres et la
#surface du toit (calculée grâce à la hauteur du pignon). Concernant la surface du toit, certains
#bâtiments (comme le b28) sont en réalité composés de plusieurs bâtiments.. Certains avec un toit
#et d'autres pas... Une moyenne est alors effectuée pour trouver une hauteur moyenne de pignon
#de tous les bâtiments et ainsi calculer la surface moyenne des toits. Cette approximation reste
#approximative et devrait être étudiée plus en profonfeur.


#-------------------------#PARAMETERS#-------------------------------#

building = 'B48'
T_building = 15

U_walls = 1.7 #coefficient de conductivité thermique du Béton [W/m²K]
U_windows = 1.5 #coefficient de conductivité thermique du double vitrage [W/m²K]
U_roof = 0.45 #coefficient de conductivité thermique d'une toiture isolée [W/m²K]

lien_fichier_excel = "C:\\Users\\Cron\\Desktop\\EnergyDATA\\Building_Data_Template_Polytech.xlsx"

#--------------------------------------------------------------------#


geometry = pd.read_excel(io=lien_fichier_excel, sheet_name='Geometry')
meteo = pd.read_excel(io=lien_fichier_excel, sheet_name='Meteo')

#récupère uniquement les données du bâtiment voulu (spécifié plus haut)
row_building = geometry.loc[geometry['Building Geometry'] == building]

#récupère la hauteur du pignon (si c'est 0 on sait que le toit est plat et peut être
#considéré comme un toit plat en béton béton)
Pignon = row_building['Height pignon m'].values[0]
is_roof_flat = 'False'

if(Pignon == 0):
    U_roof = U_walls
    is_roof_flat = 'True'


#récupère les surfaces des murs et du toit
A_walls = row_building['Exterior wall surface m^2'].values[0]

A_windows_N = row_building['North-oriented Window area m^2'].values[0]
A_windows_E = row_building['East-oriented Window area m^2'].values[0]
A_windows_S = row_building['South-oriented Window area m^2'].values[0]
A_windows_W = row_building['West-oriented Window area m^2'].values[0]

A_windows = A_windows_N + A_windows_E + A_windows_S + A_windows_W
A_roof = row_building['Zone surface m^2'].values[0]

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

#hours = generate_numbers_as_strings(23)
hours = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]

Q_days = np.zeros(365) #signature thermique de chaque jour
day = 0 #on démarre au jour 0 de l'année et on va itérer

#tableau regroupant les températures moyennes de CHAQUE jour de l'année (utilisé plus tard pour plot)
all_temp = np.zeros(365)
t = 0

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
        if (m == 'FEB' or m == 'APR' or m == 'MAY' or m == 'AUG' or m == 'AUG' or m == 'DEC'):
            lign = d+'-'+m+'-2021'
            day_lign = meteo.loc[meteo['Date'] == lign]
        else:
            lign = d+'-'+m+'-21'
            real_date = datetime.strptime(lign, '%d-%b-%y')
            day_lign = meteo.loc[meteo['Date'] == real_date]
            
        temp_tot_day = 0
        
        for h in hours:
            temperature = day_lign['Temperature C'].values[h]          
            temp_tot_day += temperature
            
        temp_mean_day = temp_tot_day/24
        all_temp[t] = temp_mean_day
        t += 1
        
        Q_day = (K/1000)*(T_building - temp_mean_day) #LA FORMULE pour calculer la puissance recquise.
        
        Q_days[day] = Q_day
        day += 1


#Ci dessous: Permet de redéfinir les puissances négatives à 0 (une puissance négative signifie
#que l'extérieur du bâtiment est plus chaud que l'intérieur, nottament en été. Il n'y a donc
#pas besoin de fournir un apport en chaleur, donc on définit la valeur à 0.)
for i in range(len(Q_days)):
    if Q_days[i] < 0:
        Q_days[i] = 0
        

#-------------------------#PLOTS#-------------------------------#

#SECTION uniquement réservée au plot des graphs et à l'estétique de ces derniers.   
jours_an = range(1, 366)


plt.plot(jours_an, Q_days, color='orangered')
plt.title(f"Thermal signature of {building}")
plt.ylabel("P, Heat power [kW]")
plt.grid(True, alpha=0.3)
plt.ylim(0, 20)

mois = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
plt.fill_between(jours_an, Q_days, where=Q_days>0, alpha=0.7, color='tomato')

plt.xticks(jours_an[::30][:12], mois, rotation=90) 

plt.show()
        
       


plt.scatter(all_temp, Q_days)
plt.title(f"Thermal signature of {building}")
plt.xlabel("θ [°C]")
plt.ylabel("P, Heat power [kW]")
plt.grid(True, alpha=0.3)

plt.show()

#--------------------------------------------------------------------#
        
        
        
        