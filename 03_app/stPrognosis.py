import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor


# ==========================================
# 1. TRAININGS-PHASE (GECACHET: Läuft nur 1x)
# ==========================================
@st.cache_resource
def trainiere_modelle(dfO, mit_lags=True):
    """Trainiert Modelle für NO2, O3 und PM10 – wahlweise mit oder ohne Lag-Features."""
    spaltenList = [
        "datum",
        "stunde",
        "temperatur",
        "luftfeuchtigkeit",
        "windgeschwindigkeit",
        "luftdruck",
        "niederschlagshoehe_mm",
        "gesamtbewoelkung",
        "no2",
        "o3",
        "pm10",
    ]
    df = dfO[spaltenList].copy()

    # Daten vorbereiten & chronologisch sortieren
    df["timestamp"] = pd.to_datetime(df["datum"]) + pd.to_timedelta(
        df["stunde"], unit="h"
    )
    df.set_index("timestamp", inplace=True)
    df = df.sort_index()

    # Filter nach Sortierung anwenden (wichtig für die ersten Lags)
    df = df[df.index >= "2008-10-01"]

    # Feature Engineering (Kalender)
    df["monat"] = df.index.month
    df["wochentag"] = df.index.dayofweek
    df["ist_wochenende"] = df["wochentag"].isin([5, 6]).astype(int)

    base_features = [
        "stunde",
        "monat",
        "ist_wochenende",
        "temperatur",
        "luftfeuchtigkeit",
        "windgeschwindigkeit",
        "luftdruck",
        "niederschlagshoehe_mm",
        "gesamtbewoelkung",
    ]
    stoffList = ["no2", "o3", "pm10"]

    # Lags nur generieren, wenn der Schalter AKTIV ist
    if mit_lags:
        for stoff in stoffList:
            df[f"{stoff}_lag_1h"] = df[stoff].shift(1)
            df[f"{stoff}_lag_2h"] = df[stoff].shift(2)
            df[f"{stoff}_lag_24h"] = df[stoff].shift(24)
            df[f"{stoff}_roll_mean_6h"] = (
                df[stoff].shift(1).rolling(window=6).mean()
            )

    ergebnisse = {}
    models = {}

    for stoff in stoffList:
        # Features für diesen Durchlauf festlegen
        if mit_lags:
            stoff_spezifische_lags = [
                f"{stoff}_lag_1h",
                f"{stoff}_lag_2h",
                f"{stoff}_lag_24h",
                f"{stoff}_roll_mean_6h",
            ]
            feature_cols = base_features + stoff_spezifische_lags
        else:
            feature_cols = base_features.copy()

        # Sauberes Cleaning: Nur Zeilen löschen, die für DIESES Modell wichtig sind
        relevante_spalten = feature_cols + [stoff]
        df_clean = df.replace([np.inf, -np.inf], np.nan).dropna(
            subset=relevante_spalten
        )

        X_stoff = df_clean[feature_cols]
        y_stoff = df_clean[stoff]

        # Chronologischer Split
        split_idx = int(len(df_clean) * 0.8)
        X_train, X_test = X_stoff.iloc[:split_idx], X_stoff.iloc[split_idx:]
        y_train, y_test = y_stoff.iloc[:split_idx], y_stoff.iloc[split_idx:]

        # Modell-Training
        model = XGBRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=5,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
        )
        model.fit(X_train, y_train)
        models[stoff] = model

        # Validierung
        y_pred = model.predict(X_test)
        ergebnisse[stoff] = {
            "MAE": mean_absolute_error(y_test, y_pred),
            "R²": r2_score(y_test, y_pred),
        }

    return models, ergebnisse



    

