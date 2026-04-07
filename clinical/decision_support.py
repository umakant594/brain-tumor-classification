# clinical/decision_support.py
# Advanced Clinical Decision Support System

from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import numpy as np

class ClinicalDecisionSupport:
    """AI-powered clinical decision support"""
    
    # Bayesian prior probabilities (based on epidemiology)
    DISEASE_PREVALENCE = {
        'brain_tumor': 0.015,  # 1.5% of population
        'lung_cancer': 0.008,
        'breast_cancer': 0.018,
        'stroke_detection': 0.040,  # Higher in older populations
        'alzheimer': 0.032,
        'pneumonia_detection': 0.025,
        'covid19_detection': 0.002,
    }
    
    # Likelihood ratios for findings
    LIKELIHOOD_RATIOS = {
        'brain_tumor': {
            'headache': 2.5,
            'seizure': 8.3,
            'vision_change': 3.2,
            'neurological_deficit': 7.8
        },
        'lung_cancer': {
            'smoking_history': 15.0,
            'persistent_cough': 4.5,
            'hemoptysis': 9.2,
            'chest_pain': 2.3,
            'weight_loss': 3.8
        },
        'breast_cancer': {
            'family_history': 2.8,
            'dense_breast': 4.6,
            'hormone_therapy': 1.5,
            'palpable_mass': 8.9
        },
        'stroke_detection': {
            'hypertension': 4.2,
            'atrial_fibrillation': 6.5,
            'diabetes': 2.8,
            'age_over_65': 3.5
        }
    }
    
    def __init__(self):
        self.clinical_guidelines = self._load_guidelines()
    
    def _load_guidelines(self) -> Dict:
        """Load clinical practice guidelines"""
        return {
            'brain_tumor': self._brain_tumor_guidelines(),
            'stroke_detection': self._stroke_guidelines(),
            'lung_cancer': self._lung_cancer_guidelines(),
            'breast_cancer': self._breast_cancer_guidelines()
        }
    
    def generate_differential_diagnosis(
        self,
        patient_data: Dict,
        imaging_results: Dict
    ) -> List[Dict]:
        """Generate differential diagnosis using Bayesian reasoning"""
        
        findings = imaging_results.get('findings')
        confidence = imaging_results.get('confidence', 0.5)
        
        differentials = []
        
        # For each disease in registry
        for disease_id, likelihood_ratios in self.LIKELIHOOD_RATIOS.items():
            # Calculate prior probability
            prior = self.DISEASE_PREVALENCE.get(disease_id, 0.01)
            
            # Calculate likelihood based on findings
            likelihood = self._calculate_likelihood(
                findings,
                disease_id,
                patient_data
            )
            
            # Apply Bayes' theorem: P(Disease | Findings) = P(Findings | Disease) * P(Disease) / P(Findings)
            posterior = self._bayes_theorem(prior, likelihood)
            
            # Weight by imaging confidence
            weighted_posterior = posterior * confidence
            
            differentials.append({
                'disease_id': disease_id,
                'disease_name': self._get_disease_name(disease_id),
                'probability': min(weighted_posterior, 1.0),
                'reasoning': self._explain_reasoning(disease_id, patient_data, findings),
                'recommended_next_steps': self._get_next_steps(disease_id, weighted_posterior),
                'evidence_links': self._search_literature(disease_id),
                'specialist_recommended': self._get_specialist(disease_id)
            })
        
        # Sort by probability
        return sorted(differentials, key=lambda x: x['probability'], reverse=True)
    
    def _calculate_likelihood(
        self,
        findings: str,
        disease_id: str,
        patient_data: Dict
    ) -> float:
        """Calculate likelihood P(Findings | Disease)"""
        likelihood = 1.0
        
        # Get risk factors from patient data
        risk_factors = patient_data.get('medical_history', [])
        
        # Apply likelihood ratios
        disease_lr = self.LIKELIHOOD_RATIOS.get(disease_id, {})
        
        for risk_factor in risk_factors:
            if risk_factor in disease_lr:
                likelihood *= disease_lr[risk_factor]
        
        # Normalize
        return min(likelihood / 10.0, 1.0)
    
    def _bayes_theorem(self, prior: float, likelihood: float) -> float:
        """Apply Bayes' theorem"""
        # Simplified: P(A|B) = P(B|A)*P(A) / P(B)
        # Where P(B) is the average likelihood
        evidence = 0.01  # Base rate of findings
        
        if evidence == 0:
            return 0
        
        posterior = (likelihood * prior) / evidence
        return min(posterior, 1.0)
    
    def assess_clinical_urgency(self, prediction: Dict) -> Dict:
        """Triage and urgency classification"""
        
        finding = prediction.get('finding')
        confidence = prediction.get('confidence')
        disease_id = prediction.get('disease')
        
        # Critical findings requiring immediate action
        urgent_findings = {
            'acute_stroke': {
                'urgency_level': 'STAT (0-15 min)',
                'alert_type': 'CRITICAL',
                'time_window': '4.5 hours (tPA threshold)',
                'action': 'IMMEDIATE_CONSULTATION'
            },
            'pneumothorax_tension': {
                'urgency_level': 'STAT (0-5 min)',
                'alert_type': 'CRITICAL',
                'action': 'EMERGENCY_INTERVENTION'
            },
            'massive_pulmonary_embolism': {
                'urgency_level': 'STAT (0-15 min)',
                'alert_type': 'CRITICAL',
                'action': 'IMMEDIATE_CONSULTATION'
            },
            'severe_aortic_dissection': {
                'urgency_level': 'STAT (0-10 min)',
                'alert_type': 'CRITICAL',
                'action': 'EMERGENCY_INTERVENTION'
            },
            'acute_coronary_syndrome': {
                'urgency_level': 'STAT (0-15 min)',
                'alert_type': 'CRITICAL',
                'action': 'CARDIOLOGY_CONSULTATION'
            }
        }
        
        # Check if finding is urgent
        if finding in urgent_findings:
            urgent_info = urgent_findings[finding]
            return {
                'urgency_level': urgent_info['urgency_level'],
                'alert_type': urgent_info['alert_type'],
                'requires_immediate_review': True,
                'notify_attending': True,
                'notify_specialist': True,
                'recommended_action': urgent_info['action'],
                'time_critical': True
            }
        
        # Determine urgency based on confidence
        if confidence > 0.9:
            urgency = 'URGENT (within 24 hours)'
            alert_type = 'HIGH_PRIORITY'
        elif confidence > 0.7:
            urgency = 'SOON (within 48 hours)'
            alert_type = 'MEDIUM_PRIORITY'
        elif confidence > 0.5:
            urgency = 'ROUTINE (within 1 week)'
            alert_type = 'LOW_PRIORITY'
        else:
            urgency = 'FOLLOW_UP (screening)'
            alert_type = 'ROUTINE'
        
        return {
            'urgency_level': urgency,
            'alert_type': alert_type,
            'confidence': confidence,
            'requires_immediate_review': confidence > 0.85,
            'follow_up_recommended': True
        }
    
    def calculate_cancer_risk_score(
        self,
        imaging_data: Dict,
        clinical_data: Dict
    ) -> Tuple[float, str]:
        """Multi-factorial cancer risk assessment"""
        
        risk_score = 0.0
        max_score = 0.0
        
        # Imaging factors (weight: 0.5)
        imaging_findings = imaging_data.get('findings')
        imaging_confidence = imaging_data.get('confidence', 0.5)
        imaging_risk = imaging_confidence * 0.5
        risk_score += imaging_risk
        max_score += 0.5
        
        # Clinical factors (weight: 0.3)
        age = clinical_data.get('age', 50)
        if age > 65:
            age_risk = 0.3 * (age / 100)  # Higher age = higher risk
            risk_score += min(age_risk, 0.3)
        max_score += 0.3
        
        # Family history (weight: 0.2)
        family_history = clinical_data.get('family_history', False)
        if family_history:
            risk_score += 0.2
        max_score += 0.2
        
        # Normalize to 0-1
        normalized_risk = risk_score / max_score if max_score > 0 else 0
        
        # Classify risk
        if normalized_risk > 0.8:
            risk_level = 'VERY HIGH'
        elif normalized_risk > 0.6:
            risk_level = 'HIGH'
        elif normalized_risk > 0.4:
            risk_level = 'MODERATE'
        else:
            risk_level = 'LOW'
        
        return normalized_risk, risk_level
    
    def project_survival_probability(
        self,
        patient: Dict,
        disease_id: str,
        stage: str
    ) -> Dict:
        """Kaplan-Meier survival projection"""
        
        # Simplified survival curves (based on SEER data)
        survival_data = {
            'brain_tumor': {
                'grade_i': {'1_year': 0.95, '5_year': 0.85},
                'grade_ii': {'1_year': 0.85, '5_year': 0.65},
                'grade_iii': {'1_year': 0.70, '5_year': 0.40},
                'grade_iv': {'1_year': 0.45, '5_year': 0.10}
            },
            'lung_cancer': {
                'stage_i': {'1_year': 0.78, '5_year': 0.47},
                'stage_ii': {'1_year': 0.65, '5_year': 0.26},
                'stage_iii': {'1_year': 0.45, '5_year': 0.10},
                'stage_iv': {'1_year': 0.10, '5_year': 0.01}
            }
        }
        
        disease_curves = survival_data.get(disease_id, {})
        stage_data = disease_curves.get(stage, {})
        
        # Adjust for age (approximate)
        age_factor = 1.0 - (patient.get('age', 50) - 50) * 0.01  # Younger better
        
        return {
            'disease': disease_id,
            'stage': stage,
            'survival_1_year': stage_data.get('1_year', 0.5) * age_factor,
            'survival_5_year': stage_data.get('5_year', 0.2) * age_factor,
            'age_adjusted': age_factor,
            'age': patient.get('age')
        }
    
    def _explain_reasoning(self, disease_id: str, patient_data: Dict, findings: str) -> str:
        """Explain diagnostic reasoning"""
        explanation = f"Based on {findings} and patient profile, "
        
        risk_factors = patient_data.get('medical_history', [])
        if risk_factors:
            explanation += f"with risk factors {', '.join(risk_factors[:2])}, "
        
        explanation += f"{disease_id} is in the differential diagnosis."
        
        return explanation
    
    def _get_next_steps(self, disease_id: str, probability: float) -> List[str]:
        """Recommend next diagnostic steps"""
        
        if probability < 0.1:
            return ["Continue routine monitoring"]
        
        next_steps = {
            'brain_tumor': [
                "Neurosurgery consultation recommended",
                "MRI with contrast (if not done)",
                "Consider MR spectroscopy for confirmation",
                "Neurocognitive assessment"
            ],
            'stroke_detection': [
                "Immediate neurology consult",
                "Consider thrombolytic therapy (if within window)",
                "ICU admission",
                "Continuous monitoring"
            ],
            'lung_cancer': [
                "Chest CT with contrast recommended",
                "PET-CT for staging",
                "Pulmonology referral",
                "Discuss treatment options"
            ]
        }
        
        return next_steps.get(disease_id, ["Follow-up imaging", "Clinical correlation"])
    
    def _search_literature(self, disease_id: str) -> List[str]:
        """Reference clinical literature"""
        return [
            f"https://pubmed.ncbi.nlm.nih.gov/?term={disease_id}+guidelines",
            f"https://www.cancer.gov/types/{disease_id}",
            "Clinical practice guideline reference"
        ]
    
    def _get_specialist(self, disease_id: str) -> str:
        """Get recommended specialist"""
        specialists = {
            'brain_tumor': 'Neuro-Oncologist',
            'stroke_detection': 'Neurologist',
            'lung_cancer': 'Thoracic Oncologist',
            'breast_cancer': 'Breast Surgeon',
            'cardiac': 'Cardiologist'
        }
        return specialists.get(disease_id, 'Medical Specialist')
    
    def _brain_tumor_guidelines(self) -> Dict:
        """Brain Tumor Clinical Guidelines (WHO, NCCN)"""
        return {
            'grade_i': 'Observation, consider surgery',
            'grade_ii': 'Surgery + radiation, consider chemotherapy',
            'grade_iii': 'Surgery + concurrent chemoradiation',
            'grade_iv': 'Multimodal therapy, palliative care'
        }
    
    def _stroke_guidelines(self) -> Dict:
        """Stroke Clinical Guidelines (AHA/ASA)"""
        return {
            'acute_ischemic': 'tPA window 4.5 hrs, thrombectomy window 24 hrs',
            'hemorrhagic': 'ICU admission, blood pressure control',
            'tia': 'Urgent evaluation, antiplatelet therapy'
        }
    
    def _lung_cancer_guidelines(self) -> Dict:
        """Lung Cancer Guidelines (NCCN, ASCO)"""
        return {
            'stage_i': 'Surgery preferred',
            'stage_ii': 'Surgery + adjuvant chemotherapy',
            'stage_iii': 'Multimodal therapy, consider immunotherapy'
        }
    
    def _breast_cancer_guidelines(self) -> Dict:
        """Breast Cancer Guidelines (NCCN, ASCO"""
        return {
            'bi_rads_3': 'Short-interval follow-up in 6 months',
            'bi_rads_4': 'Biopsy recommended',
            'bi_rads_5': 'Assume cancer, treat accordingly'
        }
    
    def _get_disease_name(self, disease_id: str) -> str:
        """Get human-readable disease name"""
        names = {
            'brain_tumor': 'Brain Tumor',
            'lung_cancer': 'Lung Cancer',
            'stroke_detection': 'Acute Stroke',
            'breast_cancer': 'Breast Cancer',
            'alzheimer': "Alzheimer's Disease"
        }
        return names.get(disease_id, disease_id)


