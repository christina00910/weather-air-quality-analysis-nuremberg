# -*- coding: utf-8 -*-
# @Author: Frank Hasdorf
# @Date:   12-05-2026 16:38:09
# @Last Modified by:   Frank Hasdorf
# @Last Modified time: 15-05-2026 13:08:55

# -*- coding: utf-8 -*-
# @Author: Frank Hasdorf
# @Date:   12-05-2026 16:38:09
# @Last Modified by:   Frank Hasdorf
# @Last Modified time: 15-05-2026 13:00:00

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go  # NEU: Für das Tachometer in Tab 3
import numpy as np

st.set_page_config(page_title="Luft & Wetter Bayern", page_icon="🌬️", layout="wide")

# --- 1. DATEN LADEN & MERGEN ---
@st.cache_data
def load_and_merge_data():
    # --- NEU: Robuste Pfadkonstruktion ---
    # 1. Ermittle das Verzeichnis, in dem dieses Skript (main2.py) liegt
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Konstruiere den absoluten Pfad zum 'data' Ordner
    # os.path.join geht einen Ordner nach oben ("..") und dann in "data"
    data_dir = os.path.join(base_dir, "data")
    
    # 3. Definiere die genauen Dateipfade
    wetter_pfad = os.path.join(data_dir, "wetterdaten_analyse.csv")
    luft_pfad = os.path.join(data_dir, "luftdaten_nurnberg.csv")
    
    # 1. Wetter laden (mit dem neuen, robusten Pfad!)
    df_wetter = pd.read_csv(wetter_pfad)
    
    # 2. Spaltennamen an das Dashboard anpassen (Mapping)
    rename_logic = {
        'Datum': 'Datum_Uhrzeit',
        'Temperatur': 'Temperatur_C',
        'Windgeschwindigkeit': 'Wind_kmh',
        'Sonnenscheindauer_Minuten': 'Sonnenschein_min',
        'Relative_Luftfeuchtigkeit': 'rhum'
    }
    df_wetter = df_wetter.rename(columns=rename_logic)
    
    # 3. Das spezielle Datumsformat (YYYYMMDDHH) konvertieren
    df_wetter['Datum_Uhrzeit'] = pd.to_datetime(df_wetter['Datum_Uhrzeit'], format='%Y%m%d%H')
    
    # 4. Luftdaten laden & Mergen
    try:
        # Auch hier den robusten Pfad verwenden
        df_luft = pd.read_csv(luft_pfad)
        df_luft['Datum_Uhrzeit'] = pd.to_datetime(df_luft['Datum_Uhrzeit'])
        
        # Inner Join: Verknüpft Wetter & Luftdaten exakt nach Stunde
        df_merged = pd.merge(df_wetter, df_luft, on='Datum_Uhrzeit', how='inner')
        st.sidebar.success("✅ Wetter & echte Luftdaten erfolgreich verknüpft!")
        
    except FileNotFoundError:
        st.sidebar.warning("⚠️ Echte UBA-Daten nicht gefunden. Nutze simulierte Daten für das Layout.")
        df_merged = df_wetter.copy()
        
        # Fallback-Simulation
        df_merged['Ozon'] = np.maximum(0, df_merged['Temperatur_C'] * 2.5 + (df_merged['Sonnenschein_min'].fillna(0) / 10) + np.random.normal(0, 10, len(df_merged)))
        df_merged['NO2'] = np.maximum(0, 60 - df_merged['Temperatur_C'] - (df_merged['Wind_kmh'] * 0.5) + np.random.normal(0, 5, len(df_merged)))

    return df_merged
    
    # 2. Spaltennamen an das Dashboard anpassen (Mapping)
    rename_logic = {
        'Datum': 'Datum_Uhrzeit',
        'Temperatur': 'Temperatur_C',
        'Windgeschwindigkeit': 'Wind_kmh',
        'Sonnenscheindauer_Minuten': 'Sonnenschein_min',
        'Relative_Luftfeuchtigkeit': 'rhum'
    }
    df_wetter = df_wetter.rename(columns=rename_logic)
    
    # 3. Das spezielle Datumsformat (YYYYMMDDHH) konvertieren
    df_wetter['Datum_Uhrzeit'] = pd.to_datetime(df_wetter['Datum_Uhrzeit'], format='%Y%m%d%H')
    
    # 4.