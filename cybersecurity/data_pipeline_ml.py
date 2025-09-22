import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import re
import joblib

def load_data(filepath):
    """Loads a CSV file into a pandas DataFrame."""
    return pd.read_csv(filepath)

def preprocess_logs(df):
    """
    Cleans and preprocesses log data.
    """
    df['log_message'] = df['log_message'].astype(str)
    df['user'] = df['log_message'].apply(lambda x: re.search(r'user=(\w+)', x).group(1) if re.search(r'user=(\w+)', x) else 'unknown')
    df['source_ip'] = df['log_message'].apply(lambda x: re.search(r'src=(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', x).group(1) if re.search(r'src=(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', x) else 'unknown')
    
    # --- FIX STARTS HERE ---
    # Isolate categorical columns for one-hot encoding
    categorical_df = pd.get_dummies(df[['user', 'source_ip']], drop_first=True, prefix=['user', 'source_ip'])
    
    # Drop the original categorical and log message columns
    df = df.drop(columns=['user', 'source_ip', 'log_message', 'timestamp'])
    
    # Concatenate the processed numerical data with the one-hot encoded categorical data
    df = pd.concat([df, categorical_df], axis=1)
    # --- FIX ENDS HERE ---
    
    return df

def train_threat_model(df):
    """
    Trains a Random Forest model to classify threats.
    """
    print("Training ML model to detect threats...")
    
    # Split data into training and testing sets
    X = df.drop(columns=['threat_type'])
    y = df['threat_type']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize and train the Random Forest model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate model
    y_pred = model.predict(X_test)
    print("Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    # Save the model
    joblib.dump(model, 'threat_model.pkl')
    print("Threat model trained and saved as 'threat_model.pkl'.")
    return model

if __name__ == "__main__":
    # Sample data
    data = {
        'timestamp': pd.to_datetime(['2025-09-22 10:00:00', '2025-09-22 10:00:05', '2025-09-22 10:00:10', '2025-09-22 10:00:15']),
        'log_message': [
            'INFO: Login successful for user=admin from src=192.168.1.10',
            'ALERT: Failed login attempt for user=root from src=10.0.0.5',
            'INFO: Process started by user=sysuser',
            'ATTACK: Multiple failed logins for user=admin from src=10.0.0.5'
        ],
        'threat_type': ['benign', 'brute_force', 'benign', 'brute_force']
    }
    sample_df = pd.DataFrame(data)
    processed_df = preprocess_logs(sample_df)
    train_threat_model(processed_df)

