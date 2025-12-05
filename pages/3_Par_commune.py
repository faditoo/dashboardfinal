import streamlit as st
from app import (
    get_data,
    apply_filters,
    show_kpis,
    show_synthese,
    plot_bar_by_commune,
)

st.title("🏙️ Analyse par commune")

df = get_data()
df_filtered = apply_filters(df)

show_kpis(df_filtered)

st.subheader("Répartition des fontaines par commune")
st.caption("Vue agrégée des fontaines par commune.")

fig_communes = plot_bar_by_commune(df_filtered)
st.plotly_chart(fig_communes, use_container_width=True)

st.markdown("#### Top 10 des communes les mieux équipées")
top10_communes = (
    df_filtered.groupby("commune")
    .size()
    .reset_index(name="nb_fontaines")
    .sort_values("nb_fontaines", ascending=False)
    .head(10)
)
st.dataframe(top10_communes, use_container_width=True)

show_synthese(df_filtered, page_label="Par commune")
