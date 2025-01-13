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
        {"Producto": "Aceite vegetal", "Precio Unitario": 40.0, "Proveedor": "Garis", "Lugar Comercial": "Garis"},
        {"Producto": "Aceituna Kalamata", "Precio Unitario": 500.0, "Proveedor": "Costco", "Lugar Comercial": "Costco"},
        {"Producto": "Aderezo balsámico", "Precio Unitario": 82.0, "Proveedor": "City Market", "Lugar Comercial": "City Market"},
        {"Producto": "Cebolla morada", "Precio Unitario": 45.0, "Proveedor": "Alejandro", "Lugar Comercial": "Central de Abastos"},
        {"Producto": "Chai vainilla", "Precio Unitario": 845.0, "Proveedor": "Etrusca", "Lugar Comercial": "Etrusca"},
        {"Producto": "Chamoy", "Precio Unitario": 57.53, "Proveedor": "Garis", "Lugar Comercial": "Garis"},
        {"Producto": "Champiñones", "Precio Unitario": 75.0, "Proveedor": "Alejandro", "Lugar Comercial": "Central de Abastos"},
        {"Producto": "Chapata", "Precio Unitario": 15.0, "Proveedor": "City Market", "Lugar Comercial": "City Market"},
        {"Producto": "Chía", "Precio Unitario": 89.61, "Proveedor": "Garis", "Lugar Comercial": "Garis"},
        {"Producto": "Chícharo congelado", "Precio Unitario": 68.32, "Proveedor": "Garis", "Lugar Comercial": "Garis"},
        {"Producto": "Chile ancho", "Precio Unitario": 0.0, "Proveedor": "General", "Lugar Comercial": "Central de Abastos"},
        {"Producto": "Chile chipotle seco", "Precio Unitario": 0.0, "Proveedor": "El piquin", "Lugar Comercial": "El piquin"},
        {"Producto": "Chile de árbol", "Precio Unitario": 0.0, "Proveedor": "El piquin", "Lugar Comercial": "El piquin"},
        {"Producto": "Chile guajillo", "Precio Unitario": 30.0, "Proveedor": "El piquin", "Lugar Comercial": "El piquin"},
        {"Producto": "Chile Habanero", "Precio Unitario": 5.0, "Proveedor": "Oswald", "Lugar Comercial": "Circuito Cuahutemoc"},
        {"Producto": "Chile morita", "Precio Unitario": 50.0, "Proveedor": "El piquin", "Lugar Comercial": "El piquin"},
        {"Producto": "Chile Poblano", "Precio Unitario": 20.0, "Proveedor": "Miguel", "Lugar Comercial": "Central de Abastos"},
        {"Producto": "Chile Serrano", "Precio Unitario": 29.0, "Proveedor": "Miguel", "Lugar Comercial": "Central de Abastos"},
        {"Producto": "Chipotles adobados", "Precio Unitario": 15.0, "Proveedor": "Garis", "Lugar Comercial": "Garis"},
        {"Producto": "Chocolate con azúcar en polvo", "Precio Unitario": 59.0, "Proveedor": "Garis", "Lugar Comercial": "Garis"},
        {"Producto": "Chorizo Toluqueño", "Precio Unitario": 120.0, "Proveedor": "Carniceria Cuahutemoc", "Lugar Comercial": "Carniceria Cuahutemoc"},
        {"Producto": "Cilantro", "Precio Unitario": 25.0, "Proveedor": "Paco", "Lugar Comercial": "Central de Abastos"},
        {"Producto": "Cilantro arromerado", "Precio Unitario": 35.0, "Proveedor": "Paco", "Lugar Comercial": "Central de Abastos"},
        {"Producto": "Cloro", "Precio Unitario": 17.0, "Proveedor": "Garis", "Lugar Comercial": "Garis"},
        {"Producto": "Coca cola original", "Precio Unitario": 17.0, "Proveedor": "Coca Cola Online", "Lugar Comercial": "Coca Cola Online"},
        {"Producto": "Coca cola sin azúcar", "Precio Unitario": 18.0, "Proveedor": "Coca Cola Online", "Lugar Comercial": "Coca Cola Online"},
        {"Producto": "Coco rallado", "Precio Unitario": 0.0, "Proveedor": "El piquin", "Lugar Comercial": "El piquin"},
        {"Producto": "Cocoa en polvo", "Precio Unitario": 38.11, "Proveedor": "Garis", "Lugar Comercial": "Garis"},
        {"Producto": "Cocoa en polvo cafetería", "Precio Unitario": 0.0, "Proveedor": "Mayordomo", "Lugar Comercial": "Mayordomo"},
        {"Producto": "Cocoa sin azúcar gourmet", "Precio Unitario": 36.0, "Proveedor": "Mayordomo", "Lugar Comercial": "Mayordomo"},
        {"Producto": "Concentrado smoothie mango", "Precio Unitario": 410.0, "Proveedor": "Etrusca", "Lugar Comercial": "Etrusca"},
        {"Producto": "Crema Ácida", "Precio Unitario": 65.0, "Proveedor": "Garis", "Lugar Comercial": "Garis"},
        {"Producto": "Domo chico p/llevar cafetería", "Precio Unitario": 329.0, "Proveedor": "Entelequia", "Lugar Comercial": "Entelequia"},
        {"Producto": "Domo grande p/llevar cafetería", "Precio Unitario": 333.0, "Proveedor": "Entelequia", "Lugar Comercial": "Entelequia"},
        {"Producto": "Espinaca", "Precio Unitario": 30.0, "Proveedor": "Paco", "Lugar Comercial": "Central de Abastos"},
        {"Producto": "Extracto vainilla", "Precio Unitario": 22.07, "Proveedor": "Garis", "Lugar Comercial": "Garis"},
        {"Producto": "Febrizze o Glade para eliminar olores", "Precio Unitario": 55.0, "Proveedor": "Garis", "Lugar Comercial": "Garis"},
        {"Producto": "Fibra metálica", "Precio Unitario": 14.44, "Proveedor": "Garis", "Lugar Comercial": "Garis"},
        {"Producto": "Frambuesa", "Precio Unitario": 40.0, "Proveedor": "Oswald", "Lugar Comercial": "Circuito Cuahutemoc"},
        {"Producto": "Fresa", "Precio Unitario": 75.0, "Proveedor": "Oswald", "Lugar Comercial": "Circuito Cuahutemoc"},
        {"Producto": "Frijol Negro", "Precio Unitario": 37.08, "Proveedor": "Garis", "Lugar Comercial": "Garis"},
        {"Producto": "Galleta Oreo", "Precio Unitario": 12.0, "Proveedor": "Garis", "Lugar Comercial": "Garis"},
        {"Producto": "Guayaba", "Precio Unitario": 20.0, "Proveedor": "Samuel", "Lugar Comercial": "Central de Abastos"},
        {"Producto": "Helado galleta", "Precio Unitario": 203.57, "Proveedor": "Sams", "Lugar Comercial": "Sams"},
        {"Producto": "Helado vainilla", "Precio Unitario": 203.57, "Proveedor": "Sams", "Lugar Comercial": "Sams"},
        {"Producto": "Helado yoghurt fresa", "Precio Unitario": 219.0, "Proveedor": "Sams", "Lugar Comercial": "Sams"},
        {"Producto": "Hierbas finas", "Precio Unitario": 0.0, "Proveedor": "El piquin", "Lugar Comercial": "El piquin"},
        {"Producto": "Huevo", "Precio Unitario": 55.0, "Proveedor": "Chucho", "Lugar Comercial": "Circuito Cuahutemoc"},
        {"Producto": "Jabón de manos", "Precio Unitario": 28.0, "Proveedor": "Garis", "Lugar Comercial": "Garis"},
        {"Producto": "Jarabe sabor maple", "Precio Unitario": 37.0, "Proveedor": "Garis", "Lugar Comercial": "Garis"},
        {"Producto": "Jitomate", "Precio Unitario": 12.0, "Proveedor": "Miguel", "Lugar Comercial": "Central de Abastos"},
        {"Producto": "Kiwi", "Precio Unitario": 110.0, "Proveedor": "Samuel", "Lugar Comercial": "Central de Abastos"},
        {"Producto": "Limón", "Precio Unitario": 15.0, "Proveedor": "Miguel", "Lugar Comercial": "Central de Abastos"},
        {"Producto": "Manzana amarilla", "Precio Unitario": 30.0, "Proveedor": "Samuel", "Lugar Comercial": "Central de Abastos"},
        {"Producto": "Matcha", "Precio Unitario": 800.0, "Proveedor": "Jorge", "Lugar Comercial": "Tés y tisanas"},
        {"Producto": "Melón", "Precio Unitario": 60.0, "Proveedor": "Samuel", "Lugar Comercial": "Central de Abastos"},
        {"Producto": "Perejil", "Precio Unitario": 20.0, "Proveedor": "Paco", "Lugar Comercial": "Central de Abastos"},
        {"Producto": "Plátano Tabasco", "Precio Unitario": 15.0, "Proveedor": "Samuel", "Lugar Comercial": "Central de Abastos"},
        {"Producto": "Queso panela", "Precio Unitario": 142.0, "Proveedor": "Silvia", "Lugar Comercial": "Circuito Cuahutemoc"},
        {"Producto": "Romero", "Precio Unitario": 0.0, "Proveedor": "El piquin", "Lugar Comercial": "El piquin"},
        {"Producto": "Tisana de frutos rojos", "Precio Unitario": 800.0, "Proveedor": "Jorge", "Lugar Comercial": "Tés y tisanas"},
        {"Producto": "Zarzamora", "Precio Unitario": 60.0, "Proveedor": "Oswald", "Lugar Comercial": "Circuito Cuahutemoc"}
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

# Mostrar insumos en un dataframe interactivo
st.markdown("#### Lista de Insumos")
insumos_df = st.session_state["insumos_df"]
if not insumos_df.empty:
    st.dataframe(insumos_df)
else:
    st.info("No hay insumos registrados.")

# Botón para mostrar el contenido del archivo CSV
if st.button("Mostrar contenido del archivo CSV"):
    if os.path.exists(INSUMOS_FILE):
        st.write(pd.read_csv(INSUMOS_FILE))
    else:
        st.warning("El archivo CSV no existe.")

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

# Botón para establecer una nueva lista de insumos predeterminados
st.markdown("#### Nueva Lista de Insumos Predeterminados")
if st.button("Actualizar insumos predeterminados con la lista actual"):
    guardar_predeterminados()
    st.success("La lista de insumos predeterminados ha sido actualizada.")

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



























