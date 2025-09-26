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

def highlight_min_non_zero(col, color):
    # Reemplaza 0 con NaN para encontrar el mínimo de los valores distintos de cero
    non_zero_vals = col.replace(0, np.nan)
    min_val = non_zero_vals.min()
    # Devuelve el estilo para el valor mínimo, por defecto para los demás
    return [f'background-color: {color}' if v == min_val else '' for v in col]

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

    for indice, local in enumerate(Locales):

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
            .highlight_max(subset=['C_Vnt'], color='#FFFF93')
            .apply(lambda x: highlight_min_non_zero(x, color='#FFFF93'), subset=['S_Evc'])
            .apply(lambda x: highlight_min_non_zero(x, color='#F8D7DA'), subset=['C_Vnt'])
            .highlight_max(subset=['S_Evc'], color='#F8D7DA')
            .format({
                'C_Vnt': '{:,.0f}',
                'C_Stk': '{:,.0f}',
                'P_Prm': '$ {:,.0f}',
                'S_Evc': '{:.1f}'
            }),
            use_container_width=True
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
    
    st.write("Datos filtrados")

    st.dataframe(
        df_filtrado.head(10).reset_index(drop=True)
        .style.hide(axis="index")
        .format({
            'Cant_Venta': '{:,.0f}',
            'Cant_Stock': '{:,.0f}',
            'PVP_Prom': '$ {:,.0f}',
            'Sem_Evac': '{:.1f}'
        })       
    )

    #df_xlsx = to_excel(df_filtrado)
""" 
    st.download_button(
        label="📥 Descargar Filtrado en Excel",
        data=to_excel(df_filtrado),
        file_name=f"Ventas_por_tienda_filtrado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
 """