"""
Data preprocessing module for Home IoT Guardian
Handles loading, cleaning, and preparing IoT traffic data for ML models
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split


def load_csv(file_path):
    """
    Load CSV file with pandas
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pd.DataFrame: Loaded dataframe
    """
    print(f"Loading data from {file_path}...")
    df = pd.read_csv(file_path)
    print(f"Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def clean_data(df, numeric_cols=None, categorical_cols=None):
    """
    Clean data: drop NaN values and encode categorical variables
    
    Args:
        df (pd.DataFrame): Input dataframe
        numeric_cols (list): List of numeric columns to normalize
        categorical_cols (list): List of categorical columns to encode
        
    Returns:
        tuple: (cleaned_df, scaler, encoded_columns)
    """
    print(f"Cleaning data... Initial shape: {df.shape}")
    
    # Drop rows with missing values
    df_clean = df.dropna()
    print(f"After dropping NaN: {df_clean.shape}")
    
    # Encode categorical variables with pd.get_dummies if specified
    encoded_columns = []
    if categorical_cols:
        for col in categorical_cols:
            if col in df_clean.columns:
                print(f"Encoding categorical column: {col}")
                dummies = pd.get_dummies(df_clean[col], prefix=col, drop_first=False)
                encoded_columns.extend(dummies.columns.tolist())
                df_clean = pd.concat([df_clean.drop(col, axis=1), dummies], axis=1)
    
    # Normalize numerical features with StandardScaler if specified
    scaler = None
    if numeric_cols:
        numeric_cols_present = [col for col in numeric_cols if col in df_clean.columns]
        if numeric_cols_present:
            print(f"Normalizing numerical columns: {numeric_cols_present}")
            scaler = StandardScaler()
            df_clean[numeric_cols_present] = scaler.fit_transform(df_clean[numeric_cols_present])
    
    print(f"Cleaning complete. Final shape: {df_clean.shape}")
    return df_clean, scaler, encoded_columns


def create_sequences(data, seq_length=10):
    """
    Create time-series sequences for LSTM models
    
    Args:
        data (np.array or pd.DataFrame): Input data
        seq_length (int): Length of each sequence (default: 10)
        
    Returns:
        np.array: Array of sequences with shape (num_sequences, seq_length, num_features)
    """
    # Convert to numpy array if it's a DataFrame
    if isinstance(data, pd.DataFrame):
        data = data.values
    
    if len(data) <= seq_length:
        print(f"Warning: Data length ({len(data)}) is less than or equal to sequence length ({seq_length})")
        return np.array([])
    
    sequences = []
    for i in range(len(data) - seq_length):
        seq = data[i:i + seq_length]
        sequences.append(seq)
    
    sequences = np.array(sequences)
    print(f"Created {sequences.shape[0]} sequences of length {seq_length}")
    print(f"Sequence shape: {sequences.shape}")
    
    return sequences


def split_train_test(X, y=None, test_size=0.2, random_state=42):
    """
    Split data into training and testing sets (80/20 by default)
    
    Args:
        X (np.array or pd.DataFrame): Features
        y (np.array or pd.Series): Labels (optional)
        test_size (float): Proportion of test set (default: 0.2)
        random_state (int): Random seed for reproducibility
        
    Returns:
        tuple: (X_train, X_test, y_train, y_test) or (X_train, X_test) if y is None
    """
    if y is not None:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        print(f"Train set: {X_train.shape[0]} samples")
        print(f"Test set: {X_test.shape[0]} samples")
        return X_train, X_test, y_train, y_test
    else:
        X_train, X_test = train_test_split(
            X, test_size=test_size, random_state=random_state
        )
        print(f"Train set: {X_train.shape[0]} samples")
        print(f"Test set: {X_test.shape[0]} samples")
        return X_train, X_test


def preprocess_pipeline(file_path, numeric_cols, categorical_cols=None, 
                        label_col=None, create_seq=False, seq_length=10):
    """
    Complete preprocessing pipeline
    
    Args:
        file_path (str): Path to CSV file
        numeric_cols (list): Numeric columns to normalize
        categorical_cols (list): Categorical columns to encode
        label_col (str): Name of label column (if any)
        create_seq (bool): Whether to create sequences for LSTM
        seq_length (int): Length of sequences (if create_seq=True)
        
    Returns:
        dict: Dictionary containing processed data and metadata
    """
    # Load data
    df = load_csv(file_path)
    
    # Separate labels if specified
    y = None
    if label_col and label_col in df.columns:
        y = df[label_col].copy()
        # Encode labels if they're categorical
        if y.dtype == 'object':
            y = y.map({'benign': 0, 'malicious': 1})
        df = df.drop(label_col, axis=1)
    
    # Clean and encode data
    df_clean, scaler, encoded_cols = clean_data(df, numeric_cols, categorical_cols)
    
    # Create sequences if requested
    if create_seq:
        X = create_sequences(df_clean, seq_length)
        if y is not None and len(X) > 0:
            # Adjust labels to match sequence count
            y = y[seq_length:].values
    else:
        X = df_clean.values
        if y is not None:
            y = y.values
    
    # Split train/test
    if y is not None:
        X_train, X_test, y_train, y_test = split_train_test(X, y)
        
        return {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test,
            'scaler': scaler,
            'encoded_columns': encoded_cols,
            'feature_names': df_clean.columns.tolist()
        }
    else:
        X_train, X_test = split_train_test(X)
        
        return {
            'X_train': X_train,
            'X_test': X_test,
            'scaler': scaler,
            'encoded_columns': encoded_cols,
            'feature_names': df_clean.columns.tolist()
        }


if __name__ == "__main__":
    # Test the preprocessing functions
    import os
    print("="*60)
    print("Testing Preprocessing Functions")
    print("="*60)
    
    # Test with mock_traffic.csv
    # Get the project root directory (parent of models/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    test_file = os.path.join(project_root, 'data', 'mock_traffic.csv')
    
    print("\n--- Test 1: Basic preprocessing without sequences ---")
    result = preprocess_pipeline(
        file_path=test_file,
        numeric_cols=['orig_pkts', 'resp_pkts', 'orig_bytes', 'resp_bytes'],
        label_col='label',
        create_seq=False
    )
    
    print(f"\nResults:")
    print(f"X_train shape: {result['X_train'].shape}")
    print(f"X_test shape: {result['X_test'].shape}")
    print(f"y_train shape: {result['y_train'].shape}")
    print(f"y_test shape: {result['y_test'].shape}")
    print(f"Feature names: {result['feature_names']}")
    
    print("\n--- Test 2: Preprocessing with LSTM sequences ---")
    result_seq = preprocess_pipeline(
        file_path=test_file,
        numeric_cols=['orig_pkts', 'resp_pkts', 'orig_bytes', 'resp_bytes'],
        label_col='label',
        create_seq=True,
        seq_length=10
    )
    
    print(f"\nResults with sequences:")
    print(f"X_train shape: {result_seq['X_train'].shape}")
    print(f"X_test shape: {result_seq['X_test'].shape}")
    print(f"y_train shape: {result_seq['y_train'].shape}")
    print(f"y_test shape: {result_seq['y_test'].shape}")
    
    # Check label distribution
    print(f"\nLabel distribution in training set:")
    unique, counts = np.unique(result['y_train'], return_counts=True)
    for label, count in zip(unique, counts):
        label_name = 'benign' if label == 0 else 'malicious'
        percentage = (count / len(result['y_train'])) * 100
        print(f"  {label_name}: {count} ({percentage:.1f}%)")
    
    print("\n" + "="*60)
    print("All tests completed successfully!")
    print("="*60)

