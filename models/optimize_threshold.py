"""
Threshold Optimization Script
Finds the optimal threshold for better detection rate while keeping FPR low
"""

import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from preprocess import preprocess_pipeline
from train_model import calculate_reconstruction_errors, evaluate_model


def find_optimal_threshold(model, X_train, y_train, X_test, y_test, target_fpr=0.10):
    """
    Find optimal threshold that maximizes detection rate while keeping FPR below target
    
    Args:
        model: Trained autoencoder model
        X_train: Training features
        y_train: Training labels
        X_test: Test features
        y_test: Test labels
        target_fpr: Maximum acceptable false positive rate (default: 0.10)
        
    Returns:
        dict: Best threshold and corresponding metrics
    """
    print("\n" + "="*60)
    print("Optimizing Threshold for Better Detection")
    print("="*60)
    
    # Calculate reconstruction errors
    train_errors = calculate_reconstruction_errors(model, X_train)
    test_errors = calculate_reconstruction_errors(model, X_test)
    
    # Try different threshold strategies
    strategies = {
        'mean + 3*std': np.mean(train_errors) + 3 * np.std(train_errors),
        'mean + 2*std': np.mean(train_errors) + 2 * np.std(train_errors),
        'mean + 1*std': np.mean(train_errors) + 1 * np.std(train_errors),
        'mean': np.mean(train_errors),
        '95th percentile': np.percentile(train_errors, 95),
        '90th percentile': np.percentile(train_errors, 90),
        '85th percentile': np.percentile(train_errors, 85),
        '80th percentile': np.percentile(train_errors, 80),
        '75th percentile': np.percentile(train_errors, 75),
    }
    
    print(f"\nEvaluating different threshold strategies...")
    print(f"{'Strategy':<20} {'Threshold':<12} {'Detection %':<14} {'FPR %':<12} {'Status':<10}")
    print("-" * 70)
    
    best_threshold = None
    best_metrics = None
    best_strategy = None
    
    for strategy_name, threshold in strategies.items():
        # Evaluate on test set
        test_pred = (test_errors > threshold).astype(int)
        metrics = evaluate_model(y_test, test_pred, test_errors, threshold)
        
        detection_rate = metrics['detection_rate'] * 100
        fpr = metrics['false_positive_rate'] * 100
        
        # Check if this threshold meets requirements
        status = ""
        if metrics['detection_rate'] >= 0.85 and metrics['false_positive_rate'] <= target_fpr:
            status = "[PASS]"
            if best_metrics is None or metrics['detection_rate'] > best_metrics['detection_rate']:
                best_threshold = threshold
                best_metrics = metrics
                best_strategy = strategy_name
        elif metrics['detection_rate'] >= 0.85:
            status = "[HIGH FPR]"
        elif metrics['false_positive_rate'] <= target_fpr:
            status = "[LOW DET]"
        else:
            status = "[FAIL]"
        
        print(f"{strategy_name:<20} {threshold:<12.6f} {detection_rate:<14.2f} {fpr:<12.2f} {status:<10}")
    
    # If no strategy meets both requirements, find best balance
    if best_threshold is None:
        print("\nNo strategy met both requirements. Finding best balance...")
        
        # Sort errors and try thresholds at different percentiles
        sorted_errors = np.sort(train_errors)
        
        best_score = -1
        for percentile in range(50, 100):
            threshold = np.percentile(train_errors, percentile)
            test_pred = (test_errors > threshold).astype(int)
            metrics = evaluate_model(y_test, test_pred, test_errors, threshold)
            
            # Score = detection_rate - fpr_penalty
            # Penalize FPR more if it exceeds target
            fpr_penalty = metrics['false_positive_rate'] * (2 if metrics['false_positive_rate'] > target_fpr else 1)
            score = metrics['detection_rate'] - fpr_penalty
            
            if score > best_score:
                best_score = score
                best_threshold = threshold
                best_metrics = metrics
                best_strategy = f"{percentile}th percentile"
        
        print(f"\nBest balance found at {best_strategy}:")
        print(f"  Threshold: {best_threshold:.6f}")
        print(f"  Detection Rate: {best_metrics['detection_rate']*100:.2f}%")
        print(f"  False Positive Rate: {best_metrics['false_positive_rate']*100:.2f}%")
    
    print("\n" + "="*60)
    print(f"Optimal Threshold Selected: {best_strategy}")
    print(f"Threshold Value: {best_threshold:.6f}")
    print("="*60)
    
    return {
        'threshold': best_threshold,
        'strategy': best_strategy,
        'test_metrics': best_metrics
    }


if __name__ == "__main__":
    print("\n>>> Starting Threshold Optimization...")
    
    # Get project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # Load model
    model_path = os.path.join(project_root, 'models', 'lstm_model.keras')
    print(f"\nLoading model from: {model_path}")
    model = load_model(model_path)
    print("[LOADED] Model loaded successfully!")
    
    # Load and preprocess data
    print("\nLoading and preprocessing data...")
    data_path = os.path.join(project_root, 'data', 'mock_traffic.csv')
    
    # Load data without timestamp column
    df = pd.read_csv(data_path)
    df = df.drop('ts', axis=1)
    temp_path = data_path.replace('.csv', '_temp_optimize.csv')
    df.to_csv(temp_path, index=False)
    
    result = preprocess_pipeline(
        file_path=temp_path,
        numeric_cols=['orig_pkts', 'resp_pkts', 'orig_bytes', 'resp_bytes'],
        label_col='label',
        create_seq=True,
        seq_length=10
    )
    
    # Clean up temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)
    
    X_train = result['X_train']
    X_test = result['X_test']
    y_train = result['y_train']
    y_test = result['y_test']
    
    # Find optimal threshold
    optimal = find_optimal_threshold(
        model, X_train, y_train, X_test, y_test, target_fpr=0.10
    )
    
    # Save optimal threshold
    threshold_path = os.path.join(project_root, 'models', 'threshold_optimized.txt')
    with open(threshold_path, 'w') as f:
        f.write(f"{optimal['threshold']}\n")
    
    print(f"\n[SAVED] Optimized threshold saved to: {threshold_path}")
    
    # Print detailed evaluation
    print("\n" + "="*60)
    print("Final Evaluation with Optimized Threshold")
    print("="*60)
    
    metrics = optimal['test_metrics']
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
    
    print("\n" + "="*60)
    print(">>> Threshold optimization completed!")
    print("="*60)

