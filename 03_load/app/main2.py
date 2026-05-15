# -*- coding: utf-8 -*-
# @Author: Frank Hasdorf
# @Date:   12-05-2026 16:38:09
# @Last Modified by:   Frank Hasdorf
# @Last Modified time: 15-05-2026 07:56:46
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go  # NEU: Für das Tachometer in Tab 3
import numpy as np

st.set_page_config(page_title="Luft & Wetter Bayern", page_icon="🌬️", layout="wide")

# --- 1. DATEN LADEN & MERGEN ---
@st.cache_data
def load_and_merge_data():
    # 1. Wetter laden
    df_wetter = pd.read_csv("data/wetter_hourly_nurnberg_1980_2023.csv")
    df_wetter['Datum_Uhrzeit'] = pd.to_datetime(df_wetter['Datum_Uhrzeit'])
    
    # 2. Luftdaten laden (Hier setzen wir einen Try-Except-Block ein)
    try:
        df_luft = pd.read_csv("data/luftdaten_nurnberg.csv")
        df_luft['Datum_Uhrzeit'] = pd.to_datetime(df_luft['Datum_Uhrzeit'])
        
        # Inner Join: Wir behalten nur die Stunden, für die wir Wetter & Luftdaten haben.
        df_merged = pd.merge(df_wetter, df_luft, on='Datum_Uhrzeit', how='inner')
        st.sidebar.success("✅ Wetter & echte Luftdaten erfolgreich verknüpft!")
        
    except FileNotFoundError:
        st.sidebar.warning("⚠️ Echte UBA-Daten nicht gefunden. Nutze simulierte Daten für das Layout.")
        df_merged = df_wetter.copy()
        
        # Wir simulieren realistische Zusammenhänge für den Test:
        df_merged['Ozon'] = np.maximum(0, df_merged['Temperatur_C'] * 2.5 + (df_merged['Sonnenschein_min'].fillna(0) / 10) + np.random.normal(0, 10, len(df_merged)))
        df_merged['NO2'] = np.maximum(0, 60 - df_merged['Temperatur_C'] - (df_merged['Wind_kmh'] * 0.5) + np.random.normal(0, 5, len(df_merged)))

    return df_merged

# Daten abrufen
df_main = load_and_merge_data()

st.title("🌬️ Luftqualität & Wetter Dashboard (Bayern)")

if not df_main.empty:
    
    # --- SIDEBAR ---
    st.sidebar.header("⚙️ Filter & Einstellungen")
    min_year = int(df_main['Datum_Uhrzeit'].dt.year.min())
    max_year = int(df_main['Datum_Uhrzeit'].dt.year.max())
    selected_year = st.sidebar.slider("Wähle ein Jahr", min_year, max_year, 2023)
    
    df_filtered = df_main[df_main['Datum_Uhrzeit'].dt.year == selected_year]
    
    # --- HAUPTBEREICH (TABS) ---
    tab1, tab2, tab3 = st.tabs(["🌡️ Wetter-Exploration", "🧪 Schadstoff-Analyse", "🤖 ML-Labor"])
    
    # --- TAB 1: WETTER ---
    with tab1:
        st.subheader(f"Wetterdaten für Nürnberg im Jahr {selected_year}")
        
        # Schnelle Metriken (KPIs)
        col1, col2, col3 = st.columns(3)
        col1.metric("Durchschnittstemperatur", f"{df_filtered['Temperatur_C'].mean():.1f} °C")
        col2.metric("Maximaler Wind", f"{df_filtered['Wind_kmh'].max():.1f} km/h")
        col3.metric("Datensätze (Stunden)", len(df_filtered))
        
        # Temperaturverlauf
        st.markdown("### Temperaturverlauf")
        fig_temp = px.line(df_filtered, x='Datum_Uhrzeit', y='Temperatur_C', 
                           title=f"Stündliche Temperatur in Nürnberg ({selected_year})",
                           color_discrete_sequence=['#FF7F0E'])
        fig_temp.update_layout(height=400) 
        st.plotly_chart(fig_temp, use_container_width=True)
        
        if st.checkbox("Zeige rohe Tabellendaten"):
            st.dataframe(df_filtered)
        
    # --- TAB 2: SCHADSTOFFE ---
    with tab2:
        st.subheader(f"Schadstoff-Analyse für Nürnberg ({selected_year})")
        
        schadstoff = st.radio("Wähle einen Schadstoff zur Analyse:", ["Ozon", "NO2"], horizontal=True)
        col_plot1, col_plot2 = st.columns(2)
        
        with col_plot1:
            st.markdown(f"### Zeitverlauf: {schadstoff}")
            fig_time = px.line(df_filtered, x='Datum_Uhrzeit', y=schadstoff, 
                               color_discrete_sequence=['#d62728'],
                               title=f"{schadstoff}-Belastung im Jahresverlauf")
            st.plotly_chart(fig_time, use_container_width=True)
            
        with col_plot2:
            st.markdown("### Die Wetter-Korrelation")
            x_achse = 'Temperatur_C' if schadstoff == 'Ozon' else 'Wind_kmh'
            
            fig_scatter = px.scatter(df_filtered, x=x_achse, y=schadstoff, 
                                     opacity=0.3,
                                     trendline="ols",
                                     color='Temperatur_C',
                                     color_continuous_scale='Inferno',
                                     title=f"Einfluss von {x_achse} auf {schadstoff}")
            st.plotly_chart(fig_scatter, use_container_width=True)

        st.info(f"💡 **Data Science Insight:** Im rechten Scatter-Plot siehst du die Korrelation. Das ist die Grundlage für unser ML-Modell in Tab 3!")

    # --- TAB 3: ML-LABOR ---
    with tab3:
        st.subheader("🤖 Vorhersage: Ozon-Belastung")
        st.markdown("**Simuliere das Wetter für morgen:**")
        
        # Eingaberegler
        col_input1, col_input2, col_input3 = st.columns(3)
        sim_temp = col_input1.slider("Temperatur (°C)", 0, 40, 28)
        sim_wind = col_input2.slider("Wind (km/h)", 0, 50, 10)
        sim_sonne = col_input3.slider("Sonne (min)", 0, 600, 450)

        # Simulation des Machine-Learning-Modells
        vorhergesagter_ozon_wert = sim_temp * 3.5 + (sim_sonne / 15) - (sim_wind * 1.2)

        # Das Plotly Tachometer
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = vorhergesagter_ozon_wert,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Vorhersage: Ozon (µg/m³)", 'font': {'size': 24}},
            number = {'suffix': " µg/m³", 'font': {'size': 40}},
            gauge = {
                'axis': {'range': [0, 250], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "rgba(0,0,0,0)"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 100], 'color': "#a3f7bf"},     # Grün (Gut)
                    {'range': [100, 180], 'color': "#fdfd96"},   # Gelb (Mäßig)
                    {'range': [180, 250], 'color': "#ffb347"}    # Orange/Rot (Kritisch)
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 6},
                    'thickness': 0.75,
                    'value': vorhergesagter_ozon_wert
                }
            }
        ))
        
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.info("💡 **Tipp:** Spiele mit den Reglern! Wenn du die Temperatur und Sonne hochdrehst und den Wind wegnimmst, wandert der Zeiger in den roten Bereich.")

else:
    st.warning("Bitte lege zuerst die CSV-Datei in den 'data' Ordner.")