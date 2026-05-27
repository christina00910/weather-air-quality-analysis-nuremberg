# -*- coding: utf-8 -*-
# @Authors: Frank Hasdorf, Christina Dürrbeck, Markus Edelhoff
# @Project: Abschlussprojekt - app_aufbau
#           Abschlussklasse Dezember 2025
# @Date:   16-05-2026 15:56:50
# @Last Modified time: 2026-05-20

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
import analyse as an
import randomForest as ran
import openMeteo as op
import stPrognosis as pr
import O3

import korrelation as kor
import styling

# Globales Styling für alle matplotlib/seaborn-Charts aktivieren
styling.apply_global_style()

# ============================================================
# 00 SEITENKONFIGURATION & CACHING
# ============================================================
custom_svg = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' height='24px' viewBox='0 -960 960 960' width='24px' fill='%231f1f1f'><path d='M131.5-131.5Q120-143 120-160v-40q0-17 11.5-28.5T160-240q17 0 28.5 11.5T200-200v40q0 17-11.5 28.5T160-120q-17 0-28.5-11.5Zm160 0Q280-143 280-160v-220q0-17 11.5-28.5T320-420q17 0 28.5 11.5T360-380v220q0 17-11.5 28.5T320-120q-17 0-28.5-11.5Zm160 0Q440-143 440-160v-140q0-17 11.5-28.5T480-340q17 0 28.5 11.5T520-300v140q0 17-11.5 28.5T480-120q-17 0-28.5-11.5Zm160 0Q600-143 600-160v-200q0-17 11.5-28.5T640-400q17 0 28.5 11.5T680-360v200q0 17-11.5 28.5T640-120q-17 0-28.5-11.5Zm160 0Q760-143 760-160v-360q0-17 11.5-28.5T800-560q17 0 28.5 11.5T840-520v360q0 17-11.5 28.5T800-120q-17 0-28.5-11.5ZM560-481q-16 0-30.5-6T503-504L400-607 188-395q-12 12-28.5 11.5T131-396q-11-12-10.5-28.5T132-452l211-211q12-12 26.5-17.5T400-686q16 0 31 5.5t26 17.5l103 103 212-212q12-12 28.5-11.5T829-771q11 12 10.5 28.5T828-715L617-504q-11 11-26 17t-31 6Z'/></svg>"

st.set_page_config(
    page_title="Schadstoff/Wetter-Korrelation am Beispiel der Stadt Nürnberg",
    page_icon=custom_svg,
    layout="wide"
)

# Mapping: Anzeige-Label im Radio -> Spaltenname im DataFrame
STOFF_MAP = {
    "Ozon (O₃)": "o3",
    "Stickstoffdioxid (NO₂)": "no2",
    "Feinstaub (PM10)": "pm10",
}


