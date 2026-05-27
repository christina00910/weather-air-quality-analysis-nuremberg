import pandas as pd
import seaborn as sns
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor

@st.cache_data
def get_cached_annual_trend(df, stoff, min_hours_per_year=6132): # 8760 * 0.7 = 6132
    """
    Berechnet den Jahrestrend extrem schnell und speichert das Ergebnis im Cache.
    Wichtig: Das Datum MUSS hierfür bereits im Hauptskript einmalig 
    mit pd.to_datetime() konvertiert worden sein!
    """
    # Nur die benötigten Spalten extrahieren (verhindert Speicher-Overhead)
    df_temp = df[['datum', stoff]].dropna().set_index('datum')
    
    # Schnelle, vektorisierte Aggregations-Logik ohne Lambda-Overhead
    # .count() zählt automatisch nur Nicht-Null-Werte
    annual_counts = df_temp[stoff].resample('YE').count()
    annual_means = df_temp[stoff].resample('YE').mean()
    
    # Filter anwenden: Nur Jahre mit genug Datenpunkten behalten
    valid_years = annual_counts[annual_counts >= min_hours_per_year].index
    chart_data = annual_means.loc[valid_years].reset_index()
    
    return chart_data

def calcMeanYear(df, stoff):
    """
    Reine Plotting-Funktion. Sie holt die berechneten Daten aus dem 
    Cache und zeichnet die Matplotlib-Figur in Millisekunden.
    """
    # Daten aus der ultraschnellen Cache-Funktion holen
    chart_data = get_cached_annual_trend(df, stoff)
    
    if chart_data.empty:
        st.warning(f"Keine ausreichenden Daten für {stoff} vorhanden (min. 70% Abdeckung benötigt).")
        return None

    # ========================================================
    # MATPLOTLIB-DARSTELLUNG (Kompakt, Dark Mode, Ohne Legende)
    # ========================================================
    fig, ax = plt.subplots(figsize=(6, 4), facecolor='black')
    ax.set_facecolor('black')
    
    ax.plot(
        chart_data['datum'].dt.year,  # Jahreszahl extrahieren
        chart_data[stoff],
        color='#4A90E2',              
        marker='o',                   
        markerfacecolor='white',      
        markeredgecolor='#4A90E2',
        linewidth=2
    )
    
    # Layout & Design
    ax.set_title(f"Jahresmittelwert Trend für {stoff.upper()}", color='white', fontsize=11, fontweight="bold")
    ax.set_xlabel("Jahr", color='white', fontsize=9)
    ax.set_ylabel(r"Mittlere Konzentration [$\mathrm{\mu g/m^3}$]", color='white', fontsize=9)
    ax.tick_params(colors='white', which='both', labelsize=8)
    
    for spine in ax.spines.values():
        spine.set_color('white')
        
    ax.grid(axis="both", linestyle="--", alpha=0.3, color='dimgray')
    ax.xaxis.get_major_locator().set_params(integer=True)
    
    plt.tight_layout()
    return fig

@st.cache_data
def get_cached_seasonal_pattern(df, stoff):
    """
    Berechnet die monatlichen Mittelwerte im Jahrzehntvergleich im Hintergrund.
    Setzt voraus, dass 'datum' bereits im Hauptskript einmalig als 
    Datetime-Objekt definiert wurde.
    """
    if 'datum' not in df.columns or stoff not in df.columns:
        return pd.DataFrame()
        
    # Lokale, schlanke Zuweisung (verhindert .copy() des gesamten DataFrames)
    df_temp = df[['datum', stoff]].dropna()
    
    # Schnelle Gruppierung über die Datetime-Properties (.dt)
    # Das unstack() wird direkt hier einmalig berechnet und im RAM gecacht
    monthly_means = df_temp.groupby([df_temp['datum'].dt.year, df_temp['datum'].dt.month])[stoff].mean().unstack()
    return monthly_means

