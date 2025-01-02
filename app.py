import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Configurar credenciales para Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDENTIALS = Credentials.from_service_account_info(
    st.secrets["google_credentials"], scopes=SCOPES
)

# Configuración de los IDs de las hojas de Google Sheets
ID_PEDIDOS = "106heHrtrvtaBVl13lvhqUzXlhLF7c3NFrbANXO1-FJk"
ID_CATALOGO = "1ERtd0fm2FY8-Pm72J3kl8J05T2ryG_fR91kOfPlPrfQ"

# Cargar Google Sheets
def cargar_hoja(sheet_id):
    client = gspread.authorize(CREDENTIALS)
    sheet = client.open_by_key(sheet_id).sheet1
    return pd.DataFrame(sheet.get_all_records())

def actualizar_hoja(sheet_id, data):
    client = gspread.authorize(CREDENTIALS)
    sheet = client.open_by_key(sheet_id).sheet1
    sheet.clear()
    sheet.update([data.columns.values.tolist()] + data.values.tolist())

# Cargar datos iniciales
st.set_page_config(page_title="Gestión de Pedidos", layout="wide")
st.title("Gestión de Pedidos")
st.markdown("### Administra, edita y organiza tus pedidos de forma rápida y sencilla.")

pedidos_df = cargar_hoja(ID_PEDIDOS)
catalogo_df = cargar_hoja(ID_CATALOGO)

# Sincronizar precios unitarios desde el catálogo
pedidos_df = pedidos_df.merge(catalogo_df[["Producto", "Precio Unitario"]], on="Producto", how="left", suffixes=("", "_catalogo"))
pedidos_df["Precio Unitario"] = pedidos_df["Precio Unitario_catalogo"]
pedidos_df.drop(columns=["Precio Unitario_catalogo"], inplace=True)

# Reemplazar valores nulos en "Proveedor"
pedidos_df["Proveedor"] = pedidos_df["Proveedor"].fillna("Desconocido")

# Función para limpiar cantidades solicitadas
def limpiar_cantidades(df):
    df["Cantidad Solicitada"] = 0
    df["Total"] = 0
    return df

# Botones destacados
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Limpiar Cantidades"):
        pedidos_df = limpiar_cantidades(pedidos_df)
        st.session_state["pedidos_df"] = pedidos_df
        st.success("¡Cantidad solicitada reiniciada a 0 para todos los productos!")
with col2:
    if st.button("📥 Descargar Pedidos"):
        pedidos_filtrados = pedidos_df[pedidos_df["Cantidad Solicitada"] > 0]
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        nombre_csv = f"Pedidos_Actualizados_{fecha_actual}.csv"
        st.download_button(
            label="Descargar CSV",
            data=pedidos_filtrados.to_csv(index=False).encode("utf-8"),
            file_name=nombre_csv,
            mime="text/csv",
        )

# Mostrar y editar pedidos agrupados por proveedor en dos columnas
st.markdown("### Pedidos Agrupados por Proveedor")
proveedores = pedidos_df["Proveedor"].unique()

# Dividir los proveedores en dos columnas
col1, col2 = st.columns(2)
for i, proveedor in enumerate(proveedores):
    col = col1 if i % 2 == 0 else col2
    with col:
        with st.expander(f"Proveedor: {proveedor}"):
            proveedor_df = pedidos_df[pedidos_df["Proveedor"] == proveedor]

            for index, row in proveedor_df.iterrows():
                # Mostrar Producto y Precio Unitario
                st.markdown(f"**{row['Producto']}**")
                st.text(f"Precio Unitario: ${row['Precio Unitario']:.2f}")

                # Cantidad y Unidad
                sub_col1, sub_col2 = st.columns([1, 1])
                with sub_col1:
                    cantidad = st.number_input(
                        "Cantidad",
                        value=row["Cantidad Solicitada"],
                        min_value=0,
                        key=f"cantidad_{index}"
                    )
                    pedidos_df.at[index, "Cantidad Solicitada"] = cantidad
                    pedidos_df.at[index, "Total"] = cantidad * row["Precio Unitario"]
                with sub_col2:
                    unidad = st.text_input(
                        "Unidad",
                        value=row["Unidad"],
                        key=f"unidad_{index}"
                    )
                    pedidos_df.at[index, "Unidad"] = unidad

# Vista previa del pedido final
st.markdown("### Vista Previa del Pedido Final")
pedido_final = pedidos_df[pedidos_df["Cantidad Solicitada"] > 0]
for index, row in pedido_final.iterrows():
    st.markdown(f"**Producto: {row['Producto']}**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"Cantidad: {row['Cantidad Solicitada']}")
    with col2:
        costo = st.number_input(
            "Costo Unitario",
            value=row["Precio Unitario"],
            min_value=0.0,
            step=0.1,
            key=f"precio_{index}"
        )
        pedidos_df.at[index, "Precio Unitario"] = costo
    with col3:
        st.write(f"Total: ${row['Cantidad Solicitada'] * row['Precio Unitario']:.2f}")

# Botón para actualizar el costo en Google Sheets
if st.button("📤 Actualizar Precios en Google Sheets"):
    try:
        actualizar_hoja(ID_PEDIDOS, pedidos_df)
        st.success("Precios actualizados correctamente en Google Sheets.")
    except Exception as e:
        st.error(f"Error al actualizar precios: {e}")

