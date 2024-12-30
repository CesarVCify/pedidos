import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de los IDs de las hojas de Google Sheets
ID_PEDIDOS = "106heHrtrvtaBVl13lvhqUzXlhLF7c3NFrbANXO1-FJk"
ID_CATALOGO = "1ERtd0fm2FY8-Pm72J3kl8J05T2ryG_fR91kOfPlPrfQ"

def obtener_url_publica(sheet_id):
    """Genera la URL de exportación pública de una hoja de Google Sheets."""
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

def cargar_hoja(sheet_id):
    """Carga datos desde una hoja pública de Google Sheets."""
    url = obtener_url_publica(sheet_id)
    try:
        df = pd.read_csv(url)
        df.columns = [col.strip() for col in df.columns]  # Limpia espacios en los encabezados
        return df
    except Exception as e:
        st.error(f"Error al cargar la hoja con ID {sheet_id}: {e}")
        return pd.DataFrame()

# Cargar datos iniciales
st.title("Gestión de Pedidos - Editar Pedidos")
st.info("Los productos solo pueden seleccionarse del catálogo cargado desde Google Sheets.")

pedidos_df = cargar_hoja(ID_PEDIDOS)
catalogo_df = cargar_hoja(ID_CATALOGO)

if pedidos_df.empty or catalogo_df.empty:
    st.warning("No se pudieron cargar los datos. Verifica que las hojas sean públicas y los IDs sean correctos.")
    st.stop()

# Validar columnas requeridas
columnas_requeridas = ["Producto", "Cantidad Solicitada", "Unidad", "Precio Unitario", "Total", "Proveedor"]
faltantes = [col for col in columnas_requeridas if col not in pedidos_df.columns]

if faltantes:
    st.error(f"Faltan las siguientes columnas en la hoja de pedidos: {faltantes}")
    st.stop()

# Reemplazar valores nulos en "Proveedor"
pedidos_df["Proveedor"] = pedidos_df["Proveedor"].fillna("Desconocido")

# Función para limpiar cantidades solicitadas
def limpiar_cantidades(df):
    df["Cantidad Solicitada"] = 0  # Reinicia todas las cantidades a 0
    return df

# Función para actualizar precios unitarios desde el catálogo
def actualizar_precios(df_pedidos, df_catalogo):
    precios = dict(zip(df_catalogo["Producto"], df_catalogo["Precio Unitario"]))
    df_pedidos["Precio Unitario"] = df_pedidos["Producto"].map(precios)
    df_pedidos["Precio Unitario"] = df_pedidos["Precio Unitario"].fillna(0.01)  # Valor predeterminado si no hay precio
    return df_pedidos

# Botón para limpiar datos
if st.button("Limpiar Cantidades Solicitadas"):
    pedidos_df = limpiar_cantidades(pedidos_df)
    st.success("¡Cantidad solicitada reiniciada a 0 para todos los productos!")

# Botón para actualizar precios
if st.button("Actualizar Precios desde Catálogo"):

