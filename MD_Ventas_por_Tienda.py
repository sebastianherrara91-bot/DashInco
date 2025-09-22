import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import GraficaBarraDoble as GBD
import io
from datetime import datetime
from excel_exporter import to_excel

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

    #df_calculos = df_filtrado.groupby(['C_L','Local','Ciudad','Marca','Tipo_Programa','Fit_Estilo','Semanas'],dropna=False).agg({'Cant_Venta': 'sum','Cant_Stock': 'sum'}).reset_index()

    # 1. (Paso previo) Creamos una columna temporal para el cálculo del peso (Precio * Venta).
    #    Pandas maneja los nulos en 'PVP_Prom' correctamente durante la multiplicación.
    df_filtrado['PVP_x_Venta'] = df_filtrado['PVP_Prom'] * df_filtrado['Cant_Venta']

    # 2. (Paso de agrupación) Modificamos tu 'groupby' para que también sume la nueva columna.
    df_calculos = df_filtrado.groupby(['C_L','Local','Ciudad','Marca','Tipo_Programa','Fit_Estilo','Semanas'], dropna=False).agg({'Cant_Venta': 'sum','Cant_Stock': 'sum','PVP_x_Venta': 'sum'}).reset_index()

    # 3. (Paso final) Calculamos el promedio y eliminamos la columna temporal.
    #    Usamos np.where para evitar la división por cero (si no hubo ventas, el precio prom es 0).
    df_calculos['PVP_Prom'] = np.where(df_calculos['Cant_Venta'] == 0,0,df_calculos['PVP_x_Venta'] / df_calculos['Cant_Venta'])
    df_calculos = df_calculos.drop(columns=['PVP_x_Venta'])

    # np.where(condición, valor_si_verdadero, valor_si_falso) La condición ahora es: si 'Cant_Venta' es 0 O '|' 'Cant_Stock' es 0
    df_calculos['Sem_Evac'] = np.where((df_calculos['Cant_Venta'] == 0) | (df_calculos['Cant_Stock'] == 0),0,df_calculos['Cant_Stock'] / df_calculos['Cant_Venta'])

    # 1. Crea la columna de ayuda. Asigna un 0 si el valor es 'programa', y 1 en otro caso.
    df_calculos['sort_key'] = (df_calculos['Tipo_Programa'] != 'programa').astype(int)
    # 2. Ordena usando la columna de ayuda PRIMERO, y luego tus otras reglas.
    df_calculos = df_calculos.sort_values(by=['sort_key', 'C_L', 'Local', 'Ciudad', 'Marca', 'Tipo_Programa', 'Fit_Estilo', 'Semanas'],ascending=[True, True, True, True, True, False, True, True])
    # 3. Elimina la columna de ayuda que ya no es necesaria.
    df_calculos = df_calculos.drop(columns=['sort_key'])
    max_semana = df_calculos['Semanas'].max()

    Colu1, Colu2 = st.columns(2)
    columnas = [Colu1, Colu2]

    for indice, local in enumerate(Locales):

        Columna_Actual = columnas[indice % 2]  # Seleccionamos la columna actual
        with Columna_Actual:

            st.subheader(f"{local[0]}-{local[1][5:]}")
            
            df_local = df_calculos[df_calculos['Local'] == local[0]].copy()
            st.dataframe(
                df_local[['Marca','Tipo_Programa','Fit_Estilo','Semanas','Cant_Venta','Cant_Stock','PVP_Prom','Sem_Evac']]
                .rename(columns={
                    'Cant_Venta': 'C_Vnt',
                    'Cant_Stock': 'C_Stk',
                    'PVP_Prom': 'P_Prm',
                    'Sem_Evac': 'S_Evc'
                })  # <--- Añade este bloque .rename()
                .reset_index(drop=True)
                .style.hide(axis="index")
                .apply(resaltar_fila_max_semana, semmax=max_semana, axis=1)
                .format({
                    'C_Vnt': '{:,.0f}',
                    'C_Stk': '{:,.0f}',
                    'P_Prm': '$ {:,.0f}',
                    'S_Evc': '{:.1f}'
                })
            )

    st.write("Datos Originales")
    
    st.dataframe(
        DataF.head(10).reset_index(drop=True)
        .style.hide(axis="index")
        .format({
            'Cant_Venta': '{:,.0f}',
            'Cant_Stock': '{:,.0f}',
            'PVP_Prom': '$ {:,.0f}',
            'Sem_Evac': '{:.1f}'
        })       
    )  
    
    if 'excel_data_tienda_original' not in st.session_state:
        st.session_state['excel_data_tienda_original'] = b'' # Initialize with empty bytes

    def generate_excel_tienda_original():
        with st.spinner("Generando Excel de datos originales..."):
            st.session_state['excel_data_tienda_original'] = to_excel(DataF)

    st.download_button(
        label="📥 Descargar en Excel",
        data=st.session_state['excel_data_tienda_original'],
        file_name=f"BD_Origen_{datetime.now().strftime('%Y-%m-%d')}.xlsx", #Con fecha de hoy
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        on_click=generate_excel_tienda_original
    )

    st.write("Datos filtrados")

    if 'excel_data_tienda_filtered' not in st.session_state:
        st.session_state['excel_data_tienda_filtered'] = b'' # Initialize with empty bytes

    def generate_excel_tienda_filtered():
        with st.spinner("Generando Excel de datos filtrados..."):
            st.session_state['excel_data_tienda_filtered'] = to_excel(df_filtrado)

    st.download_button(
        label="📥 Descargar Datos Filtrados en Excel",
        data=st.session_state['excel_data_tienda_filtered'],
        file_name=f"BD_Filtrada_Tiendas_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        on_click=generate_excel_tienda_filtered
    )
