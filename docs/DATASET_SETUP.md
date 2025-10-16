# Dataset & Preprocessing Setup - Home IoT Guardian

## Summary

This document summarizes the dataset preparation and preprocessing pipeline setup for the Home IoT Guardian project.

## ✅ Completed Tasks

### 1. Mock Traffic Dataset
- **Location**: `data/mock_traffic.csv`
- **Size**: 1,001 rows (including header)
- **Columns**: `ts`, `orig_pkts`, `resp_pkts`, `orig_bytes`, `resp_bytes`, `label`
- **Label Distribution**:
  - Benign: 801 samples (80%)
  - Malicious: 200 samples (20%)
- **Characteristics**: 
  - Normal traffic: 8-13 packets, 950-1400 bytes
  - Anomalies: 150-200 packets, 25,000-35,000 bytes (spikes)

### 2. Preprocessing Module
- **Location**: `models/preprocess.py`
- **Functions**:

#### `load_csv(file_path)`
- Loads CSV files using pandas
- Returns DataFrame with shape information

#### `clean_data(df, numeric_cols, categorical_cols)`
- Drops missing values with `df.dropna()`
- Encodes categorical variables using `pd.get_dummies()`
- Normalizes numerical features with `StandardScaler`
- Returns cleaned DataFrame, scaler, and encoded column names

#### `create_sequences(data, seq_length=10)`
- Creates time-series sequences for LSTM models
- Default sequence length: 10 timesteps
- Returns numpy array with shape `(num_sequences, seq_length, num_features)`

#### `split_train_test(X, y, test_size=0.2)`
- Splits data into training and testing sets
- Default split: 80% training, 20% testing
- Returns `X_train, X_test, y_train, y_test`

#### `preprocess_pipeline(file_path, numeric_cols, categorical_cols, label_col, create_seq, seq_length)`
- Complete end-to-end preprocessing pipeline
- Combines all preprocessing steps
- Returns dictionary with processed data and metadata

### 3. Testing Results

#### Test 1: Basic Preprocessing (Without Sequences)
```
X_train shape: (800, 5)
X_test shape: (201, 5)
y_train shape: (800,)
y_test shape: (201,)
Features: ['ts', 'orig_pkts', 'resp_pkts', 'orig_bytes', 'resp_bytes']
```

#### Test 2: Preprocessing with LSTM Sequences (seq_length=10)
```
X_train shape: (792, 10, 5)
X_test shape: (199, 10, 5)
y_train shape: (792,)
y_test shape: (199,)

Label distribution in training set:
  - benign: 650 (81.2%)
  - malicious: 150 (18.8%)
```

### 4. IoT-23 Dataset Information
- **Documentation**: `data/README.md`
- **Official Source**: https://www.stratosphereips.org/datasets-iot23
- **Recommended Version**: Lighter CSV version without full pcaps (~8.8 GB)
- **Manual Download Required**: The dataset requires manual download from the official website

## Project Structure

```
home-iot-guard/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── Procfile                    # Deployment configuration
├── runtime.txt                 # Python version specification
├── .gitignore                  # Git ignore rules
├── DATASET_SETUP.md           # This file
│
├── data/
│   ├── mock_traffic.csv       # Mock IoT traffic dataset (1001 rows)
│   └── README.md              # IoT-23 dataset download instructions
│
├── models/
│   └── preprocess.py          # Data preprocessing module
│
├── templates/                  # HTML templates (empty)
├── static/                     # Static files (empty)
└── guardian_env/              # Virtual environment (ignored by git)
```

## Usage Examples

### Example 1: Basic Preprocessing
```python
from models.preprocess import preprocess_pipeline

result = preprocess_pipeline(
    file_path='data/mock_traffic.csv',
    numeric_cols=['orig_pkts', 'resp_pkts', 'orig_bytes', 'resp_bytes'],
    label_col='label',
    create_seq=False
)

print(f"X_train shape: {result['X_train'].shape}")
print(f"y_train shape: {result['y_train'].shape}")
```

### Example 2: LSTM Sequence Creation
```python
from models.preprocess import preprocess_pipeline

result = preprocess_pipeline(
    file_path='data/mock_traffic.csv',
    numeric_cols=['orig_pkts', 'resp_pkts', 'orig_bytes', 'resp_bytes'],
    label_col='label',
    create_seq=True,
    seq_length=10
)

print(f"X_train shape: {result['X_train'].shape}")  # (samples, 10, features)
```

### Example 3: With Categorical Encoding
```python
from models.preprocess import preprocess_pipeline

# For IoT-23 dataset with 'proto' and 'service' columns
result = preprocess_pipeline(
    file_path='data/iot23_labeled.csv',
    numeric_cols=['duration', 'orig_bytes', 'resp_bytes', 'orig_pkts', 'resp_pkts'],
    categorical_cols=['proto', 'service'],
    label_col='label',
    create_seq=False
)
```

## Running the Tests

To test the preprocessing functions:

```bash
# Activate virtual environment
.\guardian_env\Scripts\Activate.ps1

# Run the preprocessing tests
python models/preprocess.py
```

## Next Steps

1. **Download IoT-23 Dataset**: Follow instructions in `data/README.md`
2. **Train ML Models**: Use the preprocessed data to train anomaly detection models
3. **Integrate with Flask**: Create API endpoints to serve the trained models
4. **Deploy**: Use the Procfile for deployment to Heroku or similar platforms

## Notes

- All preprocessing functions include proper error handling
- The pipeline supports both supervised (with labels) and unsupervised (without labels) scenarios
- StandardScaler is fit on training data and can be saved for inference
- Sequence creation reduces the number of samples by `seq_length` due to windowing
- Mock data is suitable for development and testing before using the full IoT-23 dataset

## Dependencies

All required packages are installed in the virtual environment:
- pandas: Data manipulation
- numpy: Numerical operations
- scikit-learn: Preprocessing and splitting
- tensorflow/keras: Future ML model development
- flask: Web application framework

---

**Status**: ✅ All preprocessing setup completed and tested successfully!

