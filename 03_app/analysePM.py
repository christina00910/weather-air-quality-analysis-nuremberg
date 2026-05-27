import pandas as pd
import seaborn as sns
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor

@st.cache_data
def get_cached_annual_trend(df, stoff, min_hours_per_year=6132): 
    """Berechnet den Jahrestrend für einen oder zwei Schadstoffe (z.B. pm10 & pm2x5) parallel."""
    # Falls pm10 gewählt wurde und pm2x5 existiert, beide Spalten holen
    stoffe_zu_berechnen = [stoff]
    if stoff == 'pm10' and 'pm2x5' in df.columns:
        stoffe_zu_berechnen.append('pm2x5')
        
    cols = ['datum'] + stoffe_zu_berechnen
    df_temp = df[cols].dropna(subset=['datum']).set_index('datum')
    
    # Aggregation für alle gewählten Stoffe parallel
    annual_counts = df_temp[stoff].resample('YE').count()
    annual_means = df_temp.resample('YE').mean()
    
    # Filter: Jahr ist gültig, wenn die Hauptkomponente genug Datenpunkte hat
    valid_years = annual_counts[annual_counts >= min_hours_per_year].index
    chart_data = annual_means.loc[valid_years].reset_index()
    return chart_data

def calcMeanYear(df, stoff):
    """Zeichnet die Matplotlib-Figur. Bei pm10 wird pm2x5 automatisch als zweite Linie ergänzt."""
    chart_data = get_cached_annual_trend(df, stoff)
    
    if chart_data.empty:
        st.warning(f"Keine ausreichenden Daten für {stoff} vorhanden (min. 70% Abdeckung benötigt).")
        return None

    fig, ax = plt.subplots(figsize=(5, 3), facecolor='black')
    ax.set_facecolor('black')
    
    # 1. Haupt-Schadstoff plotten (z.B. pm10, O3, NO2)
    ax.plot(
        chart_data['datum'].dt.year,
        chart_data[stoff],
        color='#4A90E2',              
        marker='o',                   
        markerfacecolor='white',      
        markeredgecolor='#4A90E2',
        linewidth=1,
        label=stoff.upper()
    )
    
    # 2. pm2x5 Zusatz-Plot, falls pm10 ausgewählt wurde und Daten existieren
    hat_pm25 = (stoff == 'pm10' and 'pm2x5' in chart_data.columns)
    if hat_pm25:
        ax.plot(
            chart_data['datum'].dt.year,
            chart_data['pm2x5'],
            color='#FF6B6B',  # Markantes Hellrot für pm2x5            
            marker='s',       # Quadratische Punkte zur Unterscheidung            
            markerfacecolor='white',      
            markeredgecolor='#FF6B6B',
            linewidth=1,
            linestyle='--',   # Gestrichelte Linie
            label='PM2.5 (pm2x5)'
        )
        # Legende einblenden
        ax.legend(facecolor='black', edgecolor='white', labelcolor='white', loc='upper right', fontsize=8)
    
    # Layout & Design
    titel = f"Jahresmittelwert Trend für {stoff.upper()}" + (" & PM2.5" if hat_pm25 else "")
    ax.set_title(titel, color='white', fontsize=10, fontweight="bold")
    ax.set_xlabel("Jahr", color='white', fontsize=5)
    ax.set_ylabel(r"Mittlere Konzentration [$\mathrm{\mu g/m^3}$]", color='white', fontsize=5)
    ax.tick_params(colors='white', which='both', labelsize=5)
    
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
    fig, ax = plt.subplots(figsize=(5, 3), facecolor='black')
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
                linewidth=1
            )
            
            # WICHTIG: Absicherung gegen leere Jahre, damit index[-1] nicht abstürzt
            letzte_gültige = daten_jahr.dropna()
            if not letzte_gültige.empty:
                letzter_monat = letzte_gültige.index[-1]
                letzter_wert = letzte_gültige[letzter_monat]
                
                # Jahreszahl direkt rechts an das Ende der Linie schreiben
                ax.text(
                    letzter_monat + 0.1, letzter_wert, str(jahr), 
                    color=farbe, fontsize=5, va='center', fontweight='bold'
                )

    # Titel und Beschriftungen
    ax.set_title(
        f"Saisonales {stoff.upper()}-Muster im Jahrzehntvergleich", 
        color='white', 
        fontsize=10, 
        fontweight="bold"
    )
    ax.set_xlabel("Monat", color='white', fontsize=5)
    ax.set_ylabel(r"Mittlere Konzentration [$\mathrm{\mu g/m^3}$]", color='white', fontsize=5)
    
    # Achsen-Gestaltung
    ax.set_xticks(range(1, 13))
    ax.tick_params(colors='white', which='both', labelsize=6)
    
    for spine in ax.spines.values():
        spine.set_color('white')
        
    ax.grid(True, linestyle="--", alpha=0.3, color='dimgray')
    ax.set_xlim(0.5, 13.5)
    
    plt.tight_layout()
    return fig



