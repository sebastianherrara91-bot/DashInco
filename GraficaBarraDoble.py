import plotly.graph_objects as go
import pandas as pd

def crear_grafica_barra_doble_horizontal(
    dataframe: pd.DataFrame,
    eje_y_col: str,
    eje_x_col1: str,
    eje_x_col2: str,
    color_hex_col: str,
    custom_data_col1: str,
    custom_data_col2: str,
    titulo: str,
    nombre_barra1: str,
    nombre_barra2: str,
    titulo_eje_x: str = "Valor",
    titulo_eje_y: str = "Categoría",
    height: int = 1000
):
    """
    Crea una gráfica de barras dobles horizontal personalizable y reutilizable.

    Args:
        dataframe (pd.DataFrame): DataFrame con los datos.
        eje_y_col (str): Nombre de la columna para el eje Y (categorías).
        eje_x_col1 (str): Nombre de la columna para los valores de la primera barra.
        eje_x_col2 (str): Nombre de la columna para los valores de la segunda barra.
        color_hex_col (str): Nombre de la columna con los códigos de color hexadecimales.
        custom_data_col1 (str): Columna con datos extra para el hover de la barra 1.
        custom_data_col2 (str): Columna con datos extra para el hover de la barra 2.
        titulo (str): Título principal del gráfico.
        nombre_barra1 (str): Nombre para la leyenda de la primera barra.
        nombre_barra2 (str): Nombre para la leyenda de la segunda barra.
        titulo_eje_x (str, optional): Título para el eje X. Defaults to "Valor".
        titulo_eje_y (str, optional): Título para el eje Y. Defaults to "Categoría".
        height (int, optional): Altura del gráfico en píxeles. Defaults to 1000.

    Returns:
        go.Figure: Objeto Figure de Plotly con el gráfico generado.
    """
    fig = go.Figure()

    # --- Barra 1 ---
    fig.add_trace(go.Bar(
        x=dataframe[eje_x_col1],
        y=dataframe[eje_y_col],
        orientation='h',
        name=nombre_barra1,
        customdata=dataframe[custom_data_col1],
        marker_color=dataframe[color_hex_col],
        marker_line_color='black',
        marker_line_width=1,
        hovertemplate=f'<b>%{{y}}</b><br><b>{nombre_barra1}:</b> %{{x:.2f}}%<br><b>Unidades:</b> %{{customdata:,}}<extra></extra>',
        text=dataframe[eje_x_col1].apply(lambda x: f'{x:.1f}%'),
        textposition='outside'
    ))

    # --- Barra 2 ---
    fig.add_trace(go.Bar(
        x=dataframe[eje_x_col2],
        y=dataframe[eje_y_col],
        orientation='h',
        name=nombre_barra2,
        customdata=dataframe[custom_data_col2],
        marker_color=dataframe[color_hex_col],
        marker_line_color='black',
        marker_line_width=1,
        hovertemplate=f'<b>%{{y}}</b><br><b>{nombre_barra2}:</b> %{{x:.2f}}%<br><b>Unidades:</b> %{{customdata:,}}<extra></extra>',
        text=dataframe[eje_x_col2].apply(lambda x: f'{x:.1f}%'),
        textposition='outside'
    ))

    # --- Layout ---
    fig.update_layout(
        template='plotly_white',
        showlegend=False,
        height=800,
        barmode='group',
        yaxis_title=titulo_eje_y,
        xaxis_title=titulo_eje_x,
        title=dict(
            text=f"<b>{titulo}</b>",
            x=0.5,
            font=dict(size=20)
        ),
        font=dict(family="sans-serif", size=12),
        yaxis=dict(categoryorder='total ascending', showgrid=False),
        xaxis=dict(showgrid=False, gridwidth=0, gridcolor='LightGray'),
        margin=dict(l=0, r=0, t=30, b=0),
        bargap=0.15,
        bargroupgap=0.1
    )

    fig.update_traces(textfont_size=10, textangle=0, textposition='outside')

    return fig
