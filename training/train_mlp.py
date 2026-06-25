import pandas as pd
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
from pathlib import Path

PROJE_KOK = Path(__file__).resolve().parent.parent
CSV_PATH = PROJE_KOK / "training" / "mlp_dataset.csv"
MODEL_PATH = PROJE_KOK / "models" / "mlp_action.pkl"
SCALER_PATH = PROJE_KOK / "models" / "mlp_scaler.pkl"
 
AKSIYON_ADLARI = {
    0: "Normal Beslenme",
    1: "Glisemik Uyari",
    2: "Agir Ogun",
    3: "Cheat Meal"
}
 
def main():
    # Veriyi yukle
    print("Veri yukleniyor...")
    df = pd.read_csv(CSV_PATH)
    print(f"  Satir sayisi: {len(df)}")
    print(f"  Sutunlar: {list(df.columns)}")
    
    X = df[["kalori", "karb", "glisemik"]].values
    y = df["aksiyon"].values
    
    print("\nSinif dagilimi:")
    for k in sorted(set(y)):
        print(f"  Sinif {k} ({AKSIYON_ADLARI[k]:20s}): {(y==k).sum()} ornek")
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\nTrain: {len(X_train)}, Test: {len(X_test)}")
    
    # Standardizasyon (3 girdi farkli olceklerde: kalori 100-900, karb 5-100, glisemik 0-75)
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)
    
    # Model
    # 3 katmanli sinir agi: 3 -> 16 -> 8 -> 4
    print("\nMLP egitimi basliyor...")
    model = MLPClassifier(
        hidden_layer_sizes=(16, 8),
        activation="relu",
        solver="adam",
        learning_rate_init=0.01,
        max_iter=2000,
        early_stopping=True,
        validation_fraction=0.15,
        n_iter_no_change=30,
        random_state=42,
        verbose=False
    )
    model.fit(X_train_s, y_train)
    
    print(f"  Egitim tamam, epoch: {model.n_iter_}")
    
    # Test accuracy
    train_acc = model.score(X_train_s, y_train)
    test_acc = model.score(X_test_s, y_test)
    print(f"\n  Train accuracy: {train_acc:.3f}")
    print(f"  Test accuracy:  {test_acc:.3f}")
    
    # Detayli rapor
    print("\nClassification report (test):")
    y_pred = model.predict(X_test_s)
    print(classification_report(
        y_test, y_pred,
        target_names=[AKSIYON_ADLARI[i] for i in sorted(AKSIYON_ADLARI.keys())]
    ))
    
    print("Confusion matrix (test):")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    
    # Modeli kaydet
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print(f"\nModel kaydedildi: {MODEL_PATH}")
    print(f"Scaler kaydedildi: {SCALER_PATH}")
    
    # Ornek tahminler
    print("\nOrnek tahminler:")
    ornekler = [
        (150, 30, 70, "Pirinc pilavi orta porsiyon"),
        (480, 55, 65, "Baklava 1 dilim"),
        (250, 35, 0, "Sis kebap orta"),
        (900, 95, 65, "Cok bol baklava (cheat)"),
    ]
    
    for kal, karb, gi, aciklama in ornekler:
        x = scaler.transform([[kal, karb, gi]])
        pred = model.predict(x)[0]
        prob = model.predict_proba(x)[0]
        print(f"  {aciklama}:")
        print(f"    [{kal} kcal, {karb}g karb, GI={gi}] -> {AKSIYON_ADLARI[pred]}")
        print(f"    Olasiliklar: {dict(zip(range(4), [f'{p:.2f}' for p in prob]))}")
 
if __name__ == "__main__":
    main()
