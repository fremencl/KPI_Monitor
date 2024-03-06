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
    }
    # Aplica el mapeo a la columna 'Sociedad CO'
    data0['Soc_Map'] = data0['Sociedad CO'].map(soc_map)
    return data0
        
# Cargamos el archivo de referencia
data0 = load_data0()

# Filtro lateral para seleccionar Sociedad
with st.sidebar:
    st.header("Parámetros")
    # Opciones para el filtro de Sociedad incluyendo una opción para mostrar todas
    opciones_sociedad = ['Todas'] + list(data0['Soc_Map'].unique())
    opcion = st.selectbox('Sociedad', opciones_sociedad)

# Filtrar data0 según la selección de Sociedad
if opcion != 'Todas':
    data_filtrada = data0[data0['Soc_Map'] == opcion]
else:
    data_filtrada = data0

# Cálculo de la cantidad de órdenes
Cantidad_ordenes = len(data_filtrada['Orden'].unique())

# Visualización del filtro y la métrica
st.write('Sociedad:', opcion)

# Definición de las columnas
col1, col2 = st.columns((1, 1))

# Uso del widget Metric de Streamlit para mostrar la cantidad de órdenes
col1.metric(label="Órdenes", value=Cantidad_ordenes)

# Ahora implementamos el gráfico en la segunda columna
with col2:
    # Preparación de los datos para el gráfico. Este paso agrupa los datos por 'Soc_Map' y cuenta las órdenes
    data_grafico = data0.groupby('Soc_Map')['Orden'].nunique().reset_index().rename(columns={'Orden': 'Cantidad_Ordenes'})
    
    # Creación del gráfico de barras con Plotly Express
    fig = px.bar(data_grafico, x='Soc_Map', y='Cantidad_Ordenes',
             title="Cantidad de Órdenes por Sociedad",
             labels={'Soc_Map': 'Sociedad', 'Cantidad_Ordenes': 'Cantidad de Órdenes'},
             color='Soc_Map',  # Define la columna que determinará el color de las barras
             color_discrete_map={'AA':'#636EFA', 'AC':'#EF553B', 'AM':'#00CC96'}  # Personaliza los colores
            )
    
    # Ajustes de estilo adicionales, si es necesario
    fig.update_layout(xaxis_title="Sociedad", yaxis_title="Cantidad de Órdenes")
    
    # Mostrar el gráfico en la aplicación Streamlit
    st.plotly_chart(fig, use_container_width=True)
