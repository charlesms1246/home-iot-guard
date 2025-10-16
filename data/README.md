# IoT-23 Dataset Information

## About the Dataset

The IoT-23 dataset is a collection of network traffic from IoT devices, including both benign and malicious traffic. It was created by Stratosphere Lab and is available at: https://www.stratosphereips.org/datasets-iot23

## Downloading the Dataset

### Option 1: Lighter CSV Version (Recommended)

Visit the official website and download the labeled flows without pcap files:
- **URL**: https://www.stratosphereips.org/datasets-iot23
- **Size**: Approximately 8.8 GB (compressed)
- **Format**: Tab-separated labeled connection logs

### Option 2: Individual Scenarios

You can download individual IoT malware capture scenarios from:
- https://mcfp.felk.cvut.cz/publicDatasets/IoT-23-Dataset/

Each scenario contains:
- `conn.log.labeled` - Network connection logs with labels
- Approximately 500K-1M flows per scenario

### Manual Download Steps

1. Visit https://www.stratosphereips.org/datasets-iot23
2. Download the "Small capture, only the conn.log labeled files in Zeek" version
3. Extract the downloaded archive
4. Place the `.conn.log.labeled` files in this directory
5. Convert to CSV format if needed (see conversion script below)

## Dataset Structure

The IoT-23 dataset connection logs contain the following fields:
- `ts` - Timestamp
- `uid` - Connection unique ID
- `id.orig_h` - Originator IP address
- `id.orig_p` - Originator port
- `id.resp_h` - Responder IP address
- `id.resp_p` - Responder port
- `proto` - Protocol (tcp, udp, icmp)
- `service` - Service type (http, dns, ssl, etc.)
- `duration` - Connection duration
- `orig_bytes` - Bytes from originator
- `resp_bytes` - Bytes from responder
- `conn_state` - Connection state
- `orig_pkts` - Packets from originator
- `resp_pkts` - Packets from responder
- `label` - Traffic label (benign or malicious)
- `detailed-label` - Detailed label with attack type

## Mock Data

For testing purposes, this directory contains `mock_traffic.csv` with 1000 rows of simulated IoT traffic:
- 70% benign traffic (normal IoT device communication)
- 30% malicious traffic (anomalies with spikes in bytes)

Use the mock data for initial development and testing of preprocessing and ML models.

## Processing the Dataset

Use the preprocessing functions in `../models/preprocess.py` to:
1. Load the CSV/TSV files
2. Clean and normalize the data
3. Encode categorical variables
4. Create time-series sequences for LSTM models
5. Split into training and testing sets

Example:
```python
from models.preprocess import preprocess_pipeline

result = preprocess_pipeline(
    file_path='data/iot23_labeled.csv',
    numeric_cols=['duration', 'orig_bytes', 'resp_bytes', 'orig_pkts', 'resp_pkts'],
    categorical_cols=['proto', 'service'],
    label_col='label',
    create_seq=True,
    seq_length=10
)
```

## Notes

- The dataset is large and may take time to download
- Ensure you have sufficient disk space (10+ GB recommended)
- The preprocessing pipeline can handle both the full dataset and individual scenarios
- Start with the mock data to test your pipeline before using the full dataset

