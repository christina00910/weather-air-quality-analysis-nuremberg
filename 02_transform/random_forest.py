# Random Forest
# Ziel: Vergleich zwischen einem erweiterten Wettermodell und einem Modell
# mit zusätzlichen Zeitfaktoren wie Rush Hour, Wochenende und Monat.

# Bibliotheken laden
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error


# Datensatz laden
df = pd.read_csv("02_transform/Schadstoff_Wetter.csv")

# Datum umwandeln
df["datum"] = pd.to_datetime(df["datum"])

# Analysezeitraum ab 2008
df = df[df["datum"].dt.year >= 2008]

# Zielvariable festlegen
# Mögliche Werte: "o3", "no2", "pm10", "pm2x5"
schadstoff = "no2"

# Zeitvariablen erstellen
df["wochentag"] = df["datum"].dt.dayofweek
df["monat"] = df["datum"].dt.month
df["wochenende"] = df["wochentag"].isin([5, 6]).astype(int)
df["rush_hour"] = df["stunde"].isin([6, 7, 8, 9, 16, 17, 18, 19]).astype(int)

# Wettermodell
# Dieses Modell nutzt meteorologische Einflussfaktoren.
features_wetter = [
    "temperatur",
    "windgeschwindigkeit",
    "windrichtung",
    "luftdruck",
    "relative_luftfeuchtigkeit",
    "niederschlagshoehe_mm",
    "sonnenscheindauer_minuten",
    "gesamtbewoelkung"]

# Erweitertes Modell
# Dieses Modell ergänzt die Wetterdaten um zeitliche Faktoren.
features_erweitert = features_wetter + [
    "rush_hour",
    "wochenende",
    "monat"]


# Funktion für Random-Forest-Modell
def random_forest_analyse(features, titel):

    # Relevante Spalten auswählen und fehlende Werte entfernen
    daten = df[features + [schadstoff]].dropna()

    # Einflussvariablen
    x = daten[features]

    # Zielvariable
    y = daten[schadstoff]

    # Trainings- und Testdaten aufteilen
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    # Random-Forest-Modell erstellen
    modell = RandomForestRegressor(n_estimators=20, random_state=42, n_jobs=-1)

    # Modell trainieren
    modell.fit(x_train, y_train)

    # Vorhersage
    vorhersage = modell.predict(x_test)

    # Modellbewertung
    r2 = r2_score(y_test, vorhersage)
    mae = mean_absolute_error(y_test, vorhersage)
    print("\n" + titel)
    print("R²:", r2)
    print("MAE:", mae)

    # Feature Importance
    importance_df = pd.DataFrame({"Variable": x.columns, "Wichtigkeit": modell.feature_importances_}).sort_values(by="Wichtigkeit", ascending=False)
    print(importance_df)

    # Visualisierung
    plt.figure(figsize=(10, 6))
    plt.bar(importance_df["Variable"], importance_df["Wichtigkeit"])
    plt.title(f"{titel} für {schadstoff.upper()}")
    plt.ylabel("Wichtigkeit")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

# Modell 1: Wettervariablen
random_forest_analyse(
    features_wetter,
    "Wichtigkeit der Wettervariablen")

# Modell 2: Wettervariablen und Zeitfaktoren
random_forest_analyse(
    features_erweitert,
    "Wichtigkeit der Wetter- und Zeitfaktoren")