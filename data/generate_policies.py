from pathlib import Path

OUTPUT_DIR = Path("data/company_docs/acme_corp")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

documents = {
    "03_password_policy.txt": """
# Acme Corp Password Policy

## Purpose
This policy defines password and authentication requirements for Acme Corp systems.

## Password Requirements
Passwords must be at least 12 characters long.
Passwords must not be shared between users.
Default passwords must be changed before production use.

## Multi-Factor Authentication
Multi-factor authentication is required for remote access and privileged administrative accounts.

## Credential Protection
Users must not store passwords in plain text or disclose them to unauthorized persons.

## Password Changes
Passwords must be changed when compromise is suspected.

## Gap intentionally left
This policy does not define a routine password expiration schedule.
""",

    "04_incident_response_policy.txt": """
# Acme Corp Incident Response Policy

## Purpose
This policy defines how Acme Corp identifies, reports, investigates, and responds to cybersecurity incidents.

## Reporting
Employees must immediately report suspected security incidents to the Information Security Department.

## Incident Classification
Incidents shall be classified according to severity and potential business impact.

## Response
The incident response team shall investigate reported incidents, contain affected systems, and coordinate recovery actions.

## Communication
Significant incidents shall be escalated to management.

## Documentation
Incident details and response actions shall be recorded.

## Gap intentionally left
No formal post-incident lessons-learned review frequency is defined.
""",

    "05_risk_management_policy.txt": """
# Acme Corp Cybersecurity Risk Management Policy

## Purpose
This policy establishes requirements for managing cybersecurity risk.

## Risk Identification
Cybersecurity risks shall be identified for systems, applications, business processes, and third-party services.

## Risk Assessment
Risks shall be evaluated based on likelihood and business impact.

## Risk Treatment
Risk owners shall determine whether risks are mitigated, transferred, accepted, or avoided.

## Risk Register
Significant risks shall be documented in a cybersecurity risk register.

## Review
High-risk items shall be reviewed by management.

## Gap intentionally left
The policy does not specify an exact organization-wide risk assessment frequency.
""",

    "06_asset_management_policy.txt": """
# Acme Corp Asset Management Policy

## Asset Inventory
Acme Corp shall maintain an inventory of information systems, devices, software, and important information assets.

## Asset Ownership
Each important asset shall have an assigned owner.

## Classification
Information assets shall be classified according to sensitivity and business importance.

## Lifecycle
Assets shall be recorded when acquired and removed from the inventory when retired.

## Responsibility
Asset owners are responsible for ensuring appropriate protection requirements are applied.
""",

    "07_backup_policy.txt": """
# Acme Corp Backup and Recovery Policy

## Purpose
This policy establishes requirements for data backup and recovery.

## Backup
Critical business information and system configurations shall be backed up regularly.

## Protection
Backup data shall be protected from unauthorized access.

## Restoration
The organization shall maintain procedures for restoring critical data from backup.

## Testing
Backup restoration shall be tested at least annually.

## Retention
Backup retention periods shall be established according to business and legal requirements.
""",

    "08_business_continuity_policy.txt": """
# Acme Corp Business Continuity Policy

## Purpose
Acme Corp shall maintain business continuity and disaster recovery capabilities.

## Business Impact
Critical services and dependencies shall be identified.

## Recovery
Recovery procedures shall exist for critical systems and business processes.

## Roles
Business continuity responsibilities shall be assigned to appropriate personnel.

## Testing
Business continuity plans shall be tested periodically.

## Gap intentionally left
The policy does not define the exact test frequency or recovery time objectives.
""",

    "09_vendor_security_policy.txt": """
# Acme Corp Third-Party and Vendor Security Policy

## Purpose
This policy defines cybersecurity requirements for suppliers and service providers.

## Due Diligence
Security risks shall be considered before engaging important third parties.

## Contracts
Relevant cybersecurity and confidentiality requirements shall be included in supplier agreements.

## Access
Third-party access to Acme Corp systems shall be authorized and limited to business need.

## Monitoring
High-risk suppliers may be reviewed based on risk.

## Gap intentionally left
A mandatory periodic reassessment schedule for all critical suppliers is not defined.
""",

    "10_security_awareness_policy.txt": """
# Acme Corp Security Awareness and Training Policy

## Purpose
This policy establishes security awareness requirements for personnel.

## Training
All employees shall receive information security awareness training.

## New Employees
New employees shall receive awareness training as part of onboarding.

## Topics
Training shall include phishing, password protection, incident reporting, and safe handling of company information.

## Records
Training completion shall be recorded.

## Gap intentionally left
The policy does not define a mandatory annual refresher frequency.
""",

    "11_logging_monitoring_policy.txt": """
# Acme Corp Logging and Monitoring Policy

## Logging
Security-relevant systems shall generate logs for authentication events, administrative actions, and significant security events.

## Protection
Logs shall be protected from unauthorized modification.

## Monitoring
The Information Security Department shall monitor important systems for suspicious activity.

## Review
Critical security alerts shall be reviewed and investigated.

## Gap intentionally left
Log retention duration is not defined.
""",

    "12_vulnerability_management_policy.txt": """
# Acme Corp Vulnerability Management Policy

## Identification
Systems shall be assessed for known vulnerabilities.

## Prioritization
Vulnerabilities shall be prioritized according to severity and business impact.

## Remediation
Critical vulnerabilities shall be remediated as soon as reasonably possible.

## Tracking
Identified vulnerabilities and remediation activities shall be tracked.

## Gap intentionally left
Specific remediation timelines by severity are not formally defined.
""",

    "13_change_management_policy.txt": """
# Acme Corp Change Management Policy

## Purpose
Changes to production systems shall be controlled to reduce operational and security risk.

## Approval
Significant production changes require authorization before implementation.

## Testing
Changes should be tested before deployment when practical.

## Documentation
Implementation and rollback information shall be documented.

## Emergency Changes
Emergency changes may follow an expedited approval process and must be documented afterward.
""",

    "14_remote_access_policy.txt": """
# Acme Corp Remote Access Policy

## Authorization
Remote access shall only be provided to authorized personnel with a business need.

## Authentication
Multi-factor authentication is required for remote access.

## Devices
Remote access should use company-approved devices where possible.

## Protection
Remote sessions shall use approved encrypted communication methods.

## Termination
Remote access shall be revoked when no longer required.
""",

    "15_data_classification_policy.txt": """
# Acme Corp Data Classification Policy

## Classification Levels
Information shall be classified according to sensitivity and business importance.

## Handling
Personnel shall handle information according to its classification.

## Access
Sensitive information shall be accessible only to authorized personnel.

## Storage
Sensitive information must be stored using approved systems.

## Disposal
Sensitive information shall be securely destroyed when no longer required.
""",

    "16_encryption_policy.txt": """
# Acme Corp Encryption Policy

## Data in Transit
Sensitive information transmitted over untrusted networks shall be encrypted.

## Data at Rest
Sensitive data stored on approved systems should use encryption where appropriate.

## Cryptographic Standards
Only approved cryptographic technologies shall be used.

## Key Protection
Cryptographic keys shall be protected against unauthorized access.

## Gap intentionally left
Formal cryptographic key rotation intervals are not defined.
""",

    "17_mobile_device_policy.txt": """
# Acme Corp Mobile Device Security Policy

## Devices
Company-managed mobile devices shall use approved security configurations.

## Authentication
Devices shall require user authentication.

## Updates
Security updates shall be installed in a timely manner.

## Lost Devices
Lost or stolen company devices must be reported immediately.

## Data Protection
Sensitive company information stored on mobile devices shall be protected.
""",

    "18_physical_security_policy.txt": """
# Acme Corp Physical Security Policy

## Facility Access
Access to restricted facilities shall be limited to authorized personnel.

## Visitors
Visitors to restricted areas shall be controlled and supervised.

## Equipment
Critical information systems shall be protected against unauthorized physical access.

## Reporting
Physical security incidents shall be reported.

## Gap intentionally left
No formal schedule for reviewing physical access permissions is defined.
""",

    "19_secure_development_policy.txt": """
# Acme Corp Secure Software Development Policy

## Security Requirements
Security requirements shall be considered during software development.

## Code Review
Important application changes should undergo peer review.

## Testing
Security testing shall be performed when appropriate before production release.

## Secrets
Credentials and sensitive secrets shall not be stored directly in source code.

## Vulnerabilities
Security defects shall be tracked and remediated.
""",

    "20_account_management_procedure.txt": """
# Acme Corp Account Management Procedure

## Account Creation
New accounts require an approved access request.

## Role Changes
Access permissions shall be updated when a user's responsibilities change.

## Termination
Accounts shall be disabled when employment ends.

## Privileged Accounts
Administrative access requires explicit approval.

## Review
System owners should review privileged accounts when requested by Information Security.

## Gap intentionally left
There is no mandatory periodic review interval for all user accounts.
"""
}

for filename, content in documents.items():
    path = OUTPUT_DIR / filename
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"Created: {path}")

print(f"\nCreated {len(documents)} documents.")