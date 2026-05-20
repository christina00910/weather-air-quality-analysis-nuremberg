# Fragestellung:
# Gibt es einen statistisch signifikanten Zusammenhang zwischen Wetter und Luftschadstoffen?

# Bibliotheken Laden
import pandas as pd
import statsmodels.api as sm
import seaborn as sns
import matplotlib.pyplot as plt

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
# Die vielen fehlenden Werte bei PM2.5 sind fachlich erklärbar, da PM2.5
# erst ab 2008 im Datensatz verfügbar ist. Die Regressionsanalyse wird deshalb 
# auf die Jahre 2008-2024 beschränkt, um eine konsistente Datenbasis zu gewährleisten.

# Analysezeitraum ab 2008 Um eine einheitliche und vergleichbare Datenbasis zu gewährleisten
df = df[df["datum"].dt.year >= 2008]
# Zeitraum prüfen
print(df["datum"].min())
print(df["datum"].max())

# Relevante Variablen für die Korrelationsanalyse
analyse_variablen = [
    "temperatur",
    "windgeschwindigkeit",
    "relative_luftfeuchtigkeit",
    "niederschlagshoehe_mm",
    "sonnenscheindauer_minuten",
    "gesamtbewoelkung",
    "o3",
    "no2",
    "pm10",
    "pm2x5"]

# Datensatz für Analyse erstellen
analyse_df = df[analyse_variablen]

# Korrelationen berechnen
korrelation = analyse_df.corr()
print(korrelation)

# Heatmap der Korrelationen erstellen
plt.figure(figsize=(12,8))
sns.heatmap(
    korrelation,
    annot=True,
    cmap="coolwarm",
    fmt=".2f")
plt.title("Korrelationsmatrix Wetterdaten und Luftschadstoffe")
plt.show()

# Bewertung der Korrelationsmatrix:
# - Temperatur und Ozon: r = 0.63
#   Starke positive Korrelation. Höhere Temperaturen gehen häufig mit höheren Ozonwerten einher.
#
# - Relative Luftfeuchtigkeit und Ozon: r = -0.72
#   Starke negative Korrelation. Höhere Luftfeuchtigkeit geht häufig mit niedrigeren Ozonwerten einher.
#
# - PM10 und PM2.5: r = 0.73
#   Starke positive Korrelation. Beide Feinstaubarten treten häufig gemeinsam erhöht auf.
#
# - Ozon und NO2: r = -0.46
#   Mittlere negative Korrelation. Höhere Ozonwerte gehen tendenziell mit niedrigeren NO2-Werten einher.
#
# - NO2 und PM10: r = 0.43
#   Mittlere positive Korrelation. Höhere NO2-Werte gehen tendenziell mit höheren PM10-Werten einher.
#
# - Sonnenscheindauer und Bewölkung: r = -0.51
#   Mittlere negative Korrelation. Mehr Sonnenschein geht erwartungsgemäß mit geringerer Bewölkung einher.
#
# - Temperatur und relative Luftfeuchtigkeit: r = -0.59
#   Mittlere bis starke negative Korrelation. Höhere Temperaturen gehen tendenziell mit geringerer relativer Luftfeuchtigkeit einher.
#
# Hinweis:
# Korrelation zeigt nur Zusammenhänge, aber keine eindeutige Ursache-Wirkung.

# Multiple Lineare Regression
# Die Regression zeigt, wie einzelne Wettervariablen die Luftschadstoffe beeinflussen 
# und ob ein signifikanter positiver oder negativer Zusammenhang besteht. 
# Aufgrund unterschiedlicher Einheiten der Wettervariablen können die Einflussstärken der Koeffizienten 
# jedoch nicht direkt miteinander verglichen werden (z.B. Temperatur mit Niederschlag)

# Zielvariable festlegen
schadstoff = "o3"

# Einflussvariablen (Wetterdaten)
x = df[[
    "temperatur",
    "windgeschwindigkeit",
    "relative_luftfeuchtigkeit",
    "niederschlagshoehe_mm",
    "sonnenscheindauer_minuten",
    "gesamtbewoelkung"]]

# Zielvariable
y = df[schadstoff]

# Datensatz für Regression vorbereiten - Fehlende Werte entfernen
regression_df = pd.concat([x, y], axis=1).dropna()

x = regression_df[[
    "temperatur",
    "windgeschwindigkeit",
    "relative_luftfeuchtigkeit",
    "niederschlagshoehe_mm",
    "sonnenscheindauer_minuten",
    "gesamtbewoelkung"]]

y = regression_df[schadstoff]

# Konstante hinzufügen, damit der Achsenabschnitt in der Regression berücksichtigt wird
x = sm.add_constant(x)

# Regression durchführen
modell = sm.OLS(y, x).fit()
print(modell.summary())
