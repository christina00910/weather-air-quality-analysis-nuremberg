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
    "Feinstaub (PM10 & PM2.5)": "pm10",
}

def showEDAPlots (df_prepared, stoff):        
    """
    Zeigt alle EDA-Plots hochperformant in Streamlit an.
    Wichtig: Übergeben Sie hier das zentral über 'prepare_base_data' 
    vorbereitete DataFrame, nicht das rohe Original!
    """

    st.divider()
    
# 1. Jahrestrend (Läuft in Millisekunden aus dem Cache)
    fig_year = an.calcMeanYear(df_prepared, stoff)

    if fig_year:

        # Grafik kleiner und kompakter anzeigen
        fig_year.set_size_inches(10, 5.5)

        # Einheitliche Schriftgrößen
        TITLE_SIZE = 19
        LABEL_SIZE = 12
        TICK_SIZE = 10

        # Achsen der bestehenden Grafik holen
        ax = fig_year.axes[0]

        # Titel anpassen
        ax.set_title(
            f"Jahresmittelwert Trend für {stoff.upper()}",
            fontsize=TITLE_SIZE,
            fontweight="bold",
            color="white",
            pad=15)

        # Achsenbeschriftungen anpassen
        ax.set_xlabel(
            "Jahr",
            fontsize=LABEL_SIZE,
            fontweight="bold")

        ax.set_ylabel(
            "Mittlere Konzentration [µg/m³]",
            fontsize=LABEL_SIZE,
            fontweight="bold")

        # Zahlen auf den Achsen
        ax.tick_params(
            axis='both',
            labelsize=TICK_SIZE)

        # Grafik anzeigen
        st.pyplot(fig_year, use_container_width=False)

        # Beschreibung unter der Grafik
        if (stoff == "o3") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt einen langfristigen Anstieg der durchschnittlichen Ozonkonzentration seit den 1980er-Jahren. Besonders in den letzten Jahren sind erhöhte Ozonwerte erkennbar, was auf den Einfluss steigender Temperaturen und intensiver Sonneneinstrahlung hinweisen kann.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "no2") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt einen langfristigen Rückgang der durchschnittlichen NO₂-Konzentrationen seit den 1990er-Jahren. Besonders in den letzten Jahren sind deutlich sinkende Werte erkennbar, was unter anderem auf strengere Emissionsgrenzwerte und technologische Entwicklungen im Verkehrssektor hinweisen könnte. Der starke Rückgang im Jahr 1993 stellt hingegen einen auffälligen Ausreißer innerhalb der Zeitreihe dar und könnte auf eine daten- oder messtechnische Besonderheit hinweisen.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "pm10") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt einen langfristigen Rückgang der PM10-Konzentrationen seit den 1980er-Jahren. Besonders ab den 2000er-Jahren sind deutlich sinkende Werte erkennbar, was auf strengere Umweltauflagen, technische Entwicklungen im Verkehrs- und Industriesektor sowie verbesserte Luftreinhaltemaßnahmen hinweisen könnte. Auch die PM2.5-Werte zeigen seit Beginn der verfügbaren Messreihe ab 2008 eine insgesamt rückläufige Entwicklung.
            </div>
            """, unsafe_allow_html=True)

    # Abstand zur nächsten Grafik
    st.markdown(
        """
        <div style="margin-top: 50px;"></div>
        """,
        unsafe_allow_html=True)

    st.divider()

    # 2. Saisonales Muster (Jahrzehntvergleich)
    fig_saison = an.calcMeanSaisonYear(df_prepared, stoff)

    if fig_saison:

        # Grafikgröße einheitlich
        fig_saison.set_size_inches(10, 5.5)

        # Einheitliche Schriftgrößen
        TITLE_SIZE = 19
        LABEL_SIZE = 12 
        TICK_SIZE = 10

        # Achsen holen
        ax = fig_saison.axes[0]

        # Jahreszahlen rechts größer machen
        for text in ax.texts:
            text.set_fontsize(10.5)

        # Titel anpassen
        ax.set_title(
            f"Saisonales {stoff.upper()}-Muster im Jahrzehntvergleich",
            fontsize=TITLE_SIZE,
            color="white",
            pad=15)

        # Achsenbeschriftungen
        ax.set_xlabel(
            "Monat",
            fontsize=LABEL_SIZE,
            fontweight="bold")

        ax.set_ylabel(
            "Mittlere Konzentration [µg/m³]",
            fontsize=LABEL_SIZE,
            fontweight="bold")

        # Zahlen auf Achsen kleiner
        ax.tick_params(
            axis='both',
            labelsize=TICK_SIZE)

        # Grafik anzeigen
        st.pyplot(fig_saison, use_container_width=False)

        # Beschreibung unter der Grafik
        if (stoff == "o3") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt ein deutlich saisonales Ozonmuster mit erhöhten Konzentrationen in den Frühjahrs- und Sommermonaten. Besonders in den neueren Jahrzehnten treten höhere Ozonwerte auf, was auf den Einfluss steigender Temperaturen und intensiver Sonneneinstrahlung hinweisen kann.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "no2") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt insgesamt sinkende NO₂-Konzentrationen über die Jahrzehnte hinweg. Gleichzeitig sind besonders in den Wintermonaten höhere Werte erkennbar, was auf verstärkte Emissionen durch Verkehr und Heizungen sowie ungünstigere meteorologische Bedingungen für den Schadstoffabbau hinweisen kann.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "pm10") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt deutliche saisonale Unterschiede der PM10-Konzentrationen im Jahrzehntvergleich. Während in den 1980er- und 2000er-Jahren teilweise höhere Belastungen in einzelnen Herbst- und Wintermonaten auftreten, liegen die Werte im Jahr 2020 insgesamt deutlich niedriger. Dies deutet langfristig auf eine Verbesserung der Luftqualität sowie auf den Einfluss verschärfter Umwelt- und Emissionsmaßnahmen hin.
            </div>
            """, unsafe_allow_html=True)

    # Abstand zur nächsten Grafik
    st.markdown(
        """
        <div style="margin-top: 50px;"></div>
        """,
        unsafe_allow_html=True
    )


    st.divider()

    # 3. Rush-Hour-Effekt (Tagesverlauf)
    fig_rush = an.rushHourEffekt(df_prepared, stoff)

    if fig_rush:

        # Grafik kompakter machen
        fig_rush.set_size_inches(10, 5.5)

        # Einheitliche Schriftgrößen
        TITLE_SIZE = 19
        LABEL_SIZE = 12
        TICK_SIZE = 10

        # Achse holen
        ax = fig_rush.axes[0]

        # Titel anpassen
        ax.set_title(
            f"Mittlerer {stoff.upper()}-Tagesverlauf (Rush-Hour-Effekt)",
            fontsize=TITLE_SIZE,
            fontweight="normal",
            color="white",
            pad=15)

        # Achsenbeschriftungen
        ax.set_xlabel(
            "Uhrzeit (Stunde)",
            fontsize=LABEL_SIZE,
            fontweight="normal")

        ax.set_ylabel(
            f"{stoff.upper()} [µg/m³]",
            fontsize=LABEL_SIZE,
            fontweight="normal")

        # Zahlen auf Achsen
        ax.tick_params(
            axis='both',
            labelsize=TICK_SIZE)

        # Grafik anzeigen
        st.pyplot(fig_rush, use_container_width=False)

        # Beschreibung unter der Grafik
        if (stoff == "o3") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt einen deutlichen Tagesverlauf der Ozonkonzentration mit niedrigen Werten in den frühen Morgenstunden und einem Maximum am Nachmittag. Dies deutet auf den Einfluss photochemischer Prozesse sowie die Wechselwirkung zwischen Sonneneinstrahlung und Stickoxiden bei der Ozonbildung hin.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "no2") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt deutliche NO₂-Spitzen während der morgendlichen und abendlichen Hauptverkehrszeiten. Besonders in den Abendstunden steigen die Konzentrationen stark an, was auf erhöhte Verkehrsemissionen sowie eine geringere Verdünnung und Durchmischung der Schadstoffe in der Luft hinweist.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "pm10") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt einen typischen Tagesverlauf der PM10- und PM2.5-Konzentrationen mit erhöhten Werten in den frühen Morgen- und Abendstunden. Besonders bei PM10 sind Spitzen während der Hauptverkehrszeiten erkennbar, was auf den Einfluss des Straßenverkehrs und weiterer menschlicher Aktivitäten hinweist. In den Nachmittagsstunden sinken die Konzentrationen dagegen deutlich ab.
            </div>
            """, unsafe_allow_html=True)

        # Abstand zur nächsten Grafik
        st.markdown(
        """
        <div style="margin-top: 50px;"></div>
        """,
        unsafe_allow_html=True)

    st.divider()

    # 4. Inversionswetterlage
    fig_inversion = an.inversionswetter(df_prepared, stoff)

    if fig_inversion:

        # Grafik kompakter machen
        fig_inversion.set_size_inches(10, 5.5)

        # Einheitliche Schriftgrößen
        TITLE_SIZE = 19
        LABEL_SIZE = 12
        TICK_SIZE = 10

        # Achse holen
        ax = fig_inversion.axes[0]

        # oberen Zusatztitel entfernen
        fig_inversion.suptitle("")

        # Titel anpassen
        ax.set_title(
            ax.get_title(),
            fontsize=TITLE_SIZE,
            fontweight="normal",
            color="white",
            pad=15)

        # Achsenbeschriftungen
        ax.set_xlabel(
            ax.get_xlabel(),
            fontsize=LABEL_SIZE,
            fontweight="bold")

        ax.set_ylabel(
            ax.get_ylabel(),
            fontsize=LABEL_SIZE,
            fontweight="normal")

        # Zahlen auf Achsen
        ax.tick_params(
            axis='both',
            labelsize=TICK_SIZE)

        # Grafik anzeigen
        st.pyplot(fig_inversion, use_container_width=False)

        # Beschreibung unter der Grafik
        if (stoff == "o3") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt deutlich niedrigere Ozonkonzentrationen während Inversionslagen mit windstillen und wolkenlosen Wetterbedingungen. Dies weist darauf hin, dass Ozon in bodennahen Smogsituationen durch Stickoxide verstärkt abgebaut wird.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "no2") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die niedrigeren NO₂-Konzentrationen bei wolkenlosen und windstillen Wetterlagen deuten auf photochemische Umwandlungsprozesse hin. Unter intensiver Sonneneinstrahlung wird Stickstoffdioxid verstärkt in Ozon umgewandelt, wodurch die gemessenen NO₂-Werte trotz stabiler Wetterlage sinken können.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "pm10") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt, dass die PM10-Konzentrationen während Inversionslagen deutlich höher ausfallen als bei normalen Wetterbedingungen. Besonders bei windstillem und wolkenlosem Wetter können sich Feinstaubpartikel stärker in Bodennähe ansammeln, da die Luft schlechter durchmischt wird. Dadurch steigt die Belastung durch Feinstaub spürbar an.
            </div>
            """, unsafe_allow_html=True)

        # Abstand zur nächsten Grafik
        st.markdown(
        """
        <div style="margin-top: 50px;"></div>
        """,
        unsafe_allow_html=True)

    st.divider()

    # 5. Jährliche LQI-Überschreitungen
    fig_exceed = an.getExceedancesPerYear(df_prepared, stoff)

    if fig_exceed:

        # Grafik kompakter machen
        fig_exceed.set_size_inches(10, 5.5)

        # Einheitliche Schriftgrößen
        TITLE_SIZE = 19
        LABEL_SIZE = 12
        TICK_SIZE = 10

        # Achse holen
        ax = fig_exceed.axes[0]

        # Titel anpassen
        ax.set_title(
            ax.get_title(),
            fontsize=TITLE_SIZE,
            fontweight="normal",
            color="white",
            pad=15
        )

        # Achsenbeschriftungen
        ax.set_xlabel(
            ax.get_xlabel(),
            fontsize=LABEL_SIZE,
            fontweight="normal"
        )

        ax.set_ylabel(
            ax.get_ylabel(),
            fontsize=LABEL_SIZE,
            fontweight="normal"
        )

        # Zahlen auf Achsen
        ax.tick_params(
            axis="both",
            labelsize=TICK_SIZE
        )

        # Grafik anzeigen
        st.pyplot(fig_exceed, use_container_width=False)

        # Beschreibung unter der Grafik
        if (stoff == "o3"):

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Anzahl der Stunden mit mindestens mäßiger Ozonbelastung ist seit den 1980er-Jahren deutlich angestiegen. Besonders in den letzten Jahren treten erhöhte Ozonkonzentrationen häufiger auf, was auf veränderte klimatische und meteorologische Bedingungen hinweist.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "no2"):

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Anzahl der Stunden mit mindestens mäßiger NO₂-Belastung steigt zunächst bis in die frühen 2000er-Jahre an. Anschließend zeigt sich ein deutlicher Rückgang, besonders seit etwa 2010. Dies deutet auf eine langfristige Verbesserung der Luftqualität hin, die unter anderem mit strengeren Emissionsvorgaben und moderneren Fahrzeug- und Heiztechnologien zusammenhängen könnte.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "pm10"):

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt einen langfristigen Rückgang der Stunden mit mindestens mäßiger Feinstaubbelastung für PM10 und PM2.5. Besonders seit den 2000er-Jahren treten belastete Stunden deutlich seltener auf, was auf Verbesserungen der Luftqualität sowie auf strengere Emissions- und Umweltmaßnahmen hinweisen kann. Trotz einzelner Schwankungen ist insgesamt ein klarer positiver Trend erkennbar.
            </div>
            """, unsafe_allow_html=True)

        # Abstand zur nächsten Grafik
        st.markdown(
            """
            <div style="margin-top: 50px;"></div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # 6. Jahreszeit
    fig_season, fig_weekend = an.analyzeSeasonAndWeekend(df_prepared, stoff)

    if fig_season:

        # Grafik kompakter machen
        fig_season.set_size_inches(10, 5.5)

        # Einheitliche Schriftgrößen
        TITLE_SIZE = 19
        LABEL_SIZE = 12
        TICK_SIZE = 10

        # Achse holen
        ax = fig_season.axes[0]

        # Titel anpassen
        ax.set_title(
            ax.get_title(),
            fontsize=TITLE_SIZE,
            fontweight="normal",
            color="white",
            pad=15)

        # Achsenbeschriftungen
        ax.set_xlabel(
            ax.get_xlabel(),
            fontsize=LABEL_SIZE,
            fontweight="normal")

        ax.set_ylabel(
            ax.get_ylabel(),
            fontsize=LABEL_SIZE,
            fontweight="normal")

        # Zahlen auf Achsen
        ax.tick_params(
            axis="both",
            labelsize=TICK_SIZE
        )

        # Grafik anzeigen
        st.pyplot(fig_season, use_container_width=False)

        # Beschreibung unter der Grafik
        if (stoff == "o3") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die höchsten Ozonkonzentrationen treten im Sommer und Frühjahr auf, während im Herbst und Winter deutlich niedrigere Werte gemessen werden. Dies verdeutlicht den starken Einfluss von Sonneneinstrahlung und höheren Temperaturen auf die Ozonbildung.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "no2") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die NO₂-Werte sind im Sommer am niedrigsten und im Winter am höchsten. Ursache dafür sind im Sommer stärkere Sonneneinstrahlung, intensivere photochemische Prozesse und eine bessere Durchmischung der Luft, während sich Schadstoffe im Winter durch geringere Sonneneinstrahlung, stabilere Luftschichten und zusätzliche Emissionen aus dem Heizungs- und Verkehrssektor höhere Konzentrationen anreichern können.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "pm10") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt höhere PM10- und PM2.5-Werte in den Herbst- und Wintermonaten, während die niedrigsten Konzentrationen im Sommer auftreten. Besonders im Winter kann sich Feinstaub durch Heizungen, Verkehr und schlechtere Luftdurchmischung stärker in Bodennähe ansammeln. Im Sommer sorgen günstigere Wetterbedingungen dagegen meist für niedrigere Belastungen.
            </div>
            """, unsafe_allow_html=True)

        # Abstand zur nächsten Grafik
        st.markdown(
            """
            <div style="margin-top: 50px;"></div>
            """,
            unsafe_allow_html=True
        )

    st.divider()
    
    # 7. Werktag/Wochenende
    if fig_weekend:

        # Grafik kompakter machen
        fig_weekend.set_size_inches(10, 5.5)

        # Einheitliche Schriftgrößen
        TITLE_SIZE = 19
        LABEL_SIZE = 12
        TICK_SIZE = 10

        # Achse holen
        ax = fig_weekend.axes[0]

        # Titel anpassen
        ax.set_title(
            ax.get_title(),
            fontsize=TITLE_SIZE,
            fontweight="normal",
            color="white",
            pad=15
        )

        # Achsenbeschriftungen
        ax.set_xlabel(
            ax.get_xlabel(),
            fontsize=LABEL_SIZE,
            fontweight="bold"
        )

        ax.set_ylabel(
            ax.get_ylabel(),
            fontsize=LABEL_SIZE,
            fontweight="normal"
        )

        # Zahlen auf Achsen
        ax.tick_params(
            axis="both",
            labelsize=TICK_SIZE
        )

        # Grafik anzeigen
        st.pyplot(fig_weekend, use_container_width=False)

        # Beschreibung unter der Grafik
        if (stoff == "o3") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt höhere durchschnittliche Ozonkonzentrationen an Wochenenden im Vergleich zu Werktagen. Dies könnte auf geringere Stickoxid-Emissionen durch den Straßenverkehr und damit einen verminderten Ozonabbau zurückzuführen sein.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "no2") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die NO₂-Konzentrationen sind an Werktagen höher als am Wochenende. Dies deutet auf den Einfluss des Berufs- und Pendlerverkehrs hin, da Stickstoffdioxid hauptsächlich durch Verbrennungsprozesse im Straßenverkehr entsteht.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "pm10") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt höhere PM10- und PM2.5-Konzentrationen an Werktagen im Vergleich zum Wochenende. Dies deutet darauf hin, dass vor allem Verkehr und andere menschliche Aktivitäten während der Arbeitswoche zur erhöhten Feinstaubbelastung beitragen. Am Wochenende fallen die Konzentrationen dagegen insgesamt etwas niedriger aus.
            </div>
            """, unsafe_allow_html=True)

        # Abstand zur nächsten Grafik
        st.markdown(
            """
            <div style="margin-top: 50px;"></div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # 8. Silvester-Effekt (nur für PM10)
    if (stoff == "pm10"):

        fig_silvester = sil.analyseSilvesterTime(df_prepared, stoff)

        if fig_silvester is not None:

            # Grafik kompakter machen
            fig_silvester.set_size_inches(10, 5.5)

            # Einheitliche Schriftgrößen
            TITLE_SIZE = 19
            LABEL_SIZE = 12
            TICK_SIZE = 10

            # Achse holen
            ax = fig_silvester.axes[0]

            # Titel anpassen
            ax.set_title(
                ax.get_title(),
                fontsize=TITLE_SIZE,
                fontweight="normal",
                color="white",
                pad=15
            )

            # Achsenbeschriftungen
            ax.set_xlabel(
                ax.get_xlabel(),
                fontsize=LABEL_SIZE,
                fontweight="normal"
            )

            ax.set_ylabel(
                ax.get_ylabel(),
                fontsize=LABEL_SIZE,
                fontweight="normal"
            )

            # Zahlen auf Achsen
            ax.tick_params(
                axis="both",
                labelsize=TICK_SIZE
            )

            # Grafik anzeigen
            st.pyplot(fig_silvester, use_container_width=False)

            # Beschreibung unter der Grafik
            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt den Verlauf der PM10-Konzentrationen rund um den Jahreswechsel. Während der Weihnachtstage (24.12.–26.12.) sinken die Feinstaubwerte zunächst, was unter anderem auf geringeres Verkehrsaufkommen und reduzierte Aktivitäten während der Feiertage hinweisen könnte.<br><br>

            Ab dem 27.12. steigen die Werte wieder an. Besonders auffällig ist der starke Peak am 01.01., der wahrscheinlich auf Feuerwerkskörper und erhöhte Feinstaubemissionen in der Silvesternacht zurückzuführen ist. Bereits kurz danach sinken die Werte wieder deutlich ab.
            </div>
            """, unsafe_allow_html=True)

            # Abstand zur nächsten Grafik
            st.markdown(
                """
                <div style="margin-top: 50px;"></div>
                """,
                unsafe_allow_html=True
            )

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
    showEDAPlots(dfOrginal, stoff_spalte)
    #if stoff_spalte == "o3":
        #O3.showO3EDAPlots()
   