def prognosis(dfO):
    """Zeigt das Trainingsergebnis an und startet die App-Struktur."""
    st.subheader("Modellqualität: Verbesserung durch Generierung von Zeitreihen-Features")

    # Schneller Abruf aus dem Cache
    """Ruft das Training zweimal auf (mit und ohne Lags)

    und liefert einen übersichtlichen Vergleich aller Ergebnisse.
    """
    print("Starte Training MIT Lags...")
    _, ergebnisse_mit = trainiere_modelle(dfO, mit_lags=True)

    print("Starte Training OHNE Lags...")
    _, ergebnisse_ohne = trainiere_modelle(dfO, mit_lags=False)

    vergleichs_daten = []

    # Daten für die Tabelle aufbereiten
    for stoff in ["no2", "o3", "pm10"]:
        vergleichs_daten.append({
            "Variante": "Ohne Lags (Nur Wetter)",
            "Schadstoff": stoff.upper(),
            "R²-Score": ergebnisse_ohne[stoff]["R²"],
        })
        vergleichs_daten.append({
            "Variante": "Mit Lags (Historie)",
            "Schadstoff": stoff.upper(),
            "R²-Score": ergebnisse_mit[stoff]["R²"],
        })
    st.info("""
    Der folgende Code berechnet die historischen Verzögerungen (Lags) und den gleitenden Durchschnitt für den Schadstoff:
    
    ```python
    # Erstellung der Lags (1h, 2h und 24h Versatz)
    df[f"{stoff}_lag_1h"] = df[stoff].shift(1)
    df[f"{stoff}_lag_2h"] = df[stoff].shift(2)
    df[f"{stoff}_lag_24h"] = df[stoff].shift(24)
    
    # Gleitender Durchschnitt der letzten 6 Stunden (verschoben um 1h)
    df[f"{stoff}_roll_mean_6h"] = (
        df[stoff].shift(1).rolling(window=6).mean()
    )
    ```
    
    *Hinweis: Durch diese Transformation entstehen in den ersten 24 Zeilen des Datensatzes `NaN`-Werte, die vor dem Modelltraining entfernt werden müssen.*
    """)

    with st.expander("Lags"):
        st.write ("""Lags sind historische Messwerte aus früheren Zeitschritten, die für aktuelle Vorhersagen genutzt werden. Wenn wir die Luftqualität für morgen berechnen, ist der Wert von heute der erste Lag  und der von gestern der zweite.
Der Einsatz von Lags ist notwendig, weil die meisten Prozesse eine Trägheit besitzen und sich aus ihrer eigenen Vergangenheit heraus entwickeln. Da Schadstoffe oder Wetterfronten nicht abrupt verschwinden, liefern diese historischen Daten dem Machine-Learning-Modell das nötige Fundament, um Trends und Zyklen präzise fortzuschreiben.""")
    # Als Pandas DataFrame für eine schöne Darstellung speichern
    df_vergleich = pd.DataFrame(vergleichs_daten)
    st.dataframe(
    df_vergleich, 
    use_container_width=True, # Nutzt die volle Bildschirmbreite
    hide_index=True           # Versteckt die unschöne Zeilennummerierung
    )

    with st.expander("Was bedeutet das Bestimmtheitsmaß R²?"):
        st.markdown("""
        Das **Bestimmtheitsmaß $R^2$** zeigt an, wie viel Prozent der echten Daten-Schwankungen das Modell mathematisch versteht. Es vergleicht die Vorhersage mit einem simplen Mittelwert.
        
        **Die Qualitätsstufen im Überblick:**
        * 🟢 **Exzellent ($R^2 > 0.8$):** Das Modell arbeitet hochpräzise. Die Vorhersagen sind extrem nah an den echten Werten.
        * 🟡 **Gut bis Akzeptabel ($0.5$ bis $0.8$):** Wichtige Trends werden richtig erkannt, kleinere Abweichungen kommen vor.
        * 🟠 **Schwach ($R^2 < 0.5$):** Das Modell erkennt nur wenige Muster. Die Vorhersage ist ungenau.
        * 🔴 **Nutzlos ($R^2 \le 0$):** Das Modell rät blind oder schneidet schlechter ab als der reine Durchschnitt.
        
        **Kurz gesagt:** Je höher der $R^2$-Wert, desto verlässlicher ist die Prognose.
        """)    
    # Aufruf der Prognose-Oberfläche
    assessProperties(ergebnisse_mit)

    return df_vergleich



