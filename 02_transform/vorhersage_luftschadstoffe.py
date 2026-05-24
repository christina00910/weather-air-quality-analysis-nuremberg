# Luftschadstoff-Vorhersage mit Random Forest und Open-Meteo API

import requests
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

# ------------------------------------------------------------
# 1. Historische Daten laden und Modell trainieren
# ------------------------------------------------------------

df = pd.read_csv("02_transform/Schadstoff_Wetter.csv")

df["datum"] = pd.to_datetime(df["datum"])
df = df[df["datum"].dt.year >= 2008]

# Zielvariable festlegen
# Möglich: "o3", "no2", "pm10", "pm2x5"
schadstoff = "pm10"

# Zeitvariablen für historische Daten erstellen
df["wochentag"] = df["datum"].dt.dayofweek
df["monat"] = df["datum"].dt.month
df["wochenende"] = df["wochentag"].isin([5, 6]).astype(int)
df["rush_hour"] = df["stunde"].isin([6, 7, 8, 9, 16, 17, 18, 19]).astype(int)

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
    "rush_hour",
    "wochenende",
    "monat"]

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
temperatur = api_daten["hourly"]["temperature_2m"][0]
relative_luftfeuchtigkeit = api_daten["hourly"]["relative_humidity_2m"][0]
niederschlagshoehe_mm = api_daten["hourly"]["precipitation"][0]
luftdruck = api_daten["hourly"]["surface_pressure"][0]
gesamtbewoelkung = api_daten["hourly"]["cloud_cover"][0]
windgeschwindigkeit = api_daten["hourly"]["wind_speed_10m"][0] / 3.6
windrichtung = api_daten["hourly"]["wind_direction_10m"][0]
sonnenscheindauer_minuten = api_daten["hourly"]["sunshine_duration"][0] / 60

# Zeitvariablen aus API-Zeitpunkt berechnen
stunde = zeitpunkt.hour
wochentag = zeitpunkt.dayofweek
monat = zeitpunkt.month
wochenende = 1 if wochentag in [5, 6] else 0
rush_hour = 1 if stunde in [6, 7, 8, 9, 16, 17, 18, 19] else 0


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
    "rush_hour": rush_hour,
    "wochenende": wochenende,
    "monat": monat}])

print("\nLive-Wetterdaten für die Vorhersage:")
print(live_daten)


# ------------------------------------------------------------
# 4. Luftschadstoff vorhersagen
# ------------------------------------------------------------

vorhersage_live = modell.predict(live_daten)

print(f"\nVorhergesagter {schadstoff.upper()}-Wert:")
print(vorhersage_live[0])