def calcMeanSaisonYear(df, stoff):
    """
    Reine Plotting-Funktion. Holt die Pivot-Tabelle aus dem Cache
    und zeichnet den Jahrzehntvergleich extrem zügig.
    """
    # Daten aus der ultraschnellen Cache-Funktion laden
    monthly_means = get_cached_seasonal_pattern(df, stoff)
    
    if monthly_means.empty:
        st.warning(f"Keine ausreichenden Daten für {stoff} zur Saisonberechnung vorhanden.")
        return None

    # ========================================================
    # MATPLOTLIB-DARSTELLUNG (Kompakt, Dark Mode, Ohne Legende)
    # ========================================================
    fig, ax = plt.subplots(figsize=(6, 4), facecolor='black')
    ax.set_facecolor('black')

    # Ziel-Jahre und Kontrastfarben für den Dark Mode
    jahre = [1990, 2000, 2010, 2020]
    farben = ["#FF6B6B", "#4DCD94", "#4A90E2", "#F5A623"]
    
    for jahr, farbe in zip(jahre, farben):
        if jahr in monthly_means.index:
            daten_jahr = monthly_means.loc[jahr]
            
            # Linie zeichnen
            ax.plot(
                daten_jahr,
                color=farbe,
                marker="o",
                markersize=4,
                linewidth=1.5
            )
            
            # WICHTIG: Absicherung gegen leere Jahre, damit index[-1] nicht abstürzt
            letzte_gültige = daten_jahr.dropna()
            if not letzte_gültige.empty:
                letzter_monat = letzte_gültige.index[-1]
                letzter_wert = letzte_gültige[letzter_monat]
                
                # Jahreszahl direkt rechts an das Ende der Linie schreiben
                ax.text(
                    letzter_monat + 0.1, letzter_wert, str(jahr), 
                    color=farbe, fontsize=8, va='center', fontweight='bold'
                )

    # Titel und Beschriftungen
    ax.set_title(
        f"Saisonales {stoff.upper()}-Muster im Jahrzehntvergleich", 
        color='white', 
        fontsize=11, 
        fontweight="bold"
    )
    ax.set_xlabel("Monat", color='white', fontsize=9)
    ax.set_ylabel(r"Mittlere Konzentration [$\mathrm{\mu g/m^3}$]", color='white', fontsize=9)
    
    # Achsen-Gestaltung
    ax.set_xticks(range(1, 13))
    ax.tick_params(colors='white', which='both', labelsize=8)
    
    for spine in ax.spines.values():
        spine.set_color('white')
        
    ax.grid(True, linestyle="--", alpha=0.3, color='dimgray')
    ax.set_xlim(0.5, 13.5)
    
    plt.tight_layout()
    return fig
@st.cache_data
def get_cached_rush_hour(df, stoff):
    """
    Aggregiert die Daten blitzschnell auf Stundenbasis im Hintergrund.
    Es wird kein teures 'to_timedelta' mehr benötigt.
    """
    if stoff not in df.columns:
        return pd.DataFrame()
        
    # Sicherstellen, dass die Stunden-Spalte als Integer vorliegt
    if 'stunde' in df.columns:
        df_temp = df[['stunde', stoff]].dropna()
        hour_col = 'stunde'
    elif 'datum' in df.columns:
        # Falls keine 'stunde'-Spalte da ist, extrahieren wir sie direkt aus dem Datum
        df_temp = df[['datum', stoff]].dropna()
        df_temp['hour_extracted'] = df_temp['datum'].dt.hour
        hour_col = 'hour_extracted'
    else:
        return pd.DataFrame()

    # Vektorisierte Gruppenbildung (ergibt exakt 24 Zeilen)
    rush_data = df_temp.groupby(hour_col)[stoff].mean().reset_index()
    rush_data.columns = ['hour', stoff]
    return rush_data

