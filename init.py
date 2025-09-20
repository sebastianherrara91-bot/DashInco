import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import GestorSQL as GSQL
import MD_Ventas_por_color as VPC
import StreamlitElements as SE

st.set_page_config(
    page_title="Ventas_Inco",
    page_icon=":bar_chart:",
    layout="wide" # layout="wide" para que se adapte al ancho de la pantalla
    )

# Inyectar CSS para forzar la reducción de márgenes laterales
st.markdown("""
    <style>
        .block-container {
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
    </style>
""", unsafe_allow_html=True)

#padding-top: 2rem !important;

def main():

    st.sidebar.header("Menu")
    menu = st.sidebar.selectbox("Seleccionar Detalle", ["Ventas por color", "Ventas por talla", "Ventas por Arte"])
    selec= menu

    dfv = GSQL.get_dataframe("Ventas_StockUltsem.sql")
    
    if not dfv.empty:
        #st.dataframe(dfv, use_container_width=True, height=500)
        if selec == "Ventas por color": VPC.main(dfv.groupby(['Ini_Cliente', 'Tipo_Programa','C_L','Local','Ciudad','Marca', 'Fecha', 'Fit_Estilo', 'COLOR', 'C_Color','Color_Hexa'],dropna=False).agg({'Cant_Venta': 'sum','Cant_stock': 'sum'}).reset_index())
        elif selec == "Ventas por talla": VPC.dashboard_por_talla(dfv)
        elif selec == "Ventas por Arte": SE.StreamElement()            
    else:
        st.warning("No se pudieron cargar los datos")
    

    #st.dataframe(dfv, width='stretch', height=500)

if __name__ == '__main__':
    main()