# ========================================================
# OPTIMIERTE CACHED & PLOTTING FUNKTIONEN (Rush-Hour)
# ========================================================

@st.cache_data
def get_cached_rush_hour(df, stoff):
    """Aggregiert die Daten blitzschnell auf Stundenbasis im Hintergrund."""
    # Falls pm10 gewählt wurde und pm2x5 existiert, beide Spalten holen
    stoffe_zu_berechnen = [stoff]
    if stoff == 'pm10' and 'pm2x5' in df.columns:
        stoffe_zu_berechnen.append('pm2x5')
        
    for s in stoffe_zu_berechnen:
        if s not in df.columns:
            return pd.DataFrame()
        
    # Spalten extrahieren basierend auf Verfügbarkeit von 'stunde' oder 'datum'
    if 'stunde' in df.columns:
        cols = ['stunde'] + stoffe_zu_berechnen
        df_temp = df[cols].dropna()
        hour_col = 'stunde'
    elif 'datum' in df.columns:
        cols = ['datum'] + stoffe_zu_berechnen
        df_temp = df[cols].dropna(subset=['datum']).copy()
        df_temp['hour_extracted'] = df_temp['datum'].dt.hour
        hour_col = 'hour_extracted'
    else:
        return pd.DataFrame()

    # Vektorisierte Gruppenbildung für alle relevanten Spalten
    rush_data = df_temp.groupby(hour_col)[stoffe_zu_berechnen].mean().reset_index()
    rush_data.rename(columns={hour_col: 'hour'}, inplace=True)
    return rush_data

def rushHourEffekt(df, stoff):
    """Zeichnet die aggregierten Stundenpunkte. Bei pm10 inkl. pm2x5."""
    rush_data = get_cached_rush_hour(df, stoff)
    
    if rush_data.empty:
        st.warning(f"Spalte für {stoff.upper()} oder Zeitspalten fehlen zur Rush-Hour-Analyse.")
        return None

    # Standard-Stile zurücksetzen & Black Mode initialisieren
    plt.rcParams.update(plt.rcParamsDefault)
    fig, ax = plt.subplots(figsize=(5, 3), facecolor='black')
    ax.set_facecolor('black')
    
    # 1. Haupt-Schadstoff plotten
    ax.plot(
        rush_data["hour"], 
        rush_data[stoff], 
        color='#4A90E2', # Blau angepasst an das erste Diagramm
        marker="o", 
        markerfacecolor='white', 
        markeredgecolor='#4A90E2',
        linewidth=1,
        label=stoff.upper()
    )
    
    # 2. pm2x5 Zusatz-Plot für pm10 Tagesverlauf
    hat_pm25 = (stoff == 'pm10' and 'pm2x5' in rush_data.columns)
    if hat_pm25:
        ax.plot(
            rush_data["hour"], 
            rush_data['pm2x5'], 
            color='#FF6B6B', # Hellrot
            marker="s", # Quadrate
            markerfacecolor='white', 
            markeredgecolor='#FF6B6B',
            linewidth=1,
            linestyle='--',
            label='PM2.5 (pm2x5)'
        )
        ax.legend(facecolor='black', edgecolor='white', labelcolor='white', loc='upper right', fontsize=5)
    
    # Textelemente färben und beschriften
    titel = f"Mittlerer {stoff.upper()}-Tagesverlauf (Rush-Hour-Effekt)" + (" & PM2.5" if hat_pm25 else "")
    ax.set_title(titel, color='white', fontsize=10, fontweight="bold", pad=10)
    ax.set_xlabel("Uhrzeit (Stunde)", color='white', fontsize=5)
    ax.set_ylabel(f"{stoff.upper()} [µg/m³]", color='white', fontsize=5)
    
    # Achsen-Design
    ax.tick_params(colors='white', which='both', labelsize=5)
    for spine in ax.spines.values():
        spine.set_color('white')
        
    ax.set_xticks(range(0, 24))
    ax.grid(True, color='dimgray', linestyle='--', linewidth=0.5, alpha=0.3)
    
    fig.tight_layout()
    return fig

