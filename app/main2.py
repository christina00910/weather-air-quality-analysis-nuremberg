import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np # NEU: Für unsere Testdaten-Generierung

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
        
        # DER MAGISCHE SCHRITT: Inner Join! 
        # Wir behalten nur die Stunden, für die wir SOWOHL Wetter ALS AUCH Luftdaten haben.
        df_merged = pd.merge(df_wetter, df_luft, on='Datum_Uhrzeit', how='inner')
        st.sidebar.success("✅ Wetter & echte Luftdaten erfolgreich verknüpft!")
        
    except FileNotFoundError:
        st.sidebar.warning("⚠️ Echte UBA-Daten nicht gefunden. Nutze simulierte Daten für das Layout.")
        df_merged = df_wetter.copy()
        
        # Wir simulieren realistische Zusammenhänge für den Test:
        # Ozon steigt mit der Temperatur und Sonne
        df_merged['Ozon'] = np.maximum(0, df_merged['Temperatur_C'] * 2.5 + (df_merged['Sonnenschein_min'].fillna(0) / 10) + np.random.normal(0, 10, len(df_merged)))
        # NO2 ist im Winter höher (Kälte) und sinkt bei viel Wind
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
    tab1, tab2, tab3 = st.tabs(["🌡️ Wetter-Exploration", "🧪 Schadstoff-Analyse", "🤖 ML-Labor (Coming Soon)"])
    
    # ... (Dein bisheriger Code für tab1 bleibt exakt gleich) ...
    with tab1:
        st.subheader("Wetterübersicht")
        st.info("Dein Temperatur-Graph von vorhin ist hier...")
        # (Hier deinen px.line Code von vorhin für das Wetter einfügen)
        
    # --- NEU: TAB 2 (SCHADSTOFFE) ---
    with tab2:
        st.subheader(f"Schadstoff-Analyse für Nürnberg ({selected_year})")
        
        # Auswahl, welchen Schadstoff wir untersuchen wollen
        schadstoff = st.radio("Wähle einen Schadstoff zur Analyse:", ["Ozon", "NO2"], horizontal=True)
        
        col_plot1, col_plot2 = st.columns(2)
        
        with col_plot1:
            st.markdown(f"### Zeitverlauf: {schadstoff}")
            # Ein klassischer Linien-Graph über das Jahr
            fig_time = px.line(df_filtered, x='Datum_Uhrzeit', y=schadstoff, 
                               color_discrete_sequence=['#d62728'],
                               title=f"{schadstoff}-Belastung im Jahresverlauf")
            st.plotly_chart(fig_time, use_container_width=True)
            
        with col_plot2:
            st.markdown("### Die Wetter-Korrelation")
            # Ein Scatterplot: Hier zeigt sich das Data Science Know-How!
            # Wir plotten z.B. Temperatur vs. Ozon
            
            # Dynamische X-Achse je nach Schadstoff (für Ozon ist Temp wichtig, für NO2 eher Wind)
            x_achse = 'Temperatur_C' if schadstoff == 'Ozon' else 'Wind_kmh'
            
            fig_scatter = px.scatter(df_filtered, x=x_achse, y=schadstoff, 
                                     opacity=0.3, # Leicht transparent, damit man Punktwolken sieht
                                     trendline="ols", # Zieht eine automatische Trendlinie!
                                     color='Temperatur_C',
                                     color_continuous_scale='Inferno',
                                     title=f"Einfluss von {x_achse} auf {schadstoff}")
            st.plotly_chart(fig_scatter, use_container_width=True)

        # Kurze Daten-Erklärung für den Betrachter
        st.info(f"💡 **Data Science Insight:** Im rechten Scatter-Plot siehst du die Korrelation. Wenn die Punkte und die Linie deutlich nach oben oder unten zeigen, hat das Wetter einen starken Einfluss auf {schadstoff}. Das wird die Grundlage für unser ML-Modell in Tab 3!")