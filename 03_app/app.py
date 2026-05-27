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
import styling

import analysePM as an
import randomForest as ran
import openMeteo as op
import stPrognosis as pr
import O3
import korrelation as kor
import silvester as sil

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
        st.pyplot(fig_year, use_container_width=False)
        if (stoff == "o3") :
            st.caption("""
            Die Grafik zeigt einen langfristigen Anstieg der durchschnittlichen Ozonkonzentration seit den 1980er-Jahren. Besonders in den letzten Jahren sind erhöhte Ozonwerte erkennbar, was auf den Einfluss steigender Temperaturen und intensiver Sonneneinstrahlung hinweisen kann.
            """)
        elif (stoff == "no2") :
            st.caption("""
        Die Grafik zeigt einen langfristigen Rückgang der durchschnittlichen NO₂-Konzentrationen seit den 1990er-Jahren. Besonders in den letzten Jahren sind deutlich sinkende Werte erkennbar, was unter anderem auf strengere Emissionsgrenzwerte und technologische Entwicklungen im Verkehrssektor hinweisen könnte. Der starke Rückgang im Jahr 1993 stellt hingegen einen auffälligen Ausreißer innerhalb der Zeitreihe dar und könnte auf eine daten- oder messtechnische Besonderheit hinweisen.
        """)   
        elif (stoff == "pm10") :
            st.caption("""
            Die Grafik zeigt einen langfristigen Rückgang der PM10-Konzentrationen seit den 1980er-Jahren. Besonders ab den 2000er-Jahren sind deutlich sinkende Werte erkennbar, was auf strengere Umweltauflagen, technische Entwicklungen im Verkehrs- und Industriesektor sowie verbesserte Luftreinhaltemaßnahmen hinweisen könnte. Auch die PM2.5-Werte zeigen seit Beginn der verfügbaren Messreihe ab 2008 eine insgesamt rückläufige Entwicklung.
            """)

    st.markdown(
        """
        <div style="margin-top: 50px;"></div>
        """,
        unsafe_allow_html=True
    )

    # 2. Saisonales Muster (Jahrzehntvergleich)
    fig_saison = an.calcMeanSaisonYear(df_prepared, stoff)
    if fig_saison: 
        st.pyplot(fig_saison, use_container_width=False)
        if (stoff == "o3") :
            st.caption("""
            Die Grafik zeigt ein deutlich saisonales Ozonmuster mit erhöhten Konzentrationen in den Frühjahrs- und Sommermonaten. Besonders in den neueren Jahrzehnten treten höhere Ozonwerte auf, was auf den Einfluss steigender Temperaturen und intensiver Sonneneinstrahlung hinweisen kann.
            """)
        elif (stoff == "no2") :
            st.caption("""
            Die Grafik zeigt insgesamt sinkende NO₂-Konzentrationen über die Jahrzehnte hinweg. Gleichzeitig sind besonders in den Wintermonaten höhere Werte erkennbar, was auf verstärkte Emissionen durch Verkehr und Heizungen sowie ungünstigere meteorologische Bedingungen für den Schadstoffabbau hinweisen kann.
            """)
        elif (stoff == "pm10") :
            st.caption("""
            Die Grafik zeigt deutliche saisonale Unterschiede der PM10-Konzentrationen im Jahrzehntvergleich. Während in den 1980er- und 2000er-Jahren teilweise höhere Belastungen in einzelnen Herbst- und Wintermonaten auftreten, liegen die Werte im Jahr 2020 insgesamt deutlich niedriger. Dies deutet langfristig auf eine Verbesserung der Luftqualität sowie auf den Einfluss verschärfter Umwelt- und Emissionsmaßnahmen hin.
            """)

        st.markdown(
        """
        <div style="margin-top: 50px;"></div>
        """,
        unsafe_allow_html=True
        )

    # 3. Rush-Hour-Effekt (Tagesverlauf)
    fig_rush = an.rushHourEffekt(df_prepared, stoff) 
    if fig_rush: 
        st.pyplot(fig_rush, use_container_width=False)
        if (stoff == "o3") :
            st.caption("""
            Die Grafik zeigt einen deutlichen Tagesverlauf der Ozonkonzentration mit niedrigen Werten in den frühen Morgenstunden und einem Maximum am Nachmittag. Dies deutet auf den Einfluss photochemischer Prozesse sowie die Wechselwirkung zwischen Sonneneinstrahlung und Stickoxiden bei der Ozonbildung hin.
            """)
        elif (stoff == "no2") :
            st.caption("""
            Die Grafik zeigt deutliche NO₂-Spitzen während der morgendlichen und abendlichen Hauptverkehrszeiten. Besonders in den Abendstunden steigen die Konzentrationen stark an, was auf erhöhte Verkehrsemissionen sowie eine geringere Verdünnung und Durchmischung der Schadstoffe in der Luft hinweist.
            """)
        elif (stoff == "pm10") :
            st.caption("""
            Die Grafik zeigt einen typischen Tagesverlauf der PM10- und PM2.5-Konzentrationen mit erhöhten Werten in den frühen Morgen- und Abendstunden. Besonders bei PM10 sind Spitzen während der Hauptverkehrszeiten erkennbar, was auf den Einfluss des Straßenverkehrs und weiterer menschlicher Aktivitäten hinweist. In den Nachmittagsstunden sinken die Konzentrationen dagegen deutlich ab.
            """)

        st.markdown(
        """
        <div style="margin-top: 50px;"></div>
        """,
        unsafe_allow_html=True
        )

    # 4. Inversionswetterlage
    fig_inversion = an.inversionswetter(df_prepared, stoff)
    if fig_inversion: 
        st.pyplot(fig_inversion, use_container_width=False)
        if (stoff == "o3") :
            st.caption("""
            Die Grafik zeigt deutlich niedrigere Ozonkonzentrationen während Inversionslagen mit windstillen und wolkenlosen Wetterbedingungen. Dies weist darauf hin, dass Ozon in bodennahen Smogsituationen durch Stickoxide verstärkt abgebaut wird.
            """)
        elif (stoff == "no2") :
            st.caption("""
            Die niedrigeren NO₂-Konzentrationen bei wolkenlosen und windstillen Wetterlagen deuten auf photochemische Umwandlungsprozesse hin. Unter intensiver Sonneneinstrahlung wird Stickstoffdioxid verstärkt in Ozon umgewandelt, wodurch die gemessenen NO₂-Werte trotz stabiler Wetterlage sinken können.
            """)
        elif (stoff == "pm10") :
            st.caption("""
            Die Grafik zeigt, dass die PM10-Konzentrationen während Inversionslagen deutlich höher ausfallen als bei normalen Wetterbedingungen. Besonders bei windstillem und wolkenlosem Wetter können sich Feinstaubpartikel stärker in Bodennähe ansammeln, da die Luft schlechter durchmischt wird. Dadurch steigt die Belastung durch Feinstaub spürbar an.
            """)

        st.markdown(
        """
        <div style="margin-top: 50px;"></div>
        """,
        unsafe_allow_html=True
        )

    # 5. Jährliche LQI-Überschreitungen
    fig_exceed = an.getExceedancesPerYear(df_prepared, stoff)
    if fig_exceed: 
        st.pyplot(fig_exceed, use_container_width=False)
        if (stoff == "o3") :
            st.caption("""
            Die Anzahl der Stunden mit mindestens mäßiger Ozonbelastung ist seit den 1980er-Jahren deutlich angestiegen. Besonders in den letzten Jahren treten erhöhte Ozonkonzentrationen häufiger auf, was auf veränderte klimatische und meteorologische Bedingungen hinweist.
            """)
        elif (stoff == "no2") :
            st.caption("""
            Die Anzahl der Stunden mit mindestens mäßiger NO₂-Belastung steigt zunächst bis in die frühen 2000er-Jahre an. Anschließend zeigt sich ein deutlicher Rückgang, besonders seit etwa 2010. Dies deutet auf eine langfristige Verbesserung der Luftqualität hin, die unter anderem mit strengeren Emissionsvorgaben und moderneren Fahrzeug- und Heiztechnologien zusammenhängen könnte.
            """)
        elif (stoff == "pm10") :
            st.caption("""
            Die Grafik zeigt einen langfristigen Rückgang der Stunden mit mindestens mäßiger Feinstaubbelastung für PM10 und PM2.5. Besonders seit den 2000er-Jahren treten belastete Stunden deutlich seltener auf, was auf Verbesserungen der Luftqualität sowie auf strengere Emissions- und Umweltmaßnahmen hinweisen kann. Trotz einzelner Schwankungen ist insgesamt ein klarer positiver Trend erkennbar.
            """)

        st.markdown(
        """
        <div style="margin-top: 50px;"></div>
        """,
        unsafe_allow_html=True
        )

    # 6. Jahreszeit & Werktag/Wochenende (Nimmt die zwei Grafiken sauber entgegen)
    fig_season, fig_weekend = an.analyzeSeasonAndWeekend(df_prepared, stoff)
    if fig_season: 
        st.pyplot(fig_season, use_container_width=False)
        if (stoff == "o3") :
            st.caption("""
            Die höchsten Ozonkonzentrationen treten im Sommer und Frühjahr auf, während im Herbst und Winter deutlich niedrigere Werte gemessen werden. Dies verdeutlicht den starken Einfluss von Sonneneinstrahlung und höheren Temperaturen auf die Ozonbildung.
            """)
        elif (stoff == "no2") :
            st.caption("""
                Die NO₂-Werte sind im Sommer am niedrigsten und im Winter am höchsten. Ursache dafür sind im Sommer stärkere Sonneneinstrahlung, intensivere photochemische Prozesse  und eine bessere Durchmischung der Luft, während sich Schadstoffe im Winter durch geringere Sonneneinstrahlung, stabilere Luftschichten und zusätzliche Emissionen aus dem Heizungs- und Verkehrssektor höhere Konzentrationen anreichern können.
                """)
        elif (stoff == "pm10") :
            st.caption("""
            Die Grafik zeigt höhere PM10- und PM2.5-Werte in den Herbst- und Wintermonaten, während die niedrigsten Konzentrationen im Sommer auftreten. Besonders im Winter kann sich Feinstaub durch Heizungen, Verkehr und schlechtere Luftdurchmischung stärker in Bodennähe ansammeln. Im Sommer sorgen günstigere Wetterbedingungen dagegen meist für niedrigere Belastungen.
            """)

        st.markdown(
        """
        <div style="margin-top: 50px;"></div>
        """,
        unsafe_allow_html=True
        )

    if fig_weekend: 
        st.pyplot(fig_weekend, use_container_width=False)
        if (stoff == "o3") :
            st.caption("""
            Die Grafik zeigt höhere durchschnittliche Ozonkonzentrationen an Wochenenden im Vergleich zu Werktagen. Dies könnte auf geringere Stickoxid-Emissionen durch den Straßenverkehr und damit einen verminderten Ozonabbau zurückzuführen sein.
            """)
        elif (stoff == "no2") :
            st.caption("""
            Die NO₂-Konzentrationen sind an Werktagen höher als am Wochenende. Dies deutet auf den Einfluss des Berufs- und Pendlerverkehrs hin, da Stickstoffdioxid hauptsächlich durch Verbrennungsprozesse im Straßenverkehr entsteht.
            """)
        elif (stoff == "pm10") :
            st.caption("""
            Die Grafik zeigt höhere PM10- und PM2.5-Konzentrationen an Werktagen im Vergleich zum Wochenende. Dies deutet darauf hin, dass vor allem Verkehr und andere menschliche Aktivitäten während der Arbeitswoche zur erhöhten Feinstaubbelastung beitragen. Am Wochenende fallen die Konzentrationen dagegen insgesamt etwas niedriger aus.
            """)

    if (stoff =="pm10") :
        fig_silvester = sil.analyseSilvesterTime (df_prepared, stoff)
        if fig_silvester is not None:
            st.pyplot(fig_silvester, use_container_width=False)
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
def showTab2():
    st.header("Wetterdaten")

    st.markdown("""
    Dieser Bereich bietet einen Überblick über die meteorologischen Eingangsdaten des Projekts. 
    Die Wetterdaten bilden die Grundlage für die Analyse der Luftqualität sowie für die späteren 
    Vorhersagemodelle.
    """)

    # Jahres-Slider
    min_year = int(dfOrginal["datum"].dt.year.min())
    max_year = int(dfOrginal["datum"].dt.year.max())

    if "selected_year" not in st.session_state:
        st.session_state.selected_year = 2023

    selected_year = st.slider(
        "Wähle ein Jahr für die Jahresübersicht:",
        min_value=min_year,
        max_value=max_year,
        value=st.session_state.selected_year,
        key="year_slider_tab2"
    )

    st.session_state.selected_year = selected_year

    # Daten für ausgewähltes Jahr filtern
    df_year = dfOrginal[dfOrginal["datum"].dt.year == selected_year].copy()

    st.subheader(f"Wetterübersicht für das Jahr {selected_year}")

    # Kennzahlen für ausgewähltes Jahr
    avg_temp = df_year["temperatur"].mean()
    avg_wind = df_year["windgeschwindigkeit"].mean()
    avg_humidity = df_year["relative_luftfeuchtigkeit"].mean()
    sum_rain = df_year["niederschlagshoehe_mm"].fillna(0).sum()
    sun_hours = df_year["sonnenscheindauer_minuten"].fillna(0).sum() / 60
    avg_clouds = df_year["gesamtbewoelkung"].mean()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Ø Temperatur", f"{avg_temp:.1f} °C", border=True)

    with col2:
        st.metric("Ø Windgeschwindigkeit", f"{avg_wind:.1f} m/s", border=True)

    with col3:
        st.metric("Ø relative Luftfeuchtigkeit", f"{avg_humidity:.1f} %", border=True)

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric("Niederschlag gesamt", f"{sum_rain:.0f} mm", border=True)

    with col5:
        st.metric("Sonnenstunden gesamt", f"{sun_hours:.0f} h", border=True)

    with col6:
        st.metric("Ø Gesamtbewölkung", f"{avg_clouds:.1f}", border=True)

    st.markdown("---")

    # Langfristige Entwicklung einzelner Wettervariablen
    st.subheader("Langfristige Entwicklung der Wettervariablen")

    st.markdown("""
    Die folgende Grafik zeigt die langfristige Entwicklung einer ausgewählten Wettervariable 
    über den gesamten verfügbaren Zeitraum. Dadurch lassen sich Trends und Veränderungen 
    über die Jahre hinweg besser einordnen.
    """)

    wetter_variablen = {
        "Temperatur": {
            "spalte": "temperatur",
            "aggregation": "mean",
            "titel": "Jahresmitteltemperatur",
            "y_label": "Temperatur [°C]",
            "plot_typ": "line"
        },
        "Windgeschwindigkeit": {
            "spalte": "windgeschwindigkeit",
            "aggregation": "mean",
            "titel": "Durchschnittliche Windgeschwindigkeit",
            "y_label": "Windgeschwindigkeit [m/s]",
            "plot_typ": "line"
        },
        "Relative Luftfeuchtigkeit": {
            "spalte": "relative_luftfeuchtigkeit",
            "aggregation": "mean",
            "titel": "Durchschnittliche relative Luftfeuchtigkeit",
            "y_label": "Relative Luftfeuchtigkeit [%]",
            "plot_typ": "line"
        },
        "Niederschlagshöhe": {
            "spalte": "niederschlagshoehe_mm",
            "aggregation": "sum",
            "titel": "Jährliche Niederschlagshöhe",
            "y_label": "Niederschlag [mm]",
            "plot_typ": "bar"
        },
        "Sonnenscheindauer": {
            "spalte": "sonnenscheindauer_minuten",
            "aggregation": "sum",
            "titel": "Jährliche Sonnenscheindauer",
            "y_label": "Sonnenscheindauer [Minuten]",
            "plot_typ": "bar"
        },
        "Gesamtbewölkung": {
            "spalte": "gesamtbewoelkung",
            "aggregation": "mean",
            "titel": "Durchschnittliche Gesamtbewölkung",
            "y_label": "Gesamtbewölkung [Achtel]",
            "plot_typ": "line"
        }
    }

    auswahl = st.selectbox(
        "Wähle eine Wettervariable für den langfristigen Verlauf:",
        options=list(wetter_variablen.keys()),
        key="weather_trend_select"
    )

    einstellung = wetter_variablen[auswahl]
    spalte = einstellung["spalte"]
    aggregation = einstellung["aggregation"]
    titel = einstellung["titel"]
    y_label = einstellung["y_label"]
    plot_typ = einstellung["plot_typ"]

    df_trend = dfOrginal.copy()
    df_trend["jahr"] = df_trend["datum"].dt.year

    if aggregation == "sum":
        trend = (
            df_trend
            .groupby("jahr")[spalte]
            .sum(min_count=1)
            .reset_index()
        )
    else:
        trend = (
            df_trend
            .groupby("jahr")[spalte]
            .mean()
            .reset_index()
        )

    trend = trend.dropna(subset=[spalte])

    start_jahr = int(trend["jahr"].min())
    end_jahr = int(trend["jahr"].max())

    if plot_typ == "bar":
        fig_trend = px.bar(
            trend,
            x="jahr",
            y=spalte,
            title=f"{titel} {start_jahr}–{end_jahr}",
            labels={
                "jahr": "Jahr",
                spalte: y_label
            }
        )
    else:
        fig_trend = px.line(
            trend,
            x="jahr",
            y=spalte,
            markers=True,
            title=f"{titel} {start_jahr}–{end_jahr}",
            labels={
                "jahr": "Jahr",
                spalte: y_label
            }
        )

        fig_trend.update_traces(
            line=dict(width=3),
            marker=dict(size=6)
        )

    fig_trend.update_layout(
        template="plotly_dark",
        height=520,
        title=dict(
            font=dict(size=22),
            x=0.02,
            xanchor="left"
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=14),
        xaxis=dict(
            title="Jahr",
            showgrid=True,
            gridcolor="rgba(255,255,255,0.12)",
            zeroline=False
        ),
        yaxis=dict(
            title=y_label,
            showgrid=True,
            gridcolor="rgba(255,255,255,0.12)",
            zeroline=False
        ),
        margin=dict(l=40, r=30, t=80, b=50),
        hovermode="x unified"
    )

    fig_trend.update_xaxes(
        title_font=dict(size=20),
        tickfont=dict(size=14),
        tickmode="linear",
        dtick=5
    )

    fig_trend.update_yaxes(
        title_font=dict(size=20),
        tickfont=dict(size=14)
    )

    if plot_typ == "bar":
        fig_trend.update_traces(
            marker_line_width=0,
            opacity=0.85
    )

    st.plotly_chart(fig_trend, use_container_width=True)

    st.caption("""
    Hinweis: Für Temperatur, Windgeschwindigkeit, relative Luftfeuchtigkeit und Gesamtbewölkung 
    werden Jahresmittelwerte dargestellt. Niederschlag und Sonnenscheindauer werden als Jahressummen ausgewiesen.
    """)

    # Rohdaten einklappbar
    with st.expander("Rohdaten anzeigen"):
        st.dataframe(
            df_year,
            height=400,
            use_container_width=True,
            hide_index=True
        )

    # Technische Datensatzinfos einklappbar
    with st.expander("Technische Datensatzinformationen anzeigen"):
        dtypes_df = pd.DataFrame({
            "Spalte": df_year.dtypes.index,
            "Datentyp": df_year.dtypes.values.astype(str),
            "Fehlende Werte": df_year.isna().sum().values
        })

        st.dataframe(
            dtypes_df,
            use_container_width=True,
            hide_index=True
        )

