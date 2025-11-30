# src/app_streamlit.py
import streamlit as st
from modelo_ia import predecir_diabetes
from conexion import conectar_bd
from datetime import date
from exportar_excel import guardar_en_excel

st.title("🩺 Diagnóstico temprano de Diabetes Tipo 2")
st.write("Ingrese los datos del paciente:")

with st.form("form"):
    nombre = st.text_input("Nombre del paciente")
    edad = st.number_input("Edad", min_value=0, max_value=120, value=30)
    genero = st.selectbox("Género", ["Masculino", "Femenino", "Otro"])
    pregnancies = st.number_input("Número de embarazos (Pregnancies)", min_value=0, value=0)
    glucose = st.number_input("Glucosa (mg/dL)", min_value=0, value=120)
    bloodpressure = st.number_input("Presión arterial (mm Hg)", min_value=0, value=70)
    skinthickness = st.number_input("Skin Thickness", min_value=0, value=20)
    insulin = st.number_input("Insulina", min_value=0, value=79)
    bmi = st.number_input("BMI (Índice de masa corporal)", min_value=0.0, value=32.0)
    dpf = st.number_input("Diabetes Pedigree Function", min_value=0.0, value=0.5)
    age = st.number_input("Edad (modelo)", min_value=0, value=30)

    submitted = st.form_submit_button("Predecir")

if submitted:
    entrada = {
        'Pregnancies': int(pregnancies),
        'Glucose': float(glucose),
        'BloodPressure': float(bloodpressure),
        'SkinThickness': float(skinthickness),
        'Insulin': float(insulin),
        'BMI': float(bmi),
        'DiabetesPedigreeFunction': float(dpf),
        'Age': int(age)
    }

    resultado = predecir_diabetes(entrada)
    pred = resultado['pred']
    prob = resultado['prob']

    st.subheader("📊 Resultado del modelo:")
    st.write(f"**Diagnóstico:** {'Positivo (riesgo)' if pred==1 else 'Negativo (bajo riesgo)'}")
    st.write(f"**Probabilidad estimada:** {prob:.2f}")

    # Guardar en la base de datos
    try:
        cnx = conectar_bd()
        cursor = cnx.cursor()

        sql = ("INSERT INTO paciente "
               "(nombre_paciente, edad, genero, pregnancies, glucose, bloodpressure, skinthickness, insulin, bmi, dpf, age, resultado_diagnostico, probabilidad, fecha_diagnostico) "
               "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")

        vals = (nombre, edad, genero, pregnancies, glucose, bloodpressure,
                skinthickness, insulin, bmi, dpf, age, pred, prob, date.today())

        cursor.execute(sql, vals)
        cnx.commit()
        cnx.close()
        st.success("✅ Registro guardado en la base de datos")
        file_path = guardar_en_excel(nombre, edad, genero, entrada, resultado)
        st.info(f"📂 Reporte exportado a: {file_path}")
    except Exception as e:
        st.error(f"❌ Error al guardar en la base de datos: {e}")
