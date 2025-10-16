"""
Home IoT Guardian - Flask Application
Main application with routes for anomaly detection and dashboard
"""

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
import os
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
import tempfile
import json

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///guardian.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASS')
app.config['MAIL_DEFAULT_SENDER'] = 'guardian@app.com'

# Initialize database and mail
db = SQLAlchemy(app)
mail = Mail(app)


# Database Models
class ScanResult(db.Model):
    """Model for storing scan results in database"""
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    anomalies_count = db.Column(db.Integer)
    details = db.Column(db.Text)  # JSON string with anomaly details
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'anomalies_count': self.anomalies_count,
            'details': json.loads(self.details) if self.details else []
        }


# Global variables for model and threshold
MODEL = None
THRESHOLD = None
SCALER = None


def load_ml_model():
    """Load the trained LSTM model and threshold"""
    global MODEL, THRESHOLD
    
    if MODEL is None:
        model_path = os.path.join('models', 'lstm_model.keras')
        if os.path.exists(model_path):
            MODEL = load_model(model_path)
            print(f"[LOADED] Model loaded from {model_path}")
        else:
            print(f"[WARNING] Model not found at {model_path}")
    
    if THRESHOLD is None:
        # Try optimized threshold first, fall back to regular threshold
        threshold_path = os.path.join('models', 'threshold_optimized.txt')
        if not os.path.exists(threshold_path):
            threshold_path = os.path.join('models', 'threshold.txt')
        
        if os.path.exists(threshold_path):
            with open(threshold_path, 'r') as f:
                THRESHOLD = float(f.read().strip())
            print(f"[LOADED] Threshold loaded: {THRESHOLD:.6f}")
        else:
            THRESHOLD = 0.12  # Default threshold
            print(f"[WARNING] Threshold file not found, using default: {THRESHOLD}")
    
    return MODEL, THRESHOLD


def preprocess_for_detection(file_path):
    """
    Preprocess uploaded CSV file for anomaly detection
    
    Args:
        file_path: Path to uploaded CSV file
        
    Returns:
        tuple: (preprocessed_sequences, original_df, feature_names)
    """
    # Read CSV
    df = pd.read_csv(file_path)
    
    # Store original data for reporting
    original_df = df.copy()
    
    # Remove timestamp if present
    if 'ts' in df.columns:
        df = df.drop('ts', axis=1)
    
    # Remove label if present (for real-world uploads)
    has_labels = 'label' in df.columns
    if has_labels:
        labels = df['label'].copy()
        df = df.drop('label', axis=1)
    else:
        labels = None
    
    # Expected features
    expected_features = ['orig_pkts', 'resp_pkts', 'orig_bytes', 'resp_bytes']
    
    # Check if all required features are present
    missing_features = [f for f in expected_features if f not in df.columns]
    if missing_features:
        raise ValueError(f"Missing required features: {missing_features}")
    
    # Select and order features
    df = df[expected_features]
    
    # Normalize features (simple standardization)
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    df_normalized = pd.DataFrame(
        scaler.fit_transform(df),
        columns=df.columns
    )
    
    # Create sequences (length 10)
    seq_length = 10
    if len(df_normalized) <= seq_length:
        raise ValueError(f"File must have more than {seq_length} rows for sequence analysis")
    
    sequences = []
    for i in range(len(df_normalized) - seq_length):
        seq = df_normalized.iloc[i:i+seq_length].values
        sequences.append(seq)
    
    sequences = np.array(sequences)
    
    return sequences, original_df, expected_features


def send_email_alert(anomalies_count, details, total_samples):
    """
    Send email alert when anomalies are detected
    
    Args:
        anomalies_count: Number of anomalies detected
        details: List of anomaly details
        total_samples: Total number of samples analyzed
    """
    try:
        # Check if email is configured
        if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
            print("[WARNING] Email not configured. Skipping email alert.")
            print(f"[ALERT] {anomalies_count} anomalies detected in {total_samples} samples!")
            return
        
        # Get recipient from environment or use default
        recipient = os.environ.get('ALERT_EMAIL', 'user@email.com')
        
        # Create message
        msg = Message(
            subject='Alert: Anomalies Detected!',
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[recipient]
        )
        
        # Format email body
        msg.body = f"""
Home IoT Guardian - Anomaly Detection Alert

SUMMARY:
--------
Total Samples Analyzed: {total_samples}
Anomalies Detected: {anomalies_count}
Anomaly Rate: {(anomalies_count/total_samples*100):.2f}%

TOP ANOMALIES:
--------------
"""
        
        # Add details for first 5 anomalies
        for i, detail in enumerate(details[:5], 1):
            msg.body += f"""
Anomaly #{i}:
  - Sequence ID: {detail['sequence_id']}
  - Error Score: {detail['error']:.6f}
  - Severity: {detail['severity']}
  - Rows: {detail['rows']}
"""
        
        msg.body += f"""
ACTION REQUIRED:
----------------
Please review the detected anomalies in the Home IoT Guardian dashboard.

Dashboard: http://localhost:5000

---
This is an automated alert from Home IoT Guardian.
"""
        
        # Send email
        mail.send(msg)
        print(f"[EMAIL] Alert sent to {recipient}")
        
    except Exception as e:
        # Handle SMTP errors gracefully
        print(f"[ERROR] Failed to send email: {str(e)}")
        print(f"[ALERT] {anomalies_count} anomalies detected in {total_samples} samples!")
        # Continue execution even if email fails


