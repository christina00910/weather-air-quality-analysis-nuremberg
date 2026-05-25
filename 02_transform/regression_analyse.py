# Fragestellung:
# Gibt es einen statistisch signifikanten Zusammenhang zwischen Wetter und Luftschadstoffen?

# Bibliotheken Laden
import os
import pandas as pd
import statsmodels.api as sm
import seaborn as sns
import matplotlib.pyplot as plt

# Ermittelt den Ordner, in dem die aktuelle app.py liegt
skript_ordner = os.path.dirname(os.path.abspath(__file__))

# Verbindet den Ordner sauber mit dem Dateinamen
csv_pfad = os.path.join(skript_ordner, "data_2.csv")
df = pd.read_csv(csv_pfad)
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
    "windrichtung",
    "luftdruck",
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

#---------------------------------------------------------------------------------
# Multiple Lineare Regression
# Die Regression zeigt, wie einzelne Wettervariablen die Luftschadstoffe beeinflussen 
# und ob ein signifikanter positiver oder negativer Zusammenhang besteht. 
# Aufgrund unterschiedlicher Einheiten der Wettervariablen können die Einflussstärken der Koeffizienten 
# jedoch nicht direkt miteinander verglichen werden (z.B. Temperatur mit Niederschlag)

# Zielvariable festlegen
schadstoff = "no2"

# Einflussvariablen (Wetterdaten)
x = df[[
    "temperatur",
    "windgeschwindigkeit",
    "windrichtung",
    "luftdruck",
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
    "windrichtung",
    "luftdruck",
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

# ------------------------------------------------------------
# Regressionsergebnisse übersichtlich darstellen
# ------------------------------------------------------------

# Ergebnisse aus dem Regressionsmodell extrahieren
regression_ergebnisse = pd.DataFrame({
    "Variable": modell.params.index,
    "Koeffizient": modell.params.values,
    "p-Wert": modell.pvalues.values})

# Konstante entfernen, da sie für die Interpretation der Einflussvariablen weniger relevant ist
regression_ergebnisse = regression_ergebnisse[
    regression_ergebnisse["Variable"] != "const"]

# Signifikanz bewerten
regression_ergebnisse["Signifikant"] = regression_ergebnisse["p-Wert"].apply(
    lambda p: "Ja" if p < 0.05 else "Nein")

# Werte runden
regression_ergebnisse["Koeffizient"] = regression_ergebnisse["Koeffizient"].round(3)
regression_ergebnisse["p-Wert"] = regression_ergebnisse["p-Wert"].apply(lambda p: "< 0.001" if p < 0.001 else round(p, 4))

# R² aus dem Modell auslesen
r2 = modell.rsquared

# Tabelle anzeigen
print("\nÜbersicht Regressionsergebnisse")
print(f"R²: {r2:.3f}")
print(regression_ergebnisse)


# ------------------------------------------------------------
# Grafik als übersichtliche Tabelle erstellen
# ------------------------------------------------------------

fig, ax = plt.subplots(figsize=(10, 5))
ax.axis("off")

ax.text(
    0.5,
    0.95,
    f"Multiple lineare Regression für {schadstoff.upper()}",
    ha="center",
    fontsize=16,
    fontweight="bold")

ax.text(
    0.5,
    0.88,
    f"R² = {r2:.3f} | Signifikanzniveau: p < 0.05",
    ha="center",
    fontsize=12)

tabelle = ax.table(
    cellText=regression_ergebnisse.values,
    colLabels=regression_ergebnisse.columns,
    cellLoc="center",
    colLoc="center",
    loc="center",
    bbox=[0.05, 0.05, 0.9, 0.75])

tabelle.auto_set_font_size(False)
tabelle.set_fontsize(10)
tabelle.scale(1, 1.3)
plt.tight_layout()
plt.show()