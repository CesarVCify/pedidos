import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Configuración de la página
st.set_page_config(page_title="Gestión de Pedidos", layout="wide")
st.title("Gestión de Pedidos - Mekima")

# Parámetros iniciales
USAR_CREDENCIALES = st.sidebar.checkbox("Usar Credenciales JSON", value=False)

# Subida de credenciales o URLs públicas
if USAR_CREDENCIALES:
    # Subir archivo JSON
    auth_key = st.sidebar.file_uploader("Sube tu archivo JSON", type="json")
    if auth_key:
        creds = Credentials.from_service_account_info(st.secrets.auth_key)
        gc = gspread.authorize(creds)
        st.sidebar.success("Credenciales cargadas con éxito")
else:
    st.sidebar.info("Usando hojas públicas de Google Sheets")

# IDs de las hojas o URLs públicas
costo_insumos_key = st.sidebar.text_input("ID de la hoja 'Costo de Insumos':", "1ERtd0fm2FY8-Pm72J3kl8J05T2ryG_fR91kOfPlPrfQ")
pedidos_key = st.sidebar.text_input("ID de la hoja 'Pedidos':", "106heHrtrvtaBVl13lvhqUzXlhLF7c3NFrbANXO1-FJk")

def obtener_url_publica(sheet_id):
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

# Cargar datos
if st.button("Cargar Datos"):
    try:
        if USAR_CREDENCIALES:
            costo_insumos_sheet = gc.open_by_key(costo_insumos_key).sheet1
            pedidos_sheet = gc.open_by_key(pedidos_key).sheet1
            costo_insumos_df = pd.DataFrame(costo_insumos_sheet.get_all_records())
            pedidos_df = pd.DataFrame(pedidos_sheet.get_all_records())
        else:
            costo_insumos_url = obtener_url_publica(costo_insumos_key)
            pedidos_url = obtener_url_publica(pedidos_key)
            costo_insumos_df = pd.read_csv(costo_insumos_url)
            pedidos_df = pd.read_csv(pedidos_url)

        # Visualizar datos cargados
        st.subheader("Datos de Costo de Insumos")
        st.dataframe(costo_insumos_df)

        st.subheader("Datos de Pedidos")
        st.dataframe(pedidos_df)

        # Procesar datos
        def calcular_costos(pedidos_df, costo_insumos_df):
            pedidos_df = pedidos_df.merge(
                costo_insumos_df[['Producto', 'Precio Unitario', 'Proveedor', 'Lugar Comercial']],
                on='Producto', how='left'
            )
            pedidos_df['Total'] = pedidos_df.apply(
                lambda row: row['Cantidad Solicitada'] * row['Precio Unitario']
                            if pd.notna(row['Cantidad Solicitada']) and pd.notna(row['Precio Unitario']) else 0,
                axis=1
            )
            return pedidos_df

        pedidos_df['Cantidad Solicitada'] = pd.to_numeric(pedidos_df['Cantidad Solicitada'], errors='coerce')
        pedidos_df = calcular_costos(pedidos_df, costo_insumos_df)

        # Resumen
        cantidad_productos = len(pedidos_df)
        suma_total = pedidos_df['Total'].sum()
        fecha_actual = datetime.now().strftime('%Y-%m-%d')

        resumen_df = pd.DataFrame({
            'Producto': ['TOTAL'],
            'Cantidad Solicitada': [cantidad_productos],
            'Unidad': ['-'],
            'Fecha': [fecha_actual],
            'Total': [suma_total],
            'Proveedor': ['-'],
            'Lugar Comercial': ['-']
        })
        pedidos_df = pd.concat([pedidos_df, resumen_df], ignore_index=True)

        # Visualizar pedidos procesados
        st.subheader("Pedidos Procesados")
        st.dataframe(pedidos_df)

        # Descargar reporte final
        st.download_button(
            label="Descargar Reporte en CSV",
            data=pedidos_df.to_csv(index=False).encode('utf-8'),
            file_name=f"Pedido_{fecha_actual}.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
