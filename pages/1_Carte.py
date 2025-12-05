import streamlit as st
from app import get_data, apply_filters, show_kpis, show_synthese, plot_map

st.title("🌍 Carte des fontaines à eau")

df = get_data()
df_filtered = apply_filters(df)

show_kpis(df_filtered)

st.subheader("Localisation des fontaines à eau")
st.caption("Chaque point correspond à une fontaine dans une station / gare du réseau RATP.")

fig_map = plot_map(df_filtered)
st.plotly_chart(fig_map, use_container_width=True)

show_synthese(df_filtered, page_label="Carte")
