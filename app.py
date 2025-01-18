import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Configuración de las credenciales
def get_gsheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/106heHrtrvtaBVl13lvhqUzXlhLF7c3NFrbANXO1-FJk/edit?gid=119992261#gid=119992261")
    return sheet

# Carga inicial de la hoja
sheet = get_gsheet()
worksheet = sheet.get_worksheet(0)  # Seleccionar la primera hoja

# Streamlit UI
st.title("Gestión de Pedidos - Mekima")

# Mostrar tabla
st.subheader("Pedidos Actuales")
data = worksheet.get_all_records()
if data:
    st.write(data)
else:
    st.write("No hay pedidos registrados.")

# Agregar un nuevo pedido
st.subheader("Agregar Nuevo Pedido")
col1, col2 = st.columns(2)

with col1:
    cliente = st.text_input("Nombre del Cliente")
    producto = st.selectbox("Producto", ["Café", "Té", "Bebida Fría", "Desayuno"])

with col2:
    cantidad = st.number_input("Cantidad", min_value=1, step=1)
    observaciones = st.text_area("Observaciones")

if st.button("Agregar Pedido"):
    if cliente and producto:
        worksheet.append_row([cliente, producto, cantidad, observaciones])
        st.success("Pedido agregado exitosamente.")
        st.experimental_rerun()
    else:
        st.error("Por favor, completa todos los campos.")

# Eliminar un pedido
st.subheader("Eliminar Pedido")
if data:
    pedido_index = st.number_input("Número de Pedido", min_value=1, max_value=len(data), step=1)
    if st.button("Eliminar Pedido"):
        worksheet.delete_rows(pedido_index + 1)  # +1 para ajustar por el encabezado
        st.success("Pedido eliminado exitosamente.")
        st.experimental_rerun()


