def rushHourEffekt(df, stoff):
    """
    Reine Plotting-Funktion. Zeichnet die 24 aggregierten Stundenpunkte 
    ohne den Overhead von Seaborn.
    """
    # Daten aus dem ultraschnellen Cache holen
    rush_data = get_cached_rush_hour(df, stoff)
    
    if rush_data.empty:
        st.warning(f"Spalte für {stoff} oder Zeitspalten fehlen zur Rush-Hour-Analyse.")
        return None

    # 1. Standard-Stile zurücksetzen
    plt.rcParams.update(plt.rcParamsDefault)
    
    # 2. Plot mit schwarzem Hintergrund initialisieren
    fig, ax = plt.subplots(figsize=(10, 4), facecolor='black')
    ax.set_facecolor('black')
    
    # 4. Standard Matplotlib-Plot nutzen (viel schneller als sns.lineplot auf Rohdaten!)
    ax.plot(
        rush_data["hour"], 
        rush_data[stoff], 
        color='white',
        marker="o", 
        markerfacecolor='white', 
        markeredgecolor='black',
        linewidth=2
    )
    
    # 5. Alle Textelemente explizit WEISS färben
    ax.set_title(f"Mittlerer {stoff.upper()}-Tagesverlauf (Rush-Hour-Effekt)", color='white', fontsize=12, pad=10)
    ax.set_xlabel("Uhrzeit", color='white')
    ax.set_ylabel(f"{stoff.upper()} [µg/m³]", color='white')
    
    # Achsenabschnitte (Ticks) und Beschriftungen weiß färben
    ax.tick_params(colors='white', which='both')
    
    # Die äußeren Rahmenlinien (Spines) weiß färben
    for spine in ax.spines.values():
        spine.set_color('white')
        
    # Gitterlinien dezent grau/weiß für gute Sichtbarkeit auf Schwarz
    ax.set_xticks(range(0, 24))
    ax.grid(True, color='dimgray', linestyle='--', linewidth=0.5)
    
    # Layout anpassen, damit nichts abgeschnitten wird
    fig.tight_layout()
    
    return fig
# ==============================================================================
# OPTIMIERUNG FÜR: getKorrelation
# ==============================================================================

@st.cache_data
def get_cached_correlation(df):
    """Berechnet die Korrelationsmatrix exakt EINMALIG im Hintergrund."""
    exclude_cols = ['datum', 'stunde', 'hour', 'timestamp', 'windklasse', 'wettertyp', 'season']
    valid_cols = [
        c for c in df.columns
        if c.lower() not in exclude_cols and np.issubdtype(df[c].dtype, np.number)]
    return df[valid_cols].corr(numeric_only=True)


def getKorrelation(df, stoff):
    """Reine Darstellungsfunktion für die Korrelationsmatrix."""
    stoff_lower = stoff.lower()

    # 1. Gecachte Matrix abrufen
    corr_matrix = get_cached_correlation(df)

    if corr_matrix.empty:
        st.warning("Keine numerischen Spalten für eine Korrelation vorhanden.")
        return None

    # 2. Spezifische Stoff-Korrelation herausholen & anzeigen
    if stoff_lower in corr_matrix.columns:
        korrelationen = corr_matrix[stoff_lower].sort_values(ascending=False)

        with st.expander(f"Korrelationen mit {stoff.upper()} anzeigen"):
            st.dataframe(
                korrelationen.to_frame(name="Korrelationskoeffizient"),
                use_container_width=True)
    else:
        st.warning(f"Schadstoff '{stoff}' wurde in der Korrelationsmatrix nicht gefunden.")

    # 3. Visuelle Heatmap
    fig, ax = plt.subplots(figsize=(15, 9))

    sns.heatmap(
        corr_matrix,
        annot=True,
        cmap="coolwarm",
        fmt=".2f",
        annot_kws={"size": 9},
        linewidths=0.4,
        linecolor="white",
        cbar_kws={"shrink": 0.75, "label": "Korrelationskoeffizient"},
        ax=ax)
    ax.set_title(
        "Korrelationsmatrix Wetterdaten und Luftschadstoffe",
        fontsize=18,
        pad=20)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis="x", labelrotation=45, labelsize=10)
    ax.tick_params(axis="y", labelrotation=0, labelsize=10)


# ==============================================================================
# OPTIMIERUNG FÜR: getEinfluss
# ==============================================================================

