import streamlit as st
import pandas as pd
import GraficaBarraDobleTalla as GBDT
from pandas.api.types import CategoricalDtype

def main(DataF):
    st.sidebar.header("Filtros Dinámicos")

    # --- Sección de Filtros --- #
    filtros_selectbox = [
        ("Cliente", "Ini_Cliente", False),
        ("Tipo Programa", "Tipo_Programa", True),
        ("Marca", "Marca", False)
    ]
    filtros_multiselect = [
        ("Fit Estilo", "Fit_Estilo", True),
        ("Semana", "Fecha", True)
    ]

    df_filtrado = DataF.copy()

    for titulo, columna, orden in filtros_selectbox:
        opciones = ['Todos'] + sorted(list(df_filtrado[columna].unique()), reverse=orden)
        seleccion = st.sidebar.selectbox(f"{titulo} (Tallas)", opciones, key=f"sb_{columna}_tallas")
        if seleccion != 'Todos':
            df_filtrado = df_filtrado[df_filtrado[columna] == seleccion]

    for titulo, columna, orden in filtros_multiselect:
        opciones = sorted(list(df_filtrado[columna].unique()), reverse=orden)
        selecciones = st.sidebar.multiselect(f"{titulo} (Tallas)", opciones, key=f"ms_{columna}_tallas")
        if selecciones:
            df_filtrado = df_filtrado[df_filtrado[columna].isin(selecciones)]

    # --- Lógica de Filtro de Participación --- #
    # Se calcula la participación total por talla sobre los datos ya filtrados por el usuario
    df_calculos = df_filtrado.groupby(['Talla'], dropna=False).agg({'Cant_Venta': 'sum', 'Cant_stock': 'sum'}).reset_index()
    df_calculos['Total_Unidades'] = df_calculos['Cant_Venta'] + df_calculos['Cant_stock']
    total_unidades_global = df_calculos['Total_Unidades'].sum()
    df_calculos['%_Participacion_Total'] = (df_calculos['Total_Unidades'] / total_unidades_global) * 100 if total_unidades_global else 0

    slider = st.sidebar.slider(
        "Quitar % participacion menor a:",
        min_value=0.00, max_value=10.00, value=0.0, step=0.50,
        format="%.2f%%", key="slider_participacion_tallas"
    )
    
    tallas_a_mantener = df_calculos[df_calculos['%_Participacion_Total'] >= slider]['Talla']
    df_filtrado = df_filtrado[df_filtrado['Talla'].isin(tallas_a_mantener)]

    # --- Lógica de Ordenamiento Personalizado para Tallas ---
    if not df_filtrado.empty:
        tallas_letras_orden = ['XXL', 'XL', 'L', 'M', 'S', 'XS', 'XXS']
        tallas_unicas = df_filtrado['Talla'].unique()
        
        tallas_letras = [t for t in tallas_unicas if str(t).upper() in tallas_letras_orden]
        tallas_numeros = [t for t in tallas_unicas if str(t).upper() not in tallas_letras_orden]

        tallas_letras_sorted = sorted(tallas_letras, key=lambda x: tallas_letras_orden.index(str(x).upper()))
        
        def safe_float(num):
            try: return float(num)
            except (ValueError, TypeError): return float('inf')

        tallas_numeros_sorted = sorted(tallas_numeros, key=safe_float)

        orden_final_tallas = tallas_letras_sorted + tallas_numeros_sorted
        talla_cat_type = CategoricalDtype(categories=orden_final_tallas, ordered=True)
        df_filtrado['Talla'] = df_filtrado['Talla'].astype(talla_cat_type)

    # --- Preparación y visualización de gráficos --- #
    Locales = df_filtrado[['Local', 'Ciudad']].drop_duplicates().sort_values(by=['Ciudad', 'Local']).values.tolist()

    Colu1, Colu2, Colu3 = st.columns(3)
    columnas = [Colu1, Colu2, Colu3]

    for indice, local in enumerate(Locales):
        Columna_Actual = columnas[indice % 3]
        with Columna_Actual:
            df_local = df_filtrado[df_filtrado['Local'] == local[0]].copy()
            
            T_Venta = df_local['Cant_Venta'].sum()
            T_Stock = df_local['Cant_stock'].sum()
            df_local['%_Participacion_Venta'] = (df_local['Cant_Venta'] / T_Venta) * 100 if T_Venta else 0
            df_local['%_Participacion_Stock'] = (df_local['Cant_stock'] / T_Stock) * 100 if T_Stock else 0

            df_local = df_local.sort_values(by='Talla')

            if not df_local.empty:
                st.subheader(f"{local[0]} - {local[1][5:]}")
                
                fig = GBDT.crear_grafica_barra_doble_horizontal(
                    dataframe=df_local,
                    eje_y_col='Talla',
                    eje_x_col1='%_Participacion_Venta',
                    eje_x_col2='%_Participacion_Stock',
                    custom_data_col1='Cant_Venta',
                    custom_data_col2='Cant_stock',
                    titulo="",
                    nombre_barra1="% Venta",
                    nombre_barra2="% Stock",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': False, 'displayModeBar': False}, key=f"talla_chart_{indice}")