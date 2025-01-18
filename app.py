import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Configurar el acceso a la hoja de cálculo
def connect_to_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/106heHrtrvtaBVl13lvhqUzXlhLF7c3NFrbANXO1-FJk/edit?gid=119992261")
    return sheet

# Función principal
def main():
    st.title("Sistema de Pedidos - Mekima")

    # Conectar a la hoja de cálculo
    try:
        sheet = connect_to_sheet()
        worksheet = sheet.get_worksheet(0)  # Primera hoja de la hoja de cálculo
    except Exception as e:
        st.error("No se pudo conectar a la hoja de cálculo. Revisa las credenciales o el enlace.")
        st.stop()

    # Cargar los productos desde la hoja de cálculo
    st.subheader("Productos Disponibles")
    products = worksheet.get_all_records()
    if not products:
        st.warning("No hay productos disponibles.")
        st.stop()

    # Mostrar productos en una tabla
    st.write("Lista de productos:")
    st.table(products)

    # Selección de productos para un pedido
    st.subheader("Generar Pedido")
    product_names = [product["Nombre"] for product in products]  # Suponiendo que la columna se llama "Nombre"
    selected_products = st.multiselect("Selecciona los productos:", product_names)

    # Seleccionar cantidades para cada producto
    order = []
    for product_name in selected_products:
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"Producto: {product_name}")
        with col2:
            qty = st.number_input(f"Cantidad de {product_name}:", min_value=1, step=1, key=product_name)
            order.append({"Producto": product_name, "Cantidad": qty})

    # Confirmar el pedido
    if st.button("Confirmar Pedido"):
        if order:
            # Agregar el pedido a una nueva hoja llamada "Pedidos"
            try:
                orders_sheet = sheet.worksheet("Pedidos")
            except gspread.exceptions.WorksheetNotFound:
                orders_sheet = sheet.add_worksheet(title="Pedidos", rows="100", cols="10")
                orders_sheet.append_row(["Producto", "Cantidad"])

            for item in order:
                orders_sheet.append_row([item["Producto"], item["Cantidad"]])
            st.success("Pedido generado exitosamente.")
            st.experimental_rerun()
        else:
            st.warning("Por favor selecciona al menos un producto.")

    # Mostrar pedidos generados
    st.subheader("Pedidos Generados")
    try:
        orders_sheet = sheet.worksheet("Pedidos")
        orders = orders_sheet.get_all_records()
        if orders:
            st.table(orders)
        else:
            st.write("No hay pedidos generados.")
    except gspread.exceptions.WorksheetNotFound:
        st.write("Aún no se ha generado ningún pedido.")

if __name__ == "__main__":
    main()



































