# Feinstaubanalyse PM10 und PM2.5
# Ziel: Deskriptiver Vergleich der beiden Feinstaubarten
# Bibliotheken laden

import pandas as pd
import matplotlib.pyplot as plt

# Daten laden
df = pd.read_csv("02_transform/Schadstoff_Wetter.csv")

# Datum umwandeln
df["datum"] = pd.to_datetime(df["datum"])

# Analysezeitraum ab 2008
# PM2.5 ist erst ab 2008 verfügbar, deshalb wird ab 2008 gefiltert.
df = df[df["datum"].dt.year >= 2008]

# Zusätzliche Zeitspalten erstellen
df["monat"] = df["datum"].dt.month
df["jahr"] = df["datum"].dt.year
df["wochentag"] = df["datum"].dt.dayofweek
df["wochenende"] = df["wochentag"].isin([5, 6]).astype(int)

# Nur relevante Feinstaubspalten auswählen
feinstaub = df[["pm10", "pm2x5"]].dropna()

# Deskriptive Statistik anzeigen
# Hier werden Mittelwert, Minimum, Maximum und Streuung der Feinstaubwerte verglichen.
print("\nDeskriptive Statistik PM10 und PM2.5")
print(feinstaub.describe())

# ------------------------------------------------------------
# 1. Durchschnittswerte von PM10 und PM2.5
# ------------------------------------------------------------
# Durchschnittswerte berechnen
# Dadurch sieht man, welche Feinstaubart im Durchschnitt höhere Werte aufweist.
mittelwerte = feinstaub.mean()

# Balkendiagramm erstellen
plt.figure(figsize=(7, 5))
plt.bar(mittelwerte.index, mittelwerte.values)
plt.title("Durchschnittliche Feinstaubwerte: PM10 vs. PM2.5")
plt.xlabel("Feinstaubart")
plt.ylabel("Durchschnittlicher Feinstaubwert")
plt.tight_layout()
plt.show()

# ------------------------------------------------------------
# 2. Monatlicher Verlauf von PM10 und PM2.5
# ------------------------------------------------------------
# Durchschnittliche Feinstaubwerte pro Monat berechnen
# Damit erkennt man saisonale Unterschiede im Jahresverlauf.
feinstaub_monat = df.groupby("monat")[["pm10", "pm2x5"]].mean()

# Liniengrafik erstellen
plt.figure(figsize=(10, 6))
plt.plot(
    feinstaub_monat.index,
    feinstaub_monat["pm10"],
    label="PM10")
plt.plot(
    feinstaub_monat.index,
    feinstaub_monat["pm2x5"],
    label="PM2.5")
plt.title("Durchschnittliche Feinstaubwerte pro Monat")
plt.xlabel("Monat")
plt.ylabel("Durchschnittlicher Feinstaubwert")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

# ------------------------------------------------------------
# 3. Tagesverlauf von PM10 und PM2.5
# ------------------------------------------------------------
# Durchschnittliche Feinstaubwerte pro Stunde berechnen
# Dadurch können typische Tagesmuster und mögliche Verkehrseinflüsse erkannt werden.
feinstaub_stunde = df.groupby("stunde")[["pm10", "pm2x5"]].mean()

# Liniengrafik erstellen
plt.figure(figsize=(10, 6))
plt.plot(
    feinstaub_stunde.index,
    feinstaub_stunde["pm10"],
    label="PM10")
plt.plot(
    feinstaub_stunde.index,
    feinstaub_stunde["pm2x5"],
    label="PM2.5")
plt.title("Durchschnittliche Feinstaubwerte pro Stunde")
plt.xlabel("Stunde")
plt.ylabel("Durchschnittlicher Feinstaubwert")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

# ------------------------------------------------------------
# 4. Feinstaubwerte: Werktag vs. Wochenende
# ------------------------------------------------------------
# Durchschnittliche Feinstaubwerte für Werktage und Wochenende berechnen
# Dadurch können Unterschiede zwischen Arbeitswoche und Wochenende untersucht werden.
feinstaub_wochenende = df.groupby("wochenende")[["pm10", "pm2x5"]].mean()

# Balkendiagramm erstellen
x_labels = ["Werktag", "Wochenende"]
x = range(len(x_labels))
plt.figure(figsize=(8, 5))
plt.bar(
    [i - 0.15 for i in x],
    feinstaub_wochenende["pm10"],
    width=0.3,
    label="PM10")
plt.bar(
    [i + 0.15 for i in x],
    feinstaub_wochenende["pm2x5"],
    width=0.3,
    label="PM2.5")
plt.xticks(x, x_labels)
plt.title("Feinstaubwerte: Werktag vs. Wochenende")
plt.ylabel("Durchschnittlicher Feinstaubwert")
plt.legend()
plt.tight_layout()
plt.show()

# ------------------------------------------------------------
# 5. Jahresdurchschnitt von PM10 und PM2.5
# ------------------------------------------------------------
# Durchschnittliche Jahreswerte berechnen
# Dadurch wird sichtbar, wie sich die Feinstaubbelastung über die Jahre verändert hat.
feinstaub_jahr = df.groupby("jahr")[["pm10", "pm2x5"]].mean()

# Liniengrafik erstellen
plt.figure(figsize=(12, 6))
plt.plot(
    feinstaub_jahr.index,
    feinstaub_jahr["pm10"],
    label="PM10")

plt.plot(
    feinstaub_jahr.index,
    feinstaub_jahr["pm2x5"],
    label="PM2.5")
plt.title("Jährliche Durchschnittswerte von PM10 und PM2.5")
plt.xlabel("Jahr")
plt.ylabel("Durchschnittlicher Feinstaubwert")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

# ------------------------------------------------------------
# 6. Durchschnittliche Feinstaubwerte nach Jahreszeit
# ------------------------------------------------------------
# Funktion zur Zuordnung der Jahreszeiten
def jahreszeit(monat):
    if monat in [12, 1, 2]:
        return "Winter"
    elif monat in [3, 4, 5]:
        return "Frühling"
    elif monat in [6, 7, 8]:
        return "Sommer"
    else:
        return "Herbst"
# Jahreszeit-Spalte erstellen
df["jahreszeit"] = df["monat"].apply(jahreszeit)

# Durchschnittliche Feinstaubwerte pro Jahreszeit berechnen
feinstaub_jahreszeit = df.groupby("jahreszeit")[["pm10", "pm2x5"]].mean()

# Reihenfolge der Jahreszeiten festlegen
feinstaub_jahreszeit = feinstaub_jahreszeit.reindex(
    ["Frühling", "Sommer", "Herbst", "Winter"])
print("\nDurchschnittliche Feinstaubwerte nach Jahreszeit")
print(feinstaub_jahreszeit)

# Balkendiagramm erstellen
feinstaub_jahreszeit.plot(
    kind="bar",
    figsize=(10, 6))
plt.title("Durchschnittliche Feinstaubwerte nach Jahreszeit")
plt.xlabel("Jahreszeit")
plt.ylabel("Durchschnittlicher Feinstaubwert")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()