import streamlit as st
import pandas as pd
from io import BytesIO

# Importamos la lógica desde paramDEF.py
import paramDEF

def main():
    st.title("Organizador de puestos y sugerencia de unificaciones")
    st.write("Sube un archivo Excel con las columnas requeridas...")

    # 1. Subida del archivo
    archivo_subido = st.file_uploader("Selecciona el archivo Excel", type=["xlsx"])

    if archivo_subido is not None:
        try:
            # Convertimos el archivo subido en un objeto BytesIO
            file_bytes = BytesIO(archivo_subido.read())

            # 2. Llamamos a la función de paramDEF.py para procesar
            #    (df_original no lo vamos a usar para la descarga, 
            #     solo df_final, que es el de advertencias/sugerencias)
            df_original, df_final = paramDEF.procesar_parametrizacion(file_bytes)

            st.subheader("Resumen de puestos (agrupado, con advertencias y sugerencias)")

            # 3. Permitimos editar df_final en línea
            df_editado = st.experimental_data_editor(df_final, num_rows="dynamic")

            st.write("###")

            # 4. Botón para descargar SOLO la tabla editada
            st.subheader("Descarga de la tabla final editada")

            def to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    # Solo creamos 1 hoja con la tabla editada
                    df.to_excel(writer, sheet_name="Resumen Puestos Editado", index=False)
                return output.getvalue()

            df_excel = to_excel(df_editado)

            st.download_button(
                label="📥 Descargar tabla editada",
                data=df_excel,
                file_name="puestos_editados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")

if __name__ == "__main__":
    main()
