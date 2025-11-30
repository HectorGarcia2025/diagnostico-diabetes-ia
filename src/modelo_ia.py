# src/modelo_ia.py
import joblib
import pandas as pd
import os

# Ruta del modelo entrenado
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'model_rf.joblib')

# Cargar modelo (solo una vez)
model = joblib.load(MODEL_PATH)

def predecir_diabetes(input_dict):
    """
    Recibe un diccionario con las características del paciente:
    {
        'Pregnancies': int,
        'Glucose': float,
        'BloodPressure': float,
        'SkinThickness': float,
        'Insulin': float,
        'BMI': float,
        'DiabetesPedigreeFunction': float,
        'Age': int
    }

    Devuelve un diccionario:
    {
        'pred': 0 o 1,
        'prob': probabilidad (float entre 0 y 1)
    }
    """
    # Columnas esperadas (orden correcto)
    cols = ['Pregnancies','Glucose','BloodPressure','SkinThickness',
            'Insulin','BMI','DiabetesPedigreeFunction','Age']

    # Crear un DataFrame con los datos del paciente
    x = pd.DataFrame([[input_dict.get(c, 0) for c in cols]], columns=cols)

    # Predicción
    pred = int(model.predict(x)[0])
    prob = float(model.predict_proba(x)[0][1])  # probabilidad clase 1 (diabetes)

    return {'pred': pred, 'prob': prob}
