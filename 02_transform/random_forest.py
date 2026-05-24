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
df = pd.read_csv("02_transform/data_2.csv")

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
    "stunde",
    "rush_hour",
    "wochenende",
    "monat"]


# Funktion für Random-Forest-Modell
def random_forest_analyse(features, modellname):

    # Relevante Spalten auswählen und fehlende Werte entfernen
    daten = df[features + [schadstoff]].dropna()

    # Einflussvariablen
    x = daten[features]

    # Zielvariable
    y = daten[schadstoff]

    # Trainings- und Testdaten aufteilen
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42)

    # Random-Forest-Modell erstellen
    modell = RandomForestRegressor(
        n_estimators=20,
        random_state=42,
        n_jobs=-1)

    # Modell trainieren
    modell.fit(x_train, y_train)

    # Vorhersage
    vorhersage = modell.predict(x_test)

    # Modellbewertung
    r2 = r2_score(y_test, vorhersage)
    mae = mean_absolute_error(y_test, vorhersage)

    # Feature Importance berechnen
    importance_df = pd.DataFrame({
        "Variable": x.columns,
        "Wichtigkeit": modell.feature_importances_})

    importance_df = importance_df.sort_values(
        by="Wichtigkeit",
        ascending=False)

    # Werte runden
    importance_df["Wichtigkeit"] = importance_df["Wichtigkeit"].round(3)

    # Ergebnisse anzeigen
    print("\n" + modellname)
    print("R²:", round(r2, 3))
    print("MAE:", round(mae, 3))
    print(importance_df)

    # ------------------------------------------------------------
    # Grafik erstellen
    # ------------------------------------------------------------

    fig, ax = plt.subplots(figsize=(10, 6))

    # Balkendiagramm erstellen
    ax.bar(
        importance_df["Variable"],
        importance_df["Wichtigkeit"])

    # Titel
    ax.set_title(
        f"{modellname} für {schadstoff.upper()}",
        fontsize=15,
        fontweight="bold")

    # Modellbewertung anzeigen
    ax.text(0.5, 0.95, f"R² = {r2:.3f} | MAE = {mae:.3f}",
        transform=ax.transAxes,
        ha="center",
        fontsize=11)

    # Achsenbeschriftungen
    ax.set_xlabel("Einflussvariable")
    ax.set_ylabel("Wichtigkeit")

    # X-Achse drehen
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


# Modell 1: Wettervariablen
random_forest_analyse(
    features_wetter,
    "Modell 1: Wettervariablen")

# Modell 2: Wettervariablen und Zeitfaktoren
random_forest_analyse(
    features_erweitert,
    "Modell 2: Wettervariablen und Zeitfaktoren")