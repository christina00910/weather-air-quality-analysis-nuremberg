# -*- coding: utf-8 -*-
# @Author: Frank Hasdorf
# @Date:   12-05-2026 16:38:09
# @Last Modified by:   Frank Hasdorf
# @Last Modified time: 16-05-2026

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Luft & Wetter Bayern", page_icon="🌬️", layout="wide")

# --- 1. DATEN LADEN ---
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_pfad = os.path.join(base_dir, 'data', 'Schadstoff_Wetter.csv')

    try:
        df = pd.read_csv(data_pfad)
        df['Datum_Uhrzeit'] = pd.to_datetime(df['datumstunde'], format='%Y%m%d%H', errors='coerce')
        df = df.rename(columns={
            'temperatur':              'Temperatur_C',
            'windgeschwindigkeit':     'Wind_ms',
            'sonnenscheindauer_minuten': 'Sonnenschein_min',
            'luftfeuchtigkeit':        'Luftfeuchtigkeit',
            'o3':  'Ozon',
            'no2': 'NO2',
            'pm10': 'PM10',
        })
        return df
    except FileNotFoundError:
        st.error("Datei 'Schadstoff_Wetter.csv' nicht im /data Ordner gefunden.")
        return pd.DataFrame()


df = load_data()

# --- 2. SIDEBAR ---
st.sidebar.header("⚙️ Filter & Einstellungen")

if df.empty:
    st.warning("⚠️ Keine Daten geladen. Bitte 'Schadstoff_Wetter.csv' in den /data Ordner legen.")
    st.stop()

min_year = int(df['Datum_Uhrzeit'].dt.year.min())
max_year = int(df['Datum_Uhrzeit'].dt.year.max())

selected_year = st.sidebar.slider(
    "Wähle ein Jahr", min_value=min_year, max_value=max_year, value=2020
)

df_year = df[df['Datum_Uhrzeit'].dt.year == selected_year].copy()

st.sidebar.markdown("---")
st.sidebar.caption(f"Datensatz: {len(df):,} Stundenwerte | {min_year}–{max_year}")

# --- 3. HAUPTBEREICH ---
st.title("🌬️ Luftqualität & Wetter Dashboard – Bayern")

tab1, tab2, tab3 = st.tabs(["🌡️ Wetter-Exploration", "🧪 Schadstoffe", "📈 Klimatrend"])

