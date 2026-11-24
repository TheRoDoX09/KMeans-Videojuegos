# Segmentación de videojuegos con K-Means

Proyecto de la tercera unidad. Usamos K-Means para agrupar videojuegos según sus ventas, sus calificaciones (crítica y usuarios) y el porcentaje de ventas en Japón. Los resultados se pueden ver en un dashboard hecho con Streamlit.

## Dataset

Video Game Sales with Ratings, de Kaggle:
https://www.kaggle.com/datasets/rush4ratio/video-game-sales-with-ratings

Tiene 16,719 registros y 16 columnas. Después de la limpieza quedaron 6,893 juegos.

## Herramientas

- Python
- Pandas y NumPy
- Scikit-learn
- Matplotlib y Seaborn
- Plotly y Streamlit (dashboard)
- Jupyter Notebook

## Estructura

- `data/raw/`: dataset original
- `data/processed/`: dataset con el cluster de cada juego y resultados del modelo
- `notebooks/analisis_kmeans.ipynb`: exploración, limpieza, K-Means y análisis
- `dashboard/app.py`: dashboard
- `ProyectoUnidad3.pdf`: documentación del proyecto

## Cómo ejecutarlo

Instalar las librerías:

```
pip install pandas numpy scikit-learn matplotlib seaborn plotly streamlit jupyter
```

Para ver el análisis, abrir `notebooks/analisis_kmeans.ipynb` en Jupyter o VS Code y ejecutar todas las celdas.

Para abrir el dashboard, desde la carpeta del proyecto:

```
streamlit run dashboard/app.py
```

Se abre en el navegador en http://localhost:8501

## Resultados

Elegimos K = 4 (silueta de 0.356). Los grupos son:

- Superventas: 1,005 juegos
- Buenos con pocas ventas: 3,676 juegos
- Populares en Japón: 575 juegos
- Mal calificados: 1,637 juegos
