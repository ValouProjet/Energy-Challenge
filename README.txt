Welcome to our project. Our group works on the Polytech buildings.
The code "energy_polytech.py" is the one you're looking for. The only goal of the code is to plot the
'Thermal Signature' and the "Load Profile' of all buildings of the Polytech zone based on data inside
excel files provided by University of Liege.
In those excel files, we have several measurements (measurements every 5 minutes).
We opted to average all these measurements to have hour-by-hour data.
At the end, the code provides a 8760x1 table for the temperature (8760 hours = a year) and a 8760x1 table
for the Powers (in kW). Graphs can thus be plotted thanks to those tables.

This is achieved through 4 functions :

➤ temperature_tri() :

This function allows to fill a table "Temp" which contains all the exterior temperatures on the Sart Tilman campus for
every hour of 2022 (for the whole year). This function collects data on the page 'Meteo' from the excel file called
"Building_Data_Template_Polytech.xlsx" (don't forget to add it on your computer and change the path name in the code).
It then returns a table of 8760 hours (1 year = 8760 hours). As the excel file provided by ULiege can have data that
are exchanged, the function also sort the table in chronological order by date.


➤ puissance_monitoring(batiment) : 

This function takes as a parameter a string (or several).
This string has to be one of the Polytech buildings and must consists of one or more buildings which are described
immediately after : ['B28_CHA_CC.csv','B52_CHA_CC.csv','B52_CHA_RC_BUR.csv','B52_CHA_RC_HALL.csv','B37_c.csv','B48_c.csv']
(don't forget to add those on your computer and change the path name in the code). It groups data by hour for each day
of each month of 2022 and returns a table containing all the powers consumed for each of those hour. It thus
represents a table of 8760 powers.


THE 2 FUNCTIONS DEFINED ABOVE WILL RETURN A TABLE OF 8760 HOURS AND A TABLE OF 8760 POWERS WHICH ARE GOING TO BE PLOTTED IN THE CODE
TO OBTAIN THE 'THERMAL SIGNATURE' AND 'LOAD PROFILE' GRAPHICS.


➤ search_error_and_solve(vecteur) :

This function is only called once inside the function above "puissance_monitoring(batiment)".
To make it short, in most of the excel files of the polytech buildings, some data are missing for some entire hours
(for example, it can be due to an electrical blackout and thus the sensors are not working anymore, this leads to a
big lack of data at a given time). In this case, the function takes as a parameter the excel file for the select
buildind and insert new lines for the missing hours in the variable containing the excel table.
The power corresponding to this added line is an average between the power at the hour just before and the hour just after.
Thanks to this function, a COMPLETE table with 8760 powers can be obtained from the function "puissance_monitoring(batiment)"
defined just above.


➤ generate_numbers_as_strings(n) :

This function creates a table going from 1 to n by putting a 0 in front of the figures (01 instead of 1, 02 instead of 2...).
In the Excel files provided by the university, this convention is used. This function therefore allows us to easily search for data in Excel files.

➤ human_heat(active, T_base_inside, K, A_ground, occup_building, h):

This function is used when the power generate by people inside the building is considered. It take the proportional occupation of the building every hour and multiplie it by the max value of heat generation and the area of the buildings.

➤ theoritical_model(building_base, is_human_heating):

This function plot the load profiles of the building consider. These load profiles are calculated with the theoritical formula : Q = A*U*(T_in-T_out). 
If we consider the function human_heat, the inside temperature needed is lower than the one without people, we therefore need more power. The curve which represent the power without human_heat is plot with a different color.
The A*U term is subdivide in three terms : - The one for the wall. 
                                           - The one for the roof.
                                           - The one for the windows.
This function also return an array of 8760 powers (one for each hour of the year) that will be used later.

➤ monitoring_model(compteur_base, temperature_tri ):

This function plot the load profiles of the building consider. These load profiles are calculated with the data collected. 
The power are calculated every hour.
This function also return an array of 8760 powers (one for each hour of the year) that will be used later.

➤ error_between_models(Q_hours_monitoring, Q_hours_theoritical, buildings_selected):

This function calculate the proportional error between the theoritical model and the model generates by the data. It is an average error on every month
