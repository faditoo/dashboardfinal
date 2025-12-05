import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ============================================================
# CONFIG GLOBALE
# ============================================================
st.set_page_config(
    page_title="Fontaines à eau – RATP",
    layout="wide",
)

st.title("💧 Fontaines à eau dans le réseau RATP")
st.caption("Données open data – visualisation interactive des fontaines dans le métro / RER / gares.")

# ============================================================
# DONNÉES & FONCTIONS COMMUNES
# ============================================================

DATA_PATH = Path("data/fontaines-a-eau-dans-le-reseau-ratp.csv")


@st.cache_data
def load_raw_data(path: Path) -> pd.DataFrame:
    """Charge le CSV brut."""
    if not path.is_file():
        raise FileNotFoundError(
            f"Fichier non trouvé : {path.resolve()}\n"
            "Vérifie que le fichier est bien dans data/ et que le nom est correct."
        )
    df = pd.read_csv(path, sep=";")
    return df


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie et enrichit les données pour le dashboard."""
    df = df.copy()

    rename_map = {
        "Ligne": "ligne",
        "Station ou Gare": "station",
        "Longitude": "longitude",
        "Latitude": "latitude",
        "Adresse": "adresse",
        "Code postal": "code_postal",
        "Commune": "commune",
        "En zone contrôlée ou non": "zone_controlee",
        "Point_geographique": "point_geo",
    }
    df = df.rename(columns=rename_map)

    df["ligne"] = df["ligne"].astype(str)
    df["station"] = df["station"].astype(str)
    df["commune"] = df["commune"].astype(str)

    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df.dropna(subset=["latitude", "longitude"])

    df["zone_controlee"] = df["zone_controlee"].fillna("non renseigné").str.lower()

    def classify_ligne(x: str) -> str:
        x_strip = x.strip()
        if x_strip.isdigit():
            return "Métro"
        if x_strip in {"A", "B", "C", "D", "E"}:
            return "RER"
        return "Autre"

    df["type_reseau"] = df["ligne"].apply(classify_ligne)
    return df


@st.cache_data
def get_data() -> pd.DataFrame:
    """Renvoie les données préparées (cachées)."""
    raw = load_raw_data(DATA_PATH)
    return prepare_data(raw)


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Affiche les filtres dans la sidebar et renvoie df filtré."""
    st.sidebar.header("🔎 Filtres")

    types_reseau = sorted(df["type_reseau"].unique())
    selected_types = st.sidebar.multiselect(
        "Type de réseau",
        options=types_reseau,
        default=types_reseau,
    )
    df_filtered = df[df["type_reseau"].isin(selected_types)]

    lignes = sorted(df_filtered["ligne"].unique())
    selected_lignes = st.sidebar.multiselect(
        "Lignes",
        options=lignes,
        default=lignes,
    )
    df_filtered = df_filtered[df_filtered["ligne"].isin(selected_lignes)]

    communes = sorted(df_filtered["commune"].unique())
    selected_communes = st.sidebar.multiselect(
        "Communes",
        options=communes,
        default=communes,
    )
    df_filtered = df_filtered[df_filtered["commune"].isin(selected_communes)]

    only_zone_ctrl = st.sidebar.checkbox("Uniquement en zone contrôlée", value=False)
    if only_zone_ctrl:
        df_filtered = df_filtered[df_filtered["zone_controlee"].str.contains("contrôlée")]

    if df_filtered.empty:
        st.warning("Aucune fontaine ne correspond aux filtres sélectionnés.")
        st.stop()

    return df_filtered


def show_kpis(df_filtered: pd.DataFrame):
    """Affiche les indicateurs clés."""
    st.markdown("### 📊 Indicateurs clés (après filtres)")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Nombre de fontaines", df_filtered.shape[0])
    with col2:
        st.metric("Lignes couvertes", df_filtered["ligne"].nunique())
    with col3:
        st.metric("Stations couvertes", df_filtered["station"].nunique())
    with col4:
        st.metric("Communes couvertes", df_filtered["commune"].nunique())


def show_synthese(df_filtered: pd.DataFrame, page_label: str = ""):
    """Affiche la synthèse textuelle en bas de page."""
    st.markdown("---")
    st.markdown("### 📝 Synthèse automatique")

    nb_f = df_filtered.shape[0]
    nb_lignes = df_filtered["ligne"].nunique()
    nb_stations = df_filtered["station"].nunique()
    nb_communes = df_filtered["commune"].nunique()

    st.markdown(
        f"""
- Avec les filtres actuels, on compte **{nb_f} fontaine(s)** répartie(s) sur **{nb_lignes} ligne(s)**  
  et **{nb_stations} station(s)**, dans **{nb_communes} commune(s)**.
- Cette page (**{page_label or "Accueil"}**) te permet de te concentrer sur un angle particulier d'analyse.
- Le graphique *par ligne* permet d’identifier les lignes les mieux équipées en fontaines.
- Le graphique *par commune* donne une vision plus macro du réseau.
- La carte interactive est idéale pour repérer rapidement **où se trouvent les points d’eau**.
"""
    )


def plot_map(df_map: pd.DataFrame):
    fig = px.scatter_mapbox(
        df_map,
        lat="latitude",
        lon="longitude",
        hover_name="station",
        hover_data={
            "ligne": True,
            "commune": True,
            "adresse": True,
            "code_postal": True,
            "zone_controlee": True,
            "latitude": False,
            "longitude": False,
        },
        color="ligne",
        zoom=11,
        height=550,
    )
    fig.update_layout(
        mapbox_style="open-street-map",
        margin=dict(l=0, r=0, t=30, b=0),
    )
    return fig


def plot_bar_by_line(df_line: pd.DataFrame):
    by_line = (
        df_line.groupby(["type_reseau", "ligne"])
        .size()
        .reset_index(name="nb_fontaines")
        .sort_values("nb_fontaines", ascending=False)
    )
    fig = px.bar(
        by_line,
        x="ligne",
        y="nb_fontaines",
        color="type_reseau",
        labels={
            "ligne": "Ligne",
            "nb_fontaines": "Nombre de fontaines",
            "type_reseau": "Type de réseau",
        },
        title="Nombre de fontaines par ligne",
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig


def plot_bar_by_commune(df_comm: pd.DataFrame):
    by_commune = (
        df_comm.groupby("commune")
        .size()
        .reset_index(name="nb_fontaines")
        .sort_values("nb_fontaines", ascending=True)
    )
    fig = px.bar(
        by_commune,
        x="nb_fontaines",
        y="commune",
        orientation="h",
        labels={
            "commune": "Commune",
            "nb_fontaines": "Nombre de fontaines",
        },
        title="Répartition des fontaines par commune",
    )
    return fig


# ============================================================
# PAGE D'ACCUEIL
# ============================================================

df = get_data()
df_filtered = apply_filters(df)

show_kpis(df_filtered)

st.markdown("### 👋 Bienvenue sur le tableau de bord")
st.write(
    """
Cette application te permet d'explorer les **fontaines à eau** présentes dans le réseau RATP
(métro, RER, gares...).  

➡ Utilise les **filtres à gauche** pour affiner l'analyse.  
➡ Navigue entre les pages en haut à gauche :
- 🌍 Carte
- 🚇 Par ligne
- 🏙️ Par commune
- 📋 Tableau détaillé
"""
)

show_synthese(df_filtered, page_label="Accueil")
