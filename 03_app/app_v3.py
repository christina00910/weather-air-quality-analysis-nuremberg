# -*- coding: utf-8 -*-
# @Authors: Frank Hasdorf, Christina Dürrbeck, Markus Edelhoff
# @Project: Abschlussprojekt - app_aufbau
#           Abschlussklasse Dezember 2025
# @Date:   16-05-2026 15:56:50
# @Last Modified time: 16-05-2026 15:56:50




import streamlit as st
import pandas as pd
import os
from pathlib import Path # für sichere Datenpfade auf jedem Rechner
import plotly.express as px # Neu. Für die interaktiven Charts nutzen wir die Plotly-Bibliothek, die sich nahtlos in Streamlit integrieren lässt.
import time

# Die Besonderheit bei Streamlit ist: st.set_page_config muss zwingend der 
# allererste Streamlit-Befehl im Skript sein, noch bevor irgendwelche anderen 
# visuellen Elemente gerendert werden.

# 1. Seitenkonfiguration
# Das SVG sauber als Data-URI formatiert (Anführungszeichen im SVG angepasst)
custom_svg = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' height='24px' viewBox='0 -960 960 960' width='24px' fill='%231f1f1f'><path d='M131.5-131.5Q120-143 120-160v-40q0-17 11.5-28.5T160-240q17 0 28.5 11.5T200-200v40q0 17-11.5 28.5T160-120q-17 0-28.5-11.5Zm160 0Q280-143 280-160v-220q0-17 11.5-28.5T320-420q17 0 28.5 11.5T360-380v220q0 17-11.5 28.5T320-120q-17 0-28.5-11.5Zm160 0Q440-143 440-160v-140q0-17 11.5-28.5T480-340q17 0 28.5 11.5T520-300v140q0 17-11.5 28.5T480-120q-17 0-28.5-11.5Zm160 0Q600-143 600-160v-200q0-17 11.5-28.5T640-400q17 0 28.5 11.5T680-360v200q0 17-11.5 28.5T640-120q-17 0-28.5-11.5Zm160 0Q760-143 760-160v-360q0-17 11.5-28.5T800-560q17 0 28.5 11.5T840-520v360q0 17-11.5 28.5T800-120q-17 0-28.5-11.5ZM560-481q-16 0-30.5-6T503-504L400-607 188-395q-12 12-28.5 11.5T131-396q-11-12-10.5-28.5T132-452l211-211q12-12 26.5-17.5T400-686q16 0 31 5.5t26 17.5l103 103 212-212q12-12 28.5-11.5T829-771q11 12 10.5 28.5T828-715L617-504q-11 11-26 17t-31 6Z'/></svg>"

st.set_page_config(
    page_title="Schadstoff/Wetter-Korrelation am Beispiel der Stadt Nürnberg",
    page_icon=custom_svg,
    layout="wide"
)


# Neu: Daten laden mit @st.cache. Das sorgt dafür, dass die Daten nur einmal geladen werden und nicht bei jedem Skriptlauf erneut eingelesen werden müssen.
@st.cache_data
def load_data():
    """
    Lädt die kombinierten Wetter- und Schadstoffdaten aus der CSV-Datei.
    
    Nutzt Streamlit-Caching (@st.cache_data), um das wiederholte Einlesen 
    von der Festplatte bei jeder Nutzerinteraktion zu verhindern.
    
    Returns:
        pd.DataFrame: Aufbereiteter Datensatz mit korrekten Datentypen und Spaltennamen.
    """
# Datenimport mit pathlib - modul
# Path(__file__).parent ist eine sehr gängige Kombination aus der 
# Python-Bibliothek pathlib. Sie ermittelt dynamisch das Verzeichnis, 
# in dem sich die gerade ausgeführte Python-Datei befindet

    base_dir = Path(__file__).parent
    data_pfad = base_dir / 'data' / 'Schadstoff_Wetter.csv'

    # CSV einlesen
    df = pd.read_csv(data_pfad)

    # WICHTIG: Erst in String casten, da 'datumstunde' als int64 eingelesen wird.
    # Das verhindert Fehler beim anschließenden Text-basierten Datetime-Parsing.
    df['Datum_Uhrzeit'] = pd.to_datetime(
        df['datumstunde'].astype(str), 
        format='%Y%m%d%H', 
        errors='coerce'
    )

    # Spalten umbenennen (Translation Layer für das Dashboard)
    df = df.rename(columns={
        'temperatur': 'Temperatur_C',
        'windgeschwindigkeit': 'Wind_ms',
        'sonnenscheindauer_minuten': 'Sonnenschein_min',
        'luftfeuchtigkeit': 'Luftfeuchtigkeit',
        'o3': 'Ozon',
        'no2': 'NO2',
        'pm10': 'PM10',
    })

    return df  

# Daten importieren
df = load_data()

