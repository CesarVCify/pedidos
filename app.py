import streamlit as st
import pandas as pd
from io import BytesIO
import os

# Configuración inicial de la página
st.set_page_config(page_title="Gestión de Insumos", layout="wide")
st.title("Gestión de Insumos")
st.markdown("### Agrega, edita y administra tus insumos fácilmente.")

# Ruta para almacenar insumos predeterminados
INSUMOS_FILE = "insumos_predeterminados.csv"

# Función para cargar insumos predeterminados desde archivo o inicializar predeterminados
@st.cache_data
def cargar_insumos():
    if os.path.exists(INSUMOS_FILE):
        return pd.read_csv(INSUMOS_FILE)
    else:
        return pd.DataFrame([
            {"Producto": "Aceite en aerosol", "Precio Unitario": 53.0, "Proveedor": "Garis", "Lugar Comercial": "Garis"},
            {"Producto": "Aceite Oliva", "Precio Unitario": 264.0, "Proveedor": "Garis", "Lugar Comercial": "Garis"},
            {"Producto": "Aceite vegetal", "Precio Unitario": 40.0, "Proveedor": "Garis", "Lugar Comercial": "Garis"},
            {"Producto": "Aceituna Kalamata", "Precio Unitario": 500.0, "Proveedor": "Costco", "Lugar Comercial": "Costco"}
        ])

# Función para guardar insumos en el archivo CSV
def guardar_insumos(insumos_df):
    insumos_df.to_csv(INSUMOS_FILE, index=False)

# Cargar insumos en el estado de la sesión
if "insumos_df" not in st.session_state:
    st.session_state["insumos_df"] = cargar_insumos()

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
    guardar_insumos(st.session_state["insumos_df"])

# Función para eliminar un insumo por índice
def eliminar_insumo(index):
    st.session_state["insumos_df"] = st.session_state["insumos_df"].drop(index).reset_index(drop=True)
    guardar_insumos(st.session_state["insumos_df"])

# Función para descargar los insumos como un archivo Excel
def descargar_insumos():
    insumos_df = st.session_state["insumos_df"]
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        insumos_df.to_excel(writer, index=False, sheet_name="Insumos")
    output.seek(0)
    return output

# Función para cargar insumos desde un archivo subido por el usuario
# Ahora reemplaza la lista actual y guarda como predeterminada
def cargar_insumos_desde_archivo(file):
    try:
        nuevo_df = pd.read_excel(file)
        if set(["Producto", "Precio Unitario", "Proveedor", "Lugar Comercial"]).issubset(nuevo_df.columns):
            st.session_state["insumos_df"] = nuevo_df  # Reemplaza los insumos actuales
            guardar_insumos(st.session_state["insumos_df"])  # Guarda los nuevos insumos como predeterminados
            st.success("Insumos cargados y guardados correctamente como predeterminados.")
        else:
            st.error("El archivo debe contener las columnas: 'Producto', 'Precio Unitario', 'Proveedor', 'Lugar Comercial'.")
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")

# Mostrar insumos en un dataframe interactivo
st.markdown("#### Lista de Insumos")
insumos_df = st.session_state["insumos_df"]
if not insumos_df.empty:
    st.dataframe(insumos_df, use_container_width=True)
else:
    st.info("No hay insumos registrados.")

# Formulario para agregar nuevos insumos
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

# Botón para cargar insumos desde un archivo
st.markdown("#### Cargar Insumos desde Archivo")
cargar_file = st.file_uploader("Sube un archivo Excel con los insumos", type=["xlsx"])
if cargar_file:
    cargar_insumos_desde_archivo(cargar_file)

# Botón para eliminar insumos seleccionados
st.markdown("#### Eliminar Insumo")
insumo_a_eliminar = st.number_input("Índice del insumo a eliminar", min_value=0, step=1, value=0)
if st.button("Eliminar Insumo"):
    if not insumos_df.empty and 0 <= insumo_a_eliminar < len(insumos_df):
        insumo_eliminado = insumos_df.iloc[insumo_a_eliminar]["Producto"]
        eliminar_insumo(insumo_a_eliminar)
        st.success(f"Insumo '{insumo_eliminado}' eliminado correctamente.")
    else:
        st.error("Índice inválido. Por favor, selecciona un índice válido.")

# Botón para sobrescribir la lista de insumos predeterminados
st.markdown("#### Guardar Lista como Predeterminada")
if st.button("Sobrescribir Lista de Insumos Predeterminados"):
    guardar_insumos(insumos_df)
    st.success("La lista actual ha sido guardada como predeterminada.")

# Botón para descargar insumos en formato Excel
st.markdown("#### Descargar Insumos")
if not insumos_df.empty:
    excel_file = descargar_insumos()
    st.download_button(
        label="Descargar Insumos en Excel",
        data=excel_file,
        file_name="insumos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )































