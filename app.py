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
st.title("Gestión de Pedidos - Editar Pedidos")
st.info("Los productos solo pueden seleccionarse del catálogo cargado desde Google Sheets.")

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
    return df

# Función para actualizar precios unitarios desde el catálogo
def actualizar_precios(df_pedidos, df_catalogo):
    precios = dict(zip(df_catalogo["Producto"], df_catalogo["Precio Unitario"]))
    df_pedidos["Precio Unitario"] = df_pedidos["Producto"].map(precios)
    df_pedidos["Precio Unitario"] = df_pedidos["Precio Unitario"].fillna(0.01)  # Valor predeterminado si no hay precio
    return df_pedidos

# Botón para limpiar datos
if st.button("Limpiar Cantidades Solicitadas"):
    pedidos_df = limpiar_cantidades(pedidos_df)
    st.success("¡Cantidad solicitada reiniciada a 0 para todos los productos!")

# Botón para actualizar precios
if st.button("Actualizar Precios desde Catálogo"):
python
Copiar código
    pedidos_df = actualizar_precios(pedidos_df, catalogo_df)
    st.success("¡Precios unitarios actualizados desde el catálogo!")

# Reemplazar valores inválidos
pedidos_df["Cantidad Solicitada"] = pedidos_df["Cantidad Solicitada"].apply(lambda x: max(x, 0) if pd.notnull(x) else 0)
pedidos_df["Precio Unitario"] = pedidos_df["Precio Unitario"].apply(lambda x: max(x, 0.01) if pd.notnull(x) else 0.01)

# Restringir productos al catálogo
productos_existentes = catalogo_df["Producto"].tolist()

# Mostrar y editar pedidos agrupados por proveedor
st.subheader("Pedidos agrupados por Proveedor")
proveedores = pedidos_df["Proveedor"].unique()

for proveedor in proveedores:
    st.markdown(f"### Proveedor: {proveedor}")
    proveedor_df = pedidos_df[pedidos_df["Proveedor"] == proveedor]
    
    for index, row in proveedor_df.iterrows():
        with st.expander(f"Editar Pedido: {row['Producto']}"):
            # Producto (solo seleccionable desde el catálogo)
            producto = st.selectbox(
                "Producto",
                options=productos_existentes,
                index=productos_existentes.index(row["Producto"]) if row["Producto"] in productos_existentes else 0,
                key=f"producto_{index}"
            )
            # Cantidad
            cantidad = st.number_input(
                "Cantidad Solicitada",
                value=row["Cantidad Solicitada"],
                min_value=0,
                key=f"cantidad_{index}"
            )
            # Unidad
            unidad = st.text_input(
                "Unidad",
                value=row["Unidad"],
                key=f"unidad_{index}"
            )
            # Precio Unitario
            precio_unitario = st.number_input(
                "Precio Unitario",
                value=row["Precio Unitario"],
                min_value=0.01,
                key=f"precio_{index}"
            )

            # Actualizar valores en el DataFrame
            pedidos_df.at[index, "Producto"] = producto
            pedidos_df.at[index, "Cantidad Solicitada"] = cantidad
            pedidos_df.at[index, "Unidad"] = unidad
            pedidos_df.at[index, "Precio Unitario"] = precio_unitario
            pedidos_df.at[index, "Total"] = cantidad * precio_unitario

# Mostrar la tabla actualizada
st.subheader("Pedidos actualizados")
st.dataframe(pedidos_df)

# Descargar pedidos actualizados
if st.button("Descargar pedidos"):
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    nombre_csv = f"Pedidos_Actualizados_{fecha_actual}.csv"
    st.download_button(
        label="Descargar CSV",
        data=pedidos_df.to_csv(index=False).encode("utf-8"),
        file_name=nombre_csv,
        mime="text/csv",
    )