#######################################################
@st.fragment
def showTab3 ():
    if schadstoff_auswahl == "Übersicht aller Stoffe":
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
        if (stoff_spalte == "o3") :
            O3.showO3EDAPlots ()
   
#######################################################
@st.fragment
def showTab4 ():
    st.header("Korrelationen zwischen Wetter und Schadstoffen")
    kor.korrelation(dfOrginal, stoff_spalte)
    
#######################################################
@st.fragment
def showTab5 ():
    if schadstoff_auswahl == "Übersicht aller Stoffe":
        st.header("Multiple Regression – Übersicht")
        st.info("Wählen Sie links einen einzelnen Schadstoff, um das entsprechende Regression zu sehen.")
    else:
        st.header(f"Multiple Regression: Wetter als Prädiktor für {schadstoff_auswahl}")
        kor.multipleLinearRegression(dfOrginal, stoff_spalte)
    
#######################################################
@st.fragment
def showTab6 ():
    if schadstoff_auswahl == "Übersicht aller Stoffe":
        st.header("Random Forest – Übersicht")
        st.info("Wählen Sie links einen einzelnen Schadstoff, um das entsprechende Random-Forest-Modell zu sehen.")
    else:
        st.header(f"Random Forest: Wetter als Prädiktor für {schadstoff_auswahl}")
        fig = ran.showDiagrams(dfOrginal, stoff_spalte)
