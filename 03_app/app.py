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

import analyse as a
import randomForest as r
import korrelation as k
# ============================================================
# 00 SEITENKONFIGURATION & CACHING
# ============================================================
custom_svg = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' height='24px' viewBox='0 -960 960 960' width='24px' fill='%231f1f1f'><path d='M131.5-131.5Q120-143 120-160v-40q0-17 11.5-28.5T160-240q17 0 28.5 11.5T200-200v40q0 17-11.5 28.5T160-120q-17 0-28.5-11.5Zm160 0Q280-143 280-160v-220q0-17 11.5-28.5T320-420q17 0 28.5 11.5T360-380v220q0 17-11.5 28.5T320-120q-17 0-28.5-11.5Zm160 0Q440-143 440-160v-140q0-17 11.5-28.5T480-340q17 0 28.5 11.5T520-300v140q0 17-11.5 28.5T480-120q-17 0-28.5-11.5Zm160 0Q600-143 600-160v-200q0-17 11.5-28.5T640-400q17 0 28.5 11.5T680-360v200q0 17-11.5 28.5T640-120q-17 0-28.5-11.5Zm160 0Q760-143 760-160v-360q0-17 11.5-28.5T800-560q17 0 28.5 11.5T840-520v360q0 17-11.5 28.5T800-120q-17 0-28.5-11.5ZM560-481q-16 0-30.5-6T503-504L400-607 188-395q-12 12-28.5 11.5T131-396q-11-12-10.5-28.5T132-452l211-211q12-12 26.5-17.5T400-686q16 0 31 5.5t26 17.5l103 103 212-212q12-12 28.5-11.5T829-771q11 12 10.5 28.5T828-715L617-504q-11 11-26 17t-31 6Z'/></svg>"

st.set_page_config(
    page_title="Schadstoff/Wetter-Korrelation am Beispiel der Stadt Nürnberg",
    page_icon=custom_svg,
    layout="wide"
)

def showEDAPlots (dfOrginal, stoff)  :        
    fig = a.calcMeanYear (dfOrginal, stoff)
    st.pyplot(fig)

    fig = a.calcMeanSaisonYear (dfOrginal, stoff)
    st.pyplot(fig)

    fig = a.rushHourEffekt (dfOrginal, stoff) 
    st.pyplot(fig)
        
    fig = a.inversionswetter (dfOrginal, stoff)
    st.pyplot(fig)

    fig = a.getExceedancesPerYear (dfOrginal, stoff)
    st.pyplot(fig)

    fig_season, fig_weekend = a.analyzeSeasonAndWeekend (dfOrginal, stoff)
    st.pyplot(fig_season)
    st.pyplot(fig_weekend)
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

dfOrginal  = load ()

# ============================================================
# 01 SIDEBAR-KONFIGURATION
# ============================================================
with st.sidebar:
    st.write("🌦️ Filter & Einstellungen")
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

    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

    min_year = int(dfOrginal['datum'].dt.year.min())
    max_year = int(dfOrginal['datum'].dt.year.max())

    selected_year = st.sidebar.slider(
        "Wähle ein Jahr für die Analyse:",
        min_value=min_year,
        max_value=max_year,
        value=2023 
    )
  
    df_year = dfOrginal[dfOrginal['datum'].dt.year == selected_year].copy()

    st.sidebar.caption(f"📊 Datensätze im Jahr {selected_year}: {len(df_year):,}")
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
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Startseite/Projektüberblick", "Explorative Analyse", "Korrelationsanalyse", "Multiple Regression", "Random Forest", "Vorhersage", "📝 Technische Insights"])    

# ------------------------------------------------------------
# TAB 1: WETTERDATEN
# ------------------------------------------------------------
with tab1:
    st.header(f"Wetterdaten für das Jahr {selected_year}")
    
    col1, col2, col3 = st.columns(3)
    
    avg_temp = df_year['temperatur'].mean()
    max_wind = df_year['windgeschwindigkeit'].max()
    sun_hours = df_year['sonnenscheindauer_minuten'].fillna(0).sum() / 60
    
    # KORREKTUR: CSS wurde in den tab1-Block eingerückt
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

    # KORREKTUR: Metrics wurden in den tab1-Block eingerückt
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