def showEDAPlots (df_prepared, stoff):        
    """
    Zeigt alle EDA-Plots hochperformant in Streamlit an.
    Wichtig: Übergeben Sie hier das zentral über 'prepare_base_data' 
    vorbereitete DataFrame, nicht das rohe Original!
    """
    # 1. Jahrestrend (Läuft in Millisekunden aus dem Cache)
    fig_year = an.calcMeanYear(df_prepared, stoff)
    if fig_year: 
        st.pyplot(fig_year)
        if (stoff == "o3") :
            st.info ("CHRISTINA1")
        elif (stoff == "no2") :
            st.info ("CHRISTINA2")
        elif (stoff == "pm10") :
            st.info ("CHRISTINA3")

    # 2. Saisonales Muster (Jahrzehntvergleich)
    fig_saison = an.calcMeanSaisonYear(df_prepared, stoff)
    if fig_saison: 
        st.pyplot(fig_saison)
        if (stoff == "o3") :
            st.info ("CHRISTINA1")
        elif (stoff == "no2") :
            st.info ("CHRISTINA2")
        elif (stoff == "pm10") :
            st.info ("CHRISTINA3")
            
    # 3. Rush-Hour-Effekt (Tagesverlauf)
    fig_rush = an.rushHourEffekt(df_prepared, stoff) 
    if fig_rush: 
        st.pyplot(fig_rush)
        if (stoff == "o3") :
            st.info ("CHRISTINA1")
        elif (stoff == "no2") :
            st.info ("CHRISTINA2")
        elif (stoff == "pm10") :
            st.info ("CHRISTINA3")
            
    # 4. Inversionswetterlage
    fig_inversion = an.inversionswetter(df_prepared, stoff)
    if fig_inversion: 
        st.pyplot(fig_inversion)
        if (stoff == "o3") :
            st.info ("CHRISTINA1")
        elif (stoff == "no2") :
            st.info ("CHRISTINA2")
        elif (stoff == "pm10") :
            st.info ("CHRISTINA3")

    # 5. Jährliche LQI-Überschreitungen
    fig_exceed = an.getExceedancesPerYear(df_prepared, stoff)
    if fig_exceed: 
        st.pyplot(fig_exceed)
        if (stoff == "o3") :
            st.info ("CHRISTINA1")
        elif (stoff == "no2") :
            st.info ("CHRISTINA2")
        elif (stoff == "pm10") :
            st.info ("CHRISTINA3")

    # 6. Jahreszeit & Werktag/Wochenende (Nimmt die zwei Grafiken sauber entgegen)
    fig_season, fig_weekend = an.analyzeSeasonAndWeekend(df_prepared, stoff)
    if fig_season: 
        st.pyplot(fig_season)
        if (stoff == "o3") :
            st.info ("CHRISTINA1")
        elif (stoff == "no2") :
            st.info ("CHRISTINA2")
        elif (stoff == "pm10") :
            st.info ("CHRISTINA3")
    if fig_weekend: 
        st.pyplot(fig_weekend)
        if (stoff == "o3") :
            st.info ("CHRISTINA1")
        elif (stoff == "no2") :
            st.info ("CHRISTINA2")
        elif (stoff == "pm10") :
            st.info ("CHRISTINA3")
    return

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
        errors='coerce'
    )
    spaltenList = ['datum', 'stunde', 'temperatur', 'luftfeuchtigkeit',  'windgeschwindigkeit', 'windrichtung',  'luftdruck', 'niederschlagshoehe_mm', 'sonnenscheindauer_minuten', 'relative_luftfeuchtigkeit', 'gesamtbewoelkung', 'no2', 'o3', 'pm10', 'pm2x5']
    dfO = dfRead[spaltenList].copy()
    return dfO 

    
