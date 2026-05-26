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
def trainiere_modelle(dfO):
    """Trainiert die Modelle einmalig und speichert sie im Cache."""
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

    # Daten vorbereiten & sortieren
    df = df[df["datum"] >= "2008-10-01"]
    df["timestamp"] = pd.to_datetime(df["datum"]) + pd.to_timedelta(
        df["stunde"], unit="h"
    )
    df.set_index("timestamp", inplace=True)
    df = df.sort_index()

    # Featuring
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

    lag_cols = []
    for stoff in stoffList:
        df[f"{stoff}_lag_1h"] = df[stoff].shift(1)
        df[f"{stoff}_lag_2h"] = df[stoff].shift(2)
        df[f"{stoff}_lag_24h"] = df[stoff].shift(24)
        df[f"{stoff}_roll_mean_6h"] = (
            df[stoff].shift(1).rolling(window=6).mean()
        )
        lag_cols.extend([
            f"{stoff}_lag_1h",
            f"{stoff}_lag_2h",
            f"{stoff}_lag_24h",
            f"{stoff}_roll_mean_6h",
        ])

    feature_cols = base_features + lag_cols
    ergebnisse = {}
    models = {}

    for stoff in stoffList:
        benoetigte_spalten = [stoff] + lag_cols
        df_clean = df.dropna(subset=benoetigte_spalten)
        df_clean = df_clean.replace([np.inf, -np.inf], np.nan).dropna(
            subset=benoetigte_spalten
        )

        X_stoff = df_clean[feature_cols]
        y_stoff = df_clean[stoff]

        split_idx = int(len(df_clean) * 0.8)
        X_train, X_test = X_stoff.iloc[:split_idx], X_stoff.iloc[split_idx:]
        y_train, y_test = y_stoff.iloc[:split_idx], y_stoff.iloc[split_idx:]

        model = XGBRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=5,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
        )
        model.fit(X_train, y_train)
        models[stoff] = model

        # Metriken berechnen
        y_pred = model.predict(X_test)
        ergebnisse[stoff] = {
            "MAE": mean_absolute_error(y_test, y_pred),
            "R²": r2_score(y_test, y_pred),
        }

    return models, ergebnisse


def prognosis(dfO):
    """Zeigt das Trainingsergebnis an und startet die App-Struktur."""
    st.subheader("⚙️ Trainingsphase & Modellqualität")

    # Schneller Abruf aus dem Cache
    models, ergebnisse = trainiere_modelle(dfO)

    # Ergebnisse anzeigen (Metriken)
    for stoff, metrics in ergebnisse.items():
        st.markdown(f"#### Ergebnisse für **{stoff.upper()}**")
        col1, col2 = st.columns(2)
        col1.metric(label="MAE", value=f"{metrics['MAE']:.2f}")
        col2.metric(label="R²-Wert", value=f"{metrics['R²']:.2f}")
        st.divider()

    st.header("📊 Zusammenfassung aller Modelle")
    df_ergebnisse = pd.DataFrame.from_dict(ergebnisse, orient="index")
    df_ergebnisse.index.name = "Stoff"
    st.dataframe(df_ergebnisse.style.format("{:.2f}"))
    st.success("Modelle erfolgreich geladen!")
    st.divider()

    # Aufruf der Prognose-Oberfläche
    assessProperties(models)


# ==========================================
# 2. INTERAKTIVE PROGNOSE-OBERFLÄCHE
# ==========================================
@st.fragment
def assessProperties(modelle):
    st.title("🌬️ Interaktive Schadstoff-Vorhersage")
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
            label="🔮 Luftqualität berechnen"
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