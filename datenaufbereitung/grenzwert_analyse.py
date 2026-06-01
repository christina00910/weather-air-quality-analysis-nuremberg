# Grenzwertüberschreitungen analysieren
# Ziel: Prüfen, wie oft ein Schadstoff einen festgelegten Grenzwert überschreitet.

# Bibliotheken laden
import pandas as pd
import matplotlib.pyplot as plt

# Daten laden
df = pd.read_csv("02_transform/alt_data_2.csv")

# Datum umwandeln
df["datum"] = pd.to_datetime(df["datum"])

# ------------------------------------------------------------
# Grenzwertüberschreitungen pro Jahr
# Grundlage: LQI-Klassen des Umweltbundesamtes
# Es wird gezählt, wie oft pro Jahr mindestens die Klasse "Mäßig"
# erreicht oder überschritten wurde.
# ------------------------------------------------------------

# Schadstoff auswählen
# Möglich: "o3", "no2", "pm10", "pm2x5"
schadstoff = "pm2x5" 

# LQI-Schwellenwert ab Klasse "Mäßig"
# Werte ab dieser Grenze gelten nicht mehr als "gut" oder "sehr gut".
lqi_grenzwerte_maessig = {
    "pm10": 28,
    "pm2x5": 16,
    "o3": 73,
    "no2": 31}

grenzwert = lqi_grenzwerte_maessig[schadstoff]

# Relevante Daten auswählen
daten = df[["datum", schadstoff]].dropna()

# Jahr aus Datum erstellen
daten["jahr"] = daten["datum"].dt.year.astype(int)

# Prüfen, ob der Grenzwert überschritten bzw. erreicht wurde
daten["ab_maessig"] = daten[schadstoff] >= grenzwert

# Überschreitungen pro Jahr zählen
ueberschreitungen_jahr = daten.groupby("jahr")["ab_maessig"].sum()

# Grafik erstellen
plt.figure(figsize=(12, 6))
plt.bar(
    ueberschreitungen_jahr.index,
    ueberschreitungen_jahr.values)
plt.title(f"Anzahl Stunden mit mindestens mäßiger Luftqualität: {schadstoff.upper()}")
plt.xlabel("Jahr")
plt.ylabel("Anzahl belasteter Stunden")

# Nur ausgewählte Jahreszahlen anzeigen
start_jahr = int(ueberschreitungen_jahr.index.min())
end_jahr = int(ueberschreitungen_jahr.index.max())
plt.xticks(range(start_jahr, end_jahr + 1, 5), rotation=45)
plt.tight_layout()
plt.show()