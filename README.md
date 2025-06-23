# Task 1: Local Network Port Scanning using Nmap

## Objective
To discover open ports and services on devices within a local network using Nmap, and analyze potential security risks.

---

##  Tools Used
- **Nmap 7.95**
- Wireshark (Optional, not used for this scan)

---

##  Steps Performed

1. Identified my local IP range using:
   ```bash
   ifconfig

## Scan Results Summary
| IP Address      | Open Ports          | Common Services          | MAC Address         | Risk Level |
| --------------- | ------------------- | ------------------------ | ------------------- | ---------- |
| 192.168.119.1   | 88, 445, 5000, 7000 | Kerberos, SMB, UPnP, AFS | B2\:BE:83\:C6:3F:65 | Medium     |
| 192.168.119.2   | None                | All ports closed         | 00:50:56\:EF:9F:74  | Low        |
| 192.168.119.254 | None (Filtered)     | Unknown                  | 00:50:56\:EA:8A:13  | Medium     |
| 192.168.119.128 | \[Scanning Host]    | N/A                      | N/A                 | -          |

## Risks Identified
Port 88 (Kerberos) → If not properly secured, may expose authentication infrastructure.

Port 445 (SMB) → Frequently targeted by ransomware; avoid exposure to public networks.

Port 5000 (UPnP) → Can be abused by malware and used in DDoS amplification attacks.

Port 7000 (AFS3 File Server) → Rarely used; may expose unnecessary file sharing services.

Filtered Ports (192.168.119.254) → Indicates firewall presence or stealth services; may need review.

