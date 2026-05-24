# Luftschadstoff-Vorhersage mit Random Forest und Open-Meteo API

import requests
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# 1. Historische Daten laden und Modell trainieren
# ------------------------------------------------------------

df = pd.read_csv("02_transform/data_2.csv")

df["datum"] = pd.to_datetime(df["datum"])
df = df[df["datum"].dt.year >= 2008]

# Zielvariable festlegen
# Möglich: "o3", "no2", "pm10", "pm2x5"
schadstoff = "o3"

# Zeitvariablen für historische Daten erstellen
df["wochentag"] = df["datum"].dt.dayofweek
df["monat"] = df["datum"].dt.month
df["wochenende"] = df["wochentag"].isin([5, 6]).astype(int)
df["rush_hour"] = df["stunde"].isin([6, 7, 8, 9, 16, 17, 18, 19]).astype(int)
df["silvester"] = (((df["datum"].dt.month == 12) & (df["datum"].dt.day == 31)) |
    ((df["datum"].dt.month == 1) & (df["datum"].dt.day == 1))).astype(int)

# Features festlegen
features = [
    "temperatur",
    "windgeschwindigkeit",
    "windrichtung",
    "luftdruck",
    "relative_luftfeuchtigkeit",
    "niederschlagshoehe_mm",
    "sonnenscheindauer_minuten",
    "gesamtbewoelkung",
    "stunde",
    "rush_hour",
    "wochenende",
    "monat",
    "silvester"]

# Daten vorbereiten
daten = df[features + [schadstoff]].dropna()

x = daten[features]
y = daten[schadstoff]

x_train, x_test, y_train, y_test = train_test_split(
    x,
    y,
    test_size=0.2,
    random_state=42)

modell = RandomForestRegressor(
    n_estimators=20,
    random_state=42,
    n_jobs=-1)

modell.fit(x_train, y_train)

# Modellbewertung
vorhersage_test = modell.predict(x_test)

r2 = r2_score(y_test, vorhersage_test)
mae = mean_absolute_error(y_test, vorhersage_test)

print("Modellbewertung")
print("R²:", r2)
print("MAE:", mae)


# ------------------------------------------------------------
# 2. Aktuelle Wetterdaten über API abrufen
# ------------------------------------------------------------

url = "https://api.open-meteo.com/v1/forecast?latitude=49.4542&longitude=11.0775&hourly=temperature_2m,relative_humidity_2m,precipitation,surface_pressure,cloud_cover,wind_speed_10m,wind_direction_10m,sunshine_duration&models=icon_seamless&forecast_days=1&forecast_hours=1&timezone=Europe%2FBerlin"

response = requests.get(url)
api_daten = response.json()

# Vorhersagezeitpunkt auslesen
zeitpunkt = pd.to_datetime(api_daten["hourly"]["time"][0])

# Datum und Uhrzeit formatieren
datum_anzeige = zeitpunkt.strftime("%d.%m.%Y")
uhrzeit_anzeige = zeitpunkt.strftime("%H:%M")
stadt = "Nürnberg"

temperatur = api_daten["hourly"]["temperature_2m"][0]
relative_luftfeuchtigkeit = api_daten["hourly"]["relative_humidity_2m"][0]
niederschlagshoehe_mm = api_daten["hourly"]["precipitation"][0]
luftdruck = api_daten["hourly"]["surface_pressure"][0]
gesamtbewoelkung = api_daten["hourly"]["cloud_cover"][0]
# Windgeschwindigkeit aus API in km/h
windgeschwindigkeit_kmh = api_daten["hourly"]["wind_speed_10m"][0]
# Für das Wettermodell in dieselbe Einheit wie die historischen Trainingsdaten umrechnen (m/s)
windgeschwindigkeit = windgeschwindigkeit_kmh / 3.6
windrichtung = api_daten["hourly"]["wind_direction_10m"][0]
sonnenscheindauer_minuten = api_daten["hourly"]["sunshine_duration"][0] / 60

# Zeitvariablen aus API-Zeitpunkt berechnen
stunde = zeitpunkt.hour
wochentag = zeitpunkt.dayofweek
monat = zeitpunkt.month
wochenende = 1 if wochentag in [5, 6] else 0
rush_hour = 1 if stunde in [6, 7, 8, 9, 16, 17, 18, 19] else 0
silvester = 1 if (
    (zeitpunkt.month == 12 and zeitpunkt.day == 31) or
    (zeitpunkt.month == 1 and zeitpunkt.day == 1)) else 0

# ------------------------------------------------------------
# 3. API-Wetterdaten in Modellformat bringen
# ------------------------------------------------------------

live_daten = pd.DataFrame([{
    "temperatur": temperatur,
    "windgeschwindigkeit": windgeschwindigkeit,
    "windrichtung": windrichtung,
    "luftdruck": luftdruck,
    "relative_luftfeuchtigkeit": relative_luftfeuchtigkeit,
    "niederschlagshoehe_mm": niederschlagshoehe_mm,
    "sonnenscheindauer_minuten": sonnenscheindauer_minuten,
    "gesamtbewoelkung": gesamtbewoelkung,
    "stunde": stunde,
    "rush_hour": rush_hour,
    "wochenende": wochenende,
    "monat": monat,
    "silvester": silvester}])

