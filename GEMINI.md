# Project Overview

This project is a data analysis and visualization application built with Python. It uses Streamlit to create an interactive web-based dashboard. The application fetches data from a SQL Server database, processes it with Pandas, and displays it to the user.

## Main Technologies

*   **Backend:** Python
*   **Frontend:** Streamlit
*   **Data Manipulation:** Pandas
*   **Database:** SQL Server (via pyodbc)
*   **Visualization:** Plotly

## Architecture

The project is structured as follows:

*   `Ventas_por_color.py`: The main application file. It contains the Streamlit UI code for the dashboard, including filters and data display.
*   `GestorSQL.py`: A data access layer that handles the connection to the SQL Server database. It contains functions for executing SQL queries and returning data as Pandas DataFrames.
*   `Querys/`: This directory stores the SQL queries used by the application.
    *   `Ventas_StockUltsem.sql`: A complex query that retrieves sales and stock data.
    *   `Tiendas.sql`: A simple query that retrieves store information.
*   `requeriment.tct`: Lists the Python dependencies. This file should be renamed to `requirements.txt`.
*   `Conexion.json`: Contains database connection credentials. **Warning: This file contains sensitive information and should not be committed to version control.**

## Building and Running

1.  **Rename `requeriment.tct` to `requirements.txt`:**
    ```bash
    mv requeriment.tct requirements.txt
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Streamlit application:**
    ```bash
    streamlit run Ventas_por_color.py
    ```

## Development Conventions

*   **Database Credentials:** Database credentials are currently hardcoded in `GestorSQL.py` and `Conexion.json`. This is a security risk. It is highly recommended to use environment variables to manage sensitive information. The `python-dotenv` library is already included in the requirements and can be used for this purpose.
*   **SQL Queries:** SQL queries are kept separate from the Python code in the `Querys/` directory. This is a good practice that improves code readability and maintainability.
