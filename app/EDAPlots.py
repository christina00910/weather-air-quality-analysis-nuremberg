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
import tabs as t


def showEDAPlots (df_prepared, stoff):        
    """
    Zeigt alle EDA-Plots hochperformant in Streamlit an.
    Wichtig: Übergeben Sie hier das zentral über 'prepare_base_data' 
    vorbereitete DataFrame, nicht das rohe Original!
    """

    st.divider()
    
# ============================================================
# Grafiken der EDA-Analyse
# ============================================================  
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
        unsafe_allow_html=True)
    
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
            labelsize=TICK_SIZE)

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
            unsafe_allow_html=True)

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
            labelsize=TICK_SIZE)

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
            unsafe_allow_html=True)

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
            axis="both",
            labelsize=TICK_SIZE)

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
            unsafe_allow_html=True)

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
                labelsize=TICK_SIZE)

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
                unsafe_allow_html=True)
    return
