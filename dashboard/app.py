
import json
import os

import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st

st.set_page_config(page_title="Videojuegos K-Means", layout="wide")

# estilo oscuro para las gráficas
pio.templates["gamer"] = pio.templates["plotly_dark"]
pio.templates["gamer"].layout.paper_bgcolor = "rgba(0,0,0,0)"
pio.templates["gamer"].layout.plot_bgcolor = "#161a26"
pio.templates["gamer"].layout.margin = dict(l=40, r=20, t=60, b=40)
pio.templates["gamer"].layout.colorway = ["#8b5cf6", "#22d3ee", "#39ff88", "#f472b6", "#facc15"]
px.defaults.template = "gamer"

# estilo de los indicadores
st.markdown("""
<style>
[data-testid="stMetric"] {
    background-color: #1a1d2e;
    border-left: 4px solid #8b5cf6;
    border-radius: 8px;
    padding: 12px 16px;
}
[data-testid="stMetricValue"] { color: #39ff88; }
h1 { color: #a78bfa !important; }
</style>
""", unsafe_allow_html=True)

ruta = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


@st.cache_data
def cargar_datos():
    df = pd.read_csv(os.path.join(ruta, "videojuegos_clusters.csv"))
    evaluacion = pd.read_csv(os.path.join(ruta, "evaluacion_k.csv"))
    with open(os.path.join(ruta, "metricas_modelo.json")) as f:
        metricas = json.load(f)
    return df, evaluacion, metricas


df, evaluacion, metricas = cargar_datos()

grupos = ["Superventas", "Buenos con pocas ventas", "Populares en Japón", "Mal calificados"]
colores = {
    "Superventas": "#8b5cf6",
    "Buenos con pocas ventas": "#39ff88",
    "Populares en Japón": "#22d3ee",
    "Mal calificados": "#f43f5e",
}

# ---------- barra lateral ----------
st.sidebar.header("Menú")
pagina = st.sidebar.radio("Página", ["Análisis general", "Segmentación K-Means"])

st.sidebar.header("Filtros")
filtro_fab = st.sidebar.multiselect("Fabricante", sorted(df["Fabricante"].unique()), default=sorted(df["Fabricante"].unique()))
filtro_genero = st.sidebar.multiselect("Género", sorted(df["Genre"].unique()), default=sorted(df["Genre"].unique()))
filtro_anios = st.sidebar.slider("Años", int(df["Year_of_Release"].min()), int(df["Year_of_Release"].max()),
                                 (int(df["Year_of_Release"].min()), int(df["Year_of_Release"].max())))
filtro_rating = st.sidebar.multiselect("Clasificación ESRB", sorted(df["Rating"].unique()), default=sorted(df["Rating"].unique()))
filtro_grupo = st.sidebar.multiselect("Grupo (cluster)", grupos, default=grupos)

datos = df[
    (df["Fabricante"].isin(filtro_fab))
    & (df["Genre"].isin(filtro_genero))
    & (df["Year_of_Release"] >= filtro_anios[0])
    & (df["Year_of_Release"] <= filtro_anios[1])
    & (df["Rating"].isin(filtro_rating))
    & (df["Grupo"].isin(filtro_grupo))
]
st.sidebar.write(f"Juegos seleccionados: {len(datos)}")

if len(datos) == 0:
    st.warning("No hay datos con esos filtros.")
    st.stop()

