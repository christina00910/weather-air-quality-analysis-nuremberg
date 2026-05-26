# Fragestellung:
# Gibt es einen statistisch signifikanten Zusammenhang zwischen Wetter und Luftschadstoffen?

# Bibliotheken Laden

import streamlit as st
import pandas as pd
import statsmodels.api as sm
import seaborn as sns
import matplotlib.pyplot as plt

def korrelation (dfO, stoff) :
    # Der Datensatz enthält:
    # - 394488 Zeilen (Beobachtungen)
    # - 30 Spalten (Wetter- und Luftschadstoffvariablen)
    # - Wetterdaten und Luftschadstoffe wurden erfolgreich zusammengeführt
    # - Die meisten numerischen Variablen liegen als float vor
    # - datum ist aktuell als String gespeichert und kann später in datetime umgewandelt werden
    
    # Bewertung:
    # Der Datensatz enthält einige fehlende Werte, insbesondere bei Niederschlag
    # und Sonnenscheindauer. Dies ist bei meteorologischen Zeitreihen üblich,
    # da bestimmte Messungen nicht durchgehend verfügbar sind oder nur unter
    # bestimmten Wetterbedingungen auftreten.
    #
    # Die vielen fehlenden Werte bei PM2.5 sind fachlich erklärbar, da PM2.5
    # erst ab 2008 im Datensatz verfügbar ist. Die Regressionsanalyse wird deshalb 
    # auf die Jahre 2008-2024 beschränkt, um eine konsistente Datenbasis zu gewährleisten.

    df = dfO.copy ()
    # Analysezeitraum ab 2008 Um eine einheitliche und vergleichbare Datenbasis zu gewährleisten
    df = df[df["datum"].dt.year >= 2008]
    
    # Relevante Variablen für die Korrelationsanalyse
    analyse_variablen = [
        "temperatur",
        "windgeschwindigkeit",
        "windrichtung",
        "luftdruck",
        "relative_luftfeuchtigkeit",
        "niederschlagshoehe_mm",
        "sonnenscheindauer_minuten",
        "gesamtbewoelkung",
        "o3",
        "no2",
        "pm10",
        "pm2x5"]
    
    # Datensatz für Analyse erstellen
    analyse_df = df[analyse_variablen]
    
    # Korrelationen berechnen
    korrelation = analyse_df.corr()
    # Zeigt die Tabelle mit farblicher Heatmap (von blau nach rot) an
    st.subheader("Korrelationsmatrix")
    st.dataframe(korrelation.style.background_gradient(cmap='coolwarm', axis=None).format("{:.2f}"))

    plt.style.use("dark_background")
    # Heatmap für Streamlit erstellen
    fig, ax = plt.subplots(figsize=(12, 8), facecolor='#0e1117')
    ax.set_facecolor('#0e1117')
    sns.heatmap(
        korrelation,
        annot=True,
        cmap="coolwarm",
        fmt=".2f",
        ax=ax,  # Übergibt das Achsen-Objekt an Seaborn
        cbar_kws={'label': 'Korrelationskoeffizient'} # Beschriftung der Farbleiste
    )
    ax.set_title("Korrelationsmatrix Wetterdaten und Luftschadstoffe")
    plt.tight_layout()
    
    # Grafik direkt in Streamlit anzeigen
    st.pyplot(fig)
    
    # Bewertung der Korrelationsmatrix:
    # - Temperatur und Ozon: r = 0.63
    #   Starke positive Korrelation. Höhere Temperaturen gehen häufig mit höheren Ozonwerten einher.
    #
    # - Relative Luftfeuchtigkeit und Ozon: r = -0.72
    #   Starke negative Korrelation. Höhere Luftfeuchtigkeit geht häufig mit niedrigeren Ozonwerten einher.
    #
    # - PM10 und PM2.5: r = 0.73
    #   Starke positive Korrelation. Beide Feinstaubarten treten häufig gemeinsam erhöht auf.
    #
    # - Ozon und NO2: r = -0.46
    #   Mittlere negative Korrelation. Höhere Ozonwerte gehen tendenziell mit niedrigeren NO2-Werten einher.
    #
    # - NO2 und PM10: r = 0.43
    #   Mittlere positive Korrelation. Höhere NO2-Werte gehen tendenziell mit höheren PM10-Werten einher.
    #
    # - Sonnenscheindauer und Bewölkung: r = -0.51
    #   Mittlere negative Korrelation. Mehr Sonnenschein geht erwartungsgemäß mit geringerer Bewölkung einher.
    #
    # - Temperatur und relative Luftfeuchtigkeit: r = -0.59
    #   Mittlere bis starke negative Korrelation. Höhere Temperaturen gehen tendenziell mit geringerer relativer Luftfeuchtigkeit einher.
    #
    # Hinweis:
    # Korrelation zeigt nur Zusammenhänge, aber keine eindeutige Ursache-Wirkung.


