# Importación de librerías necesarias
import streamlit as st
import pandas as pd
import plotly.express as px

# Simulación de un DataFrame pequeño para probar la gráfica de torta
# Este DataFrame simula el resultado de ordenes_tipo después del procesamiento y filtrado
datos_prueba = {
    'Tipo': ['Correctiva', 'Preventiva'],
    'Cantidad': [300, 200]  # Estos valores son ejemplos; ajusta según tus necesidades
}
df_prueba = pd.DataFrame(datos_prueba)

# Creación de la gráfica de torta con Plotly Express usando el DataFrame de prueba
fig = px.pie(df_prueba, names='Tipo', values='Cantidad', title="Proporción de Órdenes Preventivas y Correctivas",
             color='Tipo', color_discrete_map={'Correctiva':'#636EFA', 'Preventiva':'#EF553B'})

# Ajustes de estilo adicionales, si es necesario
fig.update_traces(textposition='inside', textinfo='percent+label')

# Mostrar el gráfico en la aplicación Streamlit
st.plotly_chart(fig, use_container_width=True)
