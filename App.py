# Importación de librerías
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta

# Título de la aplicación
st.markdown("<h1 style='text-align: center; color: black; font-size: 24px;'>MONITOR GESTIÓN DEL MANTENIMIENTO</h1>", unsafe_allow_html=True)

# Definimos la URL del archivo de referencia
DATA0_URL = 'https://streamlitmaps.s3.amazonaws.com/data_orders.csv'
# Función auxiliar para convertir fechas de Excel a Python
def excel_date(date1):
    return datetime(1899, 12, 30) + timedelta(days=date1)

# Función para cargar el archivo de referencia
def load_data0():
    # Carga el archivo CSV, decodificando y usando ";" como separador
    data0 = pd.read_csv(DATA0_URL, encoding='ISO-8859-1', sep=';')
    
    # Convierte la columna 'Fe.inic.extrema' de formato Excel a fecha
    data0['Fe.inic.extrema'] = pd.to_datetime(data0['Fe.inic.extrema'].apply(excel_date))
    
    # Extrae mes y año para cada fila
    data0['Mes_Año'] = data0['Fe.inic.extrema'].dt.to_period('M')
    
    # Mapeo de 'Sociedad CO' a 'Soc_Map'
    soc_map = {
        1000: 'AA',
        1600: 'AA',
        2000: 'AC',
        3000: 'AM',
        3100: 'AM',
        6100: 'AA',
    }
    data0['Soc_Map'] = data0['Sociedad CO'].map(soc_map)
    
    # Mapeo de 'Clase de orden' a 'Tipo_Orden'
    tipo_map = {
        'PM01': 'Correctiva',
        'PM02': 'Correctiva',
        'PM03': 'Preventiva',
    }
    data0['Tipo_Orden'] = data0['Clase de orden'].map(tipo_map)

    # Conversión de 'Ubicac.técnica' a string antes de aplicar el mapeo
    data0['Ubicac.técnica'] = data0['Ubicac.técnica'].astype(str)
    
    # Mapeo de 'Ubicac.técnica' a 'Proceso'
    def mapeo_proceso(ubicacion):
        if ubicacion.startswith('A-TRAT'):
            return 'Producción'
        elif ubicacion.startswith('A-DEPU'):
            return 'Depuración'
        else:
            return 'Distribución'
    
    data0['Proceso'] = data0['Ubicac.técnica'].apply(mapeo_proceso)

    # Conversión de 'Cst.tot.reales' a numérico, tratando errores
    data0['Cst.tot.reales'] = pd.to_numeric(data0['Cst.tot.reales'], errors='coerce').fillna(0).astype(int)
    
    return data0
        
# Cargamos el archivo de referencia
data0 = load_data0()

# Filtro lateral para seleccionar Sociedad
with st.sidebar:
    st.header("Parámetros")
    # Opciones para el filtro de Sociedad incluyendo una opción para mostrar todas
    opciones_sociedad = ['Todas'] + list(data0['Soc_Map'].unique())
    opcion = st.selectbox('Sociedad', opciones_sociedad)

    # Agregamos el filtro de Proceso
    opciones_proceso = ['Todos'] + sorted(data0['Proceso'].unique())
    opcion_proceso = st.sidebar.selectbox('Proceso', opciones_proceso)

# Filtrado basado en Sociedad
if opcion != 'Todas':
    data_filtrada = data0[data0['Soc_Map'] == opcion]
else:
    data_filtrada = data0

# Filtrado adicional basado en Proceso
if opcion_proceso != 'Todos':
    data_filtrada = data_filtrada[data_filtrada['Proceso'] == opcion_proceso]

# Visualización del filtro y la métrica general de órdenes
st.write('Sociedad:', opcion)

cantidad_correctivas = len(data_filtrada[data_filtrada['Tipo_Orden'] == 'Correctiva'])
cantidad_preventivas = len(data_filtrada[data_filtrada['Tipo_Orden'] == 'Preventiva'])

# Creación de un DataFrame para el gráfico de torta
datos_para_grafico = pd.DataFrame({
    'Tipo': ['Correctiva', 'Preventiva'],
    'Cantidad': [cantidad_correctivas, cantidad_preventivas]
})

# Definición de las columnas
col1, col2 = st.columns((1, 1))

with col1:
    # Uso del widget Metric de Streamlit para mostrar la cantidad total de órdenes
    st.metric(label="Total Órdenes", value=len(data_filtrada['Orden'].unique()))
    
    # Widgets Metric adicionales para mostrar las cantidades de órdenes correctivas y preventivas
    st.metric(label="Órdenes Correctivas", value=len(data_filtrada[data_filtrada['Tipo_Orden'] == 'Correctiva']))
    st.metric(label="Órdenes Preventivas", value=len(data_filtrada[data_filtrada['Tipo_Orden'] == 'Preventiva']))

    # Widget de métricas para mostrar la sumatoria de 'Cst.tot.reales'
    st.metric(label="Costo Total Real", value=f"{data_filtrada['Cst.tot.reales'].sum():,}")

# Implementación de la gráfica de torta en la segunda columna
with col2:
    # Creación del gráfico de torta con Plotly Express usando el nuevo DataFrame
    fig = px.pie(datos_para_grafico, names='Tipo', values='Cantidad', title="Proporción de Órdenes Preventivas y Correctivas",
                 color='Tipo', color_discrete_map={'Correctiva':'#636EFA', 'Preventiva':'#EF553B'})

    # Ajustes de estilo, como la posición del texto dentro del gráfico
    fig.update_traces(textposition='inside', textinfo='percent+label')

    # Mostrar el gráfico en la aplicación Streamlit
    st.plotly_chart(fig, use_container_width=True)

# Agregamos nuevo contenedor
st.markdown("<h2 style='text-align: center; color: black; font-size: 20px;'>Evolución Mensual del Costo Total Real</h2>", unsafe_allow_html=True)

# Preparación de datos para el gráfico de líneas
data_linea = data_filtrada.groupby('Mes_Año')['Cst.tot.reales'].sum().reset_index()
data_linea['Mes_Año'] = data_linea['Mes_Año'].astype(str)  # Convertimos a string para facilitar la visualización

# Creación del gráfico de líneas con Plotly Express
fig_linea = px.line(data_linea, x='Mes_Año', y='Cst.tot.reales',
             title="Evolución Mensual del Costo Total Real",
             labels={'Mes_Año': 'Mes/Año', 'Cst.tot.reales': 'Costo Total Real'},
             markers=True  # Agrega marcadores a cada punto de datos
            )

# Ajustes de estilo adicionales al gráfico
fig_linea.update_layout(xaxis_title="Mes/Año", yaxis_title="Costo Total Real", xaxis={'type': 'category'})

# Mostrar el gráfico en la aplicación Streamlit
st.plotly_chart(fig_linea, use_container_width=True)
