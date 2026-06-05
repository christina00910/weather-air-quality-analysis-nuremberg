# -*- coding: utf-8 -*-
# @Authors: Christina Dürrbeck, Markus Edelhoff
# @Project: Abschlussprojekt DSI - app_aufbau
# @Date:    11.05.2026 bis 29.05.2026

import streamlit as st
import pandas as pd
import os
from pathlib import Path 
import plotly.express as px
import plotly.graph_objects as go
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import seaborn as sns
import styling

import analysePM as an
import randomForest as ran
import openMeteo as op
import stPrognosis as pr
import O3
import korrelation as kor
import silvester as sil
import mytabs as t


# Globales Styling für alle matplotlib/seaborn-Charts aktivieren
styling.apply_global_style()

# ============================================================
# 00 SEITENKONFIGURATION & CACHING
# ============================================================
custom_svg = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' height='24px' viewBox='0 -960 960 960' width='24px' fill='%231f1f1f'><path d='M131.5-131.5Q120-143 120-160v-40q0-17 11.5-28.5T160-240q17 0 28.5 11.5T200-200v40q0 17-11.5 28.5T160-120q-17 0-28.5-11.5Zm160 0Q280-143 280-160v-220q0-17 11.5-28.5T320-420q17 0 28.5 11.5T360-380v220q0 17-11.5 28.5T320-120q-17 0-28.5-11.5Zm160 0Q440-143 440-160v-140q0-17 11.5-28.5T480-340q17 0 28.5 11.5T520-300v140q0 17-11.5 28.5T480-120q-17 0-28.5-11.5Zm160 0Q600-143 600-160v-200q0-17 11.5-28.5T640-400q17 0 28.5 11.5T680-360v200q0 17-11.5 28.5T640-120q-17 0-28.5-11.5Zm160 0Q760-143 760-160v-360q0-17 11.5-28.5T800-560q17 0 28.5 11.5T840-520v360q0 17-11.5 28.5T800-120q-17 0-28.5-11.5ZM560-481q-16 0-30.5-6T503-504L400-607 188-395q-12 12-28.5 11.5T131-396q-11-12-10.5-28.5T132-452l211-211q12-12 26.5-17.5T400-686q16 0 31 5.5t26 17.5l103 103 212-212q12-12 28.5-11.5T829-771q11 12 10.5 28.5T828-715L617-504q-11 11-26 17t-31 6Z'/></svg>"

st.set_page_config(
    page_title="Schadstoff/Wetter-Korrelation am Beispiel der Stadt Nürnberg",
    page_icon=custom_svg,
    layout="wide")

# Mapping: Anzeige-Label im Radio -> Spaltenname im DataFrame
STOFF_MAP = {
    "Ozon (O₃)": "o3",
    "Stickstoffdioxid (NO₂)": "no2",
    "Feinstaub (PM10 & PM2.5)": "pm10",
}



# ============================================================
# Datensatz laden und vorbereiten (wird im gesamten Projekt verwendet)
# ============================================================
@st.cache_data
def load ():
    """
    Lädt die kombinierten Wetter- und Schadstoffdaten aus der CSV-Datei.
    """
    base_dir = Path(__file__).parent
    data_pfad = base_dir / 'data' / 'Schadstoff_Wetter.csv'

    dfRead = pd.read_csv(data_pfad)

    dfRead['datum'] = pd.to_datetime(dfRead['datum'])
    
    dfRead ['datumstunde'] = pd.to_datetime(
        dfRead ['datumstunde'].astype(str), 
        format='%Y%m%d%H', 
        errors='coerce')
    
    spaltenList = ['datum', 'stunde', 'temperatur', 'luftfeuchtigkeit',  'windgeschwindigkeit', 'windrichtung',  'luftdruck', 'niederschlagshoehe_mm', 'sonnenscheindauer_minuten', 'relative_luftfeuchtigkeit', 'gesamtbewoelkung', 'no2', 'o3', 'pm10', 'pm2x5']
    dfO = dfRead[spaltenList].copy()
    return dfO 

# ============================================================
# Laden der Daten
# ============================================================
dfOrginal = load()