def getEinfluss(df, stoff):
    """
    Erstellt die zwei Diagramme nebeneinander (Windklasse vs. Temperatur).
    Reagiert dynamisch auf den gewählten Stoff und läuft dank Daten-Sampling blitzschnell.
    """
    stoff_lower = stoff.lower()
    
    # Prüfen, ob der gewählte Schadstoff überhaupt existiert
    if stoff_lower not in df.columns:
        st.error(f"Der Schadstoff '{stoff}' existiert nicht im Datensatz.")
        return None

    # Figure mit zwei Diagrammen nebeneinander erstellen
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # --- DIAGRAMM 1: Windgeschwindigkeit ---
    # Suchen der Wind-Spalte (unabhängig von Groß-/Kleinschreibung)
    wind_col = next((c for c in df.columns if c.lower() in ['windgeschwindigkeit', 'windg']), None)
    
    if wind_col:
        # Nur benötigte Spalten extrahieren (verhindert .copy()-Ballast der Gesamttabelle)
        df_wind = df[[wind_col, stoff_lower]].dropna().copy()
        
        df_wind["Windklasse"] = pd.cut(
            df_wind[wind_col],
            bins=[-1, 1, 2, 4, 6, 12],
            labels=[
                "Windstill (<1 m/s)",
                "Schwach (1-2 m/s)",
                "Mäßig (2-4 m/s)",
                "Frisch (4-6 m/s)",
                "Stark (>6 m/s)",
            ],
        )

        sns.boxplot(
            ax=ax1,
            data=df_wind,
            x="Windklasse",
            y=stoff_lower,
            hue="Windklasse",
            palette="Blues_r",
            showfliers=False,
            legend=False,
        )

        ax1.set_title(
            f"1. Einfluss der Windgeschwindigkeit auf {stoff.upper()}\n(Je mehr Wind, desto sauberer die Luft)",
            fontsize=12, fontweight="bold"
        )
        ax1.set_xlabel("Windgeschwindigkeit Klasse")
        ax1.set_ylabel(fr"{stoff.upper()}-Konzentration [$\mathrm{{\mu g/m^3}}$]")
        ax1.grid(axis="y", linestyle="--", alpha=0.7)
    else:
        ax1.text(0.5, 0.5, "Spalte 'windgeschwindigkeit' nicht im Datensatz.", ha='center', va='center', fontsize=12)

    # --- DIAGRAMM 2: Temperatur & Inversions-Effekt ---
    temp_col = next((c for c in df.columns if c.lower() in ['temperatur', 'temp']), None)
    
    if temp_col:
        df_temp = df[[temp_col, stoff_lower]].dropna()
        
        # 🔥 PERFORMANCE-HEBEL: Wenn der Datensatz sehr groß ist, ziehen wir eine repräsentative Stichprobe.
        # Das verhindert, dass 'lowess=True' die App für Minuten einfriert!
        if len(df_temp) > 3000:
            df_temp = df_temp.sample(n=3000, random_state=42)

        sns.regplot(
            ax=ax2,
            data=df_temp,
            x=temp_col,
            y=stoff_lower,
            scatter_kws={"alpha": 0.3, "color": "tab:orange", "s": 10},
            line_kws={"color": "darkred", "linewidth": 2},
            lowess=True,  # Läuft jetzt dank max. 3000 Punkten in Millisekunden
        )
        
        ax2.set_title(
            f"2. Einfluss der Temperatur auf {stoff.upper()}\n(Höhere Werte im kalten Winter / Heizperiode)",
            fontsize=12, fontweight="bold"
        )
        ax2.set_xlabel("Temperatur [°C]")
        ax2.set_ylabel(fr"{stoff.upper()}-Konzentration [$\mathrm{{\mu g/m^3}}$]")
        ax2.grid(True, linestyle="--", alpha=0.7)
    else:
        ax2.text(0.5, 0.5, "Spalte 'temperatur' nicht im Datensatz.", ha='center', va='center', fontsize=12)

    plt.tight_layout()
    return fig

