
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
import EDAPlots as eda


# ============================================================
# Wetterdaten-Tab 
# ============================================================
@st.fragment
def showTab1 (dfOrginal, stoff_spalte):
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
    st.divider()

    st.header("🔎 Analysebereiche")

    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1.2])

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
    # PROJEKTINFOS & DATENQUELLEN
    # =========================

    st.divider()

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

    st.divider()

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

    st.divider()

    st.header("📊 Verwendete Datenquellen")

    st.markdown("""
- **Deutscher Wetterdienst (DWD)**  
  Historische Wetterdaten der Messstation Nürnberg, Stations-ID 3668.

- **Bayerisches Landesamt für Umwelt (LfU)**  
  Historische Luftschadstoffdaten für NO₂, O₃, PM10 und PM2.5.

- **Open-Meteo API**  
  Aktuelle Wetterdaten für die Live-Vorhersage der Luftschadstoffwerte.
""")

    st.divider()

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

    st.divider()

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


    # Technische Datensatzinfos einklappbar
    # Rohdaten anzeigen
    with st.expander("Rohdaten anzeigen"):
        st.dataframe(
            dfOrginal,
            height=400,
            use_container_width=True,
            hide_index=True)

    # Technische Infos anzeigen
    with st.expander("Technische Datensatzinformationen anzeigen"):
        dtypes_df = pd.DataFrame({
            "Spalte": dfOrginal.columns,
            "Datentyp": dfOrginal.dtypes.astype(str),
            "Null-Werte": dfOrginal.isna().sum().values})

        st.dataframe(
            dtypes_df,
            use_container_width=True,
            hide_index=True)

    st.info("""
    Da PM2.5-Daten erst ab 2008 vollständig verfügbar sind, wurden alle vergleichenden Analysen 
    zwischen den Luftschadstoffen (z. B. Korrelationsanalyse, Multiple Regression, 
    Random Forest sowie Vorhersagemodelle) einheitlich ab dem Jahr 2008 durchgeführt.
    
    Niederschlagsdaten stehen erst ab dem Jahr 1995 vollständig zur Verfügung. 
    Zeitliche Visualisierungen zur Niederschlagsentwicklung werden daher ab 1995 dargestellt.
    """)

@st.fragment
def showTab2 (dfOrginal, stoff_spalte):
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

