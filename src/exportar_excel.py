import pandas as pd
import os
from datetime import date
from conexion import conectar_bd  # ✅ usar tu conexión existente

# --- 1. Función para obtener estadísticas desde la BD ---
def obtener_estadisticas():
    """Consulta rápida a la BD para estadísticas globales."""
    try:
        cnx = conectar_bd()
        df = pd.read_sql("SELECT resultado_diagnostico FROM paciente", cnx)
        cnx.close()

        total = len(df)
        positivos = int((df["resultado_diagnostico"] == 1).sum())
        negativos = int((df["resultado_diagnostico"] == 0).sum())

        return {
            "Total Pacientes": total,
            "Positivos (riesgo)": positivos,
            "Negativos (bajo riesgo)": negativos
        }
    except Exception as e:
        print("❌ Error en obtener_estadisticas:", e)
        return {
            "Total Pacientes": 0,
            "Positivos (riesgo)": 0,
            "Negativos (bajo riesgo)": 0
        }

# --- 2. Función para generar el Excel ---
def guardar_en_excel(nombre_paciente, edad, genero, entrada, resultado):
    """
    Genera un archivo Excel con 2 hojas:
    1) Informe individual del paciente
    2) Estadísticas globales (con gráfico)
    """
    # Datos del paciente (fila única)
    data = {
        "Nombre": nombre_paciente,
        "Edad": edad,
        "Género": genero,
        "Pregnancies": entrada['Pregnancies'],
        "Glucose": entrada['Glucose'],
        "BloodPressure": entrada['BloodPressure'],
        "SkinThickness": entrada['SkinThickness'],
        "Insulin": entrada['Insulin'],
        "BMI": entrada['BMI'],
        "DiabetesPedigreeFunction": entrada['DiabetesPedigreeFunction'],
        "Age (modelo)": entrada['Age'],
        "Resultado": "Positivo (riesgo)" if resultado['pred']==1 else "Negativo (bajo riesgo)",
        "Probabilidad": round(resultado['prob'], 2),
        "Fecha diagnóstico": date.today().strftime("%d-%m-%Y")  # ✅ fecha bien formateada
    }
    df_paciente = pd.DataFrame([data])

    # Estadísticas globales (desde la BD)
    estadisticas = obtener_estadisticas()
    df_stats = pd.DataFrame([estadisticas])

    # Carpeta de salida
    output_dir = os.path.join(os.path.dirname(__file__), "..", "reportes")
    os.makedirs(output_dir, exist_ok=True)

    filename = os.path.join(output_dir, f"reporte_{nombre_paciente}_{date.today()}.xlsx")

    # --- Escribir Excel ---
    with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:
        # --- Hoja 1: Informe del paciente ---
        df_paciente.to_excel(writer, index=False, sheet_name="Informe Médico", startrow=2)
        workbook  = writer.book
        worksheet = writer.sheets["Informe Médico"]

        # Título arriba
        worksheet.merge_range("A1:H1", "INFORME MÉDICO - DIAGNÓSTICO DIABETES TIPO 2", workbook.add_format({
            "bold": True, "align": "center", "valign": "vcenter",
            "font_size": 14, "bg_color": "#9BBB59", "border": 1
        }))

        # Estilos
        header_format = workbook.add_format({
            "bold": True, "align": "center", "valign": "vcenter",
            "bg_color": "#4F81BD", "font_color": "white", "border": 1
        })
        cell_format = workbook.add_format({
            "align": "center", "valign": "vcenter", "border": 1
        })

        # Ajustar ancho
        worksheet.set_column("A:Z", 18)

        # Encabezados + valores
        for col_num, value in enumerate(df_paciente.columns.values):
            worksheet.write(2, col_num, value, header_format)
            worksheet.write(3, col_num, df_paciente.iloc[0, col_num], cell_format)

        # Logo (si existe) debajo
        logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png")
        if os.path.exists(logo_path):
            worksheet.insert_image("A6", logo_path, {"x_scale": 0.4, "y_scale": 0.4})

        # --- Hoja 2: Estadísticas globales ---
        df_stats.to_excel(writer, index=False, sheet_name="Estadísticas", startrow=1)
        ws_stats = writer.sheets["Estadísticas"]

        ws_stats.write("A1", "📊 Estadísticas Globales", workbook.add_format({
            "bold": True, "font_size": 12, "bg_color": "#FFD966", "border": 1
        }))

        # Encabezados + valores
        for col_num, value in enumerate(df_stats.columns.values):
            ws_stats.write(1, col_num, value, header_format)
            ws_stats.write(2, col_num, df_stats.iloc[0, col_num], cell_format)
        ws_stats.set_column("A:Z", 25)

        # --- Gráfico en hoja 2 ---
        chart = workbook.add_chart({"type": "column"})
        chart.add_series({
            "categories": ["Estadísticas", 1, 1, 1, 2],  # encabezados: Positivos/Negativos
            "values":     ["Estadísticas", 2, 1, 2, 2],  # valores: cantidades
            "name": "Resultados IA"
        })
        chart.set_title({"name": "Distribución de Diagnósticos"})
        chart.set_x_axis({"name": "Tipo de Resultado"})
        chart.set_y_axis({"name": "Cantidad de Pacientes"})

        # Insertar gráfico debajo de la tabla
        ws_stats.insert_chart("A5", chart, {"x_scale": 1.2, "y_scale": 1.2})

    return filename
