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

# 2. erster visueller Test
st.title("Luftqualität & Wetter Dashboard")
st.write("Grundgerüst ist fertig")

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

df = load_data()

# Kurzer Test-Output im Browser
# st.success zeigt eine grüne Erfolgsmeldung an, ist wie st.write, nur eben grün hinterlegt
st.success(f"Daten erfolgreich geladen: {len(df)} Zeilen!") 
st.dataframe(df.head()) # Zeigt die ersten 5 Zeilen interaktiv an

