from sqlalchemy import create_engine
import pandas as pd
import streamlit as st
from pathlib import Path
import urllib

#st.cache_resource
def get_connection():

    S='186.31.65.250'
    D='DWH_INCO'
    U='User_Conect3'
    P='P3p3Inc004'

    quoted_pwd = urllib.parse.quote_plus(P)

    #[ODBC Driver 18 for SQL Server]
    # Lista de cadenas de conexión a probar, en orden de preferencia
    # Nota: Uso 'ODBC Driver 18 for SQL Server' porque es el que intentamos instalar en Debian.
    connection_strings_to_try = [
        (f"mssql+pyodbc://{U}:{quoted_pwd}@{S}/{D}?driver=ODBC+Driver+18+for+SQL+Server", "Linux"),
        (f"mssql+pyodbc://{U}:{quoted_pwd}@{S}/{D}?driver=SQL+Server", "Windows")
    ]

    last_error = None
    for conn_str, config_type in connection_strings_to_try:
        try:
            print(f"Intentando conectar con la configuración de {config_type}...")
            engine = create_engine(conn_str)
            # Intentamos una conexión real para validar
            with engine.connect():
                print(f"¡Conexión exitosa con la configuración de {config_type}!")
                return engine
        except Exception as e:
            print(f"Falló la conexión con {config_type}: {e}\n")
            last_error = e
            # Si falla, el bucle 'continue' pasa a la siguiente cadena de la lista

    # Si el bucle termina, significa que todas las conexiones fallaron.
    print("Todas las configuraciones de conexión fallaron.")
    st.error(f"No se pudo conectar a la base de datos. Último error: {last_error}")
    return None


def test_connection():
    """Función para probar la conexión"""
    try:
        engine = get_connection()
        if engine:
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Error al conectar a la base de datos: {str(e)}")
        return False

def cargar_consulta_sql(nombre_archivo):
    """Carga una consulta SQL desde un archivo .sql"""
    try:
        ruta_archivo = Path(__file__).parent / "Querys" / nombre_archivo
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        st.error(f"Error al cargar la consulta SQL: {str(e)}")
        return ""


def obtener_datos_desde_sql(conexion, consulta_sql):
    """Ejecuta una consulta SQL y devuelve un DataFrame"""
    try:
        return pd.read_sql(consulta_sql, conexion)
    except Exception as e:
        st.error(f"Error al ejecutar la consulta: {str(e)}")
        return pd.DataFrame()


@st.cache_data
def get_dataframe(consulta_sql):
    try:
        # Obtener la conexión
        engine = get_connection()
        if engine is None:
            st.error("No se pudo establecer la conexión con la base de datos.")
            return pd.DataFrame()
        
        # Consulta SQL
        query = cargar_consulta_sql(consulta_sql)
        
        # Cargar directamente en un DataFrame
        df = obtener_datos_desde_sql(engine, query)
        return df
        
    except Exception as e:
        st.error(f"Error al obtener datos: {str(e)}")
        return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error
