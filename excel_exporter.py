import pandas as pd
from io import BytesIO

def to_excel(df: pd.DataFrame) -> bytes:
    """
    Convierte un DataFrame de pandas a un archivo Excel en formato bytes.
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data
