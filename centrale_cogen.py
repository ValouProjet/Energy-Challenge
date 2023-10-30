
from CoolProp.CoolProp import PropsSI #Permet d'utiliser PropsSI, qui calcule les états thermodynamiques à partir de tables dédiées
import numpy as np #Permet de créer des tableaux (voir TPs précedents)

#Le Sart Tilman est équipé d’une centrale de cogénération alimenté par de la biomasse 
#dont la puissance thermique nominale est de 6.5 MW. La vapeur utilisée par les turbines 
#est produite par une chaudière alimentée par de la biomasse assurant une production de 
#vapeur de 13t/h à une température de 420°C et une pression de 4.2 MPa. La vapeur est 
#détendue jusqu’à une pression de 200 kPa dans une première turbine haute pression (THP)
#pour produire de l’électricité. A la sortie de celle-ci, une partie de la vapeur est soutirée 
#pour alimenter l’échangeur de chaleur connecté au réseau de chaleur. L’autre partie de la 
#vapeur est détendue dans une seconde turbine basse pression (TBP) jusqu’à environ 10 
#kPa, la pression du condenseur. Un schéma du cycle est représenté à la figure suivante. 
#Si les efficacités isentropiques des pompes et des turbines sont respectivement de 88 et 
#84% et que le rendement de l’alternateur est quant à lui de 96%

"Données" # Attention de toujours utiliser les unités SI(m,kg,j,K,s,mol) pour utiliser PropsSI

fluid = 'Water' #car centrale à vapeur


p = np.zeros(8, dtype=float)
T = np.zeros(8, dtype=float)
s = np.zeros(8, dtype=float)
h = np.zeros(8, dtype=float)


#données fournies dans l'énoncé :
T[0] = 420+273.15 # [K]
p[0] = 4.2E6 # [Pa]
p[1] = 200E3 # [Pa]
p[3] = 10E3 # [Pa]
p[5] = 200E3

eta_tur_is = 0.84
eta_alt = 0.96
eta_is_p = 0.88

Q_dot_DHN = 6.5E6 # [W] positive car puissance électrique produite par la centrale à vapeur

m_dot = (13000/3600) #[kg/s]
"Etat 1 "
(s[0],h[0]) = PropsSI(('S','H'), 'P', p[0], 'T', T[0], fluid) #déduction de l'état en entrée de turbine vu les données fournies

"Etat 2 : Turbine haute pression"

h_1_is = PropsSI('H', 'P', p[1], 'S', s[0], fluid) #enthalpie de sortie qu'aurait eu une transformation isentropique 

h[1] = eta_tur_is * (h_1_is - h[0]) + h[0] #formule de l'efficacité isentropique de la turbine 
(x_1,T[1],s[1]) = PropsSI(('Q','T','S'), 'P', p[1], 'H', h[1], fluid) #déduction de l'état en sortie de turbine

"Etat 3 : Echangeur du réseau de chaleur"

#hypo : -liquide saturé (x_2 = 0)
x_2 = 0
#hypo : - isobare
p[2] = p[1]
(h[2],T[2],s[2]) = PropsSI(('H','T','S'), 'P', p[2], 'Q', x_2, fluid) #déduction des propriétés en sortie du condenseur
y = Q_dot_DHN / (m_dot *(h[1]-h[2]))

"Etat 4 : Turbine basse pression"

h_3_is = PropsSI('H', 'P', p[3], 'S', s[1], fluid) #enthalpie de sortie qu'aurait eu une transformation isentropique 

h[3] = eta_tur_is * (h_3_is - h[1]) + h[1] #formule de l'efficacité isentropique de la turbine 
(x_3,T[3],s[3]) = PropsSI(('Q','T','S'), 'P', p[3], 'H', h[3], fluid) #déduction de l'état en sortie de turbine

"Etat 5 : condenseur"
#hypo : -liquide saturé (x_4 = 0)
x_4 = 0
#hypo : - isobare
p[4] = p[3]
(h[4],T[4],s[4]) = PropsSI(('H','T','S'), 'P', p[4], 'Q', x_4, fluid) #déduction des propriétés en sortie du condenseur

"Etat 6 : pompe basse pression"
#pour être à la même pression qu'en 3,pour pouvoir faire le mélange
h_5_is = PropsSI('H', 'P', p[5], 'S', s[4], fluid) #enthalpie de sortie qu'aurait eu une transformation isentropique 
h[5] = h[4] + ((h_5_is - h[4])/eta_is_p)
(x_5,T[5],s[5]) = PropsSI(('Q','T','S'), 'P', p[5], 'H', h[5], fluid) #déduction de l'état en sortie de la pompe

"Etat 7 : mélange"
#concervation de l'énergie et de la masse
h[6] = y*h[2] + (1-y) * h[5]
p[6] = 200E3
(x_6,T[6],s[6]) = PropsSI(('Q','T','S'), 'P', p[6], 'H', h[6], fluid) #déduction de l'état du mélange

"Etat 8 : Pompe haute pression"

p[7] = p[0]
h_7_is = PropsSI('H', 'P', p[7], 'S', s[6], fluid) #enthalpie de sortie qu'aurait eu une transformation isentropique 
h[7] = h[6] + ((h_7_is - h[6])/eta_is_p)
(x_7,T[7],s[7]) = PropsSI(('Q','T','S'), 'P', p[7], 'H', h[7], fluid) #déduction de l'état en sortie de la pompe


"Puissance net produite par l'alternateur"
# = puissance turbine basse pression + puissance turbine haute pression
W_dot_THP = m_dot * (h[1]- h[0])
W_dot_TBP = (1-y) * m_dot * (h[3]- h[1])
W_dot_PBP= (1-y) * m_dot * (h[5]- h[4])
W_dot_PHP = m_dot * (h[7] - h[6])
W_dot_net = np.abs(W_dot_THP+W_dot_TBP)*eta_alt - (W_dot_PBP+W_dot_PHP)

"Puissance fournie par le générateur de vapeur"
Q_dot_gen = m_dot * (h[0]-h[7])

"Rendement de l'unité cogénération"
#rendement électrique
eta_elec = W_dot_net / Q_dot_gen
#rendement thermique
eta_th = Q_dot_DHN / Q_dot_gen
#rendement de la cogen
eta_cogen = eta_elec + eta_th



#Rem: le "u" (=unicode) avant le texte permet d'afficher correctement les accents
print (u"La puissance net produite par l'alternateur est de %.2f MW" %(W_dot_net/1000000))
print (u"La puissance net fournie par le générateur de vapeur est de %.2f MW" %(Q_dot_gen/1000000))
print (u"Le rendement thermique est de %.2f %%" %(eta_th*100))
print (u"Le rendement électrique est de %.2f %%" %(eta_elec*100))
print (u"Le rendement total de la centrale cogénération est de %.2f %%" %(eta_cogen*100))










