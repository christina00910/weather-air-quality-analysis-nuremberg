# Bibliotheken Laden
import pandas as pd
import statsmodels.api as sm

# Daten Laden
df = pd.read_csv("02_transform/Schadstoff_Wetter.csv")

#Spalten anzeigen
print(df.columns)
# Ersten Zeilen anzeigen 
print(df.head())
# df anzeigen
print(df.info())

# Der Datensatz enthält:
# - 394488 Zeilen (Beobachtungen)
# - 30 Spalten (Wetter- und Luftschadstoffvariablen)
# - Wetterdaten und Luftschadstoffe wurden erfolgreich zusammengeführt
# - Die meisten numerischen Variablen liegen als float vor
# - datum ist aktuell als String gespeichert und kann später in datetime umgewandelt werden

# Datum in datetime umwandeln
df["datum"] = pd.to_datetime(df["datum"])
print(df.info())

# Fehlerwerte prüfen
print(df.isnull().sum())

# Bewertung:
# Der Datensatz enthält einige fehlende Werte, insbesondere bei Niederschlag
# und Sonnenscheindauer. Dies ist bei meteorologischen Zeitreihen üblich,
# da bestimmte Messungen nicht durchgehend verfügbar sind oder nur unter
# bestimmten Wetterbedingungen auftreten.
#
# Die Luftschadstoffe O3, NO2 und PM10 weisen jedoch insgesamt eine hohe
# Anzahl verfügbarer Messwerte auf, sodass die Datenbasis für die Analyse ausreichend groß ist.

