import streamlit as st
import pandas as pd
from io import BytesIO
import os

# Configuración inicial de la página
st.set_page_config(page_title="Gestión de Insumos", layout="wide")
st.title("Gestión de Insumos")
st.markdown("### Agrega, edita y elimina insumos de forma sencilla.")

# Ruta para almacenar insumos predeterminados
INSUMOS_FILE = "insumos_predeterminados.csv"

# Cargar insumos predeterminados desde archivo
if os.path.exists(INSUMOS_FILE):
    insumos_predeterminados = pd.read_csv(INSUMOS_FILE)
else:
    insumos_predeterminados = pd.DataFrame([
        {"Producto": "Aceite en aerosol", "Precio Unitario": 53.0, "Proveedor": "Garis", "Lugar Comercial": "Garis"},
        {"Producto": "Aceite Oliva", "Precio Unitario": 264.0, "Proveedor": "Garis", "Lugar Comercial": "Garis"},
        {"Producto": "Aceite vegetal", "Precio Unitario": 40.0, "Proveedor": "Garis", "Lugar Comercial": "Garis"}
    ])
    insumos_predeterminados.to_csv(INSUMOS_FILE, index=False)

# Cargar insumos predeterminados al estado de sesión
if "insumos_df" not in st.session_state:
    st.session_state["insumos_df"] = insumos_predeterminados.copy()

# Función para guardar los insumos predeterminados
def guardar_predeterminados():
    st.session_state["insumos_df"].to_csv(INSUMOS_FILE, index=False)

# Función para agregar un nuevo insumo
def agregar_insumo(producto, precio, proveedor, lugar_comercial):
    nuevo_insumo = {
        "Producto": producto,
        "Precio Unitario": precio,
        "Proveedor": proveedor,
        "Lugar Comercial": lugar_comercial
    }
    st.session_state["insumos_df"] = pd.concat([
        st.session_state["insumos_df"],
        pd.DataFrame([nuevo_insumo])
    ], ignore_index=True)
    guardar_predeterminados()

# Función para eliminar un insumo
def eliminar_insumo(index):
    st.session_state["insumos_df"] = st.session_state["insumos_df"].drop(index).reset_index(drop=True)
    guardar_predeterminados()

# Función para descargar los insumos como un archivo Excel
def descargar_insumos():
    insumos_df = st.session_state["insumos_df"]
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        insumos_df.to_excel(writer, index=False, sheet_name="Insumos")
    output.seek(0)
    return output

# Función para cargar insumos desde un archivo Excel
def cargar_insumos(file):
    try:
        nuevo_df = pd.read_excel(file)
        if set(["Producto", "Precio Unitario", "Proveedor", "Lugar Comercial"]).issubset(nuevo_df.columns):
            nuevo_df = nuevo_df[["Producto", "Precio Unitario", "Proveedor", "Lugar Comercial"]]
            st.session_state["insumos_df"] = pd.concat([
                st.session_state["insumos_df"], nuevo_df
            ], ignore_index=True)
            guardar_predeterminados()
            st.success("Insumos cargados correctamente.")
        else:
            st.error("El archivo debe contener las columnas: 'Producto', 'Precio Unitario', 'Proveedor', 'Lugar Comercial'.")
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")

# Formulario para agregar insumos
st.markdown("#### Agregar Insumo")
with st.form("form_agregar_insumo"):
    producto = st.text_input("Nombre del Producto", "")
    precio = st.number_input("Precio Unitario", min_value=0.0, step=0.01, value=0.0)
    proveedor = st.text_input("Proveedor", "")
    lugar_comercial = st.text_input("Lugar Comercial", "")
    submitted = st.form_submit_button("Agregar")

    if submitted:
        if producto and proveedor and lugar_comercial:
            agregar_insumo(producto, precio, proveedor, lugar_comercial)
            st.success(f"Insumo '{producto}' agregado correctamente.")
        else:
            st.error("Por favor, completa todos los campos antes de agregar un insumo.")

# Sección para cargar insumos desde un archivo Excel
st.markdown("#### Cargar Insumos desde un Archivo")
cargar_file = st.file_uploader("Sube un archivo Excel con los insumos", type=["xlsx"])
if cargar_file:
    cargar_insumos(cargar_file)

# Mostrar y editar los insumos existentes
st.markdown("#### Lista de Insumos")
insumos_df = st.session_state["insumos_df"]
if not insumos_df.empty:
    st.dataframe(insumos_df)

    # Seleccionar un insumo para eliminar
    st.markdown("#### Eliminar Insumo")
    index_to_delete = st.number_input("Índice del insumo a eliminar", min_value=0, max_value=len(insumos_df)-1, step=1, format="%d")
    if st.button("Eliminar Insumo"):
        eliminar_insumo(index_to_delete)
        st.warning(f"Insumo en el índice {index_to_delete} eliminado correctamente.")
else:
    st.info("No hay insumos registrados.")

# Botón para descargar insumos
st.markdown("#### Descargar Insumos")
if not insumos_df.empty:
    excel_file = descargar_insumos()
    st.download_button(
        label="Descargar Insumos en Excel",
        data=excel_file,
        file_name="insumos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )






