# ============================================================
# Explorative Analyse-Tab
# ============================================================
@st.fragment
def showTab3 (dfOrginal, stoff_spalte):
    # Einzelstoff-Ansicht (O₃, NO₂ oder PM10) - gemeinsamer Block
    beschreibungen = {
        "o3": (
        "Ozon (O₃)",
        """
        Ozon (O₃) ist ein gasförmiger Luftschadstoff, der nicht direkt ausgestoßen wird,
        sondern sich in der Atmosphäre aus sogenannten Vorläufersubstanzen bildet.
        Dazu gehören vor allem Stickoxide (NOₓ) und flüchtige organische Verbindungen,
        die beispielsweise durch Verkehr, Industrie oder Verbrennungsprozesse entstehen.

        Besonders an warmen und sonnigen Tagen kommt es durch intensive Sonneneinstrahlung
        zu chemischen Reaktionen in der Luft, wodurch die Ozonkonzentration ansteigt.
        Deshalb treten erhöhte Ozonwerte häufig im Frühjahr und Sommer auf.

        Hohe Ozonkonzentrationen können die Atemwege reizen, die Lungenfunktion beeinträchtigen
        und insbesondere für Kinder, ältere Menschen sowie Personen mit Atemwegserkrankungen
        gesundheitsschädlich sein.
        """
        ),
        "no2": (
        "Stickstoffdioxid (NO₂)",
        """
        Stickstoffdioxid (NO₂) ist ein gasförmiger Luftschadstoff, der hauptsächlich bei
        Verbrennungsprozessen entsteht. Besonders hohe Konzentrationen treten im Straßenverkehr,
        insbesondere durch Dieselfahrzeuge, Industrieanlagen und Heizsysteme auf.

        NO₂ kann die Atemwege reizen und steht in Zusammenhang mit Atemwegserkrankungen sowie
        einer verminderten Lungenfunktion. Hohe Werte treten häufig in stark befahrenen
        Stadtgebieten auf.

        Zusätzlich spielt Stickstoffdioxid eine wichtige Rolle bei der Bildung von bodennahem
        Ozon und sekundärem Feinstaub.
        """
        ),
        "pm10": (
        "Feinstaub (PM10 & PM2.5)",
        """
        Feinstaub umfasst sehr kleine Partikel in der Luft, die unter anderem durch Verkehr,
        Industrie, Heizungen, Reifen- und Bremsabrieb sowie natürliche Quellen entstehen.

        PM10 beschreibt Partikel mit einem Durchmesser von weniger als 10 Mikrometern,
        während PM2.5 noch deutlich kleinere und feinere Partikel umfasst.
        Aufgrund ihrer geringen Größe können die Partikel tief in die Atemwege eindringen.
        Besonders PM2.5 kann sogar bis in die Lungenbläschen gelangen.

        Hohe Feinstaubkonzentrationen können die Atemwege belasten und stehen in Zusammenhang
        mit Herz-Kreislauf- sowie Atemwegserkrankungen.

        Erhöhte PM10- und PM2.5-Werte treten häufig bei trockener Witterung,
        wenig Wind oder Inversionslagen auf, da sich die Schadstoffe dann schlechter
        in der Atmosphäre verteilen können.
        """
        ),
    }

    titel, info_text = beschreibungen[stoff_spalte]
    st.subheader(titel)
    st.markdown(info_text)
    eda.showEDAPlots(dfOrginal, stoff_spalte)
    #if stoff_spalte == "o3":
        #O3.showO3EDAPlots()
   
# ============================================================
# Korrelationsanalyse-Tab
# ============================================================
@st.fragment
def showTab4(dfOrginal, stoff_spalte):
    st.header("Korrelationenzwischen Wetter und Luftschadstoffen")

    st.markdown("""
    Die Korrelationsanalyse zeigt, ob und wie stark Wetterbedingungen mit der Luftqualität zusammenhängen. 
    Sie hilft dabei zu erkennen, welche Wettervariablen einen positiven oder negativen Einfluss auf die Luftschadstoffe Ozon (O₃), Stickstoffdioxid (NO₂) und Feinstaub (PM10/PM2.5) haben. 
    So lässt sich beispielsweise analysieren, ob hohe Temperaturen, Sonnenschein oder Windgeschwindigkeiten bestimmte Schadstoffkonzentrationen begünstigen oder reduzieren.
    """)

    st.divider()

    st.write("")
    kor.korrelation(dfOrginal, stoff_spalte)
    st.write("")

    with st.expander("Interpretation der Korrelationsanalyse"):

        st.markdown("""
        • Ozon (O₃) zeigt eine positive Korrelation mit Temperatur (0.63) und Sonnenscheindauer (0.39).  
        → Hohe Ozonwerte treten häufiger bei warmem und sonnigem Wetter auf.

        • NO₂ korreliert negativ mit Ozon (-0.46).  
        → Hohe NO₂-Werte gehen oft mit niedrigeren Ozonwerten einher.

        • PM10 und PM2.5 weisen eine starke positive Korrelation auf (0.73).  
        → Beide Feinstaubarten treten häufig gemeinsam auf.

        • Höhere Windgeschwindigkeiten hängen mit niedrigeren Luftschadstoffwerten zusammen.  
        → Wind verbessert die Durchmischung der Luft und reduziert Schadstoffkonzentrationen.

        • Die relative Luftfeuchtigkeit korreliert stark negativ mit Ozon (-0.72).  
        → Trockene und sonnige Wetterlagen fördern höhere Ozonkonzentrationen.

        • Niederschlag zeigt insgesamt nur schwache Zusammenhänge mit den Luftschadstoffwerten.
        """)
    
