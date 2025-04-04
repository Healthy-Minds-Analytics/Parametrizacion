import os
import streamlit as st
import pandas as pd
from io import BytesIO

# Importamos la lógica desde paramDEF.py
import paramDEF

def procesar_archivo(file_bytes, extension):
    """
    Lee el Excel en file_bytes usando el motor correcto según la extensión
    ('.xls' -> 'xlrd', '.xlsx' -> 'openpyxl'), 
    y luego llama a paramDEF.procesar_parametrizacion() para agrupar y crear la tabla final.
    """
    if extension.lower() == ".xls":
        # Necesitas xlrd instalado
        df_original, df_final = paramDEF.procesar_parametrizacion(file_bytes, engine="xlrd")
    elif extension.lower() == ".xlsx":
        # Para xlsx, usa openpyxl
        df_original, df_final = paramDEF.procesar_parametrizacion(file_bytes, engine="openpyxl")
    else:
        raise ValueError("Formato de archivo no soportado. Usa .xls o .xlsx.")
    
    return df_original, df_final

def main():
# Configura la página (opcional)
    st.set_page_config(layout="wide")

    # Definimos dos columnas: la primera estrecha para el logo, la segunda ancha para el título
    col1, col2 = st.columns([1, 5])  # Ajusta proporciones a tu gusto

    with col1:
        st.image("./Logo.png", use_container_width=True)

    with col2:
        st.write("")
    st.title("Organizador de puestos y sugerencia de unificaciones")
    st.write("Sube tu archivo Excel...")
    archivo_subido = st.file_uploader("Selecciona el archivo Excel (.xls o .xlsx)", type=["xlsx", "xls"])

    if archivo_subido is not None:
        try:
            # 1) Leemos el archivo en bytes
            file_bytes = BytesIO(archivo_subido.read())

            # 2) Detectamos la extensión
            _, extension = os.path.splitext(archivo_subido.name)

            # 3) Procesamos el archivo
            df_original, df_final = procesar_archivo(file_bytes, extension)

            st.subheader("Resumen de puestos")

            # Aquí mostramos la tabla SIN permitir edición, con scroll
            # Ajusta 'height' y 'width' a tu gusto
            st.dataframe(df_final, use_container_width=True, height=400)

            st.write("###")

            # 4. Botón para descargar la tabla final
            st.subheader("Descarga de la tabla final")

            def to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    # Solo creamos 1 hoja con la tabla
                    df.to_excel(writer, sheet_name="Resumen Puestos", index=False)
                return output.getvalue()

            df_excel = to_excel(df_final)

            st.download_button(
                label="📥 Descargar tabla final",
                data=df_excel,
                file_name="puestos_procesados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")

if __name__ == "__main__":
    main()
