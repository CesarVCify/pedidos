import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de los IDs de las hojas de Google Sheets
ID_PEDIDOS = "106heHrtrvtaBVl13lvhqUzXlhLF7c3NFrbANXO1-FJk"
ID_CATALOGO = "1ERtd0fm2FY8-Pm72J3kl8J05T2ryG_fR91kOfPlPrfQ"

def obtener_url_publica(sheet_id):
    """Genera la URL de exportación pública de una hoja de Google Sheets."""
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

def cargar_hoja(sheet_id):
    """Carga datos desde una hoja pública de Google Sheets."""
    url = obtener_url_publica(sheet_id)
    try:
        df = pd.read_csv(url)
        df.columns = [col.strip() for col in df.columns]  # Limpia espacios en los encabezados
        return df
    except Exception as e:
        st.error(f"Error al cargar la hoja con ID {sheet_id}: {e}")
        return pd.DataFrame()

# Cargar datos iniciales
st.set_page_config(page_title="Gestión de Pedidos", layout="centered")
st.title("Gestión de Pedidos")
st.markdown("### Administra, edita y organiza tus pedidos de forma rápida y sencilla.")

pedidos_df = cargar_hoja(ID_PEDIDOS)
catalogo_df = cargar_hoja(ID_CATALOGO)

if pedidos_df.empty or catalogo_df.empty:
    st.warning("No se pudieron cargar los datos. Verifica que las hojas sean públicas y los IDs sean correctos.")
    st.stop()

# Validar columnas requeridas
columnas_requeridas = ["Producto", "Cantidad Solicitada", "Unidad", "Precio Unitario", "Total", "Proveedor"]
faltantes = [col for col in columnas_requeridas if col not in pedidos_df.columns]

if faltantes:
    st.error(f"Faltan las siguientes columnas en la hoja de pedidos: {faltantes}")
    st.stop()

# Reemplazar valores nulos en "Proveedor"
pedidos_df["Proveedor"] = pedidos_df["Proveedor"].fillna("Desconocido")

# Función para limpiar cantidades solicitadas
def limpiar_cantidades(df):
    df["Cantidad Solicitada"] = 0  # Reinicia todas las cantidades a 0
    df["Total"] = 0  # También reinicia los totales
    return df

# Botones destacados
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Limpiar Cantidades"):
        pedidos_df = limpiar_cantidades(pedidos_df)  # Actualiza las cantidades y totales
        st.session_state["pedidos_df"] = pedidos_df  # Actualiza el estado global
        st.success("¡Cantidad solicitada reiniciada a 0 para todos los productos!")
with col2:
    if st.button("📥 Descargar Pedidos"):
        pedidos_filtrados = pedidos_df[pedidos_df["Cantidad Solicitada"] > 0]  # Excluir productos con cantidad 0
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        nombre_csv = f"Pedidos_Actualizados_{fecha_actual}.csv"
        st.download_button(
            label="Descargar CSV",
            data=pedidos_filtrados.to_csv(index=False).encode("utf-8"),
            file_name=nombre_csv,
            mime="text/csv",
        )

# Mostrar y editar pedidos agrupados por proveedor
st.markdown("### Pedidos Agrupados por Proveedor")
proveedores = pedidos_df["Proveedor"].unique()

for proveedor in proveedores:
    with st.expander(f"Proveedor: {proveedor}"):
        proveedor_df = pedidos_df[pedidos_df["Proveedor"] == proveedor]
        for index, row in proveedor_df.iterrows():
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.text_input(
                    "Producto",
                    value=row["Producto"],
                    key=f"producto_{index}",
                    disabled=True  # Solo lectura para evitar modificar directamente el nombre
                )
            with col2:
                cantidad = st.number_input(
                    "Cantidad",
                    value=row["Cantidad Solicitada"],
                    min_value=0,
                    key=f"cantidad_{index}"
                )
                pedidos_df.at[index, "Cantidad Solicitada"] = cantidad
                pedidos_df.at[index, "Total"] = cantidad * row["Precio Unitario"]
            with col3:
                st.text(f"${row['Total']:.2f}")  # Mostrar el total calculado

# Sincronizar cambios con la tabla principal
st.session_state["pedidos_df"] = pedidos_df

# Mostrar la tabla actualizada en una vista compacta
st.markdown("### Resumen General de Pedidos")
st.dataframe(
    pedidos_df[["Producto", "Cantidad Solicitada", "Total", "Proveedor"]],  # Solo mostrar columnas importantes
    use_container_width=True,
)



