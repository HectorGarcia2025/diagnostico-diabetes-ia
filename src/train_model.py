# src/train_model.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

def main():
    # 1. Cargar dataset (desde data/)
    df = pd.read_csv('data/pima_diabetes.csv')

    # Columnas del dataset
    X = df.drop(columns=['Outcome'])
    y = df['Outcome']

    # 2. Dividir en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 3. Entrenar Random Forest
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    # 4. Evaluar
    y_pred = clf.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print(classification_report(y_test, y_pred))

    # 5. Guardar modelo entrenado
    joblib.dump(clf, 'models/model_rf.joblib')
    print("✅ Modelo guardado en models/model_rf.joblib")

if __name__ == '__main__':
    main()