# ============================================================
# Multiple lineare Regression-Tab
# ============================================================
@st.fragment
def showTab5 (dfOrginal, stoff_spalte, schadstoff_auswahl):
    if schadstoff_auswahl == "Übersicht aller Stoffe":
        st.header("Multiple Regression – Übersicht")
        st.info("Bitte wählen Sie links einen einzelnen Schadstoff aus, um die multiple lineare Regression anzuzeigen.")
    else:
        st.header(f"Multiple lineare Regression: Wetter als Prädiktor für {schadstoff_auswahl}")
        st.markdown("""
        Die multiple lineare Regression wurde verwendet, um den Einfluss verschiedener Wettervariablen 
        auf die Luftschadstoffkonzentrationen statistisch zu untersuchen.
        Dabei wird geprüft, ob zwischen Wetterfaktoren und Schadstoffwerten signifikante Zusammenhänge bestehen. 

        Ein p-Wert kleiner als 0.05 deutet auf einen statistisch signifikanten Zusammenhang hin.
        Die Regression bestätigt damit die bereits in der Korrelationsanalyse erkennbaren Zusammenhänge 
        zwischen Wetterbedingungen und Luftschadstoffen.

        Da die Variablen unterschiedliche Einheiten besitzen (z. B. °C, km/h oder Millimeter), 
        sind die Koeffizienten jedoch nur eingeschränkt direkt miteinander vergleichbar.

        Das R² zeigt zusätzlich, wie gut die Wettervariablen die Schadstoffkonzentrationen insgesamt 
        erklären können. Das vergleichsweise niedrige R², vorallem beim Stickstoffdioxid (NO₂) und Feinstaub (PM10/PM2.5), deutet darauf hin, dass neben dem Wetter auch 
        weitere Faktoren wie Verkehr, Tageszeit, Industrie, Heizungen oder saisonale Effekte einen Einfluss 
        auf die Luftschadstoffbelastung haben.
        """)

        st.write("")

        st.divider()

        kor.multipleLinearRegression(dfOrginal, stoff_spalte)

# ============================================================
# Random Forest-Tab
# ============================================================
@st.fragment
def showTab6(dfOrginal, stoff_spalte, schadstoff_auswahl):

    if schadstoff_auswahl == "Übersicht aller Stoffe":
        st.header("Random Forest – Übersicht")
        st.info("Bitte wählen Sie links einen einzelnen Schadstoff aus, um das Random-Forest-Modell anzuzeigen.")
    else:

        st.header(f"Random Forest: Wetter als Prädiktor für {schadstoff_auswahl}")

        st.markdown("""
        Der Random-Forest-Algorithmus wurde verwendet, um den Einfluss von Wetter- und Zeitfaktoren 
        auf die Schadstoffkonzentrationen zu analysieren. Die Feature Importance zeigt dabei, 
        welche Variablen besonders relevant für die Vorhersage der jeweiligen Luftschadstoffe sind.

        Im Gegensatz zur multiplen linearen Regression können beim Random Forest auch Variablen mit 
        unterschiedlichen Einheiten (z. B. °C, km/h oder Millimeter) besser gemeinsam verarbeitet und verglichen werden.

        Die Ergebnisse zeigen insgesamt, dass sowohl Wetterbedingungen als auch Verkehrs- und Tageszeitmuster 
        relevant für die Entstehung und Verteilung der Luftschadstoffe sind.
        """)

        st.write("")

        st.divider()

        fig = ran.showDiagrams(dfOrginal, stoff_spalte)

# ============================================================
# Ablationsstudie-Tab
# ============================================================
@st.fragment
def showTab7 (dfOrginal, stoff_spalte, schadstoff_auswahl):
    st.header("Ablationsstudie: Bedeutung der Vergangenheit")
    models = pr.prognosis (dfOrginal)

