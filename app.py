import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Configuración para Google Sheets
USAR_GOOGLE_SHEETS = True  # Cambia a False si no usas Google Sheets

if USAR_GOOGLE_SHEETS:
    # Credenciales para Google Sheets (usa tu archivo JSON o st.secrets en Streamlit Cloud)
    creds = {
        "type": "service_account",
        "project_id": "tu_project_id",
        "private_key_id": "tu_private_key_id",
        "private_key": "-----BEGIN PRIVATE KEY-----\ntu_clave_privada\n-----END PRIVATE KEY-----\n",
        "client_email": "tu_email_de_servicio@tu_proyecto.iam.gserviceaccount.com",
        "client_id": "tu_client_id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/tu_email_de_servicio%40tu_proyecto.iam.gserviceaccount.com",
    }
    gc = gspread.service_account_from_dict(creds)
    sheet = gc.open_by_key("TU_ID_DE_HOJA").sheet1  # Reemplaza con el ID de tu hoja

# Cargar datos iniciales
if USAR_GOOGLE_SHEETS:
    pedidos_df = pd.DataFrame(sheet.get_all_records())
else:
    # Datos simulados
    data = {
        "Producto": ["Café", "Té", "Pan"],
        "Cantidad Solicitada": [10, 5, 20],
        "Unidad": ["kg", "kg", "piezas"],
        "Precio Unitario": [150, 100, 15],
        "Total": [1500, 500, 300],
    }
    pedidos_df = pd.DataFrame(data)

# Título de la aplicación
st.title("Gestión de Pedidos - Editar Pedidos")

# Mostrar la tabla inicial con un editor interactivo
st.subheader("Pedidos actuales")
edited_df = st.data_editor(
    pedidos_df,
    num_rows="dynamic",  # Permite agregar o eliminar filas
    use_container_width=True,
)

# Validación de datos
valido = True
if st.button("Validar y Actualizar Totales"):
    for i, row in edited_df.iterrows():
        if row["Cantidad Solicitada"] <= 0 or row["Precio Unitario"] <= 0:
            valido = False
            st.error(
                f"Error en la fila {i+1}: Cantidad y Precio deben ser positivos."
            )
            break

    if valido:
        # Calcular los totales actualizados
        edited_df["Total"] = (
            edited_df["Cantidad Solicitada"] * edited_df["Precio Unitario"]
        )
        st.success("Datos validados y totales actualizados.")
        st.write(edited_df)

        # Guardar en Google Sheets si está habilitado
        if USAR_GOOGLE_SHEETS:
            sheet.clear()  # Limpia la hoja antes de guardar los datos
            sheet.update([edited_df.columns.values.tolist()] + edited_df.values.tolist())
            st.success("Datos guardados en Google Sheets.")

# Botón para descargar los datos
st.subheader("Descargar datos")
if st.button("Descargar CSV"):
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    nombre_csv = f"Pedidos_Actualizados_{fecha_actual}.csv"
    st.download_button(
        label="Descargar CSV",
        data=edited_df.to_csv(index=False).encode("utf-8"),
        file_name=nombre_csv,
        mime="text/csv",
    )
