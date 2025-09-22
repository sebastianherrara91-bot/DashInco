import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import GestorSQL as GSQL
import MD_Ventas_por_color as VPC
import MD_Ventas_por_talla as VPT
import MD_Ventas_por_Tienda as VPTI
import StreamlitElements as SE

st.set_page_config(
    page_title="Ventas_Inco",
    page_icon=":bar_chart:",
    layout="wide" # layout="wide" para que se adapte al ancho de la pantalla
    )

# Inyectar CSS para forzar la reducción de márgenes laterales
st.markdown("""
    <style>
    /* Estilos para el contenedor principal */
    .block-container {
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* Media query para pantallas pequeñas (móviles) */
    @media (max-width: 768px) {
        .block-container {
            /* En móvil, reduce el ancho máximo para forzar el apilamiento de columnas */
            max-width: 46rem;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }

    /* Media query para pantallas grandes (escritorio) */
    @media (min-width: 769px) {
        div[data-testid="stDataFrame"] {
            min-width: 400px !important;
        }
    }

    /* Intento para ocultar el campo de búsqueda dentro del selectbox */
    div[data-testid="stSelectbox"] input {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

#padding-top: 2rem !important;

def main():

    st.sidebar.header("Menu")
    menu = st.sidebar.selectbox("Seleccionar Detalle", ["Ventas por Tienda", "Ventas por color", "Ventas por talla", "Ventas por Arte"])
    selec= menu

    dfVS1 = GSQL.get_dataframe("Ventas_StockUltsem.sql")
    dfVS8 = GSQL.get_dataframe("Ventas_Stock_8Sem.sql")
    
    if not dfVS1.empty and not dfVS8.empty:
        #st.dataframe(dfv, use_container_width=True, height=500)
        if selec == "Ventas por Tienda":
            VPTI.main(dfVS8)
        elif selec == "Ventas por color": 
            VPC.main(dfVS1.groupby(['Ini_Cliente', 'Tipo_Programa','C_L','Local','Ciudad','Marca', 'Semanas', 'Fit_Estilo', 'COLOR', 'C_Color','Color_Hexa'],dropna=False).agg({'Cant_Venta': 'sum','Cant_Stock': 'sum'}).reset_index())
        elif selec == "Ventas por talla": 
            VPT.main(dfVS1.groupby(['Ini_Cliente', 'Tipo_Programa','C_L','Local','Ciudad','Marca', 'Semanas', 'Fit_Estilo', 'Talla'],dropna=False).agg({'Cant_Venta': 'sum','Cant_Stock': 'sum'}).reset_index())
        elif selec == "Ventas por Arte": 
            SE.StreamElement()            
    else:
        st.warning("No se pudieron cargar los datos")
    

    #st.dataframe(dfv, width='stretch', height=500)

if __name__ == '__main__':
    main()
