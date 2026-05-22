# Random Forest Regressor
# Ziel: Vergleich zwischen einem reinen Wettermodell und einem erweiterten Modell
# mit zusätzlichen Zeitfaktoren wie Rush Hour, Wochenende und Monat.

# Bibliotheken laden
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error


# Datensatz laden
# Der Datensatz enthält Wetterdaten und Luftschadstoffe.
df = pd.read_csv("02_transform/Schadstoff_Wetter.csv")


# Datum in ein echtes Datumsformat umwandeln
# Dadurch können später Jahr, Monat und Wochentag aus dem Datum berechnet werden.
df["datum"] = pd.to_datetime(df["datum"])


# Analysezeitraum festlegen
# PM2.5 ist erst ab 2008 verfügbar, deshalb wird der Zeitraum ab 2008 verwendet.
df = df[df["datum"].dt.year >= 2008]


# Zielvariable festlegen
# Hier kann der zu untersuchende Luftschadstoff flexibel geändert werden.
# Mögliche Werte: "o3", "no2", "pm10", "pm2x5"
schadstoff = "pm10"


# Zeitvariablen erstellen
# Diese Variablen dienen als einfache Annäherung an zeitliche Muster,
# z. B. Berufsverkehr, Wochenend-Effekte oder saisonale Unterschiede.
df["wochentag"] = df["datum"].dt.dayofweek
df["monat"] = df["datum"].dt.month
df["wochenende"] = df["wochentag"].isin([5, 6]).astype(int)
df["rush_hour"] = df["stunde"].isin([6, 7, 8, 9, 16, 17, 18, 19]).astype(int)


# Reines Wettermodell
# Dieses Modell nutzt nur meteorologische Einflussfaktoren.
features_wetter = [
    "temperatur",
    "windgeschwindigkeit",
    "relative_luftfeuchtigkeit",
    "niederschlagshoehe_mm",
    "sonnenscheindauer_minuten",
    "gesamtbewoelkung"]


# Erweitertes Modell
# Dieses Modell ergänzt die Wetterdaten um zeitliche Faktoren.
# Dadurch soll geprüft werden, ob zeitliche Muster die Vorhersage verbessern.
features_erweitert = features_wetter + [
    "rush_hour",
    "wochenende",
    "monat"]


# Funktion für Random-Forest-Modell
# Die Funktion trainiert ein Modell, bewertet es und erstellt eine Grafik
# zur Wichtigkeit der Einflussfaktoren.
def random_forest_analyse(features, titel):

    # Relevante Spalten auswählen und fehlende Werte entfernen
    daten = df[features + [schadstoff]].dropna()

    # Einflussvariablen
    x = daten[features]

    # Zielvariable
    y = daten[schadstoff]

    # Daten in Trainings- und Testdaten aufteilen
    # 80 % werden zum Trainieren genutzt, 20 % zum Testen.
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42)

    # Random-Forest-Modell erstellen
    # n_estimators = Anzahl der Entscheidungsbäume
    # n_jobs=-1 nutzt alle verfügbaren Rechnerkerne.
    modell = RandomForestRegressor(
        n_estimators=20,
        random_state=42,
        n_jobs=-1)

    # Modell trainieren
    modell.fit(x_train, y_train)

    # Schadstoffwerte für die Testdaten vorhersagen
    vorhersage = modell.predict(x_test)

    # Modellgüte berechnen
    # R² zeigt, wie gut das Modell die Schwankungen der Schadstoffwerte erklärt.
    # MAE zeigt die durchschnittliche absolute Abweichung der Vorhersage.
    r2 = r2_score(y_test, vorhersage)
    mae = mean_absolute_error(y_test, vorhersage)

    print("\n" + titel)
    print("R²:", r2)
    print("MAE:", mae)

    # Wichtigkeit der Einflussvariablen ausgeben
    importance_df = pd.DataFrame({
        "Variable": x.columns,
        "Wichtigkeit": modell.feature_importances_})

    importance_df = importance_df.sort_values(
        by="Wichtigkeit",
        ascending=False)

    print(importance_df)

    # Wichtigkeit der Einflussvariablen visualisieren
    plt.figure(figsize=(10, 6))
    plt.bar(
        importance_df["Variable"],
        importance_df["Wichtigkeit"])

    plt.title(f"{titel} für {schadstoff.upper()}")
    plt.ylabel("Wichtigkeit")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


# Modell 1: nur Wettervariablen
random_forest_analyse(
    features_wetter,
    "Wichtigkeit der Wettervariablen")


# Modell 2: Wettervariablen und Zeitfaktoren
random_forest_analyse(
    features_erweitert,
    "Wichtigkeit der Wetter- und Zeitfaktoren")