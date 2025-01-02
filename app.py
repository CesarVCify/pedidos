import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Configuración de los IDs de las hojas de Google Sheets
ID_PEDIDOS = "106heHrtrvtaBVl13lvhqUzXlhLF7c3NFrbANXO1-FJk"
ID_CATALOGO = "1ERtd0fm2FY8-Pm72J3kl8J05T2ryG_fR91kOfPlPrfQ"

# Alcances requeridos
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Cargar credenciales desde los secrets de Streamlit
creds = Credentials.from_service_account_info(
    st.secrets["google_credentials"], scopes=SCOPES
)
client = gspread.authorize(creds)

# Función para cargar datos desde Google Sheets
def cargar_hoja(sheet_id):
    try:
        sheet = client.open_by_key(sheet_id).sheet1
        data = pd.DataFrame(sheet.get_all_records())
        return data
    except Exception as e:
        st.error(f"Error al cargar la hoja con ID {sheet_id}: {e}")
        return pd.DataFrame()

# Configurar la página
st.set_page_config(page_title="Gestión de Pedidos", layout="wide")
st.title("Gestión de Pedidos")
st.markdown("### Administra, edita y organiza tus pedidos de forma rápida y sencilla.")

# Cargar datos
pedidos_df = cargar_hoja(ID_PEDIDOS)
catalogo_df = cargar_hoja(ID_CATALOGO)

if pedidos_df.empty or catalogo_df.empty:
    st.warning("No se pudieron cargar los datos. Verifica que las hojas sean públicas y los IDs sean correctos.")
    st.stop()

# Validar columnas requeridas
columnas_requeridas_pedidos = ["Producto", "Cantidad Solicitada", "Unidad", "Proveedor"]
columnas_requeridas_catalogo = ["Producto", "Precio Unitario", "Unidad"]

faltantes_pedidos = [col for col in columnas_requeridas_pedidos if col not in pedidos_df.columns]
faltantes_catalogo = [col for col in columnas_requeridas_catalogo if col not in catalogo_df.columns]

if faltantes_pedidos:
    st.error(f"Faltan las siguientes columnas en la hoja de pedidos: {faltantes_pedidos}")
    st.stop()

if faltantes_catalogo:
    st.error(f"Faltan las siguientes columnas en la hoja del catálogo: {faltantes_catalogo}")
    st.stop()

# Sincronizar precios unitarios y unidades base desde el catálogo
catalogo_df = catalogo_df.rename(columns={"Unidad": "Unidad Base"})
pedidos_df = pedidos_df.merge(
    catalogo_df[["Producto", "Precio Unitario", "Unidad Base"]],
    on="Producto",
    how="left"
)

# Validar si "Unidad Base" y "Precio Unitario" existen y asignar valores predeterminados
if "Unidad Base" not in pedidos_df.columns:
    pedidos_df["Unidad Base"] = "unidad"
if "Precio Unitario" not in pedidos_df.columns:
    pedidos_df["Precio Unitario"] = 0

# Definir factores de conversión
conversion_factores = {
    ("kg", "g"): 1000,
    ("g", "kg"): 0.001,
    ("l", "ml"): 1000,
    ("ml", "l"): 0.001,
    ("piezas", "piezas"): 1
}

def calcular_total(row):
    unidad_base = row.get("Unidad Base", "")
    unidad_pedido = row.get("Unidad", "")
    factor = conversion_factores.get((unidad_pedido, unidad_base), 1)
    try:
        return row.get("Cantidad Solicitada", 0) / factor * row.get("Precio Unitario", 0)
    except ZeroDivisionError:
        return 0

# Actualización del total
try:
    pedidos_df["Total"] = pedidos_df.apply(calcular_total, axis=1)
except KeyError as e:
    st.error(f"Error de clave en el cálculo del total: {e}")
    st.stop()

# Reemplazar valores nulos en "Proveedor"
pedidos_df["Proveedor"] = pedidos_df["Proveedor"].fillna("Desconocido")

# Sincronizar datos globales
if "pedidos_df" not in st.session_state:
    st.session_state["pedidos_df"] = pedidos_df

pedidos_df = st.session_state["pedidos_df"]

# Solicitar contraseña para modo administrador
admin_password_correcta = "mekima12"
mensaje_error = None
if "modo_admin" not in st.session_state:
    st.session_state["modo_admin"] = False

if not st.session_state["modo_admin"]:
    with st.sidebar:
        st.markdown("### Activar Modo Administrador")
        password_input = st.text_input("Contraseña", type="password")
        if st.button("Activar"):
            if password_input == admin_password_correcta:
                st.session_state["modo_admin"] = True
                st.success("Modo Administrador activado.")
            else:
                mensaje_error = "Contraseña incorrecta."
else:
    with st.sidebar:
        st.markdown("### Modo Administrador Activado")
        if st.button("Desactivar"):
            st.session_state["modo_admin"] = False
            st.success("Modo Administrador desactivado.")

if mensaje_error:
    st.sidebar.error(mensaje_error)

# Función para limpiar cantidades solicitadas
def limpiar_cantidades():
    st.session_state["pedidos_df"]["Cantidad Solicitada"] = 0
    st.session_state["pedidos_df"]["Total"] = 0
    st.success("¡Cantidad solicitada reiniciada a 0 para todos los productos!")

# Botones destacados
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Limpiar Cantidades"):
        limpiar_cantidades()
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

# Función de búsqueda
st.markdown("### Buscar Artículo")
busqueda = st.text_input("Introduce el nombre del producto que deseas buscar:")
if busqueda:
    resultados = pedidos_df[pedidos_df["Producto"].str.contains(busqueda, case=False, na=False)]
    if resultados.empty:
        st.warning("No se encontraron resultados para tu búsqueda.")
    else:
        st.markdown("#### Resultados de la búsqueda")
        for index, row in resultados.iterrows():
            with st.expander(f"Editar: {row['Producto']}"):
                cantidad = st.number_input(
                    f"Cantidad ({row['Producto']})",
                    value=row["Cantidad Solicitada"],
                    min_value=0,
                    key=f"busqueda_cantidad_{index}"
                )
                pedidos_df.at[index, "Cantidad Solicitada"] = cantidad
                pedidos_df.at[index, "Total"] = calcular_total(row)

# Actualizar el estado global de pedidos
st.session_state["pedidos_df"] = pedidos_df

# Mostrar la tabla actualizada con filtro de cantidades > 0
st.markdown("### Resumen General de Pedidos")
pedidos_filtrados = pedidos_df[pedidos_df["Cantidad Solicitada"] > 0]
st.markdown(f"#### Total de productos por proveedor:")
productos_por_proveedor = pedidos_filtrados.groupby("Proveedor").size().reset_index(name="Productos")
st.dataframe(productos_por_proveedor, use_container_width=True)

st.dataframe(
    pedidos_filtrados[["Producto", "Cantidad Solicitada", "Unidad", "Precio Unitario", "Total", "Proveedor"]],
    use_container_width=True,
)










