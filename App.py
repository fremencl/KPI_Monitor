# Importación de librerías
import streamlit as st
import pandas as pd
import plotly.express as px

# Título de la aplicación
st.markdown("<h1 style='text-align: center; color: black; font-size: 24px;'>MONITOR GESTIÓN DEL MANTENIMIENTO</h1>", unsafe_allow_html=True)

# Definimos la URL del archivo de referencia
DATA0_URL = 'https://streamlitmaps.s3.amazonaws.com/data_orders.csv'

# Función para cargar el archivo de referencia
def load_data0():
    # Carga el archivo CSV, decodificando y usando ";" como separador
    data0 = pd.read_csv(DATA0_URL, encoding='ISO-8859-1', sep=';')
    
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

# Conteo de ordenes correctivas y preventivas para la gráfica de torta
ordenes_tipo = data_filtrada['Tipo_Orden'].value_counts().reset_index().rename(columns={'index': 'Tipo', 'Tipo_Orden': 'Cantidad'})

# Visualización del filtro y la métrica general de órdenes
st.write('Sociedad:', opcion)

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
    # Creación de la gráfica de torta con Plotly Express
    fig = px.pie(ordenes_tipo, names='Tipo', values='Cantidad', title="Proporción de Órdenes Preventivas y Correctivas",
                 color='Tipo', color_discrete_map={'Correctiva':'#636EFA', 'Preventiva':'#EF553B'})
    
    # Ajustes de estilo adicionales, si es necesario
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    # Mostrar el gráfico en la aplicación Streamlit
    st.plotly_chart(fig, use_container_width=True)