# ============================================================
# Live-Vorhersage-Tab
# ============================================================
@st.fragment
def showTab8(dfOrginal, stoff_spalte, schadstoff_auswahl):
    if schadstoff_auswahl == "Übersicht aller Stoffe":
        st.header("Vorhersage Live")
        st.info("Bitte wählen Sie links einen einzelnen Schadstoff aus, um die Live-Vorhersage anzuzeigen.")
    else:
        st.header(f"Vorhersage Live: {schadstoff_auswahl}")  
        st.markdown("""
        Die Live-Luftschadstoffvorhersage basiert auf einem erweiterten Random-Forest-Modell, 
        das historische Luftqualitätsdaten mit aktuellen Wetterdaten der Open-Meteo API kombiniert. 
        Neben klassischen Wettervariablen wurden zusätzlich zeitliche Einflussfaktoren wie Rush Hour, 
        Wochenende, Nachtstunden, Heizperiode oder Silvester integriert, damit das Modell typische Muster 
        der Luftschadstoffbelastung besser erkennen kann.

        Die besten Vorhersageergebnisse erzielt das Modell aktuell für Ozon (O₃), was sich anhand des höheren R²-Werts erkennen lässt. 
        Die Vorhersage von Stickstoffdioxid (NO₂) sowie Feinstaub (PM10 / PM2.5) ist hingegen schwieriger, 
        da diese Schadstoffe zusätzlich stark durch Verkehr, Industrie, Heizungen oder kurzfristige Ereignisse beeinflusst werden.

        Für eine noch präzisere Live-Vorhersage könnten künftig weitere Datenquellen wie aktuelle Verkehrsdaten, 
        historische Schadstoffwerte der letzten Stunden oder zusätzliche Umwelteinflüsse ergänzt werden.
        """)
        op.calcWithOpenMeteo(dfOrginal, stoff_spalte)


