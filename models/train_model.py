"""
LSTM Autoencoder Training Module for Home IoT Guardian
Trains an anomaly detection model using LSTM autoencoder architecture
"""

import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, RepeatVector, TimeDistributed
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt

# Import preprocessing functions
from preprocess import preprocess_pipeline


def build_lstm_autoencoder(timesteps, features):
    """
    Build LSTM autoencoder for anomaly detection
    
    Args:
        timesteps (int): Number of timesteps in sequence
        features (int): Number of features per timestep
        
    Returns:
        tf.keras.Model: Compiled LSTM autoencoder model
    """
    print(f"\nBuilding LSTM Autoencoder...")
    print(f"Input shape: ({timesteps}, {features})")
    
    model = Sequential([
        # Encoder
        LSTM(50, activation='relu', input_shape=(timesteps, features), return_sequences=True),
        LSTM(20, activation='relu', return_sequences=False),
        
        # Decoder
        RepeatVector(timesteps),
        LSTM(20, activation='relu', return_sequences=True),
        LSTM(50, activation='relu', return_sequences=True),
        
        # Output layer
        TimeDistributed(Dense(features))
    ])
    
    # Compile model
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    
    print("\nModel Architecture:")
    model.summary()
    
    return model


def calculate_reconstruction_errors(model, X):
    """
    Calculate reconstruction errors for anomaly detection
    
    Args:
        model: Trained autoencoder model
        X: Input sequences
        
    Returns:
        np.array: Reconstruction errors (MSE) for each sample
    """
    # Reconstruct the input
    X_reconstructed = model.predict(X, verbose=0)
    
    # Calculate MSE for each sample
    mse = np.mean(np.square(X - X_reconstructed), axis=(1, 2))
    
    return mse


def determine_threshold(train_errors, method='mean_std', std_multiplier=3):
    """
    Determine anomaly threshold based on training errors
    
    Args:
        train_errors: Reconstruction errors from training data
        method: 'mean_std', 'percentile', or 'iqr'
        std_multiplier: Number of standard deviations above mean
        
    Returns:
        float: Threshold value
    """
    if method == 'mean_std':
        threshold = np.mean(train_errors) + std_multiplier * np.std(train_errors)
    elif method == 'percentile':
        threshold = np.percentile(train_errors, 95)
    elif method == 'iqr':
        q75, q25 = np.percentile(train_errors, [75, 25])
        iqr = q75 - q25
        threshold = q75 + 1.5 * iqr
    else:
        threshold = np.mean(train_errors) + std_multiplier * np.std(train_errors)
    
    return threshold


def detect_anomalies(model, X, threshold):
    """
    Detect anomalies based on reconstruction error threshold
    
    Args:
        model: Trained autoencoder model
        X: Input sequences
        threshold: Anomaly threshold
        
    Returns:
        tuple: (predictions, reconstruction_errors)
            predictions: 0 for normal, 1 for anomaly
    """
    errors = calculate_reconstruction_errors(model, X)
    predictions = (errors > threshold).astype(int)
    
    return predictions, errors


def evaluate_model(y_true, y_pred, errors, threshold):
    """
    Evaluate model performance with detailed metrics
    
    Args:
        y_true: True labels (0=benign, 1=malicious)
        y_pred: Predicted labels (0=normal, 1=anomaly)
        errors: Reconstruction errors
        threshold: Anomaly threshold used
        
    Returns:
        dict: Evaluation metrics
    """
    # Confusion matrix
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    
    # Calculate metrics
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0
    
    metrics = {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'detection_rate': recall,  # Same as recall for anomaly detection
        'false_positive_rate': false_positive_rate,
        'true_positives': tp,
        'false_positives': fp,
        'true_negatives': tn,
        'false_negatives': fn,
        'threshold': threshold
    }
    
    return metrics


def print_evaluation_report(metrics, dataset_name=""):
    """
    Print detailed evaluation report
    
    Args:
        metrics: Dictionary of evaluation metrics
        dataset_name: Name of the dataset (train/test)
    """
    print(f"\n{'='*60}")
    print(f"Evaluation Report - {dataset_name}")
    print(f"{'='*60}")
    print(f"Threshold: {metrics['threshold']:.6f}")
    print(f"\nConfusion Matrix:")
    print(f"  True Negatives:  {metrics['true_negatives']:>4d}")
    print(f"  False Positives: {metrics['false_positives']:>4d}")
    print(f"  True Positives:  {metrics['true_positives']:>4d}")
    print(f"  False Negatives: {metrics['false_negatives']:>4d}")
    print(f"\nPerformance Metrics:")
    print(f"  Accuracy:              {metrics['accuracy']*100:>6.2f}%")
    print(f"  Precision:             {metrics['precision']*100:>6.2f}%")
    print(f"  Recall (Detection):    {metrics['recall']*100:>6.2f}%")
    print(f"  F1-Score:              {metrics['f1_score']*100:>6.2f}%")
    print(f"  False Positive Rate:   {metrics['false_positive_rate']*100:>6.2f}%")
    print(f"{'='*60}")
    
    # Check requirements
    if metrics['detection_rate'] >= 0.85:
        print("[PASS] Detection rate >= 85% requirement MET")
    else:
        print(f"[FAIL] Detection rate < 85% requirement NOT MET")
    
    if metrics['false_positive_rate'] <= 0.10:
        print("[PASS] False positive rate <= 10% requirement MET")
    else:
        print(f"[FAIL] False positive rate > 10% requirement NOT MET")
    print(f"{'='*60}\n")


