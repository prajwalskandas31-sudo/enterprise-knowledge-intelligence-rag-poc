# Enterprise Security & Compliance Policy

## 1. Password & Authentication Security
All enterprise employees must maintain strong password security across all internal systems:
- Passwords must be at least 14 characters long and include uppercase, lowercase, numbers, and special characters.
- Passwords expire every 90 days and cannot be reused within 10 iterations.
- Multi-Factor Authentication (MFA) is mandatory for all remote logins, VPN connections, and critical SaaS portals.

## 2. Data Encryption & Classification
All sensitive company data must be categorized under one of three tiers:
- **Public**: Unrestricted general data suitable for public dissemination.
- **Internal**: Proprietary operational data accessible to active staff.
- **Restricted**: PII, financial records, and cryptographic credentials requiring strict role-based access control (RBAC).

All data at rest must be encrypted using AES-256 standards. Data in transit must utilize TLS 1.3 encryption.

## 3. Incident Response Procedure
In the event of a suspected security incident or data breach:
1. Immediately contact the Security Operations Center (SOC) at `soc@enterprise.com`.
2. Do not attempt to wipe, format, or alter compromised hardware or logs.
3. The Incident Response Team will contain the outbreak within 60 minutes of notification.
