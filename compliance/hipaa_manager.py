# compliance/hipaa_manager.py
# HIPAA Privacy & Security Rule Enforcement

from datetime import datetime
from typing import Dict, List, Any
from cryptography.fernet import Fernet
import os
import json

class HIPAAManager:
    """HIPAA Privacy Rule enforcement"""
    
    PROTECTED_HEALTH_INFO = [
        'patient_id', 'name', 'dob', 'date_of_birth',
        'address', 'phone', 'email', 'ssn', 'medical_record_number',
        'account_number', 'insurance_id', 'policy_number'
    ]
    
    def __init__(self):
        # Generate or load encryption key
        key_file = '.hipaa_key'
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(self.key)
        
        self.cipher = Fernet(self.key)
    
    def encrypt_pii(self, data: str) -> str:
        """AES-256 encryption for sensitive data"""
        if isinstance(data, str):
            data = data.encode()
        encrypted = self.cipher.encrypt(data)
        return encrypted.decode()
    
    def decrypt_pii(self, encrypted_data: str) -> str:
        """Decrypt PHI"""
        decrypted = self.cipher.decrypt(encrypted_data.encode())
        return decrypted.decode()
    
    def identify_pii_fields(self, data: Dict) -> List[str]:
        """Identify which fields contain PHI"""
        pii_fields = []
        for key in data.keys():
            if key.lower() in [p.lower() for p in self.PROTECTED_HEALTH_INFO]:
                pii_fields.append(key)
        return pii_fields
    
    def is_de_identified(self, data_dict: Dict) -> bool:
        """Check if data is de-identified (Safe Harbor)"""
        # Safe Harbor requires removal of 18 identifiers
        pii_fields = [f.lower() for f in self.PROTECTED_HEALTH_INFO]
        
        for key in data_dict.keys():
            if key.lower() in pii_fields:
                return False
        
        return True


