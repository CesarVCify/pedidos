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


