import streamlit as st
import pandas as pd
import statsmodels.api as sm
import seaborn as sns
import matplotlib.pyplot as plt

# Globale Layout-Einstellungen einmalig setzen, nicht in den Funktionen
plt.style.use("dark_background")


# 1. OPTIMIERUNG: Caching für die rechenintensive Korrelationsmatrix und Grafik
@st.cache_data(show_spinner="Berechne Korrelationsmatrix...")
def berechne_und_plotte_korrelation(df, analyse_variablen):
    # Filterung direkt auf dem DataFrame ohne vorheriges teures Kopieren
    df_filtered = df[df["datum"].dt.year >= 2008]
    analyse_df = df_filtered[analyse_variablen]
    
    # Korrelation berechnen
    korrelation_matrix = analyse_df.corr()
    
    # Heatmap-Grafik erstellen und im Cache speichern
    fig, ax = plt.subplots(figsize=(12, 8), facecolor='#0e1117')
    ax.set_facecolor('#0e1117')
    sns.heatmap(
        korrelation_matrix,
        annot=True,
        cmap="coolwarm",
        fmt=".2f",
        ax=ax,
        cbar_kws={'label': 'Korrelationskoeffizient'}
    )
    ax.set_title("Korrelationsmatrix Wetterdaten und Luftschadstoffe")
    plt.tight_layout()
    
    return korrelation_matrix, fig


def korrelation(dfO, stoff):
    # Relevante Variablen für die Korrelationsanalyse
    analyse_variablen = [
        "temperatur", "windgeschwindigkeit", "windrichtung", "luftdruck",
        "relative_luftfeuchtigkeit", "niederschlagshoehe_mm", 
        "sonnenscheindauer_minuten", "gesamtbewoelkung", "o3", "no2", "pm10", "pm2x5"
    ]
    
    # Nutzt die gecachte Funktion (Verhindert sekundenlanges Laden bei Klicks)
    korrelation_matrix, fig = berechne_und_plotte_korrelation(dfO, analyse_variablen)
    
    # Zeigt die Tabelle mit farblicher Heatmap an
    st.subheader("Korrelationsmatrix")
    st.dataframe(korrelation_matrix.style.background_gradient(cmap='coolwarm', axis=None).format("{:.2f}"))
    
    # Grafik direkt in Streamlit anzeigen
    st.pyplot(fig)


# 2. OPTIMIERUNG: Caching der Statistischen Regression (Verhindert OLS-Neuberechnung bei Reruns)
@st.cache_data(show_spinner="Berechne Regression...")
def berechne_regression(df, schadstoff):
    df_filtered = df[df["datum"].dt.year >= 2008]
    
    # Spalten direkt selektieren
    wetter_variablen = [
        "temperatur", "windgeschwindigkeit", "windrichtung", "luftdruck",
        "relative_luftfeuchtigkeit", "niederschlagshoehe_mm", 
        "sonnenscheindauer_minuten", "gesamtbewoelkung"
    ]
    
    # Datensatz für Regression vorbereiten - Fehlende Werte performant entfernen
    regression_df = df_filtered[wetter_variablen + [schadstoff]].dropna()
    
    x = regression_df[wetter_variablen]
    y = regression_df[schadstoff]
    
    # Konstante hinzufügen
    x = sm.add_constant(x)
    
    # Regression durchführen
    modell = sm.OLS(y, x).fit()
    
    # Ergebnisse extrahieren
    regression_ergebnisse = pd.DataFrame({
        "Variable": modell.params.index,
        "Koeffizient": modell.params.values,
        "p-Wert": modell.pvalues.values
    })
    
    # Konstante entfernen
    regression_ergebnisse = regression_ergebnisse[regression_ergebnisse["Variable"] != "const"]
    
    # Signifikanz bewerten
    regression_ergebnisse["Signifikant"] = regression_ergebnisse["p-Wert"].apply(
        lambda p: "Ja" if p < 0.05 else "Nein"
    )
    
    # Werte formatieren
    regression_ergebnisse["Koeffizient"] = regression_ergebnisse["Koeffizient"].round(3)
    regression_ergebnisse["p-Wert"] = regression_ergebnisse["p-Wert"].apply(
        lambda p: "< 0.001" if p < 0.001 else round(p, 4)
    )
    
    return modell.rsquared, regression_ergebnisse


def multipleLinearRegression(dfO, stoff):
    # Berechnungen auslagern und cachen
    r2, regression_ergebnisse = berechne_regression(dfO, stoff)
    
    # Ergebnisse in Streamlit anzeigen
    st.subheader(f"Multiple lineare Regression für {stoff.upper()}")
    
    # Metriken darstellen
    col1, col2 = st.columns(2)
    col1.metric("R²-Score", f"{r2:.3f}")
    col2.caption("Signifikanzniveau: p < 0.05")
    
    # Schicke Web-Tabelle anzeigen
    st.dataframe(regression_ergebnisse, use_container_width=True)