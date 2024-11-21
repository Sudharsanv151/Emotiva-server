import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

def train_emotion_model():
    dataset_path = './dataset/Emotiva_dataset.csv'  # Update this with your CSV file path
    data = pd.read_csv(dataset_path)

    # Check for missing values
    print("Missing values in each column:")
    print(data.isnull().sum())

    # Drop rows with missing values
    data.dropna(inplace=True)

    # Prepare the features and target variable
    X = data[['intensity', 'socialInteraction', 'productivity', 'overwhelmed']]  # Example features
    y = data['emotion']  # Target variable

    # Convert categorical variables to numerical if needed
    X = pd.get_dummies(X)

    # Split the dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the model
    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    # Save the model
    joblib.dump(model, 'emotion_model.pkl')
    print("Model trained and saved successfully.")

if __name__ == '__main__':
    train_emotion_model()