def detect_anomalies(file_path):
    """
    Detect anomalies in uploaded CSV file
    
    Args:
        file_path: Path to uploaded CSV file
        
    Returns:
        dict: {'anomalies_count': int, 'details': list, 'total_samples': int}
    """
    try:
        # Load model and threshold
        model, threshold = load_ml_model()
        
        if model is None:
            return {
                'error': 'Model not loaded. Please train the model first.',
                'anomalies_count': 0,
                'details': [],
                'total_samples': 0
            }
        
        # Preprocess data
        sequences, original_df, features = preprocess_for_detection(file_path)
        
        # Make predictions
        reconstructed = model.predict(sequences, verbose=0)
        
        # Calculate reconstruction errors
        errors = np.mean(np.square(sequences - reconstructed), axis=(1, 2))
        
        # Detect anomalies
        anomaly_flags = errors > threshold
        anomaly_indices = np.where(anomaly_flags)[0]
        
        # Prepare detailed results
        details = []
        for idx in anomaly_indices[:100]:  # Limit to first 100 anomalies
            # Get the sequence index (accounting for sequence window)
            row_start = idx
            row_end = idx + 10
            
            detail = {
                'sequence_id': int(idx),
                'rows': f"{row_start}-{row_end}",
                'error': float(errors[idx]),
                'threshold': float(threshold),
                'severity': 'High' if errors[idx] > threshold * 1.5 else 'Medium'
            }
            
            # Add sample data from the sequence
            if row_start < len(original_df):
                sample_row = original_df.iloc[row_start].to_dict()
                detail['sample_data'] = {k: str(v) for k, v in sample_row.items()}
            
            details.append(detail)
        
        result = {
            'anomalies_count': int(len(anomaly_indices)),
            'details': details,
            'total_samples': int(len(sequences)),
            'threshold': float(threshold),
            'percentage': float(len(anomaly_indices) / len(sequences) * 100) if len(sequences) > 0 else 0
        }
        
        # Send email alert if anomalies detected
        if len(anomaly_indices) > 0:
            send_email_alert(
                anomalies_count=int(len(anomaly_indices)),
                details=details,
                total_samples=int(len(sequences))
            )
        
        return result
        
    except Exception as e:
        return {
            'error': str(e),
            'anomalies_count': 0,
            'details': [],
            'total_samples': 0
        }


# Routes
@app.route('/')
def index():
    """Render main dashboard page"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload and anomaly detection
    
    Expects:
        - 'file' in request.files (CSV file)
        
    Returns:
        JSON response with anomaly detection results
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Only CSV files are allowed'}), 400
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Detect anomalies
            result = detect_anomalies(temp_path)
            
            # Check for errors in detection
            if 'error' in result:
                return jsonify(result), 500
            
            # Store result in database
            scan_result = ScanResult(
                anomalies_count=result['anomalies_count'],
                details=json.dumps(result['details'])
            )
            db.session.add(scan_result)
            db.session.commit()
            
            # Add scan ID to result
            result['scan_id'] = scan_result.id
            
            return jsonify(result), 200
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/history', methods=['GET'])
def get_history():
    """
    Get scan history from database
    
    Returns:
        JSON array of scan results
    """
    try:
        # Get all scan results, ordered by most recent first
        results = ScanResult.query.order_by(ScanResult.timestamp.desc()).limit(50).all()
        
        # Convert to dictionary format
        history = [result.to_dict() for result in results]
        
        return jsonify(history), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch history: {str(e)}'}), 500


@app.route('/scan/<int:scan_id>', methods=['GET'])
def get_scan_details(scan_id):
    """
    Get detailed results for a specific scan
    
    Args:
        scan_id: ID of the scan result
        
    Returns:
        JSON with detailed scan information
    """
    try:
        result = ScanResult.query.get(scan_id)
        
        if result is None:
            return jsonify({'error': 'Scan not found'}), 404
        
        return jsonify(result.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch scan details: {str(e)}'}), 500


@app.route('/status', methods=['GET'])
def get_status():
    """
    Get system status (model loaded, database connection, etc.)
    
    Returns:
        JSON with system status
    """
    try:
        # Check model status
        model, threshold = load_ml_model()
        model_loaded = model is not None
        
        # Check database
        db_connected = True
        try:
            db.session.execute('SELECT 1')
        except:
            db_connected = False
        
        # Get scan count
        scan_count = ScanResult.query.count()
        
        return jsonify({
            'status': 'operational',
            'model_loaded': model_loaded,
            'threshold': float(threshold) if threshold else None,
            'database_connected': db_connected,
            'total_scans': scan_count
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
        print("[INFO] Database tables created")
    
    # Load model at startup
    load_ml_model()
    
    # Run the application
    print("\n" + "="*60)
    print("Home IoT Guardian - Starting Server")
    print("="*60)
    print(f"Server running at: http://127.0.0.1:5000")
    print("Press CTRL+C to quit")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
