import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC
from sklearn.cluster import KMeans
import joblib
import os

def train_and_save_models():
    # Load dataset
    dataset_path = 'dataset/career_data.csv'
    if not os.path.exists(dataset_path):
        print(f"Error: {dataset_path} not found. Please run generate_dataset.py first.")
        return

    df = pd.read_csv(dataset_path)

    # Features and Targets
    X = df[['CGPA', 'LeetCode', 'Projects', 'Internships', 'Communication']]
    y_placed = df['Placed']
    y_salary = df['Salary']

    # Scale the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 1. Logistic Regression (Target: Placed)
    print("Training Logistic Regression...")
    logistic_model = LogisticRegression(random_state=42)
    logistic_model.fit(X_scaled, y_placed)

    # 2. Linear Regression (Target: Salary) - train only on placed students for better salary prediction
    print("Training Linear Regression...")
    X_placed = df[df['Placed'] == 1][['CGPA', 'LeetCode', 'Projects', 'Internships', 'Communication']]
    y_salary_placed = df[df['Placed'] == 1]['Salary']
    X_placed_scaled = scaler.transform(X_placed)
    
    linear_model = LinearRegression()
    linear_model.fit(X_placed_scaled, y_salary_placed)

    # 3. SVM Classifier (Target: Placed)
    print("Training SVM Classifier...")
    svm_model = SVC(probability=True, random_state=42)
    svm_model.fit(X_scaled, y_placed)

    # 4. K-Means Clustering
    # Clusters: 4
    # Cluster 0 -> Placement Ready
    # Cluster 1 -> Needs Improvement
    # Cluster 2 -> Beginner
    # Cluster 3 -> High Potential Candidate
    print("Training K-Means Clustering...")
    kmeans_model = KMeans(n_clusters=4, random_state=42, n_init=10)
    kmeans_model.fit(X_scaled)

    # Save models
    os.makedirs('trained_models', exist_ok=True)
    
    joblib.dump(scaler, 'trained_models/scaler.pkl')
    print("Saved scaler.pkl")
    
    joblib.dump(logistic_model, 'trained_models/logistic.pkl')
    print("Saved logistic.pkl")
    
    joblib.dump(linear_model, 'trained_models/linear.pkl')
    print("Saved linear.pkl")
    
    joblib.dump(svm_model, 'trained_models/svm.pkl')
    print("Saved svm.pkl")
    
    joblib.dump(kmeans_model, 'trained_models/kmeans.pkl')
    print("Saved kmeans.pkl")
    
    print("All models trained and saved successfully.")

if __name__ == "__main__":
    train_and_save_models()
