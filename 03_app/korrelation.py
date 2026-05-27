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
    df_filtered = df[df["datum"].dt.year >= 2008]
    analyse_df = df_filtered[analyse_variablen]

    korrelation_matrix = analyse_df.corr()

    label_map = {
        "temperatur": "Temperatur",
        "windgeschwindigkeit": "Windgeschwindigkeit",
        "windrichtung": "Windrichtung",
        "luftdruck": "Luftdruck",
        "relative_luftfeuchtigkeit": "rel. Luftfeuchte",
        "niederschlagshoehe_mm": "Niederschlag",
        "sonnenscheindauer_minuten": "Sonnenscheindauer",
        "gesamtbewoelkung": "Bewölkung",
        "o3": "O₃",
        "no2": "NO₂",
        "pm10": "PM10",
        "pm2x5": "PM2.5"
    }

    korrelation_matrix = korrelation_matrix.rename(
        index=label_map,
        columns=label_map
    )

    fig, ax = plt.subplots(figsize=(11.5, 7.2), facecolor="#0e1117")
    ax.set_facecolor("#0e1117")

    sns.heatmap(
        korrelation_matrix,
        annot=True,
        cmap="coolwarm",
        center=0,
        vmin=-1,
        vmax=1,
        fmt=".2f",
        linewidths=0.35,
        linecolor="#2a2f3a",
        annot_kws={
        "size": 9,
        "weight": "normal"
        },
        cbar_kws={
        "label": "Korrelationskoeffizient",
        "shrink": 0.85,
        "pad": 0.09
        },
        ax=ax
    )

    # Titel
    ax.set_title(
        "Korrelationsmatrix: Wettervariablen und Luftschadstoffe",
        fontsize=14,
        color="white",
        fontweight="semibold",
        pad=43
    )

    ax.set_xlabel("")
    ax.set_ylabel("")

    # Achsenbeschriftungen
    ax.tick_params(
        axis="x",
        labelrotation=38,
        labelsize=10,
        colors="white",
        pad=2
    )

    ax.tick_params(
        axis="y",
        labelrotation=0,
        labelsize=10,
        colors="white",
        pad=2
    )

    # Trennlinien
    trennlinie = 8

    ax.axhline(
        trennlinie,
        color="white",
        linewidth=1.8,
        alpha=0.8
    )

    ax.axvline(
        trennlinie,
        color="white",
        linewidth=1.8,
        alpha=0.8
    )

    # Gruppenüberschriften
    ax.text(
        4,
        -0.55,
        "Wettervariablen",
        ha="center",
        va="center",
        fontsize=11,
        color="#d1d5db",
        fontweight="semibold"
    )

    ax.text(
        10,
        -0.55,
        "Luftschadstoffe",
        ha="center",
        va="center",
        fontsize=11,
        color="#d1d5db",
        fontweight="semibold"
    )

    # Colorbar optimieren
    cbar = ax.collections[0].colorbar

    cbar.ax.yaxis.label.set_color("white")
    cbar.ax.yaxis.label.set_size(11)
    cbar.ax.yaxis.label.set_weight("semibold")
    cbar.ax.yaxis.labelpad = 18
    cbar.ax.tick_params(
        colors="white",
        labelsize=9
    )

    # Außenabstände
    plt.tight_layout(pad=2.8)

    return korrelation_matrix, fig


def korrelation(dfO, stoff):
    analyse_variablen = [
        "temperatur", "windgeschwindigkeit", "windrichtung", "luftdruck",
        "relative_luftfeuchtigkeit", "niederschlagshoehe_mm", 
        "sonnenscheindauer_minuten", "gesamtbewoelkung", "o3", "no2", "pm10", "pm2x5"
    ]
    
    korrelation_matrix, fig = berechne_und_plotte_korrelation(dfO, analyse_variablen)
    
    #st.subheader("Korrelationsmatrix")
    st.pyplot(fig, use_container_width=True)


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