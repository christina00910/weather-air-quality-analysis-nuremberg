# Schadstoffe 
col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Stickstoffdioxid (NO₂)")
        st.write("""
        NO₂ entsteht vor allem bei Verbrennungsprozessen, insbesondere im Straßenverkehr.
        Erhöhte Konzentrationen können die Atemwege belasten und stehen mit Atemwegs- sowie
        Herz-Kreislauf-Erkrankungen in Verbindung.
        """)

    with col2:
        st.subheader("Ozon (O₃)")
        st.write("""
        Ozon entsteht unter Sonneneinstrahlung aus Vorläufersubstanzen wie Stickoxiden.
        Hohe Werte treten besonders bei warmem und sonnigem Wetter auf und können die
        Lungenfunktion beeinträchtigen.
        """)

    with col3:
        st.subheader("Feinstaub (PM10 / PM2.5)")
        st.write("""
        Feinstaub entsteht unter anderem durch Verkehr, Heizungen und Industrie.
        Besonders kleine Partikel können tief in die Lunge eindringen und gesundheitliche
        Belastungen verursachen.
        """)
#------------------------------------------------
# Startseite
st.title("🌍 Modulare Analyse und Vorhersage von Wetter- und Luftqualitätsdaten")

st.markdown("""
### Untersuchungsregion: Nürnberg  
### Projektzeitraum: 11.05.2026 – 29.05.2026
""")

st.info("""
**Projektteam**  
- Christina Dürbeck  
- Frank Hasdorf  
- Markus Edelhoff
""")

st.header("📌 Projektüberblick")

st.write("""
Ziel des Projekts ist die Analyse meteorologischer Einflüsse auf Luftschadstoffe in Nürnberg.
Dabei werden statistische Verfahren sowie Machine-Learning-Modelle eingesetzt, um Zusammenhänge
zwischen Wetterbedingungen und Luftqualität zu untersuchen und Luftschadstoffe vorherzusagen.
""")

#Gesundheitliche Relevanz von Luftschadstoffen
st.header("🫁 Gesundheitliche Auswirkungen von Luftschadstoffen")

st.write("""
Luftschadstoffe zählen weltweit zu den größten umweltbedingten Gesundheitsrisiken.
Im Projekt werden insbesondere Ozon (O₃), Stickstoffdioxid (NO₂) sowie Feinstaub
(PM10 und PM2.5) untersucht.
""")
st.image(
    "Bilder/gesundheit.png",
    caption="Quelle: Umweltbundesamt (2023)",
    use_container_width=True)
st.markdown("""
Die dargestellte Übersicht verdeutlicht, dass Luftschadstoffe zahlreiche Bereiche des menschlichen Körpers beeinflussen können. 
Besonders betroffen sind die Atemwege sowie das Herz-Kreislauf-System, 
jedoch stehen Luftschadstoffe auch im Zusammenhang mit neurologischen Erkrankungen, Stoffwechselerkrankungen 
sowie gesundheitlichen Risiken während der Schwangerschaft.

Die Analyse der Luftqualität besitzt daher nicht nur eine ökologische, sondern insbesondere auch eine hohe gesundheitliche Relevanz.
""")
# 3 Spalten mit Luftschadstoffen
col1, col2, col3 = st.columns(3)

#NO2-Box
with col1:
    st.subheader("Stickstoffdioxid (NO₂)")
    st.write("""
    Stickstoffdioxid (NO₂) entsteht hauptsächlich bei Verbrennungsprozessen,
    insbesondere im Straßenverkehr. Deshalb treten erhöhte Konzentrationen vor allem
    in Städten sowie entlang stark befahrener Straßen auf.
             
    Erhöhte NO₂-Konzentrationen können die Atemwege belasten und stehen unter anderem
    im Zusammenhang mit Atemwegserkrankungen sowie Herz-Kreislauf-Erkrankungen.
    Besonders empfindlich reagieren Asthmatikerinnen und Asthmatiker auf erhöhte Belastungen.
    """)

#O3-Box
with col2:
    st.subheader("O₃")
    st.write("""
    Ozon (O₃) entsteht photochemisch aus Vorläufersubstanzen wie Stickoxiden
    unter Einfluss von Sonnenlicht und tritt daher besonders bei warmem und sonnigem Wetter auf.

    Erhöhte Ozonkonzentrationen können die Lungenfunktion beeinträchtigen,
    entzündliche Reaktionen in den Atemwegen verursachen und zu Atemwegsbeschwerden führen.
    Besonders empfindliche Personen, beispielsweise Asthmatikerinnen und Asthmatiker,
    reagieren verstärkt auf hohe Ozonwerte.
    """)

#Feinstaub-Box
with col3:
    st.subheader("PM10 / PM2.5")
    st.write("""
    Feinstaub (PM10 und PM2.5) entsteht sowohl direkt bei Verbrennungsprozessen
    als auch indirekt durch chemische Reaktionen in der Atmosphäre.
    Wichtige Quellen sind insbesondere Verkehr, Heizungen sowie industrielle Prozesse.

    Je kleiner die Partikel sind, desto tiefer können sie in den Körper eindringen.
    Während PM10 hauptsächlich die oberen Atemwege belastet, kann PM2.5 bis in die
    Lungenbläschen und teilweise sogar in den Blutkreislauf gelangen.

    Feinstaub steht unter anderem im Zusammenhang mit Atemwegserkrankungen,
    Entzündungsreaktionen sowie Herz-Kreislauf-Erkrankungen.
    """)

#Datenquellen
st.header("📊 Verwendete Datenquellen")

st.markdown("""
- **Deutscher Wetterdienst (DWD)**  
  Wetterdaten der Messstation Nürnberg (Stations-ID: 3668)

- **Bayerisches Landesamt für Umwelt (LfU)**  
  Luftschadstoffdaten für NO₂, O₃, PM10 und PM2.5

- ??? API für Vorhersage ???
""")

#Datenaufbereitung
st.header("⚙️ Datenaufbereitung")

st.markdown("""
Im Rahmen der Datenaufbereitung wurden die Wetter- und Luftschadstoffdaten über Python:

- zeitlich aufeinander abgestimmt
- bereinigt und zusammengeführt
- auf fehlende Werte überprüft
- um zusätzliche zeitliche Einflussfaktoren ergänzt
""")

st.subheader("Zusätzliche Zeitvariablen")

zeitvariablen = [
    "Tageszeit (Stunde)",
    "Wochentag",
    "Monatszugehörigkeit",
    "Wochenenden",
    "Hauptverkehrszeiten (Rush Hour)",
    "Heizperiode",
    "Nachtstunden",
    "Silvestereffekt"
]

st.table(zeitvariablen)


#Datensatzübersicht
st.header("📊 Datensatzübersicht")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Analysezeitraum", "1980 – 2024")

with col2:
    st.metric("Messintervall", "Stündlich")

with col3:
    st.metric("PM2.5 verfügbar ab", "2008")

col4, col5, col6 = st.columns(3)

with col4:
    st.metric("Anzahl Datensätze", "XXXX")

with col5:
    st.metric("Anzahl Merkmale", "XXXX")

with col6:
    st.metric("Untersuchungsregion", "Nürnberg")


# Dashboard-Struktur
st.header("🧭 Aufbau des Dashboards")

st.markdown("""
1. Projektüberblick  
2. Explorative Datenanalyse  
3. Korrelationsanalyse  
4. Multiple lineare Regression  
5. Random-Forest-Analyse  
6. Live-Luftschadstoffvorhersage  
7. Fazit und Erkenntnisse
""")
