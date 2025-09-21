import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import GraficaBarraDoble as GBD
import io
from datetime import datetime

# Función para convertir el df a un archivo excel en memoria
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

def resaltar_fila_max_semana(fila,semmax):
    # Comprueba si el valor de la columna 'Semana' en la fila actual es el máximo.
    if fila['Semanas'] == semmax:
        # Si es la semana máxima, devuelve un estilo de color de fondo para cada celda de la fila.
        return ['background-color: #D4EDDA'] * len(fila)
    else:
        # Si no lo es, no devuelve ningún estilo.
        return [''] * len(fila)

def main(DataF):

    st.sidebar.header("Filtros Dinámicos")

    # Definición de Filtros de un solo Valor Seleccionable___________________________________________________________________________________________________________
    filtros_selectbox = [
        ("Cliente", "Ini_Cliente",False),
        ("Tipo Programa", "Tipo_Programa",True),
        ("Marca", "Marca",False)
    ]
    # Definición de Filtros de múltiples Valores Seleccionables___________________________________________________________________________________________________________
    filtros_multiselect = [
        ("Fit Estilo", "Fit_Estilo",True),
        ("Semanas", "Semanas",True)
    ]

    df_filtrado = DataF.copy() # Copia de DataFrame original para aplicar filtros

    # Bucle para Filtros de Selección ÚNICA (selectbox)___________________________________________________________________________________________________________
    for titulo, columna, orden in filtros_selectbox:
        opciones = ['Todos'] + sorted(list(df_filtrado[columna].unique()), reverse=orden)
        seleccion = st.sidebar.selectbox(titulo, opciones)
        if seleccion != 'Todos':
            df_filtrado = df_filtrado[df_filtrado[columna] == seleccion]

    # Bucle para Filtros de Selección MÚLTIPLE (multiselect)___________________________________________________________________________________________________________
    for titulo, columna, orden in filtros_multiselect:
        opciones = sorted(list(df_filtrado[columna].unique()), reverse=orden)
        selecciones = st.sidebar.multiselect(titulo, opciones)
        if selecciones:
            df_filtrado = df_filtrado[df_filtrado[columna].isin(selecciones)]

    # Mostramos el DataFrame filtrado___________________________________________________________________________________________________________
    # st.dataframe(df_filtrado, width='stretch', height=500)

    # Inicio de los cálculos de participación para el gráfico___________________________________________________________________________________________________________
    
    Locales = df_filtrado[['Local', 'Ciudad']].drop_duplicates().sort_values(by=['Ciudad', 'Local']).values.tolist()

    df_calculos = df_filtrado.groupby(['C_L','Local','Ciudad','Marca','Tipo_Programa','Fit_Estilo','Semanas'],dropna=False).agg({'Cant_Venta': 'sum','Cant_stock': 'sum'}).reset_index()
    # np.where(condición, valor_si_verdadero, valor_si_falso) La condición ahora es: si 'Cant_Venta' es 0 O '|' 'Cant_stock' es 0
    df_calculos['Sem_Evac'] = np.where((df_calculos['Cant_Venta'] == 0) | (df_calculos['Cant_stock'] == 0),0,df_calculos['Cant_stock'] / df_calculos['Cant_Venta'])

    # 1. Crea la columna de ayuda. Asigna un 0 si el valor es 'programa', y 1 en otro caso.
    df_calculos['sort_key'] = (df_calculos['Tipo_Programa'] != 'programa').astype(int)
    # 2. Ordena usando la columna de ayuda PRIMERO, y luego tus otras reglas.
    df_calculos = df_calculos.sort_values(by=['sort_key', 'C_L', 'Local', 'Ciudad', 'Marca', 'Tipo_Programa', 'Fit_Estilo', 'Semanas'],ascending=[True, True, True, True, True, False, True, True])
    # 3. Elimina la columna de ayuda que ya no es necesaria.
    df_calculos = df_calculos.drop(columns=['sort_key'])
    max_semana = df_calculos['Semanas'].max()

    Colu1, Colu2, Colu3 = st.columns(3)
    columnas = [Colu1,Colu2,Colu3]
    

    for indice, local in enumerate(Locales):
        
        Columna_Actual = columnas[indice % 3]#Seleccionamos la columna actual
        with Columna_Actual:
            st.title(f"{local[0]} - {local[1][5:]}")
            
            df_local = df_calculos[df_calculos['Local'] == local[0]].copy()
            st.dataframe(df_local[['Marca','Tipo_Programa','Fit_Estilo','Semanas','Cant_Venta','Cant_stock','Sem_Evac']].style.apply(resaltar_fila_max_semana,semmax=max_semana,axis=1)
                .format({
                'Cant_Venta': '{:,.0f}',
                'Cant_stock': '{:,.0f}',
                'Sem_Evac': '{:.1f}'
                })
            )

    st.dataframe(df_calculos)





