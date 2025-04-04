import pandas as pd
from io import BytesIO

def encontrar_fila_encabezados(df_raw):
    """
    Devuelve el índice de la fila que contiene los encabezados
    'CENTRO DE TRABAJO', 'DEPARTAMENTO' y 'PUESTO DE TRABAJO'.
    Si no se encuentra, retorna None.
    """
    for i, row in df_raw.iterrows():
        encabezados = [str(c).strip().upper() for c in row.values]
        if ("CENTRO DE TRABAJO" in encabezados 
            and "DEPARTAMENTO" in encabezados 
            and "PUESTO DE TRABAJO" in encabezados):
            return i
    return None

def procesar_parametrizacion(file_bytes, engine="openpyxl"):
    """
    Lee un archivo Excel (en formato BytesIO), identifica la fila de encabezados,
    agrupa datos y genera un DataFrame final con columnas extra
    ('ADVERTENCIA' y 'PROPUESTA DE UNIFICACIÓN').
    
    Retorna una tupla: (df_original, df_final).
    - df_original: DataFrame leído con la fila de encabezados apropiada.
    - df_final: DataFrame agregado/agrupado con advertencias, sugerencias y fila de TOTAL.
    """

    # 1) Leemos el Excel sin encabezados
    df_raw = pd.read_excel(file_bytes, sheet_name=0, header=None, engine=engine)

    # 2) Buscamos la fila de encabezados
    fila_encabezados = encontrar_fila_encabezados(df_raw)
    if fila_encabezados is None:
        raise ValueError("No se encontraron las columnas 'CENTRO DE TRABAJO', 'DEPARTAMENTO', 'PUESTO DE TRABAJO'.")

    # 3) Reposicionamos el puntero para volver a leer
    file_bytes.seek(0)
    df_original = pd.read_excel(file_bytes, sheet_name=0, header=fila_encabezados, engine=engine)

    # 4) Detectamos los nombres de columnas clave
    def match_column(nombre, columnas):
        for c in columnas:
            if nombre in str(c).strip().upper():
                return c
        return None

    col_centro = match_column("CENTRO DE TRABAJO", df_original.columns)
    col_dep    = match_column("DEPARTAMENTO", df_original.columns)
    col_puesto = match_column("PUESTO DE TRABAJO", df_original.columns)

    if not (col_centro and col_dep and col_puesto):
        raise ValueError("No se pudieron ubicar correctamente las columnas clave en el Excel.")

    # 5) Agrupación y conteo
    df_filtrado = df_original[[col_centro, col_dep, col_puesto]].dropna()
    df_agrupado = (
        df_filtrado
        .groupby([col_centro, col_dep, col_puesto])
        .size()
        .reset_index(name="NÚMERO DE PERSONAS")
        .sort_values(by=[col_centro, col_dep, col_puesto])
    )

    print(df_agrupado)

    # 6) Añadimos advertencias y sugerencias
    advertencias = []
    sugerencias  = []

    for i, row in df_agrupado.iterrows():
        centro  = row[col_centro]
        depto   = row[col_dep]
        puesto  = row[col_puesto]
        cant    = row["NÚMERO DE PERSONAS"]

        if cant > 2:
            # No advertencia
            advertencias.append("")
            sugerencias.append("")
        else:
            advertencias.append("⚠️ Bajo número de personas")
            # Buscamos algún otro puesto (en el mismo depto o centro) con >3 personas
            similares_depto = df_agrupado[
                (df_agrupado[col_centro] == centro) &
                (df_agrupado[col_dep] == depto) &
                (df_agrupado[col_puesto] != puesto) &
                (df_agrupado["NÚMERO DE PERSONAS"] > 3)
            ]
            if not similares_depto.empty:
                sugerencias.append(f"Unificar con: {similares_depto.iloc[0][col_puesto]}")
            else:
                similares_centro = df_agrupado[
                    (df_agrupado[col_centro] == centro) &
                    (df_agrupado[col_puesto] != puesto) &
                    (df_agrupado["NÚMERO DE PERSONAS"] > 3)
                ]
                if not similares_centro.empty:
                    sugerencias.append(f"Unificar con: {similares_centro.iloc[0][col_puesto]}")
                else:
                    sugerencias.append("Unificar con otro puesto del centro")

    df_agrupado["ADVERTENCIA"]              = advertencias
    df_agrupado["PROPUESTA DE UNIFICACIÓN"] = sugerencias

    # 7) Agregamos fila TOTAL al final
    total_personas = df_agrupado["NÚMERO DE PERSONAS"].sum()
    fila_total = pd.DataFrame({
        col_centro: ["TOTAL"],
        col_dep:    [""],
        col_puesto: [""],
        "NÚMERO DE PERSONAS": [total_personas],
        "ADVERTENCIA": [""],
        "PROPUESTA DE UNIFICACIÓN": [""]
    })

    df_final = pd.concat([df_agrupado, fila_total], ignore_index=True)

    return df_original, df_final
