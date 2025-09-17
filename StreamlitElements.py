def dashboard_por_talla(DataF):
    st.title("Dashboard Interactivo - Ventas por Talla")
    st.markdown("""
    Este es un dashboard de ejemplo. Arrastra y cambia el tamaño de las tarjetas.
    La data del DataFrame recibido no se usa en este ejemplo, pero podría usarse para llenar los gráficos.
    """)

    def handle_layout_change(updated_layout):
        st.session_state.layout_talla = updated_layout

    default_layout = [
        dashboard.Item("resumen", 0, 0, 4, 2),
        dashboard.Item("grafico_tallas", 4, 0, 8, 4),
        dashboard.Item("tabla_datos", 0, 2, 4, 4),
    ]

    layout = st.session_state.get("layout_talla", default_layout)

    with elements("dashboard_talla"):
        with dashboard.Grid(layout, onLayoutChange=handle_layout_change):
            with mui.Paper(key="resumen", sx={"display": "flex", "flexDirection": "column", "padding": "1em"}):
                mui.Typography("Resumen de Ventas", variant="h5")
                mui.Typography("Aquí irían KPIs como ventas totales, unidades, etc.")

            with mui.Paper(key="grafico_tallas", sx={"display": "flex", "flexDirection": "column", "padding": "1em"}):
                mui.Typography("Gráfico de Ventas por Talla", variant="h5")
                mui.Typography("Aquí puedes poner un gráfico de Plotly o similar.")

            with mui.Paper(key="tabla_datos", sx={"display": "flex", "flexDirection": "column", "padding": "1em"}):
                mui.Typography("Tabla de Datos", variant="h5")
                if not DataF.empty:
                    mui.Typography(f"Recibidos {len(DataF)} registros.")
                else:
                    mui.Typography("No se recibieron datos.")

    st.subheader("Datos del Layout Actual")
    st.json(st.session_state.get("layout_talla", default_layout))