# ============================================================
# SIDEBAR-KONFIGURATION
# ============================================================
with st.sidebar:
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] > div {
        padding-top: 1.2rem !important;}
    
    .sidebar-item {
    margin-bottom: 16px;}
                
    .sidebar-title {
        font-size: 25px;
        font-weight: 800;
        margin-bottom: 8px;}

    .sidebar-section-title {
        font-size: 18px;
        font-weight: 800;
        margin-bottom: 4px;}

    .sidebar-divider {
        margin: 14px 0 14px 0;
        border-top: 1px solid rgba(255,255,255,0.16);}

    div[role="radiogroup"] label {
        padding: 0px 0 !important;
        margin: 0px 0 !important;}

    div[role="radiogroup"] p {
        font-size: 17px !important;
        line-height: 1.2 !important;
        font-weight: 600 !important;}

    .sidebar-text {
        font-size: 14px;
        line-height: 1.45;}

    .sidebar-text b {
        font-size: 15px;}

    .sidebar-gap {
        height: 10px;}

    .sidebar-data-box {
        background-color: rgba(3, 149, 176, 0.1);
        padding: 9px 11px;
        border-radius: 0.5rem;
        border: 1px solid rgba(1, 132, 157, 0.8);
        font-family: 'Courier New', Courier, monospace;
        font-size: 14px;
        color: #FAFAFA;
        line-height: 1.35;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='sidebar-title'>🌦️ Filter</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-section-title'>Schadstoff-Auswahl:</div>", unsafe_allow_html=True)

    schadstoff_auswahl = st.radio(
        "",
        ["Ozon (O₃)", "Stickstoffdioxid (NO₂)", "Feinstaub (PM10 & PM2.5)"],
        label_visibility="collapsed")

    stoff_spalte = STOFF_MAP.get(schadstoff_auswahl, "no2")

    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="sidebar-data-box">
            ✅ Daten erfolgreich geladen:<br>
            {len(dfOrginal):,} Zeilen
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

    st.markdown("""
<div class="sidebar-text">

<div class="sidebar-item">
<b>Projekt:</b><br>
Analyse und Vorhersage von Wetter- und Luftqualitätsdaten
</div>

<div class="sidebar-item">
<b>Region:</b><br>
Nürnberg
</div>

<div class="sidebar-item">
<b>Projektzeitraum:</b><br>
11.05.2026 – 29.05.2026
</div>

<div class="sidebar-item">
<b>Projektteam:</b><br>
Christina Dürbeck<br>
Markus Edelhoff                
</div>

</div>
""", unsafe_allow_html=True)

# ============================================================
# TAB-DESIGN ANPASSEN
# ============================================================

st.markdown("""
<style>

/* TAB LEISTE */
.stTabs [data-baseweb="tab-list"] {
    gap: 0px;
}

/* EINZELNE TABS */
button[data-baseweb="tab"] {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    min-height: 54px !important;

    /* WICHTIG */
    padding: 0 12px !important;

    background-color: transparent !important;

    border: none !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;

    transition: all 0.2s ease-in-out;
}

/* LETZTE LINIE WEG */
button[data-baseweb="tab"]:last-child {
    border-right: none !important;}

/* TAB TEXT */
button[data-baseweb="tab"] p {
    font-size: 15px !important;
    font-weight: 600 !important;

    margin: 0 !important;
    text-align: center !important;

    line-height: 1.2 !important;}

/* AKTIVER TAB */
button[data-baseweb="tab"][aria-selected="true"] p {
    color: #00B5E2 !important;}

/* HOVER */
button[data-baseweb="tab"]:hover {
    background-color: rgba(255,255,255,0.025) !important;}

</style>
""", unsafe_allow_html=True)

# ============================================================
# 02 TABS DEFINIEREN & SEITENSTRUKTUR
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs(
    ["Startseite", "Wetterdaten", "Explorative Analyse", "Korrelationsanalyse",
     "Multiple Regression", "Random Forest", "Vorhersage Live", "Vorhersage", "Fazit", "Technische Insights"])

# ------------------------------------------------------------
# TAB 1: Einleitung & Überblick
# ------------------------------------------------------------
# =========================
# TITEL & EINLEITUNG
# =========================
with tab1:
    t.showTab1 (dfOrginal, stoff_spalte)
# ------------------------------------------------------------
# TAB 2: WETTERDATEN
# ------------------------------------------------------------
with tab2:
    t.showTab2 (dfOrginal, stoff_spalte)
# ============================================================
# TAB 3: EXPLORATIVE ANALYSE / LUFTQUALITÄT
# ============================================================
with tab3:
    t.showTab3 (dfOrginal, stoff_spalte)
# ============================================================
# TAB 4: KORRELATIONSANALYSE
# ============================================================
with tab4:
    t.showTab4 (dfOrginal, stoff_spalte)
# ============================================================
# TAB 5: MULTIPLE REGRESSION
# ============================================================
with tab5:
    t.showTab5 (dfOrginal, stoff_spalte, schadstoff_auswahl)
# ============================================================
# TAB 6: RANDOM FOREST
# ============================================================
with tab6:
    t.showTab6 (dfOrginal, stoff_spalte, schadstoff_auswahl)
# ============================================================
# TAB 7: VORHERSAGE1
# ============================================================
with tab7:
    t.showTab8 (dfOrginal, stoff_spalte, schadstoff_auswahl)
# ============================================================
# TAB 8: VORHERSAGE2
# ============================================================
with tab8:
    t.showTab7 (dfOrginal, stoff_spalte, schadstoff_auswahl)
# ============================================================
# TAB 9: FAZIT
# ============================================================
with tab9:
    t.showTab9 (dfOrginal, stoff_spalte)
# ============================================================
# TAB 10: TECHNISCHE INSIGHTS
# ============================================================
with tab10:
    st.header("Technische Insights")

    def render_tech_tab():
        skript_ordner = Path(__file__).parent
        css_datei = skript_ordner / "tech_tab.css"
        html_datei = skript_ordner / "tech_tab_content.html"  # JETZT KORREKT
        try:
            # 1. CSS laden und rendern
            css_inhalt = css_datei.read_text(encoding="utf-8")
            st.markdown(f"<style>{css_inhalt}</style>", unsafe_allow_html=True)
    
            # 2. HTML-Content laden und rendern
            html_inhalt = html_datei.read_text(encoding="utf-8")
            st.html(html_inhalt)  # st.html rendert reines HTML sauber
        except FileNotFoundError:
              st.error(f"Die Datei '{css_datei.name}' wurde nicht gefunden.")

    render_tech_tab()