@st.cache_data
def process_inversionswetter(df, stoff_lower):
    """
    Berechnet die Inversions-Bedingung einmalig im Hintergrund.
    Extrahiert nur die benötigten Daten, um den Speicher zu entlasten.
    """
    required_weather = ['windgeschwindigkeit', 'gesamtbewoelkung', 'luftdruck']
    
    # Prüfen, ob alle benötigten Wetterspalten existieren
    if not all(col in df.columns for col in required_weather) or stoff_lower not in df.columns:
        return pd.DataFrame()
        
    # Nur relevante Spalten kopieren (sehr leichtgewichtig)
    df_mini = df[required_weather + [stoff_lower]].dropna().copy()
    
    # Vektorisierte Zuweisung der Wetterlage
    inversions_wetter = (df_mini['windgeschwindigkeit'] < 1.5) & \
                        (df_mini['gesamtbewoelkung'] <= 2) & \
                        (df_mini['luftdruck'] > 1020)
                        
    df_mini['Wettertyp'] = np.where(inversions_wetter, 'Inversionslage (wolkenlos & windstill)', 'Normales Wetter')
    return df_mini[['Wettertyp', stoff_lower]]

def inversionswetter(df, stoff):
    """
    Reine Plotting-Funktion. Holt die vorbereiteten Daten aus dem Cache 
    und rendert das Boxplot ohne Verzögerung.
    """
    stoff_lower = stoff.lower()
    
    # Daten aus dem Cache abrufen
    df_plot = process_inversionswetter(df, stoff_lower)
    
    # Standard-Stile zurücksetzen
    plt.rcParams.update(plt.rcParamsDefault)
    
    fig, ax = plt.subplots(figsize=(7, 6), facecolor='black')
    ax.set_facecolor('black')
    
    farben = {
        "Normales Wetter": "#4A90E2",      
        "Inversionslage (wolkenlos & windstill)": "#FF6B6B", 
    }

    # Absicherung: Prüfen, ob die Cache-Tabelle befüllt wurde
    if not df_plot.empty:
        sns.boxplot(
            ax=ax,
            data=df_plot,
            x="Wettertyp",
            y=stoff_lower,
            hue="Wettertyp",
            palette=farben,
            showfliers=False,
            legend=False
        )
    else:
        ax.text(0.5, 0.5, f"Schadstoff '{stoff}' oder Wetterdaten\nfehlen im Datensatz", 
                color='white', ha='center', va='center', transform=ax.transAxes, fontsize=12)

    # Styling an Dark Mode anpassen
    ax.set_xlabel("")
    ax.set_ylabel(r"Konzentration [$\mathrm{\mu g/m^3}$]", color='white')
    ax.tick_params(colors='white', which='both')
    
    for spine in ax.spines.values():
        spine.set_color('white')
        
    ax.grid(axis="y", linestyle="--", alpha=0.3, color='dimgray')

    # Dynamische LaTeX-Titelvergabe je nach gewähltem Schadstoff
    if stoff_lower == "no2":
        ax.set_title(r"Stickstoffdioxid ($\mathrm{NO_2}$)" + "\n" + r"(Verkehrs- & Heizungsstau)", color='white', fontsize=12)
    elif stoff_lower == "pm10":
        ax.set_title(r"Feinstaub ($\mathrm{PM_{10}}$)" + "\n" + r"(Starke Akkumulation bei Inversion)", color='white', fontsize=12)
    elif stoff_lower == "o3":
        ax.set_title(r"Ozon ($\mathrm{O_3}$)" + "\n" + r"(Abbau am Boden bei Smog)", color='white', fontsize=12)
    else:
        ax.set_title(f"{stoff.upper()}-Profil im Vergleich", color='white', fontsize=12)

    plt.suptitle(
        f"Einfluss der Wetterlage auf {stoff.upper()}",
        fontsize=13,
        fontweight="bold",
        color="white"
    )
    
    plt.tight_layout()
    return fig

