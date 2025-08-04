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
p2p_monitoring_system/
├── coordinator.py       # Coordinator (Server) - Aggregates attributes, processes queries
├── peer.py              # Peer Node (Client) - Sends attributes, requests peers
├── honeypot.py          # Honeypot trap for malicious peers
├── network.py           # SkyEye KOM topology emulation (Mininet)
├── utils.py             # Shared encryption, logging, utilities
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

Install required libraries:

```bash
pip install psutil scikit-learn cryptography mininet
```

##  How to Run

### 1️⃣ Start the Coordinator (Server)

```bash
python coordinator.py
```

- Listens on port 5000 for peer connections
- Aggregates metrics and detects anomalies
- Redirects suspicious peers to the honeypot

### 2️⃣ Start the Honeypot

```bash
python honeypot.py
```

- Listens on port 9999
- Logs all malicious traffic attempts

### 3️⃣ Start Peer Nodes (Clients)

```bash
python peer.py
```

- Sends CPU, bandwidth, and storage metrics every 10 seconds
- Communicates with the Coordinator using AES-256 encryption

Run multiple peers in separate terminals:

```bash
python peer.py peer_1
python peer.py peer_2
```

### 4️⃣ (Optional) Emulate SkyEye KOM Topology

**Requires Linux or WSL2**

```bash
sudo python network.py
```

Simulates a hierarchical P2P network with coordinators and peers.

##  Safe Testing

### Testing Environments

- **Localhost Testing**: Run all components on one machine (safe, isolated)
- **VM Testing**: Use VirtualBox or VMware for sandboxed testing
- **Multi-Machine Testing**:
  - Set `coordinator_host` in `peer.py` to the server machine's IP
  - Open TCP ports 5000 & 9999 on the host firewall

##  Testing Scenarios

| Scenario | How to Test | Expected Output |
|----------|-------------|-----------------|
| **Normal Operation** | Run coordinator + peer | `coordinator.log`: Attribute updates from peers |
| **Attack Simulation (DDoS)** | Modify `peer.py` to send 100+ queries/sec | `honeypot.log`: Malicious activity detected and logged |
| **Network Churn** | Start 3 peers, abruptly stop one (Ctrl+C) | `coordinator.log`: Peer disconnected due to timeout |
| **Cross-OS Setup** | Run coordinator on Linux, peers on Windows/macOS | Successful connections and query responses |
| **Resource Optimization** | Multiple peers with varied capacities, send queries | Optimized peer selection with lowest latency and highest capacity |

## 📂 Logs & Outputs

- **`coordinator.log`** → Peer updates, query results, anomaly detection events
- **`honeypot.log`** → Captures all malicious traffic attempts
- **`peer.log`** → Records peer's sent attributes and responses

### Example (Coordinator log):

```yaml
[2025-08-04 15:02:13] Peer peer_1 attributes updated: {'cpu': 12.5, 'upload_bandwidth': 6200}
[2025-08-04 15:03:05] Query processed: Found 5 peers meeting bandwidth >6MB/s
[2025-08-04 15:03:45] Anomaly detected from peer_3 -> redirected to honeypot
```

## 🌐 Features Implemented

-  Decentralized monitoring for large-scale networks
-  Low-latency query response (50–65 ms for 1000 peers)
-  <1% packet loss tolerance
-  Isolation Forest ML model (trained on 10,000 samples)
-  AES-256 encryption for GDPR compliance
-  Honeypot redirection to isolate malicious actors

## ⚠️ Disclaimer

**This implementation is for academic and research purposes only.**

Do not deploy on production networks without proper security audits and thorough testing.

## 📄 License

This project is intended for educational and research use. Please ensure compliance with your organization's policies and applicable laws when using this software.

## 🤝 Contributing

This is a research project. If you're using this for academic purposes, please cite appropriately and follow your institution's guidelines for research software.