# ============================================================
# TAB 2: LUFTQUALITÄT
# ============================================================
with tab2:
    st.header(f"Luftqualität & Schadstoffanalyse ({selected_year})")

    schadstoff_auswahl = st.radio(
        "Spezifische Schadstoff-Detailansicht:",
        ["Übersicht aller Stoffe", "Ozon (O₃)", "Stickstoffdioxid (NO₂)", "Feinstaub (PM10)"],
        horizontal=True 
    )
    
    st.markdown("---")

    # KORREKTUR: Gesamte if-elif Logik wurde sauber unter "with tab2" eingerückt
    if schadstoff_auswahl == "Übersicht aller Stoffe":
        st.subheader("Gesamtübersicht der Luftbelastung vs. WHO-Grenzwerte")
        st.write("Die Dreiecke zeigen die Abweichung zu den offiziellen WHO-Jahresgrenzwerten an (Grün = Unter dem Limit, Rot = Überschreitung).")
        
        c1, c2, c3 = st.columns(3)
        
        mean_ozon = df_year['o3'].mean()
        mean_no2  = df_year['no2'].mean()
        mean_pm10 = df_year['pm10'].mean()
        
        
        diff_ozon = mean_ozon - 100
        diff_no2  = mean_no2 - 25
        diff_pm10 = mean_pm10 - 15
        
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
        
        st.markdown("---")
        # KORREKTUR: Doppelten if-Zweig zusammengeführt
        st.info("Hier kommt später irgendein kombinierter Chart für alle Schadstoffe hin.")

    elif schadstoff_auswahl == "Ozon (O₃)":

        stoff = 'o3'
        st.subheader("Ozon (O₃) – Detailanalyse")
        st.info("Ozon ist ein bedingtes Reizgas, das besonders im Sommer bei hoher Einstrahlung entsteht. Weitere wissenschaftliche Beschreibung ergänzen......")
        #showEDAPlots (dfOrginal, stoff)
        
        st.info("Chart 1: Ozon_Paradoxon: Wie Ozon trotz Hitze und Sonne im Stadtgebiet niedriger sein kann als auf dem Land")
        # ==============================================================================================================
        # Chart Titrationseffekt Rush-Hour vs. Wochenende (3 Tage) - Ozon-Paradoxon
        # 1. Zeitfenster: Sonntag und Montag aus der Hitzewelle 2018
        # ==========================================
        tage = {
            '2018-07-24': 'Dienstag, 24.07.2018',
            '2018-08-19': 'Sonntag, 19.08.2018'
        }

        # ==========================================
        # 2. Nürnberg (Stadt) - Stundenwerte laden
        # ==========================================
        df_stadt = pd.read_csv('data/Schadstoff_Wetter.csv')
        df_stadt['timestamp'] = pd.to_datetime(df_stadt['datum']) + pd.to_timedelta(df_stadt['stunde'] - 1, unit='h')

        # Alle nötigen Spalten extrahieren (inkl. Sonnenscheindauer)
        df_stadt = df_stadt[['timestamp', 'o3', 'no2', 'sonnenscheindauer_minuten']].copy()
        df_stadt.rename(columns={'o3': 'o3_stadt', 'no2': 'no2_stadt'}, inplace=True)

        # Sonnenscheindauer (Minuten/h) in Prozent umrechnen für die Darstellung
        df_stadt['sonne_prozent'] = df_stadt['sonnenscheindauer_minuten'] / 60 * 100

        # ==========================================
        # 3. Tiefenbach (Land) - aus vorbereiteter Parquet
        # ==========================================
        df_land = pd.read_parquet('data/o3_stundenwerte_2018_station_tiefenbach.parquet')

        # ==========================================
        # 4. Merge und Plotting
        # ==========================================
        df_merged = pd.merge(df_stadt, df_land, on='timestamp', how='inner')
        df_merged.set_index('timestamp', inplace=True)
        df_merged.sort_index(inplace=True)

        # Subplots: zwei Tage nebeneinander, geteilte Y-Achse für Schadstoffe
        fig, axes = plt.subplots(1, 2, figsize=(18, 8), sharey=True)

        for ax, (tag, label) in zip(axes, tage.items()):
            # Daten für diesen Tag filtern
            mask = (df_merged.index >= tag) & (df_merged.index <= tag + ' 23:59:59')
            df_tag = df_merged.loc[mask]
            
            if df_tag.empty:
                ax.text(0.5, 0.5, f'Keine Daten für {label}', ha='center', va='center', transform=ax.transAxes)
                continue
            
            # --- Sonnenscheindauer als Hintergrundfläche (zweite Y-Achse) ---
            ax2 = ax.twinx()
            ax2.fill_between(df_tag.index, 0, df_tag['sonne_prozent'],
                            color='#ffb000', alpha=0.20, zorder=0, label='Sonnenschein (% der Stunde)')
            ax2.set_ylim(0, 100)
            ax2.set_ylabel('Sonnenscheindauer (% der Stunde)', fontsize=11, color='#cc8800')
            ax2.tick_params(axis='y', colors='#cc8800')
            
            # --- Schadstoff-Linien (vordere Y-Achse) ---
            ax.plot(df_tag.index, df_tag['o3_land'], label='Ozon (O3) Land - Tiefenbach',
                    color='#2ca02c', linewidth=3, zorder=3)
            ax.plot(df_tag.index, df_tag['o3_stadt'], label='Ozon (O3) Stadt - Nürnberg',
                    color='#7f7f7f', linewidth=2.5, zorder=3)
            ax.plot(df_tag.index, df_tag['no2_stadt'], label='Stickstoffdioxid (NO2) Stadt - Nürnberg',
                    color='#d62728', linestyle='--', linewidth=2, zorder=3)
            
            # --- Berufsverkehr-Zonen nur am Werktag ---
            is_werktag = pd.to_datetime(tag).weekday() < 5
            if is_werktag:
                day = pd.to_datetime(tag)
                ax.axvspan(day + pd.Timedelta(hours=6, minutes=30),
                        day + pd.Timedelta(hours=9, minutes=30),
                        color='gray', alpha=0.20, zorder=1)
                ax.axvspan(day + pd.Timedelta(hours=15, minutes=30),
                        day + pd.Timedelta(hours=18, minutes=30),
                        color='gray', alpha=0.20, zorder=1)
            
            # Achsen-Formatierung
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=3))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.set_xlabel(f'Uhrzeit am {label}', fontsize=12)
            ax.set_ylim(0, 170)
            ax.grid(True, linestyle=':', alpha=0.6, zorder=0)
            ax.set_title(label, fontsize=13, fontweight='bold', pad=10)

        # Y-Label nur einmal links
        axes[0].set_ylabel('Konzentration (µg/m³)', fontsize=12)

        # Gemeinsame Legende unten
        handles, labels = axes[0].get_legend_handles_labels()
        handles.append(mpatches.Patch(color='#ffb000', alpha=0.20, label='Sonnenschein (% der Stunde)'))
        labels.append('Sonnenschein (% der Stunde)')
        handles.append(mpatches.Patch(color='gray', alpha=0.20, label='Berufsverkehr (nur Werktag)'))
        labels.append('Berufsverkehr (nur Werktag)')

        fig.legend(handles=handles, labels=labels, loc='lower center',
                bbox_to_anchor=(0.5, -0.02), ncol=5, frameon=False, fontsize=11)

        # Übergeordneter Titel
        fig.suptitle('Chart #2:Ozon-Photochemie: Sonntag vs. Werktag (August 2018)\n'
                    'Wie Berufsverkehr und Sonneneinstrahlung den O3/NO2-Tagesgang prägen',
                    fontsize=16, fontweight='bold', y=1.00)

        fig.tight_layout(rect=[0, 0.04, 1, 0.97])
        st.pyplot(fig)

        # ============================================================
        # Kennzahlen + Erklärung zum Chart
        # ============================================================
        
        # --- Kennzahlen-Tabelle direkt unter dem Chart ---
        kennzahlen = pd.DataFrame({
            'Kennzahl': ['Sonnenscheindauer', 'Temperatur (max)', 'NO₂ (max)', 'O₃ Stadt (max)', 'O₃ Land (max)'],
            'Di, 24.07.2018': ['822 Min', '30,1 °C', '117 µg/m³', '130 µg/m³', '130 µg/m³'],
            'So, 19.08.2018': ['774 Min', '30,5 °C', '65 µg/m³', '129 µg/m³', '151 µg/m³'],
        })
        st.dataframe(kennzahlen, hide_index=True, use_container_width=True)
        
        # --- Ausführliche Erklärung im Expander ---
        with st.expander("📊 Was zeigt dieser Vergleich?", expanded=False):
            st.markdown("""
            **Die Idee: Ein natürliches Experiment**
            
            Beide Tage hatten **fast identisches Wetter** – Sonnenscheindauer und
            Temperatur unterscheiden sich nur minimal. Damit ist die Photochemie
            als Treiber „kontrolliert", und der Hauptunterschied zwischen den
            Tagen ist der **Berufsverkehr**.
            
            **Was man im Chart sieht:**
            
            - 🌅 **Morgens am Werktag** (graue Zone): Der Berufsverkehr drückt NO₂
              hoch, gleichzeitig bleibt das Stadt-Ozon unterdrückt – das ist der
              **Titrations-Effekt** (NO + O₃ → NO₂ + O₂).
            - ☀️ **Mittags** zerlegt die UV-Strahlung das NO₂ wieder, neues Ozon
              entsteht – Stadt- und Land-Ozon nähern sich an.
            - 🌆 **Abendspitze** am Sonntag (~21 Uhr): Auch ohne Pendlerverkehr
              gibt es einen NO₂-Peak (Freizeitverkehr, Heimkommen).
            - 🌿 **Tiefenbach (Land)** bleibt konstant bei ~120 µg/m³ – fernab von
              NO₂-Quellen wird das Ozon nicht „weggefressen".
            
            **Methodischer Hinweis:** Der direkte Werktag-Sonntag-Vergleich bei
            gleichem Wetter ist eine einfache Form eines *Matched-Sample-Designs*
            – damit lässt sich der Verkehrseffekt isolieren, ohne ein komplexes
            Regressionsmodell zu rechnen.
            """)


                   
    elif schadstoff_auswahl == "Stickstoffdioxid (NO₂)":
        stoff = 'no2'
        st.subheader("Stickstoffdioxid (NO₂) – Analysen")
        st.write("NO₂ entsteht primär bei Verbrennungsprozessen (z. B. Dieselmotoren).")
        showEDAPlots (dfOrginal, stoff)

    elif schadstoff_auswahl == "Feinstaub (PM10)":
        stoff = 'pm10'
        st.subheader("Feinstaub (PM10) – Partikelanalyse")
        st.write("Feinstaubpartikel dringen tief in die Atemwege ein. Quellen sind Industrie, Heizungen und Abrieb.")
        st.info("Hier platzieren wir die Feinstaub-Statistiken.")
        showEDAPlots (dfOrginal, stoff)

