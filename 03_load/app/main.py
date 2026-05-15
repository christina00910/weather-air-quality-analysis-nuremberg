import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Seiten-Konfiguration (Muss immer ganz oben stehen!)
st.set_page_config(page_title="Luft & Wetter Bayern", page_icon="🌬️", layout="wide")

# 2. Daten laden (mit Cache für maximale Geschwindigkeit!)
@st.cache_data
def load_weather_data():
    # Da wir die App meistens aus dem Hauptordner starten, 
    # ist der Pfad 'data/dateiname.csv'
    try:
        df = pd.read_csv("data/wetter_hourly_nurnberg_1980_2023.csv")
        # Wichtig: Pandas sagen, dass die Spalte ein echtes Datum ist
        df['Datum_Uhrzeit'] = pd.to_datetime(df['Datum_Uhrzeit'])
        return df
    except FileNotFoundError:
        st.error("Fehler: Die Datei 'wetter_hourly_nurnberg_1980_2023.csv' wurde im Ordner 'data' nicht gefunden.")
        return pd.DataFrame() # Leerer DataFrame als Fallback

# Daten abrufen
df_wetter = load_weather_data()

# 3. Das Dashboard Gerüst bauen
st.title("🌬️ Luftqualität & Wetter Dashboard (Bayern)")

# Prüfen, ob Daten erfolgreich geladen wurden
if not df_wetter.empty:
    
    # --- SIDEBAR ---
    st.sidebar.header("⚙️ Filter & Einstellungen")
    
    # Da 44 Jahre auf einmal zu unübersichtlich sind, lassen wir den User ein Jahr wählen
    min_year = int(df_wetter['Datum_Uhrzeit'].dt.year.min())
    max_year = int(df_wetter['Datum_Uhrzeit'].dt.year.max())
    
    selected_year = st.sidebar.slider("Wähle ein Jahr", min_value=min_year, max_value=max_year, value=2023)
    
    # Daten auf das ausgewählte Jahr filtern
    df_filtered = df_wetter[df_wetter['Datum_Uhrzeit'].dt.year == selected_year]
    
    # --- HAUPTBEREICH (TABS) ---
    tab1, tab2, tab3 = st.tabs(["🌡️ Wetter-Exploration", "🧪 Schadstoffe (Coming Soon)", "🤖 ML-Labor (Coming Soon)"])
    
    with tab1:
        st.subheader(f"Wetterdaten für Nürnberg im Jahr {selected_year}")
        
        # Ein paar schnelle Metriken (KPIs) ganz oben
        col1, col2, col3 = st.columns(3)
        col1.metric("Durchschnittstemperatur", f"{df_filtered['Temperatur_C'].mean():.1f} °C")
        col2.metric("Maximaler Wind", f"{df_filtered['Wind_kmh'].max():.1f} km/h")
        col3.metric("Datensätze (Stunden)", len(df_filtered))
        
        # Ein interaktiver Plotly-Graph für die Temperatur
        st.markdown("### Temperaturverlauf")
        fig_temp = px.line(df_filtered, x='Datum_Uhrzeit', y='Temperatur_C', 
                           title=f"Stündliche Temperatur in Nürnberg ({selected_year})",
                           color_discrete_sequence=['#FF7F0E']) # Schönes Orange
        
        # Macht den Graphen etwas flacher und übersichtlicher
        fig_temp.update_layout(height=400) 
        st.plotly_chart(fig_temp, use_container_width=True)
        
        # Ein Schalter (Toggle), um die rohen Daten als Tabelle zu sehen
        if st.checkbox("Zeige rohe Tabellendaten"):
            st.dataframe(df_filtered)

else:
    st.warning("Bitte lege zuerst die CSV-Datei in den 'data' Ordner.")