def plot_training_history(history, save_path='models/training_history.png'):
    """
    Plot training history
    
    Args:
        history: Keras training history object
        save_path: Path to save the plot
    """
    plt.figure(figsize=(12, 4))
    
    # Loss plot
    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Model Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss (MSE)')
    plt.legend()
    plt.grid(True)
    
    # MAE plot
    plt.subplot(1, 2, 2)
    plt.plot(history.history['mae'], label='Training MAE')
    plt.plot(history.history['val_mae'], label='Validation MAE')
    plt.title('Model MAE')
    plt.xlabel('Epoch')
    plt.ylabel('MAE')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(save_path)
    print(f"\nTraining history plot saved to: {save_path}")
    plt.close()


def train_lstm_autoencoder(data_path='data/mock_traffic.csv', 
                           seq_length=10,
                           epochs=50,
                           batch_size=32,
                           model_save_path='models/lstm_model.keras'):
    """
    Complete training pipeline for LSTM autoencoder
    
    Args:
        data_path: Path to data file
        seq_length: Sequence length for LSTM
        epochs: Number of training epochs
        batch_size: Training batch size
        model_save_path: Path to save trained model
        
    Returns:
        tuple: (model, threshold, metrics)
    """
    print("\n" + "="*60)
    print("LSTM Autoencoder Training Pipeline")
    print("="*60)
    
    # Step 1: Load and preprocess data
    print("\n[Step 1] Loading and preprocessing data...")
    
    # Get project root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    full_data_path = os.path.join(project_root, data_path)
    
    # Load data without timestamp column (it causes numerical issues)
    df = pd.read_csv(full_data_path)
    df = df.drop('ts', axis=1)  # Remove timestamp column
    temp_path = full_data_path.replace('.csv', '_temp.csv')
    df.to_csv(temp_path, index=False)
    
    result = preprocess_pipeline(
        file_path=temp_path,
        numeric_cols=['orig_pkts', 'resp_pkts', 'orig_bytes', 'resp_bytes'],
        label_col='label',
        create_seq=True,
        seq_length=seq_length
    )
    
    # Clean up temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)
    
    X_train = result['X_train']
    X_test = result['X_test']
    y_train = result['y_train']
    y_test = result['y_test']
    
    print(f"\nData shapes:")
    print(f"  X_train: {X_train.shape}")
    print(f"  X_test: {X_test.shape}")
    print(f"  y_train: {y_train.shape}")
    print(f"  y_test: {y_test.shape}")
    
    # Get dimensions
    timesteps = X_train.shape[1]
    features = X_train.shape[2]
    
    # Step 2: Build model
    print("\n[Step 2] Building LSTM autoencoder model...")
    model = build_lstm_autoencoder(timesteps, features)
    
    # Step 3: Train model
    print("\n[Step 3] Training model...")
    print(f"Epochs: {epochs}, Batch size: {batch_size}")
    
    # Callbacks
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True, verbose=1),
        ModelCheckpoint(model_save_path, monitor='val_loss', save_best_only=True, verbose=1)
    ]
    
    # Train on all data (autoencoder learns to reconstruct)
    history = model.fit(
        X_train, X_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(X_test, X_test),
        callbacks=callbacks,
        verbose=1
    )
    
    print(f"\n[SAVED] Model saved to: {model_save_path}")
    
    # Plot training history
    plot_path = os.path.join(project_root, 'models', 'training_history.png')
    plot_training_history(history, plot_path)
    
    # Step 4: Calculate threshold
    print("\n[Step 4] Calculating anomaly threshold...")
    
    # Calculate reconstruction errors on training data
    train_errors = calculate_reconstruction_errors(model, X_train)
    
    # Determine threshold (mean + 3*std)
    threshold = determine_threshold(train_errors, method='mean_std', std_multiplier=3)
    
    print(f"Training error statistics:")
    print(f"  Mean: {np.mean(train_errors):.6f}")
    print(f"  Std:  {np.std(train_errors):.6f}")
    print(f"  Threshold (mean + 3*std): {threshold:.6f}")
    
    # Step 5: Evaluate on training set
    print("\n[Step 5] Evaluating on training set...")
    train_pred, train_errors_final = detect_anomalies(model, X_train, threshold)
    train_metrics = evaluate_model(y_train, train_pred, train_errors_final, threshold)
    print_evaluation_report(train_metrics, "Training Set")
    
    # Step 6: Evaluate on test set
    print("\n[Step 6] Evaluating on test set...")
    test_pred, test_errors = detect_anomalies(model, X_test, threshold)
    test_metrics = evaluate_model(y_test, test_pred, test_errors, threshold)
    print_evaluation_report(test_metrics, "Test Set")
    
    # Save threshold
    threshold_path = os.path.join(project_root, 'models', 'threshold.txt')
    with open(threshold_path, 'w') as f:
        f.write(f"{threshold}\n")
    print(f"[SAVED] Threshold saved to: {threshold_path}")
    
    return model, threshold, test_metrics