# ============================================================
# TAB 1: WETTER
# ============================================================
with tab1:
    st.subheader(f"Wetterdaten {selected_year}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Ø Temperatur", f"{df_year['Temperatur_C'].mean():.1f} °C")
    col2.metric("Max. Wind", f"{df_year['Wind_ms'].max():.1f} m/s")
    col3.metric("Gesamte Sonnenstunden", f"{df_year['Sonnenschein_min'].fillna(0).sum() / 60:.0f} h")

    # Tägliche Aggregate für übersichtlichere Charts
    df_daily = (
        df_year
        .set_index('Datum_Uhrzeit')
        .resample('D')
        .agg(
            Temperatur_C=('Temperatur_C', 'mean'),
            Wind_ms=('Wind_ms', 'mean'),
            Sonnenschein_min=('Sonnenschein_min', 'sum'),
        )
        .reset_index()
    )

    st.markdown("### Temperaturverlauf")
    fig_temp = px.line(
        df_daily, x='Datum_Uhrzeit', y='Temperatur_C',
        title=f"Tägliche Ø Temperatur ({selected_year})",
        labels={'Datum_Uhrzeit': 'Datum', 'Temperatur_C': 'Temperatur (°C)'},
        color_discrete_sequence=['#FF7F0E'],
    )
    fig_temp.update_layout(height=350)
    st.plotly_chart(fig_temp, use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        fig_wind = px.line(
            df_daily, x='Datum_Uhrzeit', y='Wind_ms',
            title="Ø Windgeschwindigkeit (m/s)",
            labels={'Datum_Uhrzeit': 'Datum', 'Wind_ms': 'Wind (m/s)'},
            color_discrete_sequence=['#1F77B4'],
        )
        fig_wind.update_layout(height=300)
        st.plotly_chart(fig_wind, use_container_width=True)

    with col_b:
        fig_sun = px.bar(
            df_daily, x='Datum_Uhrzeit', y='Sonnenschein_min',
            title="Sonnenscheindauer pro Tag (Minuten)",
            labels={'Datum_Uhrzeit': 'Datum', 'Sonnenschein_min': 'Minuten'},
            color_discrete_sequence=['#FFC300'],
        )
        fig_sun.update_layout(height=300)
        st.plotly_chart(fig_sun, use_container_width=True)

    if st.checkbox("Rohdaten anzeigen", key="tab1_raw"):
        st.dataframe(
            df_year[['Datum_Uhrzeit', 'Temperatur_C', 'Wind_ms', 'Sonnenschein_min', 'Luftfeuchtigkeit']]
            .dropna(subset=['Temperatur_C']),
            use_container_width=True,
        )

# ============================================================
# TAB 2: SCHADSTOFFE
# ============================================================
with tab2:
    st.subheader(f"Luftqualität {selected_year}")

    df_luft = df_year[['Datum_Uhrzeit', 'Ozon', 'NO2', 'PM10', 'Temperatur_C', 'Sonnenschein_min']].copy()

    col1, col2, col3 = st.columns(3)
    col1.metric("Ø Ozon (O₃)", f"{df_luft['Ozon'].mean():.1f} µg/m³")
    col2.metric("Ø Stickstoffdioxid (NO₂)", f"{df_luft['NO2'].mean():.1f} µg/m³")
    col3.metric("Ø Feinstaub (PM10)", f"{df_luft['PM10'].mean():.1f} µg/m³")

    df_luft_daily = (
        df_luft
        .set_index('Datum_Uhrzeit')
        .resample('D')
        .mean()
        .reset_index()
    )

    st.markdown("### Schadstoffverläufe")
    df_melt = df_luft_daily.melt(
        id_vars='Datum_Uhrzeit',
        value_vars=['Ozon', 'NO2', 'PM10'],
        var_name='Schadstoff',
        value_name='Konzentration (µg/m³)',
    )
    fig_luft = px.line(
        df_melt, x='Datum_Uhrzeit', y='Konzentration (µg/m³)', color='Schadstoff',
        title=f"Tägliche Schadstoffkonzentration ({selected_year})",
        labels={'Datum_Uhrzeit': 'Datum'},
        color_discrete_map={'Ozon': '#2CA02C', 'NO2': '#D62728', 'PM10': '#9467BD'},
    )
    fig_luft.update_layout(height=380)
    st.plotly_chart(fig_luft, use_container_width=True)

    st.markdown("### Zusammenhang Temperatur & Ozon")
    df_scatter = df_luft[['Temperatur_C', 'Ozon', 'Sonnenschein_min']].dropna()
    if not df_scatter.empty:
        fig_scatter = px.scatter(
            df_scatter.sample(min(len(df_scatter), 3000), random_state=42),
            x='Temperatur_C', y='Ozon',
            color='Sonnenschein_min',
            color_continuous_scale='YlOrRd',
            title="Temperatur vs. Ozon (Farbe = Sonnenscheindauer)",
            labels={
                'Temperatur_C': 'Temperatur (°C)',
                'Ozon': 'Ozon (µg/m³)',
                'Sonnenschein_min': 'Sonnenschein (min)',
            },
            opacity=0.5,
            trendline='ols',
        )
        fig_scatter.update_layout(height=380)
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("Nicht genügend Daten für den Scatter-Plot in diesem Jahr.")

    st.markdown("### WHO-Grenzwerte (Referenz)")
    grenzwerte = pd.DataFrame({
        'Schadstoff':     ['Ozon (O₃)', 'Stickstoffdioxid (NO₂)', 'Feinstaub (PM10)'],
        'WHO-Grenzwert':  ['100 µg/m³ (8h-Mittel)', '25 µg/m³ (Jahresmittel)', '15 µg/m³ (Jahresmittel)'],
        'Ø Messwert':     [
            f"{df_luft['Ozon'].mean():.1f} µg/m³",
            f"{df_luft['NO2'].mean():.1f} µg/m³",
            f"{df_luft['PM10'].mean():.1f} µg/m³",
        ],
    })
    st.dataframe(grenzwerte, use_container_width=True, hide_index=True)

# ============================================================
# TAB 3: KLIMATREND
# ============================================================
with tab3:
    st.subheader(f"Langzeit-Klimatrend ({min_year}–{max_year})")
    st.caption("Jährliche Durchschnittswerte über den gesamten Datensatz.")

    df_yearly = (
        df
        .set_index('Datum_Uhrzeit')
        .resample('YE')
        .agg(
            Temperatur_C=('Temperatur_C', 'mean'),
            Wind_ms=('Wind_ms', 'mean'),
            Ozon=('Ozon', 'mean'),
            NO2=('NO2', 'mean'),
            PM10=('PM10', 'mean'),
        )
        .reset_index()
    )
    df_yearly['Jahr'] = df_yearly['Datum_Uhrzeit'].dt.year

    col1, col2 = st.columns(2)

    with col1:
        valid_t = df_yearly[['Jahr', 'Temperatur_C']].dropna()
        fig_t = px.line(
            df_yearly, x='Jahr', y='Temperatur_C',
            title="Jährliche Ø Temperatur",
            labels={'Temperatur_C': 'Temperatur (°C)'},
            color_discrete_sequence=['#FF7F0E'],
            markers=True,
        )
        if len(valid_t) >= 2:
            z = np.polyfit(valid_t['Jahr'], valid_t['Temperatur_C'], 1)
            p = np.poly1d(z)
            fig_t.add_scatter(
                x=valid_t['Jahr'], y=p(valid_t['Jahr']),
                mode='lines', name='Trend',
                line=dict(dash='dash', color='red', width=2),
            )
        fig_t.update_layout(height=320)
        st.plotly_chart(fig_t, use_container_width=True)

    with col2:
        df_poll_yearly = df_yearly[['Jahr', 'Ozon', 'NO2', 'PM10']].melt(
            id_vars='Jahr', var_name='Schadstoff', value_name='µg/m³'
        )
        fig_p = px.line(
            df_poll_yearly, x='Jahr', y='µg/m³', color='Schadstoff',
            title="Jährliche Ø Schadstoffwerte",
            color_discrete_map={'Ozon': '#2CA02C', 'NO2': '#D62728', 'PM10': '#9467BD'},
            markers=True,
        )
        fig_p.update_layout(height=320)
        st.plotly_chart(fig_p, use_container_width=True)

    # Tachometer: Luftqualitäts-Index für das gewählte Jahr
    st.markdown(f"### Luftqualitäts-Index für {selected_year}")
    st.caption("Eigener Index basierend auf PM10 und NO₂ im Verhältnis zu WHO-Grenzwerten (0 = sehr gut, 100 = sehr schlecht).")

    pm10_val = df_year['PM10'].mean()
    no2_val  = df_year['NO2'].mean()

    # Normierung: PM10-Anteil (WHO 15 µg/m³) + NO2-Anteil (WHO 25 µg/m³), je 50 Punkte
    pm10_score = min(50, (pm10_val / 15) * 25) if not np.isnan(pm10_val) else 25
    no2_score  = min(50, (no2_val  / 25) * 25) if not np.isnan(no2_val)  else 25
    index_val  = round(pm10_score + no2_score, 1)

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=index_val,
        title={'text': "Luftqualitäts-Index"},
        delta={'reference': 50, 'increasing': {'color': 'red'}, 'decreasing': {'color': 'green'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': 'darkblue'},
            'steps': [
                {'range': [0,  25], 'color': '#2ecc71'},
                {'range': [25, 50], 'color': '#f1c40f'},
                {'range': [50, 75], 'color': '#e67e22'},
                {'range': [75, 100], 'color': '#e74c3c'},
            ],
            'threshold': {
                'line': {'color': 'black', 'width': 4},
                'thickness': 0.75,
                'value': 50,
            },
        },
    ))
    fig_gauge.update_layout(height=350)
    st.plotly_chart(fig_gauge, use_container_width=True)