# ============================================================
# Fazit-Tab
# ============================================================
@st.fragment
def showTab9 (dfOrginal, stoff_spalte):
    st.header("Fazit und Ausblick")

    st.markdown("""
    Die Analyse zeigt, dass Wetterbedingungen einen messbaren Einfluss auf die Luftqualität in Nürnberg haben. 
    Besonders deutlich werden die Zusammenhänge bei Ozon, während Stickstoffdioxid und Feinstaub zusätzlich stark 
    durch weitere Einflussfaktoren geprägt werden.
    """)

    st.divider()

    st.subheader("Zentrale Erkenntnisse")

    st.markdown("""
    #### 🌞 Ozon (O₃)
    Steigt vor allem bei hohen Temperaturen und intensiver Sonneneinstrahlung an.  
    Die Analyse zeigt, dass Ozon stark durch meteorologische Bedingungen beeinflusst wird. Aufgrund steigender Temperaturen und zunehmender Hitzeperioden könnten Ozonbelastungen künftig weiter an Bedeutung gewinnen. 
    
    Zusätzlich besteht eine enge Wechselwirkung zwischen Ozon und Stickstoffdioxid. Obwohl sinkende NO₂-Werte grundsätzlich positiv sind, können sie unter bestimmten Bedingungen dazu führen, dass Ozon langsamer abgebaut wird und dadurch höhere Ozonkonzentrationen entstehen.

    ### 🚗 Stickstoffdioxid (NO₂)
    Zeigt langfristig eher sinkende Werte.  
    Dies kann unter anderem auf technische Entwicklungen, strengere Emissionsvorgaben und Veränderungen im Verkehrssektor hindeuten.

    ### 🌫️ Feinstaub (PM10 und PM2.5)
    Weist ebenfalls rückläufige Tendenzen auf.  
    Gleichzeitig zeigen die Analysen, dass Feinstaub besonders bei Inversionslagen, geringer Luftdurchmischung und verkehrsnahen Situationen erhöht auftreten kann.

    ### ❤️ Gesundheitliche Bedeutung
    Trotz teilweise sinkender Schadstoffwerte bleibt Luftverschmutzung weiterhin ein relevantes Gesundheitsthema. Besonders erhöhte Ozonwerte können die Atemwege belasten und stehen in Zusammenhang mit gesundheitlichen Risiken für empfindliche Personengruppen.

    ### 🌍 Regionale Unterschiede
    Die Analyse verdeutlicht außerdem, dass Luftqualität regional sehr unterschiedlich ausfallen kann. Während in Nürnberg teilweise rückläufige Entwicklungen erkennbar sind, können Luftschadstoffbelastungen in anderen Regionen oder Großstädten deutlich stärker ausfallen.

    ### 📊 Grenzen der Wetterdaten
    Wetterdaten allein erklären die Luftqualität nur teilweise. Die multiple Regression zeigt, dass meteorologische Variablen zwar signifikante Zusammenhänge aufweisen, die Erklärungskraft jedoch begrenzt bleibt.

    ### ⏱️ Zeitliche Muster
    Zeitliche Variablen verbessern die Vorhersage deutlich. Durch Faktoren wie Stunde, Monat, Wochenende oder Rush Hour können typische Tages- und Jahresmuster besser abgebildet werden.
    """)

    st.divider()

    st.subheader("Ausblick")

    st.markdown("""
    * Das Projekt zeigt, dass datenbasierte Verfahren wie Korrelationsanalysen, multiple lineare Regression und Random-Forest-Modelle geeignet sind, Zusammenhänge zwischen Wetter und Luftqualität sichtbar zu machen.
                
    * Die Analyse bezieht sich ausschließlich auf die Region Nürnberg. Für zukünftige Untersuchungen könnten weitere Städte, Regionen oder internationale Datensätze integriert werden, um Unterschiede zwischen verschiedenen Umwelt- und Klimabedingungen besser vergleichen zu können.
                
    * Für präzisere Vorhersagen sollten zusätzlich weitere Einflussfaktoren wie Verkehrsdaten, Industrieemissionen, Heizverhalten oder historische Schadstoffwerte ergänzt werden. Dadurch könnten insbesondere die Vorhersagen von Stickstoffdioxid und Feinstaub weiter verbessert werden.
                
    * Insgesamt verdeutlicht das Projekt, dass Luftqualität ein komplexes Zusammenspiel aus Wetter, menschlichen Aktivitäten und zeitlichen Mustern darstellt und weiterhin eine wichtige Rolle für Umwelt und Gesundheit spielt.
    """)


    with st.expander("💡 Mögliche Erweiterungen für zukünftige Analysen"):

        st.markdown("""
        - Einbindung zusätzlicher Verkehrsdaten zur Verbesserung der Vorhersage von Stickstoffdioxid (NO₂)
        - Berücksichtigung weiterer Emissionsquellen wie Industrieanlagen, Heizsysteme oder Baustellen
        - Integration historischer Schadstoffmesswerte zur Verbesserung kurzfristiger Vorhersagen
        - Erweiterung der Analyse auf weitere Städte und Regionen zur Untersuchung regionaler Unterschiede
        - Vergleich unterschiedlicher Messstationen innerhalb Nürnbergs oder Bayerns
        - Berücksichtigung detaillierter meteorologischer Einflussfaktoren wie Inversionslagen, Luftaustausch oder Windströmungen
        - Einsatz weiterer Machine-Learning-Verfahren wie Gradient Boosting oder neuronaler Netze
        - Entwicklung eines automatisierten Warnsystems für erhöhte Luftschadstoffbelastungen
        - Verknüpfung von Luftqualitäts- und Gesundheitsdaten zur Untersuchung möglicher gesundheitlicher Auswirkungen
        """)

    st.markdown("<br>", unsafe_allow_html=True)

    st.success("""
    Zusammenfassend zeigt das Dashboard: Wetter- und Zeitfaktoren liefern wichtige Hinweise auf die Entwicklung der Luftqualität. 
    Für präzisere Vorhersagen müssen jedoch zusätzliche Emissionsquellen und lokale Einflussfaktoren berücksichtigt werden.
    """)
