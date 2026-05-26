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
    "Bilder/Rolle der Luftschadstoffe für die Gesundheit.png",
    caption="Quelle: Umweltbundesamt (2023)",
    use_container_width=True)

# 3 Spalten mit Luftschadstoffen
col1, col2, col3 = st.columns(3)

#NO2-Box
with col1:
    st.subheader("NO₂")
    st.write("""
    Entsteht hauptsächlich im Straßenverkehr.
    
    Kann Atemwege belasten und steht im Zusammenhang
    mit Herz-Kreislauf-Erkrankungen.
    """)

#O3-Box
with col2:
    st.subheader("O₃")
    st.write("""
    Entsteht photochemisch unter Sonneneinstrahlung.
    
    Kann die Lungenfunktion beeinträchtigen
    und Atemwegsbeschwerden verursachen.
    """)

#Feinstaub-Box
with col3:
    st.subheader("PM10 / PM2.5")
    st.write("""
    Entsteht durch Verkehr, Heizungen und Industrie.
    
    Kleine Partikel können tief in die Lunge
    und teilweise in den Blutkreislauf gelangen.
    """)

#Datenquellen
st.header("📊 Verwendete Datenquellen")

st.markdown("""
- **Deutscher Wetterdienst (DWD)**  
  Wetterdaten der Messstation Nürnberg (Stations-ID: 3668)

- **Bayerisches Landesamt für Umwelt (LfU)**  
  Luftschadstoffdaten für NO₂, O₃, PM10 und PM2.5
""")

#Datenaufbereitung
st.header("⚙️ Datenaufbereitung")

st.markdown("""
Die Wetter- und Luftschadstoffdaten wurden:

- synchronisiert
- bereinigt
- zusammengeführt
- auf fehlende Werte überprüft
- um zusätzliche Zeitvariablen ergänzt
""")

st.subheader("Zusätzliche Zeitvariablen")

zeitvariablen = [
    "Stunde",
    "Wochentag",
    "Monat",
    "Wochenende",
    "Rush Hour",
    "Heizperiode",
    "Nachtstunden",
    "Silvestereffekt"
]

st.table(zeitvariablen)


#Datensatzübersicht
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Zeitraum", "1980–2024")

with col2:
    st.metric("Zeitauflösung", "Stündlich")

with col3:
    st.metric("PM2.5 verfügbar ab", "2008")

col4, col5 = st.columns(2)

with col4:
    st.metric("Anzahl Zeilen", "XXXX")

with col5:
    st.metric("Anzahl Variablen", "XXXX")


# Dashboard-Struktur
st.header("🧭 Aufbau des Dashboards")

st.markdown("""
1. Projektüberblick  
2. Explorative Datenanalyse  
3. Zeitliche Analysen  
4. Korrelationsanalyse  
5. Multiple lineare Regression  
6. Random-Forest-Analyse  
7. Live-Luftschadstoffvorhersage  
8. Fazit und Erkenntnisse
""")