# ==========================================
# 2. INTERAKTIVE PROGNOSE-OBERFLÄCHE
# ==========================================
@st.fragment
def assessProperties(modelle):
    st.title("Interaktive Schadstoff-Vorhersage")
    st.write(
        "Stelle die Szenario-Werte ein und klicke unten auf den Button, um die Werte zu berechnen."
    )

    # Start des Formulars: Verhindert Neuladen bei Slider-Bewegung!
    with st.form("wetter_prognose_form"):

        col_wetter, col_lags = st.columns(2)

        with col_wetter:
            st.markdown("### 🌤️ Wetterparameter & Zeit")
            stunde = st.slider(
                "Uhrzeit (Stunde)", min_value=0, max_value=23, value=8
            )
            monat = st.slider("Monat", min_value=1, max_value=12, value=1)
            ist_wochenende = st.selectbox(
                "Wochenende?",
                options=[0, 1],
                format_func=lambda x: "Ja" if x == 1 else "Nein",
            )
            temperatur = st.number_input("Temperatur (°C)", value=5.0, step=0.5)
            windgeschwindigkeit = st.slider(
                "Windgeschwindigkeit (m/s)",
                min_value=0.0,
                max_value=20.0,
                value=6.5,
            )
            luftdruck = st.number_input(
                "Luftdruck (hPa)", value=1005.0, step=1.0
            )
            niederschlag = st.number_input(
                "Niederschlagshöhe (mm)", value=2.0, step=0.1
            )
            bewoelkung = st.slider(
                "Gesamtbewölkung (Achtel)", min_value=0, max_value=8, value=8
            )
            luftfeuchtigkeit = np.nan

        with col_lags:
            st.markdown("### 📊 Historische Werte (Lags & Mittelwerte)")

            st.markdown("**NO₂-Historie (µg/m³)**")
            no2_1h = st.number_input("NO₂ vor 1 Std.", value=20.0)
            no2_2h = st.number_input("NO₂ vor 2 Std.", value=22.0)
            no2_24h = st.number_input("NO₂ vor 24 Std.", value=25.0)
            no2_mean6h = st.number_input(
                "NO₂ Mittelwert (letzte 6 Std.)", value=21.0
            )

            st.markdown("**O₃-Historie (µg/m³)**")
            o3_1h = st.number_input("O₃ vor 1 Std.", value=40.0)
            o3_2h = st.number_input("O₃ vor 2 Std.", value=38.0)
            o3_24h = st.number_input("O₃ vor 24 Std.", value=45.0)
            o3_mean6h = st.number_input(
                "O₃ Mittelwert (letzte 6 Std.)", value=41.0
            )

            st.markdown("**PM₁₀-Historie (µg/m³)**")
            pm10_1h = st.number_input("PM₁₀ vor 1 Std.", value=15.0)
            pm10_2h = st.number_input("PM₁₀ vor 2 Std.", value=16.0)
            pm10_24h = st.number_input("PM₁₀ vor 24 Std.", value=18.0)
            pm10_mean6h = st.number_input(
                "PM₁₀ Mittelwert (letzte 6 Std.)", value=15.5
            )

        # Der entscheidende Button innerhalb des Formulars
        submit_button = st.form_submit_button(
            label="Luftqualität berechnen"
        )

    # 3. VORHERSAGE AUSFÜHREN (Erst nach Button-Klick)
    if submit_button:
        # DataFrame mit allen 21 Features exakt nach Modell-Vorgabe bauen
        wetter_szenarien = pd.DataFrame([
            {
                "stunde": stunde,
                "monat": monat,
                "ist_wochenende": ist_wochenende,
                "temperatur": temperatur,
                "luftfeuchtigkeit": luftfeuchtigkeit,
                "windgeschwindigkeit": windgeschwindigkeit,
                "luftdruck": luftdruck,
                "niederschlagshoehe_mm": niederschlag,
                "gesamtbewoelkung": bewoelkung,
                "no2_lag_1h": no2_1h,
                "no2_lag_2h": no2_2h,
                "no2_lag_24h": no2_24h,
                "no2_roll_mean_6h": no2_mean6h,
                "o3_lag_1h": o3_1h,
                "o3_lag_2h": o3_2h,
                "o3_lag_24h": o3_24h,
                "o3_roll_mean_6h": o3_mean6h,
                "pm10_lag_1h": pm10_1h,
                "pm10_lag_2h": pm10_2h,
                "pm10_lag_24h": pm10_24h,
                "pm10_roll_mean_6h": pm10_mean6h,
            }
        ])

        # Berechnungen für alle drei Schadstoffe (Skalar-Fehlerbehebung integriert)
        pred_no2 = modelle["no2"].predict(wetter_szenarien)[0]
        pred_o3 = modelle["o3"].predict(wetter_szenarien)[0]
        pred_pm10 = modelle["pm10"].predict(wetter_szenarien)[0]

        # Visuelle Ausgabe der Ergebnisse in 3 Spalten
        st.success("Vorhergesagte Werte berechnet:")
        c1, c2, c3 = st.columns(3)
        c1.metric(label="Vorhergesagtes NO₂", value=f"{pred_no2:.2f} µg/m³")
        c2.metric(label="Vorhergesagtes O₃", value=f"{pred_o3:.2f} µg/m³")
        c3.metric(label="Vorhergesagtes PM₁₀", value=f"{pred_pm10:.2f} µg/m³")