# ==============================================================================
# OPTIMIERUNG FÜR: getKorrelation
# ==============================================================================

@st.cache_data
def get_cached_correlation(df):
    """Berechnet die Korrelationsmatrix exakt EINMALIG im Hintergrund."""
    # Hilfs- oder Stringspalten vorab filtern, um Berechnung zu beschleunigen
    exclude_cols = ['datum', 'stunde', 'hour', 'timestamp', 'windklasse', 'wettertyp', 'season']
    valid_cols = [c for c in df.columns if c.lower() not in exclude_cols and np.issubdtype(df[c].dtype, np.number)]
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
        st.dataframe(korrelationen.to_frame(name="Korrelationskoeffizient"), width='content')
    else:
        st.warning(f"Schadstoff '{stoff}' wurde in der Korrelationsmatrix nicht gefunden.")

    # 3. Visuelle Heatmap
    fig, ax = plt.subplots(figsize=(5, 3))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    ax.set_title("Korrelationsmatrix der Messreihe")
    plt.tight_layout()
    return fig


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
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(5, 3))

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
            fontsize=10, fontweight="bold"
        )
        ax1.set_xlabel("Windgeschwindigkeit Klasse", color='white', fontsize=5)
        ax1.set_ylabel(fr"{stoff.upper()}-Konzentration [$\mathrm{{\mu g/m^3}}$]")
        ax1.grid(axis="y", linestyle="--", alpha=0.7)
    else:
        ax1.text(0.5, 0.5, "Spalte 'windgeschwindigkeit' nicht im Datensatz.", ha='center', va='center', fontsize=10)

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
            line_kws={"color": "darkred", "linewidth": 1},
            lowess=True,  # Läuft jetzt dank max. 3000 Punkten in Millisekunden
        )
        
        ax2.set_title(
            f"2. Einfluss der Temperatur auf {stoff.upper()}\n(Höhere Werte im kalten Winter / Heizperiode)",
            fontsize=10, fontweight="bold"
        )
        ax2.set_xlabel("Temperatur [°C]", color='white', fontsize=5)
        ax2.set_ylabel(fr"{stoff.upper()}-Konzentration [$\mathrm{{\mu g/m^3}}$]")
        ax2.grid(True, linestyle="--", alpha=0.7)
    else:
        ax2.text(0.5, 0.5, "Spalte 'temperatur' nicht im Datensatz.", ha='center', va='center', fontsize=10)

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
    
    fig, ax = plt.subplots(figsize=(5, 3), facecolor='black')
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
                color='white', ha='center', va='center', transform=ax.transAxes, fontsize=10)

    # Styling an Dark Mode anpassen
    ax.set_xlabel("")
    ax.set_ylabel(r"Konzentration [$\mathrm{\mu g/m^3}$]", color='white', fontsize=5)
    ax.tick_params(colors='white', which='both', labelsize=5)
    
    for spine in ax.spines.values():
        spine.set_color('white')
        
    ax.grid(axis="y", linestyle="--", alpha=0.3, color='dimgray')

    # Dynamische LaTeX-Titelvergabe je nach gewähltem Schadstoff
    if stoff_lower == "no2":
        ax.set_title(r"Stickstoffdioxid ($\mathrm{NO_2}$)" + "\n" + r"(Verkehrs- & Heizungsstau)", color='white', fontsize=10)
    elif stoff_lower == "pm10":
        ax.set_title(r"Feinstaub ($\mathrm{PM_{10}}$)" + "\n" + r"(Starke Akkumulation bei Inversion)", color='white', fontsize=10)
    elif stoff_lower == "o3":
        ax.set_title(r"Ozon ($\mathrm{O_3}$)" + "\n" + r"(Abbau am Boden bei Smog)", color='white', fontsize=10)
    else:
        ax.set_title(f"{stoff.upper()}-Profil im Vergleich", color='white', fontsize=10)

    plt.suptitle(
        f"Einfluss der Wetterlage auf {stoff.upper()}",
        fontsize=5,
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
    fig, ax = plt.subplots(figsize=(5, 3), facecolor='black')
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
    ax.set_title(f"{stoff.upper()}-Belastung: Smog- vs. Normaltage", color='white', fontsize=10, fontweight="bold")
    ax.set_xlabel("Jahrzehnt (Dekade)", color='white', fontsize=5)
    ax.set_ylabel(r"Mittlere Konzentration [$\mathrm{\mu g/m^3}$]", color='white', fontsize=5)
    
    ax.set_xticks(x)
    ax.set_xticklabels(plot_data.index)
    ax.tick_params(colors='white', which='both', labelsize=8)
    
    for spine in ax.spines.values():
        spine.set_color('white')

    ax.grid(axis="y", linestyle="--", alpha=0.3, color='dimgray')
    
    ax.legend(title="Typ des Tages", loc="upper right", 
              facecolor='black', edgecolor='white', labelcolor='white', fontsize=5, title_fontsize=5)

    plt.tight_layout()
    
    return fig, vergleich_tabelle

@st.cache_data
def process_season_weekend(df, stoff_lower):
    """ Berechnet saisonale Trends und Wochenend-Vergleiche im Hintergrund parallel. """
    # Partner-Spalte pm2x5 einbinden, falls pm10 gewählt wurde
    stoffe_zu_berechnen = [stoff_lower]
    if stoff_lower == 'pm10' and 'pm2x5' in df.columns:
        stoffe_zu_berechnen.append('pm2x5')
        
    for s in stoffe_zu_berechnen:
        if s not in df.columns:
            return pd.DataFrame(), pd.DataFrame()
            
    if 'datum' not in df.columns:
        return pd.DataFrame(), pd.DataFrame()
    
    # Benötigte Spalten extrahieren (verhindert Speicher-Overhead)
    cols = ['datum'] + stoffe_zu_berechnen
    df_temp = df[cols].dropna(subset=['datum']).copy()
    
    # Filtern ab 2008
    df_temp = df_temp[df_temp["datum"].dt.year >= 2008]
    if df_temp.empty:
        return pd.DataFrame(), pd.DataFrame()
        
    df_temp["wochentag"] = df_temp["datum"].dt.dayofweek
    df_temp["monat"] = df_temp["datum"].dt.month
    df_temp["wochenende"] = df_temp["wochentag"].isin([5, 6]).astype(int)

    # Vektorisierter Performance-Hebel für Jahreszeiten
    season_map = {
        12: "Winter", 1: "Winter", 2: "Winter",
        3: "Frühling", 4: "Frühling", 5: "Frühling",
        6: "Sommer", 7: "Sommer", 8: "Sommer",
        9: "Herbst", 10: "Herbst", 11: "Herbst"
    }
    df_temp["season"] = df_temp["monat"].map(season_map)

    # Aggregationen parallel für alle benötigten Spalten durchführen
    season_order = ["Frühling", "Sommer", "Herbst", "Winter"]
    
    schadstoff_jahreszeit = df_temp.groupby("season")[stoffe_zu_berechnen].mean().reindex(season_order)
    schadstoff_wochenende = df_temp.groupby("wochenende")[stoffe_zu_berechnen].mean()

    return schadstoff_jahreszeit, schadstoff_wochenende

def analyzeSeasonAndWeekend(df, stoff):
    """ Reine Plotting-Funktion. Zeichnet gruppierte Balken bei pm10 & pm2x5. """
    stoff_lower = stoff.lower()
    schadstoff_jahreszeit, schadstoff_wochenende = process_season_weekend(df, stoff_lower)

    if schadstoff_jahreszeit.empty or schadstoff_wochenende.empty:
        st.warning(f"Keine ausreichenden Daten ab 2008 für {stoff.upper()} vorhanden.")
        return None, None

    plt.rcParams.update(plt.rcParamsDefault)
    
    # Flag für Dual-Modus prüfen
    hat_pm25 = (stoff_lower == 'pm10' and 'pm2x5' in schadstoff_jahreszeit.columns)
    width = 0.35  # Balkenbreite für den Gruppen-Versatz

    # ========================================================
    # --- DIAGRAMM 1: JAHRESZEIT ---
    # ========================================================
    fig_season, ax_season = plt.subplots(figsize=(5, 3), facecolor='black')
    ax_season.set_facecolor('black')
    
    x_season = np.arange(len(schadstoff_jahreszeit.index))
    
    if hat_pm25:
        ax_season.bar(x_season - width/2, schadstoff_jahreszeit[stoff_lower], width, color="#4A90E2", label="PM10")
        ax_season.bar(x_season + width/2, schadstoff_jahreszeit['pm2x5'], width, color="#FF6B6B", label="PM2.5")
        ax_season.legend(facecolor='black', edgecolor='white', labelcolor='white', loc='upper right', fontsize=5)
    else:
        ax_season.bar(schadstoff_jahreszeit.index, schadstoff_jahreszeit[stoff_lower], color="#4A90E2")
        
    titel_season = f"Mittlere {stoff.upper()}-Werte nach Jahreszeit" + (" & PM2.5" if hat_pm25 else "")
    ax_season.set_title(titel_season, color='white', fontsize=9, fontweight="bold") # <-- GEÄNDERT: Von 10 auf 9
    ax_season.set_xlabel("Jahreszeit", color='white', fontsize=5.5)                 # <-- GEÄNDERT: Von 5 auf 5.5
    ax_season.set_ylabel(r"Durchschnittliche Konzentration [$\mathrm{\mu g/m^3}$]", color='white', fontsize=5.5) # <-- Von 5 auf 5.5
    
    ax_season.set_xticks(x_season)
    # WICHTIG: fontsize direkt beim Setzen der Textlabels übergeben, damit es greift:
    ax_season.set_xticklabels(schadstoff_jahreszeit.index, fontsize=4.5, color='white') 
    
    ax_season.tick_params(colors='white', which='both', labelsize=4.5)              # <-- GEÄNDERT: Von 8 auf winzige 4.5
    for spine in ax_season.spines.values(): spine.set_color('white')
    ax_season.grid(axis="y", linestyle="--", alpha=0.3, color='dimgray')
    fig_season.tight_layout()

    # ========================================================
    # --- DIAGRAMM 2: WERKTAG VS. WOCHENENDE ---
    # ========================================================
    fig_weekend, ax_weekend = plt.subplots(figsize=(5, 3), facecolor='black')
    ax_weekend.set_facecolor('black')
    
    labels_weekend = ["Werktag", "Wochenende"]
    x_weekend = np.arange(len(labels_weekend))
    
    if hat_pm25:
        ax_weekend.bar(x_weekend - width/2, schadstoff_wochenende[stoff_lower], width, color="#4A90E2", label="PM10")
        ax_weekend.bar(x_weekend + width/2, schadstoff_wochenende['pm2x5'], width, color="#FF6B6B", label="PM2.5")
        ax_weekend.legend(facecolor='black', edgecolor='white', labelcolor='white', loc='upper right', fontsize=5)
    else:
        ax_weekend.bar(labels_weekend, schadstoff_wochenende[stoff_lower], color="#FF6B6B")
        
    titel_weekend = f"{stoff.upper()}: Werktag vs. Wochenende" + (" & PM2.5" if hat_pm25 else "")
    ax_weekend.set_title(titel_weekend, color='white', fontsize=9, fontweight="bold") # <-- GEÄNDERT: Von 10 auf 9
    ax_weekend.set_ylabel(r"Durchschnittliche Konzentration [$\mathrm{\mu g/m^3}$]", color='white', fontsize=5.5) # <-- Von 5 auf 5.5
    
    ax_weekend.set_xticks(x_weekend)
    ax_weekend.set_xticklabels(labels_weekend, fontsize=4.5, color='white')          # <-- GEÄNDERT: Von 5 auf 4.5
    
    ax_weekend.tick_params(colors='white', which='both', labelsize=4.5)             # <-- GEÄNDERT: Von 7 auf winzige 4.5
    for spine in ax_weekend.spines.values(): spine.set_color('white')
    ax_weekend.grid(axis="y", linestyle="--", alpha=0.3, color='dimgray')
    fig_weekend.tight_layout()
    return fig_season, fig_weekend

# ==============================================================================
# OPTIMIERUNG FÜR: getExceedancesPerYear
# ==============================================================================
@st.cache_data
def process_exceedances(df, stoff_lower):
    """Berechnet LQI-Überschreitungen extrem schnell im RAM-Cache."""
    lqi_grenzwerte_maessig = {"pm10": 28, "pm2x5": 16, "o3": 73, "no2": 31}
    
    # Welche Stoffe müssen berechnet werden?
    stoffe_zu_berechnen = [stoff_lower]
    if stoff_lower == 'pm10' and 'pm2x5' in df.columns:
        stoffe_zu_berechnen.append('pm2x5')
        
    # Validierung
    for s in stoffe_zu_berechnen:
        if s not in lqi_grenzwerte_maessig or s not in df.columns:
            return pd.DataFrame()
            
    if 'datum' not in df.columns:
        return pd.DataFrame()
        
    cols = ['datum'] + stoffe_zu_berechnen
    df_temp = df[cols].dropna(subset=['datum']).copy()
    df_temp["jahr"] = df_temp["datum"].dt.year.astype(int)
    
    # Überschreitungen über boolesche Masken für alle relevanten Stoffe berechnen
    for s in stoffe_zu_berechnen:
        df_temp[f"ab_maessig_{s}"] = df_temp[s] >= lqi_grenzwerte_maessig[s]
        
    # Spaltennamen für das Groupby bestimmen
    agg_cols = [f"ab_maessig_{s}" for s in stoffe_zu_berechnen]
    
    # Gruppieren und Summe bilden
    result = df_temp.groupby("jahr")[agg_cols].sum()
    # Spaltennamen vereinfachen (z.B. zurück zu 'pm10' und 'pm2x5')
    result.columns = stoffe_zu_berechnen
    return result

def getExceedancesPerYear(df, stoff):
    """Zeichnet das Überschreitungsdiagramm. Bei pm10 inkl. pm2x5 als gruppiertes Balkendiagramm."""
    stoff_lower = stoff.lower()
    ueberschreitungen_jahr = process_exceedances(df, stoff_lower)

    if ueberschreitungen_jahr.empty:
        st.warning(f"Schadstoff '{stoff.upper()}' wird nicht unterstützt oder Spalten fehlen.")
        return None

    plt.rcParams.update(plt.rcParamsDefault)
    fig, ax = plt.subplots(figsize=(5, 3), facecolor='black')
    ax.set_facecolor('black')

    jahre_int = ueberschreitungen_jahr.index
    jahre_str = jahre_int.astype(str)
    x = np.arange(len(jahre_int))  # Positionen der Gruppen
    
    # Prüfen, ob pm2x5 als zweite Serie für pm10 existiert
    hat_pm25 = (stoff_lower == 'pm10' and 'pm2x5' in ueberschreitungen_jahr.columns)

    if hat_pm25:
        width = 0.35  # Breite der einzelnen Balken
        # Balken für pm10 (links)
        ax.bar(x - width/2, ueberschreitungen_jahr[stoff_lower], width, color="#4A90E2", label="PM10 (>= 28 µg/m³)")
        # Balken für pm2x5 (rechts)
        ax.bar(x + width/2, ueberschreitungen_jahr['pm2x5'], width, color="#FF6B6B", label="PM2.5 (>= 16 µg/m³)")
        ax.legend(facecolor='black', edgecolor='white', labelcolor='white', loc='upper right', fontsize=5)
    else:
        # Einzelner Balken für o3 oder no2
        ax.bar(jahre_str, ueberschreitungen_jahr[stoff_lower], color="#4A90E2")

    # Layout & Achsen-Design
    titel = f"Stunden mit mindestens mäßiger Luftqualität: {stoff.upper()}" + (" & PM2.5" if hat_pm25 else "")
    ax.set_title(titel, color='white', fontsize=10, fontweight="bold", pad=10)
    ax.set_xlabel("Jahr", color='white', fontsize=5)
    ax.set_ylabel("Anzahl belasteter Stunden", color='white', fontsize=5)
    
    ticks_to_show = list(range(0, len(jahre_str), 10))
    labels_to_show = [jahre_str[i] for i in ticks_to_show]
    
    ax.set_xticks(ticks_to_show)
    ax.set_xticklabels(labels_to_show, rotation=0, ha='center')
    ax.tick_params(colors='white', which='both', labelsize=5)
    
    for spine in ax.spines.values(): 
        spine.set_color('white')
        
    ax.grid(axis="y", linestyle="--", alpha=0.3, color='dimgray')

    plt.tight_layout()
    return fig