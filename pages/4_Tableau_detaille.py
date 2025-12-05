import streamlit as st
from app import get_data, apply_filters, show_kpis, show_synthese

st.title("📋 Tableau détaillé des fontaines")

df = get_data()
df_filtered = apply_filters(df)

show_kpis(df_filtered)

st.subheader("Tableau détaillé des fontaines filtrées")

colonnes_affichees = [
    "type_reseau",
    "ligne",
    "station",
    "adresse",
    "code_postal",
    "commune",
    "zone_controlee",
    "latitude",
    "longitude",
]

st.dataframe(
    df_filtered[colonnes_affichees].sort_values(["type_reseau", "ligne", "station"]),
    use_container_width=True,
)

csv_bytes = df_filtered[colonnes_affichees].to_csv(index=False).encode("utf-8")

st.download_button(
    "📥 Télécharger les données filtrées (CSV)",
    data=csv_bytes,
    file_name="fontaines_filtrees.csv",
    mime="text/csv",
)

show_synthese(df_filtered, page_label="Tableau détaillé")
