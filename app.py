import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from gspread_pandas import Spread, Client

# Configuration
st.set_page_config(page_title="Editor de Insumos", page_icon="📈", layout="wide")

# Google Sheets Authentication
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
credentials = st.secrets["gcp_service_account"]
credentials = service_account.Credentials.from_service_account_info(
    credentials, scopes=scope
)
spread = Spread("Precio_insumos", creds=credentials)

def load_data(sheet_name):
    """Load data from the specified Google Sheet."""
    return spread.sheet_to_df(sheet=sheet_name)

def save_data(sheet_name, df):
    """Save data to the specified Google Sheet."""
    spread.df_to_sheet(df, sheet=sheet_name, replace=True)

# Load data from Google Sheets
sheet_name = "Hoja 1"
st.title("Editor de Insumos")

try:
    df = load_data(sheet_name)
    st.success("Datos cargados correctamente")
except Exception as e:
    st.error(f"Error al cargar datos: {e}")
    st.stop()

# Display and edit data
data = st.experimental_data_editor(
    df,
    use_container_width=True,
    num_rows="dynamic",
    key="editor",
)

# Add a new product
st.subheader("Agregar un nuevo producto")

with st.form("add_product_form"):
    new_product = st.text_input("Producto")
    new_lugar_comercial = st.text_input("Lugar Comercial")
    new_proveedor = st.text_input("Proveedor")
    new_precio_unitario = st.number_input("Precio Unitario", min_value=0.0, step=0.01)

    submitted = st.form_submit_button("Agregar Producto")

if submitted:
    new_row = {
        "Producto": new_product,
        "Lugar Comercial": new_lugar_comercial,
        "Proveedor": new_proveedor,
        "Precio Unitario": new_precio_unitario,
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    st.success("Producto agregado exitosamente.")

# Delete a product
st.subheader("Eliminar un producto")
with st.form("delete_product_form"):
    product_to_delete = st.text_input("Nombre del producto a eliminar")
    delete_submitted = st.form_submit_button("Eliminar Producto")

if delete_submitted:
    if product_to_delete in df["Producto"].values:
        df = df[df["Producto"] != product_to_delete]
        st.success(f"Producto '{product_to_delete}' eliminado exitosamente.")
    else:
        st.error(f"Producto '{product_to_delete}' no encontrado.")

# Save the updated data
if st.button("Guardar Cambios"):
    try:
        save_data(sheet_name, df)
        st.success("Datos guardados correctamente")
    except Exception as e:
        st.error(f"Error al guardar datos: {e}")

