#######################################################
@st.fragment
def showTab2 ():
    st.header("Wetterdaten")

    # Jahres-Slider oberhalb der Metrics
    # Wert wird in st.session_state.selected_year gespiegelt -> auch in Tab 3 verfügbar
    min_year = int(dfOrginal['datum'].dt.year.min())
    max_year = int(dfOrginal['datum'].dt.year.max())

    if "selected_year" not in st.session_state:
        st.session_state.selected_year = 2023

    selected_year = st.slider(
        "Wähle ein Jahr für die Analyse:",
        min_value=min_year,
        max_value=max_year,
        value=st.session_state.selected_year,
        key="year_slider_tab2"
    )
    st.session_state.selected_year = selected_year

    # Daten filtern
    df_year = dfOrginal[dfOrginal['datum'].dt.year == selected_year].copy()

    st.subheader(f"Übersicht für das Jahr {selected_year}")

    col1, col2, col3 = st.columns(3)

    avg_temp = df_year['temperatur'].mean()
    max_wind = df_year['windgeschwindigkeit'].max()
    sun_hours = df_year['sonnenscheindauer_minuten'].fillna(0).sum() / 60

    st.markdown(
        """
        <style>
        div[data-testid="stMetricLabel"] p {
            font-size: 14px !important;
        }
        div[data-testid="stMetricValue"] {
            font-size: 24px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    col1.metric("Ø Temperatur", f"{avg_temp:.1f} °C", border=True)
    col2.metric("Max. Windgeschwindigkeit", f"{max_wind:.1f} m/s", border=True)
    col3.metric("Gesamte Sonnenstunden", f"{sun_hours:.0f} h", border=True)

    st.dataframe(df_year, height=400, use_container_width=True, hide_index=True)

    st.markdown(
        f"""
        <div style="background-color: rgba(0, 104, 249, 0.1); padding: 10px; border-radius: 0.3rem; border: 1px solid rgba(0, 104, 249, 0.2);">
            <b>Hinweis zur Datenbasis:</b> Dieser Tab nutzt die im RAM liegende gefilterte Variable <code>df_year</code> für das Jahr {selected_year}.
        </div>
        """,
        unsafe_allow_html=True
    )
    
#######################################################
@st.fragment
def showTab3 ():
    # Slider auch hier - teilt sich den Wert mit Tab 2 über st.session_state.selected_year
    min_year_t3 = int(dfOrginal['datum'].dt.year.min())
    max_year_t3 = int(dfOrginal['datum'].dt.year.max())
    selected_year_t3 = st.slider(
        "Wähle ein Jahr für die Analyse:",
        min_value=min_year_t3,
        max_value=max_year_t3,
        value=st.session_state.selected_year,
        key="year_slider_tab3"
    )
    st.session_state.selected_year = selected_year_t3

    # df_year neu auf Basis des aktuellen Slider-Werts berechnen
    df_year = dfOrginal[dfOrginal['datum'].dt.year == selected_year_t3].copy()

    st.header(f"Luftqualität & Schadstoffanalyse ({selected_year_t3})")
    st.markdown("---")

    if schadstoff_auswahl == "Übersicht aller Stoffe":
        st.subheader("Gesamtübersicht der Luftbelastung vs. WHO-Grenzwerte")
        st.write("Die Dreiecke zeigen die Abweichung zu den offiziellen WHO-Jahresgrenzwerten an (Grün = Unter dem Limit, Rot = Überschreitung).")

        c1, c2, c3, c4 = st.columns(4)

        mean_ozon  = df_year['o3'].mean()
        mean_no2   = df_year['no2'].mean()
        mean_pm10  = df_year['pm10'].mean()
        mean_pm25  = df_year['pm2x5'].mean()

        # WHO-Jahresgrenzwerte (µg/m³)
        diff_ozon = mean_ozon - 100
        diff_no2  = mean_no2 - 25
        diff_pm10 = mean_pm10 - 15
        diff_pm25 = mean_pm25 - 5

        c1.metric(
            label="Ø Ozon (Ziel: ≤100)",
            value=f"{mean_ozon:.1f} µg/m³",
            delta=f"{diff_ozon:+.1f} µg/m³ vs. WHO",
            delta_color="inverse"
        )

        c2.metric(
            label="Ø NO₂ (Ziel: ≤25)",
            value=f"{mean_no2:.1f} µg/m³",
            delta=f"{diff_no2:+.1f} µg/m³ vs. WHO",
            delta_color="inverse"
        )

        c3.metric(
            label="Ø PM10 (Ziel: ≤15)",
            value=f"{mean_pm10:.1f} µg/m³",
            delta=f"{diff_pm10:+.1f} µg/m³ vs. WHO",
            delta_color="inverse"
        )

        c4.metric(
            label="Ø PM2.5 (Ziel: ≤5)",
            value=f"{mean_pm25:.1f} µg/m³",
            delta=f"{diff_pm25:+.1f} µg/m³ vs. WHO",
            delta_color="inverse"
        )

        st.markdown("---")

    else:
        # Einzelstoff-Ansicht (O₃, NO₂ oder PM10) - gemeinsamer Block
        beschreibungen = {
            "o3": (
                "Ozon (O₃) – Detailanalyse",
                "Ozon ist ein bedingtes Reizgas, das besonders im Sommer bei hoher Einstrahlung entsteht. Weitere wissenschaftliche Beschreibung ergänzen......"
            ),
            "no2": (
                "Stickstoffdioxid (NO₂) – Analysen",
                "NO₂ entsteht primär bei Verbrennungsprozessen (z. B. Dieselmotoren)."
            ),
            "pm10": (
                "Feinstaub (PM10) – Partikelanalyse",
                "Feinstaubpartikel dringen tief in die Atemwege ein. Quellen sind Industrie, Heizungen und Abrieb."
            ),
        }
        titel, info_text = beschreibungen[stoff_spalte]
        st.subheader(titel)
        st.info(info_text)
        showEDAPlots(dfOrginal, stoff_spalte)
    
    
#######################################################
@st.fragment
def showTab4 ():
    if schadstoff_auswahl == "Übersicht aller Stoffe":
        st.header("Korrelationen zwischen Wetter und Schadstoffen – Übersicht")
        st.info("🚧 Diese Übersichtsseite wird zu einem späteren Zeitpunkt befüllt. "
                "Wählen Sie links einen einzelnen Schadstoff, um die Korrelationsanalyse zu sehen.")
    else:
        st.header(f"Korrelationen zwischen Wetter und {schadstoff_auswahl} über die Jahre")
        kor.korrelation(dfOrginal, stoff_spalte)
    
#######################################################
@st.fragment
def showTab5 ():
    if schadstoff_auswahl == "Übersicht aller Stoffe":
        st.header("Multiple Regression – Übersicht")
        st.info("🚧 Diese Übersichtsseite wird zu einem späteren Zeitpunkt befüllt. "
                "Wählen Sie links einen einzelnen Schadstoff, um die Regressionsanalyse zu sehen.")
    else:
        st.header(f"Multiple Regression: Wetter als Prädiktor für {schadstoff_auswahl}")
        kor.multipleLinearRegression(dfOrginal, stoff_spalte)
    
#######################################################
@st.fragment
def showTab6 ():
    if schadstoff_auswahl == "Übersicht aller Stoffe":
        st.header("Random Forest – Übersicht")
        st.info("🚧 Diese Übersichtsseite wird zu einem späteren Zeitpunkt befüllt. "
                "Wählen Sie links einen einzelnen Schadstoff, um das Random-Forest-Modell zu sehen.")
    else:
        st.header(f"Random Forest: Wetter als Prädiktor für {schadstoff_auswahl}")
        fig = ran.showDiagrams(dfOrginal, stoff_spalte)
#######################################################
@st.fragment
def showTab7 ():
    st.header("Vorhersage")
    models = pr.prognosis (dfOrginal)
#    O3.showO3EDAPlots ()

#######################################################
@st.fragment
def showTab8 ():
    st.header("Vorhersage")
    op.calcWithOpenMeteo (dfOrginal, stoff_spalte)

#######################################################

dfOrginal = load()

# ============================================================
# 01 SIDEBAR-KONFIGURATION
# ============================================================
with st.sidebar:
    st.write("🌦️ Filter & Einstellungen")
    st.markdown("---")

    # Globale Schadstoff-Auswahl (wirkt in Tab 3, 4, 5, 6)
    schadstoff_auswahl = st.radio(
        "Schadstoff-Auswahl:",
        ["Übersicht aller Stoffe", "Ozon (O₃)", "Stickstoffdioxid (NO₂)", "Feinstaub (PM10)"],
    )

    # Spaltenname für Tabs, die einen einzelnen Stoff brauchen
    # Fallback bei "Übersicht aller Stoffe" -> no2
    stoff_spalte = STOFF_MAP.get(schadstoff_auswahl, "no2")

    st.markdown("---")

    with st.spinner("Loading..."):
        time.sleep(2)

    st.markdown(
        f"""
        <div style="background-color: rgba(3, 149, 176, 0.1); padding: 12px; border-radius: 0.5rem; border: 1px solid rgba(1, 132, 157, 0.8);">
            <span style="font-family: 'Courier New', Courier, monospace; font-size: 11px; color: #FAFAFA;">
                ✅ Daten erfolgreich geladen: {len(dfOrginal):,} Zeilen!
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)

    # Sticky Footer
    st.markdown(
        """
        <style>
            .sidebar-footer {
                position: absolute; 
                bottom: 0;
                left: 0;
                width: 100%;
                background-color: #262730; 
                padding: 15px 20px 20px 20px; 
                text-align: left;
                font-size: 12px;
                color: #888888;
                z-index: 999; 
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

# ============================================================
# 02 TABS DEFINIEREN & SEITENSTRUKTUR
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(
    ["Startseite", "Wetterdaten", "Explorative Analyse", "Korrelationsanalyse",
     "Multiple Regression", "Random Forest", "Vorhersage", "Vorhersage Live", "📝 Technische Insights"]
)

# ------------------------------------------------------------
# TAB 1: Einleitung & Überblick
# ------------------------------------------------------------
# =========================
# TITEL & EINLEITUNG
# =========================
with tab1:
    st.title("🌍 Analyse und Vorhersage von Wetter- und Luftqualitätsdaten")

    st.markdown("""
Willkommen zu unserer interaktiven Analyse der Wetter- und Luftqualitätsdaten für die Stadt Nürnberg.

Dieses Dashboard bietet einen Überblick über die verwendeten Daten, 
die gesundheitliche Relevanz verschiedener Luftschadstoffe sowie die eingesetzten 
statistischen Verfahren und Machine-Learning-Modelle.

Die einzelnen Tabs führen durch die verschiedenen Analysebereiche – 
von der explorativen Datenanalyse über Korrelations- und Regressionsverfahren 
bis hin zu Vorhersagemodellen für Luftschadstoffkonzentrationen.
""")

    st.markdown("### 🔎 Analysebereiche")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.info("📊 Explorative Analyse")

    with col2:
        st.info("📈 Korrelationen")

    with col3:
        st.info("📉 Multiple Regression")

    with col4:
        st.info("🌲 Random Forest")

    with col5:
        st.info("🔮 Vorhersagemodelle")

    # =========================
    # PROJEKT-INFOS
    # =========================

    st.markdown("""
<div style="
    display: flex;
    justify-content: space-between;
    gap: 40px;
    margin-top: 25px;
    margin-bottom: 10px;
    padding: 20px 10px 10px 10px;
">

<div>
    <div style="font-size:16px; color:#9CA3AF;">
        👥 Projektteam
    </div>
    <div style="font-size:20px; font-weight:600; line-height:1.6;">
        Christina Dürbeck<br>
        Frank Hasdorf<br>
        Markus Edelhoff
    </div>
</div>

<div>
    <div style="font-size:16px; color:#9CA3AF;">
        📅 Projektzeitraum
    </div>
    <div style="font-size:20px; font-weight:600; line-height:1.6;">
        11.05. – 29.05.2026
    </div>
</div>

<div>
    <div style="font-size:16px; color:#9CA3AF;">
        📍 Untersuchungsregion
    </div>
    <div style="font-size:20px; font-weight:600; line-height:1.6;">
        Nürnberg
    </div>
</div>

</div>
""", unsafe_allow_html=True)

    st.header("📌 Projektüberblick")

    st.write("""
Ziel des Projekts ist die Untersuchung des Zusammenhangs zwischen meteorologischen 
Einflussfaktoren und der Luftqualität in Nürnberg. Dafür werden historische Wetter- 
und Luftschadstoffdaten zusammengeführt, aufbereitet und analysiert.

Im Fokus stehen die Luftschadstoffe Ozon (O₃), Stickstoffdioxid (NO₂) sowie 
Feinstaub (PM10 und PM2.5). Zur Auswertung werden explorative Analysen, 
Korrelationsverfahren, multiple lineare Regressionen sowie Random-Forest-Modelle eingesetzt.

Zusätzlich werden verschiedene Vorhersageansätze entwickelt, um Luftschadstoffkonzentrationen 
auf Basis meteorologischer, zeitlicher und historischer Einflussgrößen prognostizieren zu können.
""")

    st.header("🫁 Gesundheitliche Auswirkungen von Luftschadstoffen")

    st.write("""
Luftschadstoffe zählen zu den bedeutendsten umweltbedingten Gesundheitsrisiken. 
Sie können insbesondere die Atemwege und das Herz-Kreislauf-System beeinträchtigen 
und stehen mit verschiedenen gesundheitlichen Erkrankungen in Zusammenhang.
""")

    base_dir = Path(__file__).parent
    bild_pfad = base_dir / "Bilder" / "gesundheit.png"

    st.image(
        str(bild_pfad),
        width=900
    )

    st.info("""
Die Grafik zeigt, dass Luftschadstoffe mit verschiedenen gesundheitlichen Belastungen verbunden sein können.
""")

    st.header("📊 Verwendete Datenquellen")

    st.markdown("""
- **Deutscher Wetterdienst (DWD)**  
  Historische Wetterdaten der Messstation Nürnberg, Stations-ID 3668.

- **Bayerisches Landesamt für Umwelt (LfU)**  
  Historische Luftschadstoffdaten für NO₂, O₃, PM10 und PM2.5.

- **Open-Meteo API**  
  Aktuelle Wetterdaten für die Live-Vorhersage der Luftschadstoffwerte.
""")

    st.header("⚙️ Datenaufbereitung")

    st.markdown("""
Im Rahmen der Datenaufbereitung wurden die Wetter- und Luftschadstoffdaten in Python
verarbeitet und für die Analyse vorbereitet.

Dabei wurden die Daten:
- zeitlich aufeinander abgestimmt
- bereinigt und zusammengeführt
- auf fehlende Werte überprüft
- um zusätzliche zeitliche Einflussfaktoren ergänzt
""")

    with st.expander("Verwendete Wetter- und Schadstoffvariablen anzeigen"):

        variablen_df = pd.DataFrame({
            "Kategorie": [
                "Wetterdaten",
                "Wetterdaten",
                "Wetterdaten",
                "Wetterdaten",
                "Wetterdaten",
                "Wetterdaten",
                "Wetterdaten",
                "Wetterdaten",
                "Luftschadstoffe",
                "Luftschadstoffe",
                "Luftschadstoffe",
                "Luftschadstoffe"
            ],

            "Variable": [
                "Temperatur",
                "Windgeschwindigkeit",
                "Windrichtung",
                "Luftdruck",
                "Relative Luftfeuchtigkeit",
                "Niederschlagshöhe",
                "Sonnenscheindauer",
                "Gesamtbewölkung",
                "Ozon (O₃)",
                "Stickstoffdioxid (NO₂)",
                "Feinstaub PM10",
                "Feinstaub PM2.5"
            ]
        })

        st.dataframe(
            variablen_df,
            use_container_width=True,
            hide_index=True
        )

    with st.expander("Zusätzliche Zeitvariablen anzeigen"):

        zeitvariablen = pd.DataFrame({
            "Zeitvariable": [
                "Tageszeit",
                "Wochentag",
                "Monat",
                "Wochenende",
                "Hauptverkehrszeit",
                "Heizperiode",
                "Nachtstunden",
                "Silvestereffekt"
            ],
            "Beschreibung": [
                "Stunde des Tages zur Analyse typischer Tagesverläufe",
                "Unterscheidung einzelner Wochentage",
                "Erfassung saisonaler Muster",
                "Unterscheidung zwischen Werktagen und Wochenende",
                "Typische Berufsverkehrszeiten am Morgen und Abend",
                "Monate mit potenziell erhöhtem Heizverhalten",
                "Zeiten mit geringerer Sonneneinstrahlung und stabileren Luftschichten",
                "Sondereffekt rund um den Jahreswechsel"
            ]
        })

        st.dataframe(
            zeitvariablen,
            use_container_width=True,
            hide_index=True
        )

    st.header("📊 Datensatzübersicht")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Analysezeitraum", "1980 – 2024")

    with col2:
        st.metric("Messintervall", "stündlich")

    with col3:
        st.metric("PM2.5 verfügbar ab", "2008")

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric("Anzahl Datensätze", f"{len(dfOrginal):,}".replace(",", "."))

    with col5:
        st.metric("Anzahl Variablen", dfOrginal.shape[1])

    with col6:
        st.metric("Untersuchungsregion", "Nürnberg")

    st.info("""
Da PM2.5-Daten erst ab 2008 vollständig verfügbar sind, wurden alle vergleichenden Analysen 
zwischen den Luftschadstoffen (z. B. Korrelationsanalyse, Multiple Regression, 
Random Forest sowie Vorhersagemodelle) einheitlich ab dem Jahr 2008 durchgeführt.
""")

# ------------------------------------------------------------
# TAB 2: WETTERDATEN
# ------------------------------------------------------------
with tab2:
    showTab2 ()
# ============================================================
# TAB 3: EXPLORATIVE ANALYSE / LUFTQUALITÄT
# ============================================================
with tab3:
    showTab3 ()

# ============================================================
# TAB 4: KORRELATIONSANALYSE
# ============================================================
with tab4:
    showTab4 ()

# ============================================================
# TAB 5: MULTIPLE REGRESSION
# ============================================================
with tab5:
    showTab5 ()

# ============================================================
# TAB 6: RANDOM FOREST
# ============================================================
with tab6:
    showTab6 ()

# ============================================================
# TAB 7: VORHERSAGE1
# ============================================================
with tab7:
    showTab7 ()

# ============================================================
# TAB 7: VORHERSAGE2
# ============================================================
with tab8:
    showTab8 ()
# ============================================================
# TAB 8: TECHNISCHE INSIGHTS
# ============================================================
with tab9:
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