# Seitenleiste definieren
with st.sidebar:
    
    st.write("🌦️ Filter & Einstellungen")
    st.markdown("---")

    with st.spinner("Loading..."):
        time.sleep(2)
        
    # --- Custom Success Message mit Courier und 11px ---
    st.markdown(
        f"""
        <div style="background-color: rgba(46, 134, 43, 0.2); padding: 12px; border-radius: 0.5rem; border: 1px solid rgba(46, 134, 43, 0.4);">
            <span style="font-family: 'Courier New', Courier, monospace; font-size: 11px; color: #FAFAFA;">
                ✅ Daten erfolgreich geladen: {len(df)} Zeilen!
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

      # Der unsichtbare Platzhalter ---
    # Sorgt dafür, dass der letzte Inhalt nicht dauerhaft hinter dem Footer verschwindet.
    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

    # 1. Dynamisch das kleinste und größte Jahr aus den Daten ermitteln
    min_year = int(df['Datum_Uhrzeit'].dt.year.min())
    max_year = int(df['Datum_Uhrzeit'].dt.year.max())

    # 2. Den Slider erstellen
    selected_year = st.sidebar.slider(
        "Wähle ein Jahr für die Analyse:",
        min_value=min_year,
        max_value=max_year,
        value=2020  # Startwert, wenn die App geöffnet wird
    )
    
    # 3. Das DataFrame basierend auf der Auswahl filtern
    # Das .copy() verhindert die Pandas 'SettingWithCopyWarning' bei späteren Berechnungen
    df_year = df[df['Datum_Uhrzeit'].dt.year == selected_year].copy()
    
    # Kleines visuelles Feedback in der Sidebar
    st.sidebar.caption(f"📊 Datensätze im Jahr {selected_year}: {len(df_year):,}")


    # Der unsichtbare Platzhalter ---
    # Sorgt dafür, dass der letzte Inhalt nicht dauerhaft hinter dem Footer verschwindet.
    st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)

    # --- Der "Sticky" Footer mit Hintergrund ---
    st.markdown(
        """
        <style>
            .sidebar-footer {
                position: absolute; /* Bindet ihn an die Seitenleiste */
                bottom: 0;
                left: 0;
                width: 100%;
                background-color: #262730; /* Standard Streamlit Dark-Mode Seitenleisten-Farbe */
                /* WICHTIG: Padding angepasst! Oben 15px, Rechts 20px, Unten 20px, Links 20px */
                padding: 15px 20px 20px 20px; 
                text-align: left;
                font-size: 12px;
                color: #888888;
                z-index: 999; /* Zwingt den Footer in den absoluten Vordergrund */
            }
        </style>
  
        <div class="sidebar-footer">
            <hr style="margin-top: 0; margin-bottom: 10px; border-color: #444444;">
            <b>Projekt:</b> <br>Modulare Analyse von Wetter- und Luftqualitätsdaten<br>
            <b>Milestone 1:</b> Nürnberg<br>
            <b>Team:</b> Christina, Markus, Frank
        </div>
        """,
        unsafe_allow_html=True
    )




# Tabs definieren
tab1, tab2, tab3 = st.tabs(["Wetterdaten", "Luftqualität", "Klimatrends"])    

# Tab 1: Wetterdaten
with tab1:
    st.header(f"Wetterdaten für das Jahr {selected_year}")

# 1. Wir teilen den Platz horizontal in 3 Spalten auf
    col1, col2, col3 = st.columns(3)
    
    # 2. Wir nutzen df_year im RAM, um blitzschnell Aggregate zu berechnen
    avg_temp = df_year['Temperatur_C'].mean()
    max_wind = df_year['Wind_ms'].max()
    sun_hours = df_year['Sonnenschein_min'].fillna(0).sum() / 60
    
    # 3. Wir befüllen die Spalten mit den fertigen Kennzahlen
    col1.metric("Ø Temperatur", f"{avg_temp:.1f} °C")
    col2.metric("Max. Windgeschwindigkeit", f"{max_wind:.1f} m/s")
    col3.metric("Gesamte Sonnenstunden", f"{sun_hours:.0f} h")
    
    # Dataframe-Anzeige: Wir zeigen hier bewusst das gefilterte df_year an, um die Performance zu optimieren.
    st.dataframe(df, height=200, use_container_width=True)

    
    # WICHTIG: Hier übergeben wir jetzt das GEFILTERTE df_year statt df!
    st.dataframe(df_year, height=400, use_container_width=True)
    st.echo()

    # Infobox unter Grafiken
    st.markdown(
    f"""
    <div style="background-color: rgba(0, 104, 249, 0.1); padding: 10px; border-radius: 0.3rem; border: 1px solid rgba(0, 104, 249, 0.2);">
        <span style="font-family: 'Courier New', Courier, monospace; font-size: 11px; color: #FAFAFA;">
            📄 Dateipfad: "data" / "Schadstoff_Wetter.csv" <br>
            Filterung: df_year = df[df['Datum_Uhrzeit'].dt.year == selected_year].copy()
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

# Tab 2: Luftqualität
with tab2:
    st.header("Luftqualität über die Zeit")

# Tab 3: Klimatrends
with tab3:
    st.header("Klimatrends")  
    st.write("hier kommen Korrelationen rein")
    