#######################################################
@st.fragment
def showTab7 ():
    st.header("Vorhersage")
    models = pr.prognosis (dfOrginal)

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
    border-right: none !important;
}

/* TAB TEXT */
button[data-baseweb="tab"] p {
    font-size: 15px !important;
    font-weight: 600 !important;

    margin: 0 !important;
    text-align: center !important;

    line-height: 1.2 !important;
}

/* AKTIVER TAB */
button[data-baseweb="tab"][aria-selected="true"] p {
    color: #00B5E2 !important;
}

/* HOVER */
button[data-baseweb="tab"]:hover {
    background-color: rgba(255,255,255,0.025) !important;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# 02 TABS DEFINIEREN & SEITENSTRUKTUR
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(
    ["Startseite", "Wetterdaten", "Explorative Analyse", "Korrelationsanalyse",
     "Multiple Regression", "Random Forest", "Vorhersage", "Vorhersage Live", "Technische Insights"]
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

    st.markdown(
        "<div style='margin-top: 50px;'></div>",
        unsafe_allow_html=True
    )

    st.header("🔎 Analysebereiche")

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

    st.markdown(
        "<div style='margin-top: 50px;'></div>",
        unsafe_allow_html=True
    )

    st.header("📋 Projektinfos")

    st.markdown("""
<div style="
    display: flex;
    justify-content: flex-start;
    gap: 80px;
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

    st.markdown(
        "<div style='margin-top: 30px;'></div>",
        unsafe_allow_html=True
    )

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

    st.markdown(
        "<div style='margin-top: 30px;'></div>",
        unsafe_allow_html=True
    )

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

    st.caption("""
    Die Grafik zeigt, dass Luftschadstoffe mit verschiedenen gesundheitlichen Belastungen verbunden sein können.
    """)

    st.markdown(
        "<div style='margin-top: 30px;'></div>",
        unsafe_allow_html=True
    )

    st.header("📊 Verwendete Datenquellen")

    st.markdown("""
- **Deutscher Wetterdienst (DWD)**  
  Historische Wetterdaten der Messstation Nürnberg, Stations-ID 3668.

- **Bayerisches Landesamt für Umwelt (LfU)**  
  Historische Luftschadstoffdaten für NO₂, O₃, PM10 und PM2.5.

- **Open-Meteo API**  
  Aktuelle Wetterdaten für die Live-Vorhersage der Luftschadstoffwerte.
""")

    st.markdown(
        "<div style='margin-top: 30px;'></div>",
        unsafe_allow_html=True
    )

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

    st.markdown(
        "<div style='margin-top: 30px;'></div>",
        unsafe_allow_html=True
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
    
    Niederschlagsdaten stehen erst ab dem Jahr 1995 vollständig zur Verfügung. 
    Zeitliche Visualisierungen zur Niederschlagsentwicklung werden daher ab 1995 dargestellt.
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