# ============================================================
# TAB 3: KORRELATIONSANALYSE
# ============================================================
with tab3:
    st.header("Korrelationen zwischen Wetter und Schadstoffen über die Jahre")
    k.korrelation (dfOrginal, "no2")


# ============================================================
# TAB 4: MULTIPLE REGRESSION
# ============================================================
with tab4:
    st.header("Multiple Regression: Wetter als Prädiktor für Schadstoffbelastung")
    k.multipleLinearRegression (dfOrginal, "no2")

# ============================================================
# TAB 5: RANDOM FOREST
# ============================================================
with tab5:
    st.header("Random Forest: Wetter als Prädiktor für Schadstoffbelastung")
    fig = r.showDiagrams (dfOrginal, "no2")

# ============================================================
# TAB 4: VORHERSAGE
# ============================================================
with tab6:
    st.header("Vorhersage")
    st.write("Lorem Ipsum")
    st.info("Lorem Ipsum")

# ============================================================
# TAB 4: TECHNISCHE INSIGHTS
# ============================================================
with tab7:
    st.header("Technische Insights")
    
    def render_tech_tab():
        # CSS laden und injizieren
        css = Path("tech_tab.css").read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    
        # HTML-Content laden und rendern
        html = Path("tech_tab_content.html").read_text(encoding="utf-8")
        st.html(html)   # st.html (Streamlit ≥ 1.33) rendert reines HTML sauber
    
    render_tech_tab()
