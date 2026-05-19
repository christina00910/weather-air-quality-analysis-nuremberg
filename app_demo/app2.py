import pathlib
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. SETUP & DATEN LADEN (Angepasst an Schadstoff_Wetter.csv)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Luft & Wetter Bayern", layout="wide")
st.title("🌤️ Luftqualität & Wetter-Dynamik in Bayern")

@st.cache_data
def load_data():
    # 1. Ermittelt den absoluten Pfad des Ordners, in dem app2.py liegt
    base_dir = pathlib.Path(__file__).parent.resolve()
    
    # 2. Baut den Pfad exakt zusammen: .../app_demo/data/Schadstoff_Wetter.csv
    file_path = base_dir / "data" / "Schadstoff_Wetter.csv"
    
    # 3. Lade die Datei mit dem absoluten Pfad
    df = pd.read_csv(file_path)
    
    # ... hier folgt dein restlicher Code (Datum parsen etc.) ...
    return df
    
    # 2. Datum parsen und echten Timestamp aus 'datum' und 'stunde' generieren
    df['datum'] = pd.to_datetime(df['datum'], errors='coerce')
    df['timestamp'] = df['datum'] + pd.to_timedelta(df['stunde'], unit='h')
    
    # 3. Zeit-Features für die Tabs extrahieren
    df['Jahr'] = df['datum'].dt.year
    df['Monat'] = df['datum'].dt.month
    
    # 4. Quick-Fix für fehlende Werte (NaNs), damit die Diagramme nicht brechen.
    # Wenn Ihr das Notebook 1 fertig haben, wird das hier obsolet!
    df['temperatur'] = df['temperatur'].ffill()
    df['o3'] = df['o3'].ffill()
    df['no2'] = df['no2'].ffill()
    df['pm10'] = df['pm10'].ffill()
    df['niederschlagshoehe_mm'] = df['niederschlagshoehe_mm'].fillna(0) # Leere Regenfelder sind oft 0 mm
    
    return df

with st.spinner("Lade 400.000 Datensätze..."):
    df = load_data()

# -----------------------------------------------------------------------------
# 2. DASHBOARD STRUKTUR (Tabs)
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🌧️ Washout-Effekt", 
    "☀️ Ozon-Paradoxon", 
    "⏱️ Chronobiologie", 
    "📈 Langzeittrend"
])

# =============================================================================
# TAB 1: Der Washout-Effekt (Niederschlag vs. Feinstaub)
# =============================================================================
with tab1:
    st.header("Reinigung der Atmosphäre durch Regen")
    st.markdown("Wie stark sinkt die Feinstaubbelastung (PM10) an Regentagen?")
    
    # Kategorisierung in 'Trocken' und 'Regen' anhand der echten Spalte
    df_washout = df[['niederschlagshoehe_mm', 'pm10']].dropna().copy()
    df_washout['Wetterlage'] = df_washout['niederschlagshoehe_mm'].apply(
        lambda x: 'Regen (>0 mm)' if x > 0 else 'Trocken (0 mm)'
    )
    
    fig_washout = px.box(
        df_washout, 
        x='Wetterlage', 
        y='pm10',
        color='Wetterlage',
        color_discrete_map={'Trocken (0 mm)': '#ef553b', 'Regen (>0 mm)': '#636efa'},
        title="PM10-Verteilung: Trockenheit vs. Niederschlag",
        template="plotly_dark",
        labels={'pm10': 'PM10 (µg/m³)'}
    )
    
    # Achse begrenzen (auf das 95% Quantil), um die Boxen trotz extremer Ausreißer gut zu sehen
    q95 = df_washout['pm10'].quantile(0.95)
    fig_washout.update_yaxes(range=[0, q95])
    
    st.plotly_chart(fig_washout, use_container_width=True)