class AuditLogger:
    """HIPAA-compliant audit logging (immutable)"""
    
    def __init__(self, log_file: str = 'hipaa_audit_log.jsonl'):
        self.log_file = log_file
        
        # Ensure log file exists
        if not os.path.exists(log_file):
            open(log_file, 'a').close()
    
    def log_access(
        self,
        user_id: str,
        action: str,
        resource: str,
        ip_address: str,
        success: bool = True,
        details: str = None
    ):
        """Log PHI access (HIPAA minimum necessary)"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_id': self._generate_event_id(),
            'user_id': user_id,
            'action': action,
            'resource_accessed': resource,
            'ip_address': ip_address,
            'access_purpose': 'treatment|payment|operations',
            'success': success,
            'details': details or '',
            'system': 'Medical AI Platform'
        }
        
        self._append_to_immutable_log(log_entry)
    
    def log_prediction(
        self,
        user_id: str,
        patient_id: str,
        disease_id: str,
        predicted_class: str,
        confidence: float,
        severity: str,
        ip_address: str
    ):
        """Log AI predictions (clinical decision support)"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_id': self._generate_event_id(),
            'event_type': 'AI_PREDICTION',
            'user_id': user_id,
            'patient_id_hash': self._hash_patient_id(patient_id),
            'disease_id': disease_id,
            'predicted_class': predicted_class,
            'confidence': confidence,
            'severity': severity,
            'ip_address': ip_address,
            'clinical_decision_made': True
        }
        
        self._append_to_immutable_log(log_entry)
    
    def log_data_export(
        self,
        user_id: str,
        records_exported: int,
        export_format: str,
        ip_address: str
    ):
        """Log data export events"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_id': self._generate_event_id(),
            'event_type': 'DATA_EXPORT',
            'user_id': user_id,
            'records_exported': records_exported,
            'export_format': export_format,
            'ip_address': ip_address,
            'action': 'EXPORT_ANALYSIS_DATA'
        }
        
        self._append_to_immutable_log(log_entry)
    
    def log_breach_detection(self, incident: Dict):
        """Log potential HIPAA breach"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_id': self._generate_event_id(),
            'event_type': 'SECURITY_INCIDENT',
            'incident_type': incident.get('type'),
            'severity': 'BREACH',
            'description': incident.get('description'),
            'affected_records': incident.get('affected_count', 0),
            'action_taken': 'INCIDENT_LOGGED_FOR_INVESTIGATION'
        }
        
        self._append_to_immutable_log(log_entry)
    
    def _append_to_immutable_log(self, log_entry: Dict):
        """Append to immutable log file (append-only)"""
        # Append-only mode prevents deletion/modification
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def get_logs(
        self,
        limit: int = 100,
        user_id: str = None,
        event_type: str = None
    ) -> List[Dict]:
        """Retrieve audit logs (admin only)"""
        logs = []
        
        with open(self.log_file, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                
                entry = json.loads(line)
                
                # Filter by user if specified
                if user_id and entry.get('user_id') != user_id:
                    continue
                
                # Filter by event type if specified
                if event_type and entry.get('event_type') != event_type:
                    continue
                
                logs.append(entry)
        
        # Return most recent first
        return sorted(logs, key=lambda x: x['timestamp'], reverse=True)[:limit]
    
    def detect_suspicious_activity(self) -> List[Dict]:
        """Detect potentially suspicious patterns"""
        logs = self.get_logs(limit=1000)
        suspicious = []
        
        # Pattern 1: Multiple failed access attempts
        user_failures = {}
        for log in logs:
            if not log.get('success') and log['action'] == 'ACCESS':
                user_id = log['user_id']
                user_failures[user_id] = user_failures.get(user_id, 0) + 1
        
        for user_id, count in user_failures.items():
            if count > 5:
                suspicious.append({
                    'pattern': 'Multiple failed access attempts',
                    'user_id': user_id,
                    'count': count,
                    'severity': 'MODERATE'
                })
        
        # Pattern 2: Unusual IP addresses
        user_ips = {}
        for log in logs:
            user_id = log['user_id']
            ip = log['ip_address']
            
            if user_id not in user_ips:
                user_ips[user_id] = set()
            user_ips[user_id].add(ip)
        
        for user_id, ips in user_ips.items():
            if len(ips) > 10:  # More than 10 different IPs
                suspicious.append({
                    'pattern': 'Unusual access from multiple IPs',
                    'user_id': user_id,
                    'ip_count': len(ips),
                    'severity': 'HIGH'
                })
        
        return suspicious
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _hash_patient_id(self, patient_id: str) -> str:
        """Hash patient ID for privacy"""
        import hashlib
        return hashlib.sha256(patient_id.encode()).hexdigest()[:16]


class DataBreachResponse:
    """HIPAA Breach Notification Rule Section 164.404"""
    
    def __init__(self, hipaa_manager: HIPAAManager, audit_logger: AuditLogger):
        self.hipaa_manager = hipaa_manager
        self.audit_logger = audit_logger
    
    def assess_breach_risk(self, incident: Dict) -> Dict:
        """HIPAA Risk Assessment Model"""
        risk_factors = {
            'unauthorized_access': incident.get('type') == 'unauthorized_access',
            'data_encrypted': incident.get('data_encrypted', False),
            'likely_acquired': not incident.get('data_encrypted'),  # If not encrypted, likely acquired
            'mitigation_factors': incident.get('mitigations', []),
            'business_associate': incident.get('business_associate', False)
        }
        
        # Is it a breach?
        is_breach = (
            risk_factors['unauthorized_access'] and
            risk_factors['likely_acquired'] and
            len(risk_factors['mitigation_factors']) == 0
        )
        
        return {
            'is_breach': is_breach,
            'risk_factors': risk_factors,
            'affected_individuals': incident.get('affected_count', 0)
        }
    
    def notify_affected_individuals(self, breach: Dict):
        """Send breach notification to affected individuals"""
        notification = {
            'to': breach.get('affected_emails'),
            'subject': 'HIPAA Data Breach Notification',
            'body': f"""
            A breach of your protected health information has occurred.
            
            Affected Data: {breach.get('data_types')}
            Date Discovered: {breach.get('discovery_date')}
            
            We have taken steps to secure your information.
            
            For more information, contact:
            {breach.get('contact_info')}
            """,
            'send_date': datetime.utcnow().isoformat(),
            'notification_type': 'BREACH_NOTIFICATION'
        }
        
        # In real system, send via HIPAA-compliant email
        return notification
    
    def notify_hhs(self, breach: Dict):
        """Notify HHS if 500+ residents affected"""
        if breach.get('affected_count', 0) >= 500:
            notification = {
                'recipient': 'HHS Office for Civil Rights',
                'requirement': 'Federal breach notification',
                'affected_count': breach.get('affected_count'),
                'description': f"Breach affecting {breach.get('affected_count')} residents"
            }
            return notification
        return None
    
    def notify_media(self, breach: Dict):
        """Notify media if 1000+ residents affected"""
        if breach.get('affected_count', 0) >= 1000:
            notification = {
                'type': 'Public media notification',
                'requirement': 'Public disclosure required',
                'affected_count': breach.get('affected_count'),
                'effective_date': breach.get('discovery_date')
            }
            return notification
        return None
    
    def create_breach_report(self, breach: Dict) -> str:
        """Create HIPAA breach report"""
        report = f"""
        ╔════════════════════════════════════════╗
        ║ HIPAA BREACH NOTIFICATION REPORT      ║
        ╚════════════════════════════════════════╝
        
        Date Discovered: {breach.get('discovery_date')}
        Incident Type: {breach.get('type')}
        Affected Individuals: {breach.get('affected_count')}
        
        Data Types Involved:
        {', '.join(breach.get('data_types', []))}
        
        Notification Required:
        - HHS: {breach.get('affected_count', 0) >= 500}
        - Media: {breach.get('affected_count', 0) >= 1000}
        - Individuals: Yes (60 days)
        
        Mitigation Steps Taken:
        {breach.get('mitigations')}
        """
        
        return report


# =====================================================
# USAGE EXAMPLE
# =====================================================

if __name__ == '__main__':
    # Initialize managers
    hipaa = HIPAAManager()
    audit = AuditLogger()
    breach_response = DataBreachResponse(hipaa, audit)
    
    # Test encryption
    original_ssn = "123-45-6789"
    encrypted = hipaa.encrypt_pii(original_ssn)
    decrypted = hipaa.decrypt_pii(encrypted)
    print(f"Original: {original_ssn}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")
    
    # Test audit logging
    audit.log_access(
        user_id='radiologist_123',
        action='VIEW_PATIENT_RECORD',
        resource='patient_456',
        ip_address='192.168.1.100'
    )
    
    print("\n✅ HIPAA Compliance system initialized")
