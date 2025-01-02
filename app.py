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
pedidos_df["Unidad Base"] = pedidos_df["Unidad Base"].fillna("unidad")
pedidos_df["Precio Unitario"] = pedidos_df["Precio Unitario"].fillna(0)

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

# Estado inicial de expansión de proveedores
if "proveedor_expandido" not in st.session_state:
    st.session_state["proveedor_expandido"] = {proveedor: False for proveedor in pedidos_df["Proveedor"].unique()}

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

# Resumen de Pedidos por Proveedor
st.markdown("### Resumen por Proveedor")
resumen_proveedor = pedidos_df.groupby("Proveedor")["Total"].sum().reset_index()
st.dataframe(resumen_proveedor, use_container_width=True)

# Mostrar y editar pedidos agrupados por proveedor en dos columnas
st.markdown("### Pedidos Agrupados por Proveedor")
proveedores = pedidos_df["Proveedor"].unique()

# Botón para expandir/contraer todos
if st.button("🔽 Expandir Todo"):
    for proveedor in proveedores:
        st.session_state.proveedor_expandido[proveedor] = True

if st.button("🔼 Contraer Todo"):
    for proveedor in proveedores:
        st.session_state.proveedor_expandido[proveedor] = False

# Dividir los proveedores en dos columnas
col1, col2 = st.columns(2)
unidades_disponibles = ["kg", "g", "l", "ml", "piezas"]
for i, proveedor in enumerate(proveedores):
    col = col1 if i % 2 == 0 else col2
    with col:
        # Usar el estado actual de expansión para cada proveedor
        with st.expander(f"Proveedor: {proveedor}", expanded=st.session_state.proveedor_expandido[proveedor]):
            proveedor_df = pedidos_df[pedidos_df["Proveedor"] == proveedor]

            for index, row in proveedor_df.iterrows():
                # Mostrar Producto y Precio Unitario
                st.markdown(f"**{row['Producto']}**")
                st.text(f"Precio Unitario: ${row['Precio Unitario']:.2f} ({row['Unidad Base']})")

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
                    pedidos_df.at[index, "Total"] = calcular_total(row)
                with sub_col2:
                    unidad = st.selectbox(
                        "Unidad",
                        unidades_disponibles,
                        index=unidades_disponibles.index(row["Unidad"])
                        if row["Unidad"] in unidades_disponibles else 0,
                        key=f"unidad_{index}"
                    )
                    pedidos_df.at[index, "Unidad"] = unidad

                # Edición del precio unitario en modo administrador
                if st.session_state["modo_admin"]:
                    nuevo_precio = st.number_input(
                        "Nuevo Precio Unitario:",
                        value=row["Precio Unitario"],
                        min_value=0.0,
                        step=0.01,
                        key=f"nuevo_precio_{index}"
                    )
                    if st.button("Actualizar Precio", key=f"actualizar_precio_{index}"):
                        pedidos_df.at[index, "Precio Unitario"] = nuevo_precio
                        pedidos_df.at[index, "Total"] = calcular_total(row)
                        st.success(f"Precio actualizado para {row['Producto']}.")
                        st.session_state["pedidos_df"] = pedidos_df

            # Botón para contraer esta sección específica
            if st.button(f"Contraer {proveedor}", key=f"contraer_{proveedor}"):
                st.session_state.proveedor_expandido[proveedor] = False

# Actualizar el estado global de pedidos
st.session_state["pedidos_df"] = pedidos_df

# Mostrar la tabla actualizada con filtro de cantidades > 0
st.markdown("### Resumen General de Pedidos")
pedidos_filtrados = pedidos_df[pedidos_df["Cantidad Solicitada"] > 0]
st.dataframe(
    pedidos_filtrados[["Producto", "Cantidad Solicitada", "Unidad", "Precio Unitario", "Total", "Proveedor"]],
    use_container_width=True,
)