# =============================================================================
# TAB 2: Das Ozon-Paradoxon (Dual-Axis Chart)
# =============================================================================
with tab2:
    st.header("Das Ozon-Paradoxon im Hochsommer")
    st.markdown("Ozon entsteht durch Sonneneinstrahlung unter Verbrauch von NO₂.")
    
    # Dynamische Jahresauswahl für den Nutzer
    verfuegbare_jahre = df['Jahr'].dropna().unique()
    selected_year = st.selectbox("Wähle ein Jahr für den Sommer-Zoom:", sorted(verfuegbare_jahre, reverse=True))
    
    # Filtern auf Juli (Monat 7) des gewählten Jahres (erste 14 Tage für Übersichtlichkeit)
    df_sommer = df[(df['Monat'] == 7) & (df['Jahr'] == selected_year)].head(24*14) 
    
    fig_ozon = go.Figure()

    # Temperatur im Hintergrund
    fig_ozon.add_trace(go.Scatter(
        x=df_sommer['timestamp'], y=df_sommer['temperatur'],
        name="Temperatur (°C)", fill='tozeroy', mode='lines',
        line=dict(color='rgba(255, 165, 0, 0.3)'), yaxis='y1'
    ))

    # Ozon (steigt bei Sonne/Hitze)
    fig_ozon.add_trace(go.Scatter(
        x=df_sommer['timestamp'], y=df_sommer['o3'],
        name="Ozon (µg/m³)", mode='lines',
        line=dict(color='#00CC96', width=3), yaxis='y2'
    ))

    # NO2 (wird verbraucht, verhält sich gegenläufig)
    fig_ozon.add_trace(go.Scatter(
        x=df_sommer['timestamp'], y=df_sommer['no2'],
        name="NO₂ (µg/m³)", mode='lines',
        line=dict(color='#EF553B', width=3, dash='dot'), yaxis='y2'
    ))

    fig_ozon.update_layout(
        title=f"Zusammenspiel im Juli {int(selected_year)}",
        template="plotly_dark",
        yaxis=dict(title="Temperatur (°C)", side='left', showgrid=False),
        yaxis2=dict(title="Schadstoffe (µg/m³)", side='right', overlaying='y', showgrid=True),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_ozon, use_container_width=True)

# =============================================================================
# TAB 3: Chronobiologie (2D-Heatmap)
# =============================================================================
with tab3:
    st.header("Die Rhythmen der Luftverschmutzung")
    st.markdown("Wann ist die NO₂-Belastung im Jahres- und Tagesverlauf am höchsten (Berufsverkehr/Winter)?")
    
    # Aggregation mit echten Spalten 'Monat', 'stunde' und 'no2'
    df_heatmap = df.groupby(['Monat', 'stunde'])['no2'].mean().reset_index()
    heatmap_matrix = df_heatmap.pivot(index='Monat', columns='stunde', values='no2')
    
    fig_heat = px.imshow(
        heatmap_matrix,
        labels=dict(x="Uhrzeit (0-23)", y="Monat (1-12)", color="Ø NO₂ (µg/m³)"),
        x=heatmap_matrix.columns,
        y=['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'],
        color_continuous_scale="Inferno",
        title="Durchschnittliche NO₂-Belastung nach Uhrzeit & Monat",
        template="plotly_dark"
    )
    
    fig_heat.update_yaxes(autorange="reversed")
    st.plotly_chart(fig_heat, use_container_width=True)

# =============================================================================
# TAB 4: Klima-Langzeittrend 
# =============================================================================
with tab4:
    st.header("Langzeittrend seit Messbeginn")
    st.markdown("Klimaerwärmung vs. Erfolge in der Luftreinhaltung (Katalysatoren, Filter).")
    
    # Hier aggregieren wir live, da Streamlit das bei 400k Zeilen noch ganz gut wegschafft.
    df_trend = df.groupby('Jahr')[['temperatur', 'pm10', 'no2']].mean().reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_temp = px.line(
            df_trend, x='Jahr', y='temperatur', 
            title="Ø Jahres-Temperatur (°C)",
            color_discrete_sequence=['#FFA550'],
            template="plotly_dark",
            labels={'temperatur': 'Temperatur (°C)'}
        )
        fig_temp.update_traces(mode='lines+markers')
        st.plotly_chart(fig_temp, use_container_width=True)
        
    with col2:
        df_trend_melt = pd.melt(
            df_trend, id_vars=['Jahr'], value_vars=['pm10', 'no2'],
            var_name='Schadstoff', value_name='µg/m³'
        )
        fig_schadstoffe = px.line(
            df_trend_melt, x='Jahr', y='µg/m³', color='Schadstoff',
            title="Ø Jahres-Schadstoffbelastung",
            template="plotly_dark"
        )
        fig_schadstoffe.update_traces(mode='lines+markers')
        st.plotly_chart(fig_schadstoffe, use_container_width=True)