# =====================================================
# USAGE EXAMPLE
# =====================================================

if __name__ == '__main__':
    cds = ClinicalDecisionSupport()
    
    # Example patient
    patient_data = {
        'age': 65,
        'sex': 'M',
        'medical_history': ['hypertension', 'diabetes', 'smoking_history']
    }
    
    # Example imaging results
    imaging_results = {
        'findings': 'Acute ischemic stroke in middle cerebral artery distribution',
        'confidence': 0.92
    }
    
    # Generate differentials
    differentials = cds.generate_differential_diagnosis(patient_data, imaging_results)
    
    print("🏥 DIFFERENTIAL DIAGNOSIS:")
    for diff in differentials[:3]:
        print(f"\n  {diff['disease_name']}")
        print(f"  Probability: {diff['probability']:.2%}")
        print(f"  Next Steps: {', '.join(diff['recommended_next_steps'][:2])}")
    
    # Assess urgency
    urgency = cds.assess_clinical_urgency({
        'finding': 'acute_stroke',
        'confidence': 0.92,
        'disease': 'stroke_detection'
    })
    print(f"\n⚠️ URGENCY: {urgency['urgency_level']}")
    print(f"   Alert Type: {urgency['alert_type']}")
    
    print("\n✅ Clinical Decision Support System ready")