#######################################################
@st.fragment
def showTab4():
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
    
#######################################################
@st.fragment
def showTab5 ():
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
#######################################################
@st.fragment
def showTab6():

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
#######################################################
@st.fragment
def showTab7 ():
    st.header("Ablationsstudie: Bedeutung der Vergangenheit")
    models = pr.prognosis (dfOrginal)

#######################################################
@st.fragment
def showTab8():
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

#######################################################

dfOrginal = load()

# ============================================================
# 01 SIDEBAR-KONFIGURATION
# ============================================================
with st.sidebar:
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] > div {
        padding-top: 1.2rem !important;
    }
    
    .sidebar-item {
    margin-bottom: 16px;
    }
                
    .sidebar-title {
        font-size: 25px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .sidebar-section-title {
        font-size: 18px;
        font-weight: 800;
        margin-bottom: 4px;
    }

    .sidebar-divider {
        margin: 14px 0 14px 0;
        border-top: 1px solid rgba(255,255,255,0.16);
    }

    div[role="radiogroup"] label {
        padding: 0px 0 !important;
        margin: 0px 0 !important;
    }

    div[role="radiogroup"] p {
        font-size: 17px !important;
        line-height: 1.2 !important;
        font-weight: 600 !important;
    }

    .sidebar-text {
        font-size: 14px;
        line-height: 1.45;
    }

    .sidebar-text b {
        font-size: 15px;
    }

    .sidebar-gap {
        height: 10px;
    }

    .sidebar-data-box {
        background-color: rgba(3, 149, 176, 0.1);
        padding: 9px 11px;
        border-radius: 0.5rem;
        border: 1px solid rgba(1, 132, 157, 0.8);
        font-family: 'Courier New', Courier, monospace;
        font-size: 14px;
        color: #FAFAFA;
        line-height: 1.35;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='sidebar-title'>🌦️ Filter & Einstellungen</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-section-title'>Schadstoff-Auswahl:</div>", unsafe_allow_html=True)

    schadstoff_auswahl = st.radio(
        "",
        ["Ozon (O₃)", "Stickstoffdioxid (NO₂)", "Feinstaub (PM10 & PM2.5)"],
        label_visibility="collapsed"
    )

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
Markus Edelhoff<br>
Frank Hasdorf                
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
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs(
    ["Startseite", "Wetterdaten", "Explorative Analyse", "Korrelationsanalyse",
     "Multiple Regression", "Random Forest", "Vorhersage Live", "Vorhersage", "Fazit", "Technische Insights"]
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
    st.divider()

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
            hide_index=True
        )

    # Technische Infos anzeigen
    with st.expander("Technische Datensatzinformationen anzeigen"):
        dtypes_df = pd.DataFrame({
            "Spalte": dfOrginal.columns,
            "Datentyp": dfOrginal.dtypes.astype(str),
            "Null-Werte": dfOrginal.isna().sum().values
        })

        st.dataframe(
            dtypes_df,
            use_container_width=True,
            hide_index=True
        )

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
    showTab8 ()

# ============================================================
# TAB 8: VORHERSAGE2
# ============================================================
with tab8:
    showTab7 ()

# ============================================================
# TAB 9: Fazit
# ============================================================
# ============================================================
# TAB 9: FAZIT
# ============================================================
with tab9:
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
    
    Zusätzlich kann der Rückgang von Stickstoffdioxid dazu beitragen, dass Ozon in Bodennähe langsamer abgebaut wird, da Stickstoffoxide unter bestimmten Bedingungen am Abbau von Ozon beteiligt sind. Dieser Zusammenhang wird teilweise auch als „Ozonparadoxon“ beschrieben.

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
        - Einbindung zusätzlicher Verkehrsdaten, z. B. Verkehrsaufkommen, Staubereiche oder Echtzeit-Verkehrsflüsse  
        - Berücksichtigung weiterer Emissionsquellen wie Industrie, Heizungen oder Baustellen  
        - Integration vorheriger Schadstoffmesswerte der letzten Stunden oder Tage zur besseren Erkennung kurzfristiger Belastungsmuster  
        - Erweiterung der Analyse auf weitere Städte, Regionen oder internationale Datensätze  
        - Vergleich verschiedener Messstationen innerhalb Nürnbergs oder Bayerns  
        - Einbindung detaillierter Wetterlagen wie Inversion, Luftaustausch oder Windströmungen  
        - Einsatz weiterer Machine-Learning-Modelle wie Gradient Boosting oder neuronale Netze  
        - Entwicklung eines Live-Warnsystems für erhöhte Luftschadstoffbelastungen und gesundheitliche Risiken  
        - Kombination von Luftqualitäts- und Gesundheitsdaten zur Analyse möglicher gesundheitlicher Auswirkungen  
        """)

    st.markdown("<br>", unsafe_allow_html=True)

    st.success("""
    Zusammenfassend zeigt das Dashboard: Wetter- und Zeitfaktoren liefern wichtige Hinweise auf die Entwicklung der Luftqualität. 
    Für präzisere Vorhersagen müssen jedoch zusätzliche Emissionsquellen und lokale Einflussfaktoren berücksichtigt werden.
    """)

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