@st.cache_data
def process_smog_data(df, stoff):
    """
    Berechnet die historische Smog-Statistik ab 1990 im Hintergrund.
    Setzt voraus, dass das Datum bereits einmalig im Hauptskript als Datetime vorliegt.
    """
    stoff_lower = stoff.lower()
    if stoff_lower not in df.columns or 'windgeschwindigkeit' not in df.columns or 'luftdruck' not in df.columns:
        return pd.DataFrame(), pd.DataFrame()

    # Nur benötigte Spalten filtern (spart massiv Arbeitsspeicher)
    # Falls keine 'timestamp'-Spalte existiert, bauen wir sie ressourcenschonend über den Datetime-Index
    df_temp = df[['datum', 'hour', 'windgeschwindigkeit', 'luftdruck', stoff_lower]].dropna().copy()
    
    # Schneller Zeitstempel-Zusammenbau ohne langsame timedelta-Schleifen
    df_temp['timestamp'] = df_temp['datum'] + pd.to_timedelta(df_temp['hour'], unit='h')
    df_temp.set_index('timestamp', inplace=True)
    
    # Filtern ab 1990
    df_filtered = df_temp[df_temp.index >= "1990-01-01"].copy()
    if df_filtered.empty:
        return pd.DataFrame(), pd.DataFrame()

    # Jahrzehnte berechnen
    df_filtered["Jahr"] = df_filtered.index.year
    df_filtered["Dekade"] = (df_filtered["Jahr"] // 10) * 10
    df_filtered["Dekade_Str"] = df_filtered["Dekade"].astype(str) + "er"

    # Smog-Stunden identifizieren
    stunden_mit_smog = (df_filtered["windgeschwindigkeit"] <= 1.5) & (df_filtered["luftdruck"] >= 992)
    
    # Smog-Tage ermitteln (mindestens 4 Smog-Stunden pro Tag)
    smog_stunden_pro_tag = stunden_mit_smog.resample("D").sum()
    smog_tage_set = set(smog_stunden_pro_tag[smog_stunden_pro_tag >= 4].index.date)

    # Tagestyp zuweisen (Extrem schnell via List-Comprehension auf Set-Basis)
    df_filtered["Tagestyp"] = ["Smogtag" if d in smog_tage_set else "Normaltag" for d in df_filtered.index.date]

    # Numerische Aggregation für die Tabelle & den Plot
    vergleich_tabelle = (
        df_filtered.groupby(["Dekade_Str", "Tagestyp"], observed=False)[stoff_lower]
        .mean()
        .unstack()
    )

    # Prozentualen Schadstoff-Aufschlag berechnen
    if "Smogtag" in vergleich_tabelle.columns and "Normaltag" in vergleich_tabelle.columns:
        vergleich_tabelle["Smog-Aufschlag (%)"] = (
            (vergleich_tabelle["Smogtag"] - vergleich_tabelle["Normaltag"])
            / vergleich_tabelle["Normaltag"]
        ) * 100

    return df_filtered[["Dekade_Str", "Tagestyp", stoff_lower]], vergleich_tabelle


def smogVSNormal(df, stoff):
    """
    Reine Plot- und Bereitstellungsfunktion.
    Gibt die fertige Figure und das aggregierte Dataframe zurück.
    """
    stoff_lower = stoff.lower()
    
    # Berechnungen aus dem Cache holen
    df_plot, vergleich_tabelle = process_smog_data(df, stoff_lower)
    
    if vergleich_tabelle.empty:
        st.warning(f"Keine ausreichenden Daten für die Smog-Analyse von {stoff} vorhanden.")
        return None, pd.DataFrame()

    # ========================================================
    # GRAFISCHE DARSTELLUNG (Kompakt & Dark Mode)
    # ========================================================
    plt.rcParams.update(plt.rcParamsDefault)
    fig, ax = plt.subplots(figsize=(6, 4), facecolor='black')
    ax.set_facecolor('black')

    # Schneller nativer Matplotlib-Bar-Plot über Pivot-Tabelle statt Seaborn-Rohdaten-Loop
    plot_data = vergleich_tabelle[["Normaltag", "Smogtag"]].dropna()
    
    x = np.arange(len(plot_data.index))
    width = 0.35

    ax.bar(x - width/2, plot_data["Normaltag"], width, label="Normaltag", color="#4A90E2")
    ax.bar(x + width/2, plot_data["Smogtag"], width, label="Smogtag", color="#FF6B6B")

    # Grenzwert einzeichnen
    if stoff_lower == "no2":
        ax.axhline(
            y=40, color="white", linestyle="--", linewidth=1,
            label=r"Jahresgrenzwert ($40\ \mathrm{\mu g/m^3}$)",
        )

    # Achsen-Beschriftungen & Styling
    ax.set_title(f"{stoff.upper()}-Belastung: Smog- vs. Normaltage", color='white', fontsize=11, fontweight="bold")
    ax.set_xlabel("Jahrzehnt (Dekade)", color='white', fontsize=9)
    ax.set_ylabel(r"Mittlere Konzentration [$\mathrm{\mu g/m^3}$]", color='white', fontsize=9)
    
    ax.set_xticks(x)
    ax.set_xticklabels(plot_data.index)
    ax.tick_params(colors='white', which='both', labelsize=8)
    
    for spine in ax.spines.values():
        spine.set_color('white')

    ax.grid(axis="y", linestyle="--", alpha=0.3, color='dimgray')
    
    ax.legend(title="Typ des Tages", loc="upper right", 
              facecolor='black', edgecolor='white', labelcolor='white', fontsize=8, title_fontsize=8)

    plt.tight_layout()
    
    return fig, vergleich_tabelle

# ==============================================================================
# OPTIMIERUNG FÜR: analyzeSeasonAndWeekend
# ==============================================================================

@st.cache_data
def process_season_weekend(df, stoff_lower):
    """ Berechnet saisonale Trends und Wochenend-Vergleiche im Hintergrund. """
    if stoff_lower not in df.columns or 'datum' not in df.columns:
        return pd.Series(), pd.Series()
    
    # Nur benötigte Spalten extrahieren (verhindert Speicher-Overhead)
    df_temp = df[['datum', stoff_lower]].dropna().copy()
    
    # Filtern ab 2008
    df_temp = df_temp[df_temp["datum"].dt.year >= 2008]
    if df_temp.empty:
        return pd.Series(), pd.Series()
        
    df_temp["wochentag"] = df_temp["datum"].dt.dayofweek
    df_temp["monat"] = df_temp["datum"].dt.month
    df_temp["wochenende"] = df_temp["wochentag"].isin([5, 6]).astype(int)

    # Vektorisierter Performance-Hebel: Schnelles Mapping statt langsamer .apply()-Schleife
    season_map = {
        12: "Winter", 1: "Winter", 2: "Winter",
        3: "Frühling", 4: "Frühling", 5: "Frühling",
        6: "Sommer", 7: "Sommer", 8: "Sommer",
        9: "Herbst", 10: "Herbst", 11: "Herbst"
    }
    df_temp["season"] = df_temp["monat"].map(season_map)

    # Aggregationen durchführen
    season_order = ["Frühling", "Sommer", "Herbst", "Winter"]
    schadstoff_jahreszeit = df_temp.groupby("season")[stoff_lower].mean().reindex(season_order)
    schadstoff_wochenende = df_temp.groupby("wochenende")[stoff_lower].mean()

    return schadstoff_jahreszeit, schadstoff_wochenende

def analyzeSeasonAndWeekend(df, stoff):
    """ Reine Plotting-Funktion. Holt aggregierte Daten aus dem Cache. """
    stoff_lower = stoff.lower()
    schadstoff_jahreszeit, schadstoff_wochenende = process_season_weekend(df, stoff_lower)

    if schadstoff_jahreszeit.empty or schadstoff_wochenende.empty:
        st.warning(f"Keine ausreichenden Daten ab 2008 für {stoff} vorhanden.")
        return None, None

    plt.rcParams.update(plt.rcParamsDefault)

    # --- DIAGRAMM 1: JAHRESZEIT ---
    fig_season, ax_season = plt.subplots(figsize=(5, 4), facecolor='black')
    ax_season.set_facecolor('black')
    ax_season.bar(schadstoff_jahreszeit.index, schadstoff_jahreszeit.values, color="#4A90E2")
    ax_season.set_title(f"Mittlere {stoff.upper()}-Werte nach Jahreszeit", color='white', fontsize=10, fontweight="bold")
    ax_season.set_xlabel("Jahreszeit", color='white', fontsize=9)
    ax_season.set_ylabel(r"Durchschnittliche Konzentration [$\mathrm{\mu g/m^3}$]", color='white', fontsize=9)
    ax_season.tick_params(colors='white', which='both', labelsize=8)
    for spine in ax_season.spines.values(): spine.set_color('white')
    ax_season.grid(axis="y", linestyle="--", alpha=0.3, color='dimgray')
    fig_season.tight_layout()

    # --- DIAGRAMM 2: WERKTAG VS. WOCHENENDE ---
    fig_weekend, ax_weekend = plt.subplots(figsize=(5, 4), facecolor='black')
    ax_weekend.set_facecolor('black')
    ax_weekend.bar(["Werktag", "Wochenende"], schadstoff_wochenende.values, color="#FF6B6B")
    ax_weekend.set_title(f"{stoff.upper()}: Werktag vs. Wochenende", color='white', fontsize=10, fontweight="bold")
    ax_weekend.set_ylabel(r"Durchschnittliche Konzentration [$\mathrm{\mu g/m^3}$]", color='white', fontsize=9)
    ax_weekend.tick_params(colors='white', which='both', labelsize=8)
    for spine in ax_weekend.spines.values(): spine.set_color('white')
    ax_weekend.grid(axis="y", linestyle="--", alpha=0.3, color='dimgray')
    fig_weekend.tight_layout()

    return fig_season, fig_weekend


# ==============================================================================
# OPTIMIERUNG FÜR: getExceedancesPerYear
# ==============================================================================

@st.cache_data
def process_exceedances(df, stoff_lower):
    """ Berechnet LQI-Überschreitungen extrem schnell im RAM-Cache. """
    lqi_grenzwerte_maessig = {"pm10": 28, "pm2x5": 16, "o3": 73, "no2": 31}
    
    if stoff_lower not in lqi_grenzwerte_maessig or stoff_lower not in df.columns or 'datum' not in df.columns:
        return pd.Series()
        
    grenzwert = lqi_grenzwerte_maessig[stoff_lower]
    df_temp = df[['datum', stoff_lower]].dropna().copy()
    
    # Jahr direkt extrahieren und Zählung über boolesche Maske summieren
    df_temp["jahr"] = df_temp["datum"].dt.year.astype(int)
    df_temp["ab_maessig"] = df_temp[stoff_lower] >= grenzwert
    
    return df_temp.groupby("jahr")["ab_maessig"].sum()

def getExceedancesPerYear(df, stoff):
    """ Zeichnet das Überschreitungsdiagramm in Mikrosekunden. """
    stoff_lower = stoff.lower()
    ueberschreitungen_jahr = process_exceedances(df, stoff_lower)

    if ueberschreitungen_jahr.empty:
        st.warning(f"Schadstoff '{stoff}' wird nicht unterstützt oder Spalten fehlen.")
        return None

    # UI-Ausgaben sauber separiert (läuft nun außerhalb der Logik)
    st.write(f"### 📊 Jährliche Auswertung: LQI-Überschreitungen ({stoff.upper()})")
    st.write(f"### 📈 Stunden mit mindestens mäßiger Luftqualität ({stoff.upper()})")

    plt.rcParams.update(plt.rcParamsDefault)
    fig, ax = plt.subplots(figsize=(5, 3), facecolor='black')
    ax.set_facecolor('black')

    jahre = ueberschreitungen_jahr.index.astype(str)
    ax.bar(jahre, ueberschreitungen_jahr.values, color="#4A90E2")

    ax.set_title(f"Stunden mit mindestens mäßiger Luftqualität: {stoff.upper()}", color='white', fontsize=10, fontweight="bold")
    ax.set_xlabel("Jahr", color='white', fontsize=9)
    ax.set_ylabel("Anzahl belasteter Stunden", color='white', fontsize=9)
    ax.tick_params(colors='white', which='both', labelsize=8)
    
    # Ticks ausdünnen, damit Achsenbeschriftungen nicht überlappen
    ax.set_xticks(range(0, len(jahre), 5))
    ax.set_xticklabels(jahre[::5], rotation=45, ha='right')
    
    for spine in ax.spines.values(): spine.set_color('white')
    ax.grid(axis="y", linestyle="--", alpha=0.3, color='dimgray')

    plt.tight_layout()
    return fig