# ---------- página 1 ----------
if pagina == "Análisis general":
    st.title("Ventas y calificaciones de videojuegos")
    st.write("Datos de Kaggle (Video Game Sales with Ratings), juegos de 1985 a 2016. Las ventas están en millones de copias.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Juegos", len(datos))
    c2.metric("Ventas totales (millones)", round(datos["Global_Sales"].sum(), 1))
    c3.metric("Promedio crítica", round(datos["Critic_Score"].mean(), 1))
    c4.metric("Promedio usuarios", round(datos["User_Score"].mean(), 2))

    col1, col2 = st.columns(2)
    ventas_anio = datos.groupby("Year_of_Release")["Global_Sales"].sum().reset_index()
    fig = px.line(ventas_anio, x="Year_of_Release", y="Global_Sales", title="Ventas por año",
                  labels={"Year_of_Release": "Año", "Global_Sales": "Ventas (millones)"})
    col1.plotly_chart(fig, theme=None, width="stretch")

    regiones = pd.DataFrame({
        "Región": ["Norteamérica", "Europa", "Japón", "Otros"],
        "Ventas": [datos["NA_Sales"].sum(), datos["EU_Sales"].sum(), datos["JP_Sales"].sum(), datos["Other_Sales"].sum()],
    })
    fig = px.pie(regiones, names="Región", values="Ventas", title="Ventas por región")
    col2.plotly_chart(fig, theme=None, width="stretch")

    col1, col2 = st.columns(2)
    ventas_genero = datos.groupby("Genre")["Global_Sales"].sum().sort_values().reset_index()
    fig = px.bar(ventas_genero, x="Global_Sales", y="Genre", orientation="h", title="Ventas por género",
                 labels={"Global_Sales": "Ventas (millones)", "Genre": "Género"})
    col1.plotly_chart(fig, theme=None, width="stretch")

    fig = px.scatter(datos, x="Critic_Score", y="User_Score", opacity=0.4, hover_name="Name",
                     title="Calificación crítica vs usuarios", labels={"Critic_Score": "Crítica", "User_Score": "Usuarios"})
    col2.plotly_chart(fig, theme=None, width="stretch")

    col1, col2 = st.columns(2)
    ventas_fab = datos.groupby("Fabricante")["Global_Sales"].sum().sort_values(ascending=False).reset_index()
    fig = px.bar(ventas_fab, x="Fabricante", y="Global_Sales", title="Ventas por fabricante",
                 labels={"Global_Sales": "Ventas (millones)"})
    col1.plotly_chart(fig, theme=None, width="stretch")

    fig = px.histogram(datos, x="Critic_Score", nbins=40, title="Distribución de la calificación de la crítica",
                       labels={"Critic_Score": "Crítica"})
    col2.plotly_chart(fig, theme=None, width="stretch")

    st.subheader("Los 10 juegos más vendidos")
    top10 = datos.sort_values("Global_Sales", ascending=False).head(10)
    st.dataframe(top10[["Name", "Platform", "Year_of_Release", "Genre", "Global_Sales", "Critic_Score", "User_Score", "Grupo"]],
                 hide_index=True)

    st.subheader("Estadísticas descriptivas")
    st.dataframe(datos[["Global_Sales", "NA_Sales", "EU_Sales", "JP_Sales", "Critic_Score", "User_Score"]].describe().round(2))

