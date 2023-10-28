import pandas as pd

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