def multipleLinearRegression (dfO, stoff) :

    df = dfO.copy ()
#---------------------------------------------------------------------------------
# Multiple Lineare Regression
# Die Regression zeigt, wie einzelne Wettervariablen die Luftschadstoffe beeinflussen 
# und ob ein signifikanter positiver oder negativer Zusammenhang besteht. 
# Aufgrund unterschiedlicher Einheiten der Wettervariablen können die Einflussstärken der Koeffizienten 
# jedoch nicht direkt miteinander verglichen werden (z.B. Temperatur mit Niederschlag)

# Zielvariable festlegen
    schadstoff = stoff

    df = df[df["datum"].dt.year >= 2008]

    # Einflussvariablen (Wetterdaten)
    x = df[[
        "temperatur",
        "windgeschwindigkeit",
        "windrichtung",
        "luftdruck",
        "relative_luftfeuchtigkeit",
        "niederschlagshoehe_mm",
        "sonnenscheindauer_minuten",
        "gesamtbewoelkung"]]
    
    # Zielvariable
    y = df[schadstoff]
    
    # Datensatz für Regression vorbereiten - Fehlende Werte entfernen
    regression_df = pd.concat([x, y], axis=1).dropna()
    
    x = regression_df[[
        "temperatur",
        "windgeschwindigkeit",
        "windrichtung",
        "luftdruck",
        "relative_luftfeuchtigkeit",
        "niederschlagshoehe_mm",
        "sonnenscheindauer_minuten",
        "gesamtbewoelkung"]]
    
    y = regression_df[schadstoff]
    
    # Konstante hinzufügen, damit der Achsenabschnitt in der Regression berücksichtigt wird
    x = sm.add_constant(x)
    
    # Regression durchführen
    modell = sm.OLS(y, x).fit()
    print(modell.summary())
    
    # ------------------------------------------------------------
    # Regressionsergebnisse übersichtlich darstellen
    # ------------------------------------------------------------
    
    # Ergebnisse aus dem Regressionsmodell extrahieren
    regression_ergebnisse = pd.DataFrame({
        "Variable": modell.params.index,
        "Koeffizient": modell.params.values,
        "p-Wert": modell.pvalues.values})
    
    # Konstante entfernen, da sie für die Interpretation der Einflussvariablen weniger relevant ist
    regression_ergebnisse = regression_ergebnisse[
        regression_ergebnisse["Variable"] != "const"]
    
    # Signifikanz bewerten
    regression_ergebnisse["Signifikant"] = regression_ergebnisse["p-Wert"].apply(
        lambda p: "Ja" if p < 0.05 else "Nein")
    
    # Werte runden
    regression_ergebnisse["Koeffizient"] = regression_ergebnisse["Koeffizient"].round(3)
    regression_ergebnisse["p-Wert"] = regression_ergebnisse["p-Wert"].apply(lambda p: "< 0.001" if p < 0.001 else round(p, 4))
    
    # R² aus dem Modell auslesen
    r2 = modell.rsquared
    
    # Tabelle anzeigen
    st.subheader("\nÜbersicht Regressionsergebnisse")
    st.write (f"R²: {r2:.3f}")
    st.write (regression_ergebnisse)
    
    
    # ------------------------------------------------------------
    # Grafik als übersichtliche Tabelle erstellen
    # ------------------------------------------------------------
    # Ergebnisse in Streamlit anzeigen (Ersetzt die alten print-Befehle)
    st.subheader(f"Multiple lineare Regression für {schadstoff.upper()}")
    
    # Metriken hübsch darstellen
    col1, col2 = st.columns(2)
    col1.metric("R²-Score", f"{r2:.3f}")
    col2.caption("Signifikanzniveau: p < 0.05")
    
    # Die Tabelle direkt als interaktive, schicke Web-Tabelle anzeigen
    # (Ersetzt den gesamten fig, ax = plt.subplots() und ax.table Block)
    st.dataframe(regression_ergebnisse, use_container_width=True)