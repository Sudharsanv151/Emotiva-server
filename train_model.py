import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
import seaborn as sns
import pickle

file_path = r"D:\EE-Projects\Emotiva\Emotiva-server\combinations_improved.csv"
data = pd.read_csv(file_path)

encoders = {}
for column in ["emotion", "socialInteraction", "productivity", "overwhelmed", "RId"]:
    encoders[column] = LabelEncoder()
    data[column] = encoders[column].fit_transform(data[column])

with open("encoders_xgb.pkl", "wb") as f:
    pickle.dump(encoders, f)

X = data[["emotion", "intensity", "socialInteraction", "productivity", "overwhelmed"]]
y = data["RId"]

X.loc[:, "intensity"] = X["intensity"].astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

xgb_model = XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42, eval_metric='mlogloss')
xgb_model.fit(X_train, y_train)

y_pred = xgb_model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted', zero_division=1)
recall = recall_score(y_test, y_pred, average='weighted', zero_division=1)
f1 = f1_score(y_test, y_pred, average='weighted')

print(f"Accuracy: {accuracy * 100:.2f}%")
print(f"Precision: {precision * 100:.2f}%")
print(f"Recall: {recall * 100:.2f}%")
print(f"F1-Score: {f1 * 100:.2f}%")


with open("xgb_model.pkl", "wb") as f:
    pickle.dump(xgb_model, f)

def recommend(emotion, intensity, social_interaction, productivity, overwhelmed):
    try:
        with open("encoders_xgb.pkl", "rb") as f:
            encoders = pickle.load(f)
        with open("xgb_model.pkl", "rb") as f:
            model = pickle.load(f)

        input_data = {
            "emotion": encoders["emotion"].transform([emotion])[0],
            "intensity": int(intensity),
            "socialInteraction": encoders["socialInteraction"].transform([social_interaction])[0],
            "productivity": encoders["productivity"].transform([productivity])[0],
            "overwhelmed": encoders["overwhelmed"].transform([overwhelmed])[0],
        }
        input_df = pd.DataFrame([input_data])

        prediction = model.predict(input_df)[0]

        recommended_rid = encoders["RId"].inverse_transform([prediction])[0]
        return f"Recommended RId: {recommended_rid}"

    except ValueError as e:
        return f"Error: {e}"

print(recommend("happy", 7, "frequently", "yes", "no"))
