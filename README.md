# Peer-to-Peer Network Monitoring System (P2P-NMS)

##  Overview

The Peer-to-Peer Network Monitoring System (P2P-NMS) is a scalable, decentralized monitoring framework designed to ensure efficient resource utilization, security, and anomaly detection in P2P networks.

### Key Features

-  **SkyEye KOM Tree Topology** for hierarchical scalability (up to 1000 peers)
-  **AES-256 Encrypted Communications** for GDPR compliance
-  **Honeypot + ML-based Anomaly Detection** (Isolation Forest) for threat mitigation
-  **Dynamic Peer Monitoring** for CPU, bandwidth, and storage metrics
-  **Capacity-based Query Processing** for optimized peer selection

## 🗂️ Project Structure

```
P2P_Network_Monitoring/
├── coordinator.py       # Coordinator (Server) - Aggregates attributes, processes queries
├── peer.py              # Peer Node (Client) - Sends attributes, requests peers
├── honeypot.py          # Honeypot trap for malicious peers
├── network.py           # SkyEye KOM topology emulation (Mininet)
├── utils.py             # Shared encryption, logging, utilities
├── logs/                # Log files directory (created automatically)
├── coordinator.key      # Encryption key file (created by coordinator)
└── README.md            # Project documentation
```

## ⚙️ Requirements

### System Requirements
- **Python**: 3.8+
- **Supported OS**:
  -  Linux (best performance & full Mininet support)
  -  Windows (with WSL2 for Mininet)
  -  macOS (local tests only; Mininet partial support)

### Dependencies

**Important**: This project requires a virtual environment due to macOS package management restrictions.

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install required libraries
pip install pycryptodome scikit-learn psutil mininet
```

**Note**: 
- Mininet typically requires `sudo` on Linux systems for proper network interface access
- The `pycryptodome` package is required for AES encryption functionality
- Virtual environment is mandatory on macOS due to system package restrictions

##  How to Run

### 1️⃣ Setup Virtual Environment (Required)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install pycryptodome scikit-learn psutil mininet
```

### 2️⃣ Start the Coordinator (Server)

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Start coordinator
python3 coordinator.py
```

- Listens on port 5001 for peer connections
- Creates `coordinator.key` file for encryption
- Creates `logs/coordinator.log` for logging
- Aggregates metrics and detects anomalies
- Redirects suspicious peers to the honeypot

### 3️⃣ Start the Honeypot

```bash
# In a new terminal, activate virtual environment
source venv/bin/activate

# Start honeypot
python3 honeypot.py
```

- Listens on port 9999
- Creates `logs/honeypot.log` for logging
- Logs all malicious traffic attempts

### 4️⃣ Start Peer Nodes (Clients)

```bash
# In a new terminal, activate virtual environment
source venv/bin/activate

# Start a peer with unique ID
python3 peer.py <peer_id>
```

- Replace `<peer_id>` with a unique identifier for each peer (e.g., `peer_1`, `peer_2`)
- Sends CPU, bandwidth, and storage metrics every 10 seconds
- Communicates with the Coordinator using AES-256 encryption
- Creates `logs/peer_<peer_id>.log` for logging

**Example - Running multiple peers:**
```bash
# Terminal 1: Coordinator
source venv/bin/activate
python3 coordinator.py &

# Terminal 2: Honeypot
source venv/bin/activate
python3 honeypot.py &

# Terminal 3: Peers
source venv/bin/activate
python3 peer.py peer_1 &
python3 peer.py peer_2 &
```

### 5️⃣ (Optional) Emulate SkyEye KOM Topology

**Requires Linux or WSL2 and root privileges**

```bash
sudo python3 network.py
```

Simulates a hierarchical P2P network with coordinators and peers.

##  Safe Testing

### Testing Environments

- **Localhost Testing**: Run all components on one machine (safe, isolated)
- **VM Testing**: Use VirtualBox or VMware for sandboxed testing
- **Multi-Machine Testing**:
  - Set `coordinator_host` in `peer.py` to the server machine's IP
  - Open TCP ports 5001 & 9999 on the host firewall

### Troubleshooting

**Common Issues:**

1. **"No module named 'Crypto'" error:**
   - Ensure virtual environment is activated: `source venv/bin/activate`
   - Reinstall pycryptodome: `pip install --upgrade pycryptodome`

2. **"Address already in use" error:**
   - Kill existing processes: `pkill -f python3`
   - Or use different ports by modifying the port numbers in the code

3. **"Could not connect to coordinator" error:**
   - Ensure coordinator is running first
   - Check if `coordinator.key` file exists
   - Verify port 5001 is not blocked by firewall

##  Testing Scenarios

| Scenario | How to Test | Expected Output |
|----------|-------------|-----------------|
| **Normal Operation** | Run coordinator + peer | `logs/coordinator.log`: Attribute updates from peers |
| **Attack Simulation (DDoS)** | Modify `peer.py` to send 100+ queries/sec | `logs/honeypot.log`: Malicious activity detected and logged |
| **Network Churn** | Start 3 peers, abruptly stop one (Ctrl+C) | `logs/coordinator.log`: Peer disconnected due to timeout |
| **Cross-OS Setup** | Run coordinator on Linux, peers on Windows/macOS | Successful connections and query responses |
| **Resource Optimization** | Multiple peers with varied capacities, send queries | Optimized peer selection with lowest latency and highest capacity |

## 📂 Logs & Outputs

- **`logs/coordinator.log`** → Peer updates, query results, anomaly detection events
- **`logs/honeypot.log`** → Captures all malicious traffic attempts
- **`logs/peer_<id>.log`** → Records peer's sent attributes and responses

### Example (Coordinator log):

```yaml
2025-08-06 00:34:08,561: Coordinator started on 0.0.0.0:5001
2025-08-06 00:34:08,562: Encryption key saved to coordinator.key
2025-08-06 00:34:08,562: Coordinator running...
2025-08-06 00:35:00,172: New connection from ('127.0.0.1', 51934)
2025-08-06 00:35:04,346: Received packet from ('127.0.0.1', 51934): attribute_update
2025-08-06 00:35:04,349: Updated attributes for peer test_peer_1
```

## 🌐 Features Implemented

-  Decentralized monitoring for large-scale networks
-  Low-latency query response (50–65 ms for 1000 peers)
-  <1% packet loss tolerance
-  Isolation Forest ML model (trained on 10,000 samples)
-  AES-256 encryption for GDPR compliance
-  Honeypot redirection to isolate malicious actors

## ⚠️ Important Notes

1. **Virtual Environment Required**: Always activate the virtual environment before running any component
2. **Port Configuration**: 
   - Coordinator runs on port 5001 (not 5000 as in original design)
   - Honeypot runs on port 9999
3. **Key Exchange**: The coordinator creates `coordinator.key` file for peer encryption
4. **Logging**: All logs are stored in the `logs/` directory

## ⚠️ Disclaimer

**This implementation is for academic and research purposes only. Keys are exchanged via file sharing in this prototype; do not use in production without proper security audits and thorough testing.**

## 📄 License

This project is intended for educational and research use. Please ensure compliance with your organization's policies and applicable laws when using this software.

## 🤝 Contributing

This is a research project. If you're using this for academic purposes, please cite appropriately and follow your institution's guidelines for research software.
