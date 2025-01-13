import streamlit as st
import pandas as pd
from io import BytesIO
pip install openpyxl

# Configuración inicial de la página
st.set_page_config(page_title="Gestión de Insumos", layout="wide")
st.title("Gestión de Insumos")
st.markdown("### Agrega, edita y elimina insumos de forma sencilla.")

# Crear un DataFrame inicial vacío o con algunos insumos de ejemplo
if "insumos_df" not in st.session_state:
    st.session_state["insumos_df"] = pd.DataFrame(columns=["Producto", "Precio Unitario", "Proveedor", "Lugar Comercial"])

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

# Función para eliminar un insumo
def eliminar_insumo(index):
    st.session_state["insumos_df"] = st.session_state["insumos_df"].drop(index).reset_index(drop=True)

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
    for index, row in insumos_df.iterrows():
        with st.expander(f"{row['Producto']}"):
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 2, 1])
            with col1:
                st.text_input("Producto", value=row["Producto"], key=f"producto_{index}")
            with col2:
                st.number_input("Precio Unitario", value=row["Precio Unitario"], key=f"precio_{index}")
            with col3:
                st.text_input("Proveedor", value=row["Proveedor"], key=f"proveedor_{index}")
            with col4:
                st.text_input("Lugar Comercial", value=row["Lugar Comercial"], key=f"lugar_comercial_{index}")
            with col5:
                if st.button("Eliminar", key=f"eliminar_{index}"):
                    eliminar_insumo(index)
                    st.warning(f"Insumo '{row['Producto']}' eliminado correctamente.")
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


















