import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Configuración para Google Sheets
USAR_GOOGLE_SHEETS = True  # Cambia a False si no usas Google Sheets

if USAR_GOOGLE_SHEETS:
    # Configuración de credenciales desde secretos seguros
    import json
    creds = json.loads(st.secrets["google_credentials"])  # Usa st.secrets en Streamlit Cloud
    gc = gspread.service_account_from_dict(creds)
    sheet = gc.open_by_key("TU_ID_DE_HOJA").sheet1  # Reemplaza con el ID de tu hoja de pedidos
    catalogo_sheet = gc.open_by_key("TU_ID_DE_CATALOGO").sheet1  # Reemplaza con el ID de tu hoja de catálogo

# Cargar datos iniciales
if USAR_GOOGLE_SHEETS:
    pedidos_df = pd.DataFrame(sheet.get_all_records())
    catalogo_df = pd.DataFrame(catalogo_sheet.get_all_records())
else:
    # Datos simulados
    pedidos_df = pd.DataFrame({
        "Producto": ["Café", "Té", "Pan"],
        "Cantidad Solicitada": [10, 5, 20],
        "Unidad": ["kg", "kg", "piezas"],
        "Precio Unitario": [150, 100, 15],
        "Total": [1500, 500, 300],
    })
    catalogo_df = pd.DataFrame({"Producto": ["Café", "Té", "Pan"]})

# Título de la aplicación
st.title("Gestión de Pedidos - Editar Pedidos")

# Obtener lista de productos del catálogo
productos_existentes = catalogo_df["Producto"].tolist()

# Mostrar y editar los pedidos
st.subheader("Editar pedidos")
for index, row in pedidos_df.iterrows():
    with st.expander(f"Editar Pedido: {row['Producto']}"):
        # Campo Producto (solo seleccionable del catálogo)
        producto = st.selectbox(
            "Producto",
            options=productos_existentes,
            index=productos_existentes.index(row["Producto"]),
            key=f"producto_{index}"
        )
        # Campos editables
        cantidad = st.number_input(
            "Cantidad Solicitada",
            value=row["Cantidad Solicitada"],
            min_value=1,
            key=f"cantidad_{index}"
        )
        unidad = st.text_input(
            "Unidad",
            value=row["Unidad"],
            key=f"unidad_{index}"
        )
        precio_unitario = st.number_input(
            "Precio Unitario",
            value=row["Precio Unitario"],
            min_value=0.01,
            key=f"precio_{index}"
        )

        # Actualizar valores en el DataFrame
        pedidos_df.at[index, "Producto"] = producto
        pedidos_df.at[index, "Cantidad Solicitada"] = cantidad
        pedidos_df.at[index, "Unidad"] = unidad
        pedidos_df.at[index, "Precio Unitario"] = precio_unitario
        pedidos_df.at[index, "Total"] = cantidad * precio_unitario

# Mostrar la tabla actualizada
st.subheader("Pedidos actualizados")
st.dataframe(pedidos_df)

# Guardar cambios en Google Sheets
if st.button("Guardar cambios"):
    if USAR_GOOGLE_SHEETS:
        sheet.clear()  # Limpia la hoja antes de guardar los datos
        sheet.update([pedidos_df.columns.values.tolist()] + pedidos_df.values.tolist())
        st.success("Datos guardados en Google Sheets.")

# Descargar los pedidos actualizados
if st.button("Descargar pedidos"):
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    nombre_csv = f"Pedidos_Actualizados_{fecha_actual}.csv"
    st.download_button(
        label="Descargar CSV",
        data=pedidos_df.to_csv(index=False).encode("utf-8"),
        file_name=nombre_csv,
        mime="text/csv",
    )