print("\nLive-Wetterdaten für die Vorhersage:")
print(live_daten)


# ------------------------------------------------------------
# 4. Luftschadstoff vorhersagen
# ------------------------------------------------------------

vorhersage_live = modell.predict(live_daten)

print(f"\nVorhergesagter {schadstoff.upper()}-Wert:")
print(vorhersage_live[0])

# ------------------------------------------------------------
# 5. Live-Wetterdaten grafisch darstellen
# ------------------------------------------------------------

wert = vorhersage_live[0]

def lqi_einordnung(schadstoff, wert):
    if schadstoff == "pm10":
        if wert <= 9:
            return "Sehr gut"
        elif wert <= 27:
            return "Gut"
        elif wert <= 54:
            return "Mäßig"
        elif wert <= 90:
            return "Schlecht"
        else:
            return "Sehr schlecht"

    elif schadstoff == "pm2x5":
        if wert <= 5:
            return "Sehr gut"
        elif wert <= 15:
            return "Gut"
        elif wert <= 30:
            return "Mäßig"
        elif wert <= 50:
            return "Schlecht"
        else:
            return "Sehr schlecht"

    elif schadstoff == "o3":
        if wert <= 24:
            return "Sehr gut"
        elif wert <= 72:
            return "Gut"
        elif wert <= 144:
            return "Mäßig"
        elif wert <= 240:
            return "Schlecht"
        else:
            return "Sehr schlecht"

    elif schadstoff == "no2":
        if wert <= 10:
            return "Sehr gut"
        elif wert <= 30:
            return "Gut"
        elif wert <= 60:
            return "Mäßig"
        elif wert <= 100:
            return "Schlecht"
        else:
            return "Sehr schlecht"


lqi_klasse = lqi_einordnung(schadstoff, wert)

# Wetterdaten für Anzeige vorbereiten
anzeige_daten = [
    ["Temperatur", f"{temperatur:.1f} °C"],
    ["Windgeschwindigkeit", f"{windgeschwindigkeit_kmh:.1f} km/h"],
    ["Windrichtung", f"{windrichtung:.0f} °"],
    ["Luftdruck", f"{luftdruck:.1f} hPa"],
    ["Relative Luftfeuchtigkeit", f"{relative_luftfeuchtigkeit:.0f} %"],
    ["Niederschlag", f"{niederschlagshoehe_mm:.1f} mm"],
    ["Sonnenscheindauer", f"{sonnenscheindauer_minuten:.0f} min"],
    ["Gesamtbewölkung", f"{gesamtbewoelkung:.0f} %"]]

# Grafik / Übersicht erstellen
# Farben je nach LQI-Klasse festlegen
lqi_farben = {
    "Sehr gut": "#008000",       # dunkelgrün
    "Gut": "#7AC943",            # hellgrün
    "Mäßig": "#FFD966",          # gelb
    "Schlecht": "#FF6B6B",       # hellrot
    "Sehr schlecht": "#8B0000"}  # dunkelrot

lqi_farbe = lqi_farben[lqi_klasse]

# Grafik / Übersicht erstellen
fig, ax = plt.subplots(figsize=(9, 7))
ax.axis("off")

ax.text(
    0.5,
    0.95,
    "Stündliche Live-Luftschadstoffvorhersage",
    ha="center",
    fontsize=18,
    fontweight="bold")

ax.text(
    0.5,
    0.90,
    f"{stadt} | {datum_anzeige} | {uhrzeit_anzeige} Uhr",
    ha="center",
    fontsize=11,
    color="gray")

ax.text(
    0.5,
    0.84,
    f"Vorhergesagter {schadstoff.upper()}-Wert: {wert:.1f} µg/m³",
    ha="center",
    fontsize=16,
    fontweight="bold")

# LQI farbig hinterlegen
ax.text(
    0.5,
    0.76,
    f"Luftqualitätsindex: {lqi_klasse}",
    ha="center",
    fontsize=15,
    fontweight="bold",
    bbox=dict(
        boxstyle="round,pad=0.4",
        facecolor=lqi_farbe,
        edgecolor="black",
        linewidth=1.2))

# Tabelle mit Wetterdaten
tabelle = ax.table(
    cellText=anzeige_daten,
    colLabels=["Wettervariable", "Aktueller Wert"],
    cellLoc="left",
    colLoc="left",
    loc="center",
    bbox=[0.15, 0.05, 0.7, 0.62])

tabelle.auto_set_font_size(False)
tabelle.set_fontsize(11)
tabelle.scale(1, 1.3)

# Tabellenkopf fett machen
for spalte in range(2):
    zelle = tabelle[(0, spalte)]
    zelle.set_text_props(weight="bold")
    zelle.set_facecolor("#EAEAEA")

plt.tight_layout()
plt.show()