def test_model_loading_and_prediction(model_path='models/lstm_model.keras',
                                      threshold_path='models/threshold.txt',
                                      data_path='data/mock_traffic.csv'):
    """
    Test loading the trained model and making predictions
    
    Args:
        model_path: Path to saved model
        threshold_path: Path to saved threshold
        data_path: Path to test data
    """
    print("\n" + "="*60)
    print("Testing Model Loading and Prediction")
    print("="*60)
    
    # Get project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # Load model
    full_model_path = os.path.join(project_root, model_path)
    print(f"\n[1] Loading model from: {full_model_path}")
    model = load_model(full_model_path)
    print("[LOADED] Model loaded successfully!")
    
    # Load threshold
    full_threshold_path = os.path.join(project_root, threshold_path)
    print(f"\n[2] Loading threshold from: {full_threshold_path}")
    with open(full_threshold_path, 'r') as f:
        threshold = float(f.read().strip())
    print(f"[LOADED] Threshold loaded: {threshold:.6f}")
    
    # Load sample data
    full_data_path = os.path.join(project_root, data_path)
    print(f"\n[3] Loading sample data from: {full_data_path}")
    
    # Load data without timestamp column
    df_test = pd.read_csv(full_data_path)
    df_test = df_test.drop('ts', axis=1)
    temp_test_path = full_data_path.replace('.csv', '_temp_test.csv')
    df_test.to_csv(temp_test_path, index=False)
    
    result = preprocess_pipeline(
        file_path=temp_test_path,
        numeric_cols=['orig_pkts', 'resp_pkts', 'orig_bytes', 'resp_bytes'],
        label_col='label',
        create_seq=True,
        seq_length=10
    )
    
    # Clean up temp file
    if os.path.exists(temp_test_path):
        os.remove(temp_test_path)
    
    X_test = result['X_test']
    y_test = result['y_test']
    
    # Make predictions on first 10 samples
    print(f"\n[4] Making predictions on {min(10, len(X_test))} samples...")
    sample_X = X_test[:10]
    sample_y = y_test[:10]
    
    # Predict
    predictions, errors = detect_anomalies(model, sample_X, threshold)
    
    print("\nPrediction Results:")
    print(f"{'Sample':<8} {'True Label':<12} {'Predicted':<12} {'Error':<12} {'Status':<10}")
    print("-" * 60)
    
    for i in range(len(sample_X)):
        true_label = 'Malicious' if sample_y[i] == 1 else 'Benign'
        pred_label = 'Anomaly' if predictions[i] == 1 else 'Normal'
        status = '[CORRECT]' if sample_y[i] == predictions[i] else '[WRONG]'
        print(f"{i+1:<8} {true_label:<12} {pred_label:<12} {errors[i]:<12.6f} {status:<10}")
    
    print("\n" + "="*60)
    print("[SUCCESS] Model loading and prediction test completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Train the model
    print("\n>>> Starting LSTM Autoencoder Training...")
    
    try:
        model, threshold, metrics = train_lstm_autoencoder(
            data_path='data/mock_traffic.csv',
            seq_length=10,
            epochs=50,
            batch_size=32,
            model_save_path='models/lstm_model.keras'
        )
        
        print("\n>>> Training completed successfully!")
        
        # Test model loading and prediction
        print("\n" + "="*60)
        print("Testing model loading and prediction...")
        print("="*60)
        
        test_model_loading_and_prediction(
            model_path='models/lstm_model.keras',
            threshold_path='models/threshold.txt',
            data_path='data/mock_traffic.csv'
        )
        
        print("\n>>> All tasks completed successfully!")
        print("\nModel files created:")
        print("  - models/lstm_model.keras (trained model)")
        print("  - models/threshold.txt (anomaly threshold)")
        print("  - models/training_history.png (training plots)")
        
    except Exception as e:
        print(f"\n>>> Error during training: {str(e)}")
        import traceback
        traceback.print_exc()

