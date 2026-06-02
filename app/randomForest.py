# Random Forest
# Ziel: Vergleich zwischen einem erweiterten Wettermodell und einem Modell
# mit zusätzlichen Zeitfaktoren wie Rush Hour, Wochenende und Monat.

# Bibliotheken laden
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error


def showDiagrams (dfO, stoff) :
    df = dfO.copy ()
# Datum umwandeln
    df["datum"] = pd.to_datetime(df["datum"])
    
    # Analysezeitraum ab 2008
    df = df[df["datum"].dt.year >= 2008]
    
    # Zielvariable festlegen
    # Mögliche Werte: "o3", "no2", "pm10", "pm2x5"
    schadstoff = stoff #"no2"
    
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

    geforderte_spalten = features_wetter + [schadstoff]
    fehlende_spalten = [col for col in geforderte_spalten if col not in df.columns]
    
    if fehlende_spalten:
        st.error(f"Folgende Spalten fehlen im Datensatz: {fehlende_spalten}")
        st.write("Verfügbare Spalten im DataFrame:", list(df.columns))
        st.stop()  # Stoppt die Ausführung an dieser Stelle
    
    # Erweitertes Modell
    # Dieses Modell ergänzt die Wetterdaten um zeitliche Faktoren.
    features_erweitert = features_wetter + [
        "stunde",
        "rush_hour",
        "wochenende",
        "monat"]

    # Modell 1: Wettervariablen
    fig = random_forest_analyse(
        df,
        schadstoff,
        features_wetter,
        "Modell 1: Wettervariablen")
    st.pyplot(fig)
    st.caption("""
    Hinweis: Modell 1 verwendet ausschließlich Wettervariablen zur Vorhersage der Luftschadstoffkonzentrationen.
    """)

    st.divider()

    # Modell 2: Wettervariablen und Zeitfaktoren
    fig = random_forest_analyse(
        df,
        schadstoff,
        features_erweitert,
        "Modell 2: Wettervariablen und Zeitfaktoren")
    st.pyplot(fig)
    st.caption("""
    Hinweis: Modell 2 ergänzt zusätzlich Zeitvariablen wie Stunde, Monat, Wochenende und Rush Hour, wodurch zeitliche Muster der Luftschadstoffbelastung besser erkannt werden können.
    """)
    return

# Funktion für Random-Forest-Modell
def random_forest_analyse(data, schadstoff, features, modellname):

    # Relevante Spalten auswählen und fehlende Werte entfernen
    daten = data[features + [schadstoff]].dropna()

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
        n_estimators=100,
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

    # Diagramm erstellen (Nutzt jetzt Ihr korrektes importance_df)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x="Wichtigkeit", 
        y="Variable", 
        data=importance_df, 
        palette="viridis", 
        ax=ax
    )
    ax.set_title(f"{modellname}\nFeature Wichtigkeit für {schadstoff.upper()} (R²: {r2:.2f}, MAE: {mae:.2f})")
    ax.set_xlabel("Relative Wichtigkeit")
    ax.set_ylabel("Merkmale")
    plt.tight_layout()
    return fig

