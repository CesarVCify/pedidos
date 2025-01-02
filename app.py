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
columnas_requeridas_pedidos = ["Producto", "Cantidad Solicitada", "Unidad", "Precio Unitario", "Total", "Proveedor"]
columnas_requeridas_catalogo = ["Producto", "Precio Unitario"]

faltantes_pedidos = [col for col in columnas_requeridas_pedidos if col not in pedidos_df.columns]
faltantes_catalogo = [col for col in columnas_requeridas_catalogo if col not in catalogo_df.columns]

if faltantes_pedidos:
    st.error(f"Faltan las siguientes columnas en la hoja de pedidos: {faltantes_pedidos}")
    st.stop()

if faltantes_catalogo:
    st.error(f"Faltan las siguientes columnas en la hoja del catálogo: {faltantes_catalogo}")
    st.stop()

# Sincronizar precios unitarios desde el catálogo
pedidos_df = pedidos_df.merge(catalogo_df[["Producto", "Precio Unitario"]], on="Producto", how="left", suffixes=("", "_catalogo"))
pedidos_df["Precio Unitario"] = pedidos_df["Precio Unitario_catalogo"]
pedidos_df.drop(columns=["Precio Unitario_catalogo"], inplace=True)

# Reemplazar valores nulos en "Proveedor"
pedidos_df["Proveedor"] = pedidos_df["Proveedor"].fillna("Desconocido")

# Estado inicial de expansión de proveedores
if "proveedor_expandido" not in st.session_state:
    st.session_state.proveedor_expandido = {proveedor: False for proveedor in pedidos_df["Proveedor"].unique()}

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
                pedidos_df.at[index, "Total"] = cantidad * row["Precio Unitario"]

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

# Contraseña de administrador para edición de precio
if "admin_authenticated" not in st.session_state:
    st.session_state["admin_authenticated"] = False

admin_password = st.text_input("Introduce la contraseña de administrador para editar el precio unitario:", type="password")
if admin_password == "mekima12":
    st.session_state["admin_authenticated"] = True
    st.success("Acceso de administrador concedido. Ahora puedes editar los precios unitarios.")

for i, proveedor in enumerate(proveedores):
    col = col1 if i % 2 == 0 else col2
    with col:
        # Usar el estado actual de expansión para cada proveedor
        with st.expander(f"Proveedor: {proveedor}", expanded=st.session_state.proveedor_expandido[proveedor]):
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
                    unidad = st.selectbox(
                        "Unidad",
                        unidades_disponibles,
                        index=unidades_disponibles.index(row["Unidad"]) if row["Unidad"] in unidades_disponibles else 0,
                        key=f"unidad_{index}"
                    )
                    pedidos_df.at[index, "Unidad"] = unidad

                # Edición de precio unitario
                if st.session_state["admin_authenticated"]:
                    nuevo_precio = st.number_input(
                        f"Actualizar Precio Unitario ({row['Producto']})",
                        value=row["Precio Unitario"],
                        min_value=0.0,
                        step=0.1,
                        key=f"precio_{index}"
                    )
                    if st.button(f"Guardar Precio ({row['Producto']})", key=f"guardar_precio_{index}"):
                        pedidos_df.at[index, "Precio Unitario"] = nuevo_precio
                        pedidos_df.at[index, "Total"] = nuevo_precio * row["Cantidad Solicitada"]
                        st.success(f"Precio unitario actualizado para {row['Producto']}.")
                        st.session_state["admin_authenticated"] = False

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