# ---------- página 2 ----------
else:
    st.title("Segmentación de videojuegos con K-Means")
    st.write("Variables usadas: calificación de la crítica, calificación de usuarios, ventas globales (log) "
             "y porcentaje de ventas en Japón.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Número de clusters", metricas["K"])
    c2.metric("Silueta", round(metricas["silueta"], 3))
    c3.metric("Davies-Bouldin", round(metricas["davies_bouldin"], 3))
    c4.metric("Juegos en el modelo", metricas["registros_modelo"])

    col1, col2 = st.columns(2)
    conteo = datos["Grupo"].value_counts().reindex(grupos).dropna().reset_index()
    conteo.columns = ["Grupo", "Juegos"]
    fig = px.bar(conteo, x="Grupo", y="Juegos", color="Grupo", color_discrete_map=colores, text="Juegos",
                 title="Juegos por grupo")
    fig.update_layout(showlegend=False)
    col1.plotly_chart(fig, theme=None, width="stretch")

    fig = px.scatter(datos, x="Critic_Score", y="Global_Sales", color="Grupo", log_y=True, opacity=0.6,
                     color_discrete_map=colores, category_orders={"Grupo": grupos}, hover_name="Name",
                     title="Crítica vs ventas por grupo",
                     labels={"Critic_Score": "Crítica", "Global_Sales": "Ventas (millones, escala log)"})
    col2.plotly_chart(fig, theme=None, width="stretch")

    col1, col2 = st.columns(2)
    promedios = datos.groupby("Grupo")[["Critic_Score", "User_Score"]].mean().reindex(grupos).dropna().reset_index()
    promedios["User_Score"] = promedios["User_Score"] * 10
    promedios = promedios.rename(columns={"Critic_Score": "Crítica", "User_Score": "Usuarios (x10)"})
    fig = px.bar(promedios.melt(id_vars="Grupo"), x="variable", y="value", color="Grupo", barmode="group",
                 color_discrete_map=colores, title="Calificación promedio por grupo",
                 labels={"variable": "", "value": "Promedio"})
    col1.plotly_chart(fig, theme=None, width="stretch")

    fig = px.box(datos, x="Grupo", y="Global_Sales", color="Grupo", log_y=True, color_discrete_map=colores,
                 category_orders={"Grupo": grupos}, title="Ventas por grupo",
                 labels={"Global_Sales": "Ventas (millones, escala log)"})
    fig.update_layout(showlegend=False)
    col2.plotly_chart(fig, theme=None, width="stretch")

    col1, col2 = st.columns(2)
    japon = datos.groupby("Grupo")["JP_Share"].mean().reindex(grupos).dropna().reset_index()
    japon["JP_Share"] = japon["JP_Share"] * 100
    fig = px.bar(japon, x="Grupo", y="JP_Share", color="Grupo", color_discrete_map=colores,
                 title="% de ventas en Japón por grupo", labels={"JP_Share": "% ventas en Japón"})
    fig.update_layout(showlegend=False)
    col1.plotly_chart(fig, theme=None, width="stretch")

    fig = px.line(evaluacion, x="K", y="Silueta", markers=True, title="Silueta para cada valor de K")
    col2.plotly_chart(fig, theme=None, width="stretch")

    st.subheader("Estadísticas por grupo")
    tabla = datos.groupby("Grupo").agg(
        Juegos=("Name", "count"),
        Ventas_totales=("Global_Sales", "sum"),
        Ventas_promedio=("Global_Sales", "mean"),
        Ventas_mediana=("Global_Sales", "median"),
        Critica=("Critic_Score", "mean"),
        Usuarios=("User_Score", "mean"),
    ).reindex(grupos).dropna()
    st.dataframe(tabla.round(2))

    st.subheader("Descripción de los grupos")
    st.write("**Superventas:** los juegos que más venden y con mejor crítica (83 en promedio). "
             "Ejemplos: Wii Sports, Mario Kart Wii, GTA.")
    st.write("**Buenos con pocas ventas:** el grupo más grande. Tienen buena calificación de usuarios (7.75) "
             "pero venden poco, la mediana es de 0.24 millones.")
    st.write("**Populares en Japón:** el 60% de sus ventas son en Japón. La mayoría son RPG como Dragon Quest y Monster Hunter.")
    st.write("**Mal calificados:** crítica de 53 y usuarios de 5.4 en promedio. Muchos son juegos de fiesta o de licencias.")

    st.subheader("Hallazgos y recomendaciones")
    st.write("""
Hallazgos:
1. Los superventas son el 14.6% de los juegos pero tienen el 62% de las ventas.
2. Un juego bien calificado no necesariamente vende mucho.
3. Japón es un mercado diferente, con un grupo propio de juegos.

Recomendaciones:
1. Invertir en las franquicias fuertes y darle más publicidad a los juegos buenos que vendieron poco.
2. Usar una estrategia diferente para vender los juegos japoneses en otros países.
3. Cuidar la calidad de los juegos de licencia, porque las malas calificaciones no ayudan a vender.
""")
