import streamlit as st
from app import (
    get_data,
    apply_filters,
    show_kpis,
    show_synthese,
    plot_bar_by_line,
)

st.title("🚇 Analyse par ligne")

df = get_data()
df_filtered = apply_filters(df)

show_kpis(df_filtered)

st.subheader("Nombre de fontaines par ligne")
st.caption("Avec distinction du type de réseau (métro / RER / autre).")

fig_lines = plot_bar_by_line(df_filtered)
st.plotly_chart(fig_lines, use_container_width=True)

st.markdown("#### Top 10 des lignes les mieux équipées")
top10_lines = (
    df_filtered.groupby("ligne")
    .size()
    .reset_index(name="nb_fontaines")
    .sort_values("nb_fontaines", ascending=False)
    .head(10)
)
st.dataframe(top10_lines, use_container_width=True)

show_synthese(df_filtered, page_label="Par ligne")
