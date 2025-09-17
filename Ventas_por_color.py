import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import GraficaBarraDoble as GBD
import io
from datetime import datetime

st.set_page_config(
    page_title="Ventas por Color",
    page_icon=":bar_chart:", 
    layout="wide" # layout="wide" para que se adapte al ancho de la pantalla
    )

# Función para convertir el df a un archivo excel en memoria
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

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
        ("Semana", "Fecha",True)
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
    
    df_calculos = df_filtrado.groupby(['COLOR','Color_Hexa'],dropna=False).agg({'Cant_Venta': 'sum','Cant_stock': 'sum'}).reset_index()
    df_calculos['Total_Unidades'] = df_calculos['Cant_Venta'] + df_calculos['Cant_stock']
    total_unidades_global = df_calculos['Total_Unidades'].sum()
    df_calculos['%_Participacion_Total'] = (df_calculos['Total_Unidades'] / total_unidades_global) * 100 if total_unidades_global else None

    slider = st.sidebar.slider(
        "Quitar % participacion menor a: ", # texto
        min_value=0.00, # valor minimo
        max_value=10.00, # valor maximo
        value=1.50, # Valor Inicial
        step=0.50, # Incremento de 1 en 1
        format="%.2f%%" # Formato de 2 decimales
        )
    
    st.sidebar.write(f'Quitar menor a {slider} % de participación')    
    df_calculos = df_calculos[df_calculos['%_Participacion_Total'] >= slider]
    Colores = df_calculos['COLOR'].unique().tolist()
    
    df_ParaFor = df_filtrado.groupby(['C_L','Local','Ciudad','COLOR','Color_Hexa'],dropna=False).agg({'Cant_Venta': 'sum','Cant_stock': 'sum'}).reset_index()
    df_ParaFor = df_ParaFor[df_ParaFor['COLOR'].isin(Colores)]

    Locales = df_ParaFor[['Local', 'Ciudad']].drop_duplicates().sort_values(by=['Ciudad', 'Local']).values.tolist()

    Colu1, Colu2, Colu3 = st.columns(3)
    columnas = [Colu1,Colu2,Colu3]
    for indice, local in enumerate(Locales):

        Columna_Actual = columnas[indice % 3]#Seleccionamos la columna actual

        with Columna_Actual:
            df_local = df_ParaFor[df_ParaFor['Local'] == local[0]] 
            df_local = df_local.groupby(['COLOR', 'Color_Hexa']).agg({'Cant_Venta': 'sum', 'Cant_stock': 'sum'}).reset_index()
            T_Venta = df_local['Cant_Venta'].sum()
            T_Stock = df_local['Cant_stock'].sum()
            df_local['%_Participacion_Venta'] = (df_local['Cant_Venta'] / T_Venta) * 100 if T_Venta else None
            df_local['%_Participacion_Stock'] = (df_local['Cant_stock'] / T_Stock) * 100 if T_Stock else None

            #st.dataframe(df_local, width='stretch', height=500)

            # INICIO: Gráfico de Barras de Participación por Color___________________________________________________________________________________________________________
            # 1. Agregamos los datos por COLOR y Color_Hexa para el gráfico___________________________________________________________________________________________________________
            df_chart = df_local.dropna(subset=['COLOR', 'Color_Hexa']).copy()
            df_chart = df_chart.groupby(['COLOR', 'Color_Hexa']).agg({'%_Participacion_Venta': 'sum', '%_Participacion_Stock': 'sum', 'Cant_Venta': 'sum', 'Cant_stock': 'sum'}).reset_index()

            # Solo proceder si tenemos datos para graficar
            if not df_chart.empty:
                # 2. Llamamos a la función reutilizable para crear la gráfica
                fig = GBD.crear_grafica_barra_doble_horizontal(
                    dataframe=df_chart,
                    eje_y_col='COLOR',
                    eje_x_col1='%_Participacion_Venta',
                    eje_x_col2='%_Participacion_Stock',
                    color_hex_col='Color_Hexa',
                    custom_data_col1='Cant_Venta',
                    custom_data_col2='Cant_stock',
                    titulo=f"{local[0]} - {local[1][5:]}",  # el [5:] quita los primeros 5 caracteres
                    nombre_barra1="% Venta",
                    nombre_barra2="% Stock",
                    titulo_eje_x="",
                    titulo_eje_y="",
                    height=500
                )

                # 3. Mostramos el gráfico en Streamlit
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay datos suficientes para generar el gráfico de participación por color después de aplicar los filtros.")
        # FIN: Gráfico de Barras___________________________________________________________________________________________________________
    st.write("Datos originales")
    st.dataframe(DataF, width='stretch', height=200)
    excel_data = to_excel(DataF)
    st.download_button(
        label="📥 Descargar en Excel",
        data=excel_data,
        file_name=f"BD_Original_{datetime.now().strftime('%Y-%m-%d')}.xlsx", #Con fecha de hoy
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.write("Datos filtrados")
    st.dataframe(df_filtrado, width='stretch', height=200)
    excel_data = to_excel(df_filtrado)
    st.download_button(
        label="📥 Descargar en Excel",
        data=excel_data,
        file_name=f"BD_Filtrada_{datetime.now().strftime('%Y-%m-%d')}.xlsx", #Con fecha de hoy
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )



