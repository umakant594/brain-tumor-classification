# 🏥 Phase 7 Implementation: Multi-Disease Architecture

**Status:** Ready for Development  
**Complexity:** High (Requires redesign of core architecture)  
**Timeline:** 8 weeks  

---

## Architecture Overview

```
CURRENT (Single Disease)           →    ENHANCED (Multi-Disease)
┌─────────────────┐                    ┌─────────────────────────┐
│  Brain Tumor    │                    │  Disease Registry       │
│  CNN Model      │                    │  ├─ Brain Tumor         │
│  /predict       │                    │  ├─ Lung Cancer         │
│  Single disease │                    │  ├─ Breast Cancer       │
└─────────────────┘                    │  ├─ Stroke              │
                                       │  ├─ Alzheimer           │
                                       │  └─ ... (10+ diseases)  │
                                       ├─ Modality Handler      │
                                       │  ├─ MRI (multi-seq)     │
                                       │  ├─ CT                  │
                                       │  ├─ X-Ray               │
                                       │  └─ Ultrasound          │
                                       ├─ Ensemble System       │
                                       │  └─ Per-disease models  │
                                       └─ API Layer             │
                                          └─ Dynamic routing    │
```

---

## 📁 New Project Structure

```
Application Root/
├── 📂 models/
│   ├── __init__.py
│   ├── disease_registry.py         ⭐ NEW: Central registry
│   ├── modality_handler.py         ⭐ NEW: Imaging support
│   ├── model_loader.py             ⭐ NEW: Dynamic loading
│   ├── ensemble_manager.py         ⭐ NEW: Multi-model ensemble
│   └── base_classifiers/
│       ├── oncology/
│       │   ├── brain_tumor_model.py
│       │   ├── lung_cancer_model.py
│       │   ├── breast_cancer_model.py
│       │   └── colorectal_cancer_model.py
│       ├── neurology/
│       │   ├── alzheimer_model.py
│       │   ├── stroke_detection_model.py
│       │   └── ms_detection_model.py
│       ├── cardiology/
│       │   ├── cad_model.py
│       │   └── cardiac_dysfunction_model.py
│       └── pulmonology/
│           ├── pneumonia_model.py
│           └── covid_detection_model.py
│
├── 📂 compliance/
│   ├── __init__.py
│   ├── hipaa_manager.py            ⭐ NEW: HIPAA enforcement
│   ├── fda_precert.py              ⭐ NEW: FDA compliance
│   ├── fhir_connector.py           ⭐ NEW: HL7/FHIR
│   └── audit_logger.py             ⭐ NEW: Immutable logs
│
├── 📂 clinical/
│   ├── __init__.py
│   ├── decision_support.py         ⭐ NEW: CDS engine
│   ├── differential_diagnosis.py   ⭐ NEW: Differential gen
│   ├── explainability.py           ⭐ NEW: XAI engine
│   └── clinical_alerts.py          ⭐ NEW: Urgent findings
│
├── 📂 integration/
│   ├── __init__.py
│   ├── pacs_handler.py             ⭐ NEW: DICOM/PACS
│   ├── ehr_client.py               ⭐ NEW: EHR APIs
│   └── worklist_manager.py         ⭐ NEW: Radiology worklist
│
├── 📂 analytics/
│   ├── __init__.py
│   ├── epidemiology.py             ⭐ NEW: Population health
│   ├── performance_monitoring.py   ⭐ NEW: KPI tracking
│   └── outcomes_tracker.py         ⭐ NEW: Patient outcomes
│
├── app_government.py               ⭐ NEW: Enhanced Flask app
├── config_multi_disease.py         ⭐ NEW: Configuration
└── requirements_government.txt     ⭐ NEW: All dependencies
```

---

## 🔧 Implementation Code

### **1. Disease Registry (Core)**

```python
# models/disease_registry.py

from enum import Enum
from typing import Dict, List, Optional
import json

class SeverityLevel(Enum):
    """Clinical severity classifications"""
    NORMAL = 0
    MILD = 1
    MODERATE = 2
    SEVERE = 3
    CRITICAL = 4

class MedicalSpecialty(Enum):
    """Medical specialties"""
    NEUROSURGERY = "Neurosurgery"
    ONCOLOGY = "Oncology"
    RADIOLOGY = "Radiology"
    CARDIOLOGY = "Cardiology"
    PULMONOLOGY = "Pulmonology"
    NEUROLOGY = "Neurology"

class Disease:
    """Single disease model"""
    
    def __init__(
        self,
        disease_id: str,
        name: str,
        category: str,
        icd10_code: str,
        snomed_code: str,
        description: str,
        models: List[str],
        modalities: List[str],
        output_classes: List[str],
        requires_specialist: str,
        confidence_threshold: float,
        approved_by: List[str]
    ):
        self.disease_id = disease_id
        self.name = name
        self.category = category
        self.icd10_code = icd10_code
        self.snomed_code = snomed_code
        self.description = description
        self.models = models  # ['model_v1', 'model_v2', 'ensemble']
        self.modalities = modalities  # ['mri_t1', 'mri_t2', 'ct']
        self.output_classes = output_classes
        self.requires_specialist = requires_specialist
        self.confidence_threshold = confidence_threshold
        self.approved_by = approved_by  # ['FDA', 'CE-IVD']
        self.severity_scale = list(SeverityLevel)
    
    def to_dict(self):
        return {
            'disease_id': self.disease_id,
            'name': self.name,
            'category': self.category,
            'icd10_code': self.icd10_code,
            'snomed_code': self.snomed_code,
            'output_classes': self.output_classes,
            'confidence_threshold': self.confidence_threshold
        }

class DiseaseRegistry:
    """Central disease configuration registry"""
    
    def __init__(self):
        self.diseases: Dict[str, Disease] = {}
        self._load_diseases()
    
    def _load_diseases(self):
        """Initialize all supported diseases"""
        
        # ONCOLOGY
        self.register_disease(Disease(
            disease_id='brain_tumor',
            name='Brain Tumor Classification',
            category='oncology',
            icd10_code='C71',
            snomed_code='126952004',
            description='Primary and secondary central nervous system tumors',
            models=['cnn_v1', 'resnet50', 'efficientnet_b7'],
            modalities=['mri_t1', 'mri_t2', 'mri_flair'],
            output_classes=['normal', 'benign', 'grade_i', 'grade_ii', 'grade_iii', 'grade_iv'],
            requires_specialist='Neuro-Oncologist',
            confidence_threshold=0.85,
            approved_by=['FDA', 'CE-IVD']
        ))
        
        self.register_disease(Disease(
            disease_id='lung_cancer',
            name='Lung Cancer Nodule Detection',
            category='oncology',
            icd10_code='C34',
            snomed_code='39611004',
            description='Lung nodule classification and malignancy assessment',
            models=['radiomics_model', 'vgg16'],
            modalities=['ct_chest', 'ct_hrct', 'pet_ct'],
            output_classes=['normal', 'nodule_benign', 'sclc', 'nsclc_adenocarcinoma', 'nsclc_squamous'],
            requires_specialist='Thoracic Oncologist',
            confidence_threshold=0.88,
            approved_by=['FDA']
        ))
        
        self.register_disease(Disease(
            disease_id='breast_cancer',
            name='Breast Cancer Screening',
            category='oncology',
            icd10_code='C50',
            snomed_code='126926000',
            description='Mammography and breast MRI analysis',
            models=['dense_net', 'inception_v3'],
            modalities=['mammography_2d', 'mammography_3d_tomo', 'mri_breast'],
            output_classes=['bi_rads_0', 'bi_rads_1', 'bi_rads_2', 'bi_rads_3', 'bi_rads_4', 'bi_rads_5', 'bi_rads_6'],
            requires_specialist='Breast Surgeon',
            confidence_threshold=0.90,
            approved_by=['FDA', 'CE-IVD']
        ))
        
        self.register_disease(Disease(
            disease_id='colorectal_cancer',
            name='Colorectal Polyp Classification',
            category='oncology',
            icd10_code='C18-C20',
            snomed_code='126931000',
            description='Endoscopy-based polyp classification',
            models=['cnn_endoscopy', 'resnet50'],
            modalities=['endoscopy_rgb', 'ct_colonography'],
            output_classes=['normal', 'hyperplastic', 'adenoma_low_grade', 'adenoma_high_grade', 'carcinoma'],
            requires_specialist='Gastroenterologist',
            confidence_threshold=0.87,
            approved_by=['CE-IVD']
        ))
        
        # NEUROLOGY
        self.register_disease(Disease(
            disease_id='alzheimer',
            name='Alzheimer Disease Detection',
            category='neurology',
            icd10_code='G30',
            snomed_code='26929004',
            description='Cognitive decline classification using structural and functional MRI',
            models=['3d_cnn', 'resnet3d'],
            modalities=['mri_t1', 'mri_t2', 'pet_fdog'],
            output_classes=['cognitive_normal', 'mild_cognitive_impairment', 'dementia'],
            requires_specialist='Neurologist',
            confidence_threshold=0.82,
            approved_by=['CE-IVD']
        ))
        
        self.register_disease(Disease(
            disease_id='stroke_detection',
            name='Acute Stroke Detection',
            category='neurology',
            icd10_code='I63-I64',
            snomed_code='230690007',
            description='Acute ischemic and hemorrhagic stroke detection',
            models=['stroke_cnn', 'efficientnet_b5'],
            modalities=['ct_brain', 'mri_dwi', 'mri_perfusion'],
            output_classes=['normal', 'acute_ischemic', 'chronic_ischemic', 'hemorrhagic', 'subarachnoid'],
            requires_specialist='Neurologist',
            confidence_threshold=0.95,  # HIGH confidence for stroke
            approved_by=['FDA']
        ))
        
        self.register_disease(Disease(
            disease_id='multiple_sclerosis',
            name='Multiple Sclerosis Lesion Detection',
            category='neurology',
            icd10_code='G35',
            snomed_code='24700007',
            description='MS lesion segmentation and quantification',
            models=['unet_ms', 'segnet'],
            modalities=['mri_t1', 'mri_t2', 'mri_flair'],
            output_classes=['normal', 'active_lesion', 'chronic_lesion', 'atrophic_area'],
            requires_specialist='Neurologist',
            confidence_threshold=0.80,
            approved_by=['CE-IVD']
        ))
        
        # CARDIOLOGY
        self.register_disease(Disease(
            disease_id='coronary_artery_disease',
            name='Coronary Artery Disease Detection',
            category='cardiology',
            icd10_code='I24-I25',
            snomed_code='53741008',
            description='CAD assessment with plaque quantification',
            models=['cardiac_cnn', 'resnet50'],
            modalities=['ct_angiography', 'pet_ct'],
            output_classes=['normal', 'minimal_stenosis', 'mild_stenosis', 'moderate_stenosis', 'severe_stenosis'],
            requires_specialist='Cardiologist',
            confidence_threshold=0.88,
            approved_by=['FDA', 'CE-IVD']
        ))
        
        self.register_disease(Disease(
            disease_id='cardiac_dysfunction',
            name='Cardiac Dysfunction Assessment',
            category='cardiology',
            icd10_code='I50',
            snomed_code='84114007',
            description='Ejection fraction and ventricular function assessment',
            models=['echo_cnn', '3d_conv'],
            modalities=['echocardiography', 'cardiac_mri', 'cardiac_ct'],
            output_classes=['normal_ejection_fraction', 'mildly_reduced', 'moderately_reduced', 'severely_reduced'],
            requires_specialist='Cardiologist',
            confidence_threshold=0.85,
            approved_by=['CE-IVD']
        ))
        
        # PULMONOLOGY
        self.register_disease(Disease(
            disease_id='pneumonia_detection',
            name='Pneumonia Detection',
            category='pulmonology',
            icd10_code='J12-J18',
            snomed_code='233604007',
            description='Bacterial, viral, fungal pneumonia classification',
            models=['chest_xray_cnn', 'efficientnet'],
            modalities=['chest_xray_pa', 'chest_xray_lateral', 'ct_chest'],
            output_classes=['normal', 'bacterial_pneumonia', 'viral_pneumonia', 'fungal_pneumonia', 'aspiration'],
            requires_specialist='Pulmonologist',
            confidence_threshold=0.90,
            approved_by=['FDA', 'CE-IVD']
        ))
        
        self.register_disease(Disease(
            disease_id='covid19_detection',
            name='COVID-19 Lung Involvement',
            category='pulmonology',
            icd10_code='U07.1',
            snomed_code='840539006',
            description='COVID-19 pneumonia severity assessment',
            models=['covid_cnn', 'densenet'],
            modalities=['chest_xray', 'ct_chest'],
            output_classes=['normal', 'typical_covid', 'indeterminate', 'atypical'],
            requires_specialist='Pulmonologist',
            confidence_threshold=0.88,
            approved_by=['CE-IVD']
        ))
    
    def register_disease(self, disease: Disease):
        """Register a new disease"""
        self.diseases[disease.disease_id] = disease
    
    def get_disease(self, disease_id: str) -> Optional[Disease]:
        """Retrieve disease configuration"""
        return self.diseases.get(disease_id)
    
    def get_by_category(self, category: str) -> List[Disease]:
        """Get all diseases in a category"""
        return [d for d in self.diseases.values() if d.category == category]
    
    def get_by_modality(self, modality: str) -> List[Disease]:
        """Get all diseases supportable by a modality"""
        return [d for d in self.diseases.values() if modality in d.modalities]
    
    def list_all_diseases(self) -> List[Dict]:
        """Export all diseases"""
        return [d.to_dict() for d in self.diseases.values()]
    
    def get_recommended_follow_up(self, disease_id: str, severity: SeverityLevel) -> Dict:
        """Get follow-up recommendations"""
        disease = self.get_disease(disease_id)
        
        follow_ups = {
            SeverityLevel.NORMAL: {
                'interval_days': 365,
                'urgency': 'routine',
                'imaging_modality': disease.modalities[0]
            },
            SeverityLevel.MILD: {
                'interval_days': 90,
                'urgency': 'soon',
                'imaging_modality': disease.modalities[0]
            },
            SeverityLevel.MODERATE: {
                'interval_days': 14,
                'urgency': 'urgent',
                'imaging_modality': 'enhanced_imaging',
                'specialist_consultation': True
            },
            SeverityLevel.SEVERE: {
                'interval_days': 1,
                'urgency': 'stat',
                'imaging_modality': 'multi_modality',
                'specialist_consultation': True,
                'hospitalization': True
            },
            SeverityLevel.CRITICAL: {
                'interval_days': 0,
                'urgency': 'emergency',
                'imaging_modality': 'stat_imaging',
                'specialist_consultation': True,
                'hospitalization': True,
                'intensive_care': True
            }
        }
        
        return follow_ups[severity]

# =====================================================
# USAGE EXAMPLE
# =====================================================

if __name__ == '__main__':
    registry = DiseaseRegistry()
    
    # List all diseases
    print("📋 SUPPORTED DISEASES:")
    for disease in registry.list_all_diseases():
        print(f"  - {disease['name']} ({disease['disease_id']})")
    
    # Get specific disease
    brain_tumor = registry.get_disease('brain_tumor')
    print(f"\n🧠 {brain_tumor.name}")
    print(f"   ICD-10: {brain_tumor.icd10_code}")
    print(f"   SNOMED: {brain_tumor.snomed_code}")
    print(f"   Models: {', '.join(brain_tumor.models)}")
    print(f"   Modalities: {', '.join(brain_tumor.modalities)}")
    
    # Get by category
    print(f"\n🏥 ONCOLOGY DISEASES:")
    for disease in registry.get_by_category('oncology'):
        print(f"  - {disease.name}")
    
    # Get by modality
    print(f"\n🔍 DISEASES WITH MRI SUPPORT:")
    for disease in registry.get_by_modality('mri_t1'):
        print(f"  - {disease.name}")
    
    # Follow-up recommendations
    followup = registry.get_recommended_follow_up('stroke_detection', SeverityLevel.CRITICAL)
    print(f"\n⏰ FOLLOW-UP (STROKE-CRITICAL):")
    print(f"   Urgency: {followup['urgency']}")
    print(f"   Interval: {followup['interval_days']} days")
```

---

### **2. Modality Handler**

```python
# models/modality_handler.py

from enum import Enum
from typing import Dict, Tuple
import numpy as np

class Modality(Enum):
    """Supported imaging modalities"""
    MRI_T1 = "mri_t1"
    MRI_T2 = "mri_t2"
    MRI_FLAIR = "mri_flair"
    CT_BRAIN = "ct_brain"
    CT_CHEST = "ct_chest"
    CT_ANGIOGRAPHY = "ct_angiography"
    CHEST_XRAY = "chest_xray"
    MAMMOGRAPHY = "mammography"
    ULTRASOUND = "ultrasound"
    PATHOLOGY = "pathology"

class ModalitySpecification:
    """Specifications for each modality"""
    
    def __init__(
        self,
        modality: Modality,
        expected_shape: Tuple[int, int, int],
        color_space: str,
        bit_depth: int,
        preprocessing_pipeline: str,
        windowing_presets: Dict = None
    ):
        self.modality = modality
        self.expected_shape = expected_shape
        self.color_space = color_space
        self.bit_depth = bit_depth
        self.preprocessing_pipeline = preprocessing_pipeline
        self.windowing_presets = windowing_presets or {}

class ModalityHandler:
    """Handle different imaging modalities"""
    
    MODALITY_SPECS = {
        Modality.MRI_T1: ModalitySpecification(
            modality=Modality.MRI_T1,
            expected_shape=(256, 256, 176),  # 3D volume
            color_space='grayscale',
            bit_depth=16,
            preprocessing_pipeline='mri_normalize'
        ),
        Modality.MRI_T2: ModalitySpecification(
            modality=Modality.MRI_T2,
            expected_shape=(256, 256, 176),
            color_space='grayscale',
            bit_depth=16,
            preprocessing_pipeline='mri_normalize'
        ),
        Modality.CT_BRAIN: ModalitySpecification(
            modality=Modality.CT_BRAIN,
            expected_shape=(512, 512, 200),
            color_space='grayscale',
            bit_depth=12,
            preprocessing_pipeline='ct_hounsfield_normalize',
            windowing_presets={'brain': (40, 80), 'bone': (400, 800)}
        ),
        Modality.CHEST_XRAY: ModalitySpecification(
            modality=Modality.CHEST_XRAY,
            expected_shape=(2048, 2048),
            color_space='grayscale',
            bit_depth=16,
            preprocessing_pipeline='xray_normalize'
        ),
        Modality.PATHOLOGY: ModalitySpecification(
            modality=Modality.PATHOLOGY,
            expected_shape=(2560, 1920, 3),  # RGB WSI tile
            color_space='rgb',
            bit_depth=8,
            preprocessing_pipeline='color_normalization'
        ),
    }
    
    @staticmethod
    def validate_modality(image: np.ndarray, modality: Modality) -> Tuple[bool, str]:
        """Validate image for modality"""
        spec = ModalityHandler.MODALITY_SPECS.get(modality)
        
        if len(image.shape) == 2 and len(spec.expected_shape) == 3:
            return False, f"Expected 3D volume for {modality.value}"
        
        if image.dtype != np.uint8 and image.dtype != np.uint16:
            return False, f"Unsupported data type: {image.dtype}"
        
        return True, "Valid"
    
    @staticmethod
    def preprocess_mri(image: np.ndarray, sequence_type: str) -> np.ndarray:
        """MRI preprocessing"""
        # Z-score normalization
        mean = np.mean(image)
        std = np.std(image)
        normalized = (image - mean) / (std + 1e-8)
        
        # Clip outliers
        normalized = np.clip(normalized, -3, 3)
        
        return normalized
    
    @staticmethod
    def preprocess_ct(image: np.ndarray, window_preset: str = 'brain') -> np.ndarray:
        """CT preprocessing with Hounsfield windowing"""
        windows = {
            'brain': (40, 80),
            'bone': (400, 800),
            'lung': (-600, -200),
            'mediastinum': (40, 400)
        }
        
        center, width = windows.get(window_preset, (40, 400))
        
        # Apply window
        windowed = np.clip(image, center - width/2, center + width/2)
        
        # Normalize to 0-1
        windowed = (windowed - (center - width/2)) / width
        
        return windowed
    
    @staticmethod
    def preprocess_xray(image: np.ndarray) -> np.ndarray:
        """Chest X-ray preprocessing"""
        # Histogram equalization
        hist, bins = np.histogram(image.flatten(), 256, [0, 256])
        cdf = hist.cumsum()
        cdf_normalized = cdf * hist.max() / cdf.max()
        
        return cdf_normalized[image]
    
    @staticmethod
    def get_preprocessing_function(modality: Modality):
        """Get preprocessing function for modality"""
        preprocess_map = {
            Modality.MRI_T1: ModalityHandler.preprocess_mri,
            Modality.MRI_T2: ModalityHandler.preprocess_mri,
            Modality.MRI_FLAIR: ModalityHandler.preprocess_mri,
            Modality.CT_BRAIN: ModalityHandler.preprocess_ct,
            Modality.CT_CHEST: ModalityHandler.preprocess_ct,
            Modality.CHEST_XRAY: ModalityHandler.preprocess_xray,
        }
        return preprocess_map.get(modality)
```

---

### **3. Dynamic Model Loader**

```python
# models/model_loader.py

import tensorflow as tf
from typing import Dict, List
import os

class ModelLoader:
    """Dynamically load disease-specific models"""
    
    def __init__(self, model_base_path: str):
        self.model_base_path = model_base_path
        self.loaded_models: Dict[str, tf.keras.Model] = {}
    
    def load_model_for_disease(self, disease_id: str, model_name: str) -> tf.keras.Model:
        """Load a specific model for a disease"""
        cache_key = f"{disease_id}:{model_name}"
        
        # Check cache
        if cache_key in self.loaded_models:
            return self.loaded_models[cache_key]
        
        # Construct path
        model_path = os.path.join(
            self.model_base_path,
            disease_id,
            f"{model_name}.h5"
        )
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        # Load model
        model = tf.keras.models.load_model(model_path, custom_objects={
            'precision': tf.keras.metrics.Precision(),
            'recall': tf.keras.metrics.Recall(),
            'auc': tf.keras.metrics.AUC()
        })
        
        # Cache
        self.loaded_models[cache_key] = model
        
        return model
    
    def load_ensemble_for_disease(self, disease_id: str) -> List[tf.keras.Model]:
        """Load all models for a disease (for ensemble)"""
        from .disease_registry import DiseaseRegistry
        
        registry = DiseaseRegistry()
        disease = registry.get_disease(disease_id)
        
        models = []
        for model_name in disease.models:
            model = self.load_model_for_disease(disease_id, model_name)
            models.append(model)
        
        return models
```

---

Now I'll create the **Enhanced Flask App** for multi-disease:
<function_calls>
<invoke name="create_file">
<parameter name="content"># app_multi_disease.py
# Multi-disease enhanced Flask application

from flask import Flask, request, jsonify, render_template
from flask_session import Session
import numpy as np
import os
from datetime import datetime
from typing import Dict, List, Tuple
import logging

# Import new modules
from models.disease_registry import DiseaseRegistry, SeverityLevel
from models.modality_handler import ModalityHandler, Modality
from models.model_loader import ModelLoader
from compliance.hipaa_manager import HIPAAManager, AuditLogger
from clinical.decision_support import ClinicalDecisionSupport
from security import SecurityManager, ImageValidator, RateLimiter

# =====================================================
# FLASK APP SETUP
# =====================================================

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
Session(app)

# Initialize managers
disease_registry = DiseaseRegistry()
modality_handler = ModalityHandler()
model_loader = ModelLoader('models/weights')
hipaa_manager = HIPAAManager()
security_manager = SecurityManager()
image_validator = ImageValidator()
rate_limiter = RateLimiter(requests_per_hour=100)
audit_logger = AuditLogger()
cds_engine = ClinicalDecisionSupport()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =====================================================
# UTILITIES
# =====================================================

def get_client_ip():
    """Get client IP address"""
    if request.environ.get('HTTP_CF_CONNECTING_IP'):
        return request.environ['HTTP_CF_CONNECTING_IP']
    return request.remote_addr

def classify_severity(confidence: float, disease_id: str) -> SeverityLevel:
    """Classify severity based on confidence"""
    disease = disease_registry.get_disease(disease_id)
    
    if confidence > 0.9:
        return SeverityLevel.CRITICAL
    elif confidence > 0.8:
        return SeverityLevel.SEVERE
    elif confidence > 0.7:
        return SeverityLevel.MODERATE
    elif confidence > 0.5:
        return SeverityLevel.MILD
    else:
        return SeverityLevel.NORMAL

def check_rate_limit():
    """Check rate limiting"""
    ip = get_client_ip()
    if not rate_limiter.is_allowed(ip):
        return False, rate_limiter.get_remaining(ip)
    return True, rate_limiter.get_remaining(ip)

# =====================================================
# API ENDPOINTS - DISEASE DISCOVERY
# =====================================================

@app.route('/api/v2/diseases', methods=['GET'])
def list_diseases():
    """List all supported diseases"""
    allowed, remaining = check_rate_limit()
    if not allowed:
        return {'error': 'Rate limit exceeded'}, 429
    
    category = request.args.get('category')
    
    if category:
        diseases = disease_registry.get_by_category(category)
    else:
        diseases = list(disease_registry.diseases.values())
    
    response = {
        'total_diseases': len(diseases),
        'diseases': [d.to_dict() for d in diseases],
        'rate_limit_remaining': remaining
    }
    
    # Log for audit
    audit_logger.log_access(
        user_id=request.headers.get('X-User-ID', 'anonymous'),
        action='LIST_DISEASES',
        resource='disease_and_modality_registry',
        ip_address=get_client_ip()
    )
    
    return jsonify(response), 200

@app.route('/api/v2/diseases/<disease_id>', methods=['GET'])
def get_disease_details(disease_id: str):
    """Get detailed disease information"""
    allowed, remaining = check_rate_limit()
    if not allowed:
        return {'error': 'Rate limit exceeded'}, 429
    
    disease = disease_registry.get_disease(disease_id)
    
    if not disease:
        audit_logger.log_access(
            user_id=request.headers.get('X-User-ID', 'anonymous'),
            action='GET_DISEASE_FAILED',
            resource=disease_id,
            ip_address=get_client_ip()
        )
        return {'error': f'Disease not found: {disease_id}'}, 404
    
    response = {
        'disease': disease.to_dict(),
        'specialist': disease.requires_specialist,
        'confidence_threshold': disease.confidence_threshold,
        'approved_by': disease.approved_by,
        'modalities_supported': disease.modalities,
        'output_classes': disease.output_classes,
        'rate_limit_remaining': remaining
    }
    
    audit_logger.log_access(
        user_id=request.headers.get('X-User-ID', 'anonymous'),
        action='GET_DISEASE_DETAILS',
        resource=disease_id,
        ip_address=get_client_ip()
    )
    
    return jsonify(response), 200

@app.route('/api/v2/modalities', methods=['GET'])
def list_modalities():
    """List all supported imaging modalities"""
    allowed, remaining = check_rate_limit()
    if not allowed:
        return {'error': 'Rate limit exceeded'}, 429
    
    modalities = []
    for modality in Modality:
        spec = ModalityHandler.MODALITY_SPECS.get(modality)
        if spec:
            modalities.append({
                'modality_id': modality.value,
                'color_space': spec.color_space,
                'bit_depth': spec.bit_depth,
                'preprocessing': spec.preprocessing_pipeline
            })
    
    response = {
        'total_modalities': len(modalities),
        'modalities': modalities,
        'rate_limit_remaining': remaining
    }
    
    return jsonify(response), 200

@app.route('/api/v2/modalities/<modality_id>/diseases', methods=['GET'])
def get_diseases_by_modality(modality_id: str):
    """Get diseases detectable by a modality"""
    allowed, remaining = check_rate_limit()
    if not allowed:
        return {'error': 'Rate limit exceeded'}, 429
    
    diseases = disease_registry.get_by_modality(modality_id)
    
    response = {
        'modality': modality_id,
        'supported_diseases': [d.to_dict() for d in diseases],
        'total': len(diseases),
        'rate_limit_remaining': remaining
    }
    
    return jsonify(response), 200

# =====================================================
# API ENDPOINTS - PREDICTION
# =====================================================

@app.route('/api/v2/predict', methods=['POST'])
def predict_multi_disease():
    """Predict disease from image with multi-disease support"""
    allowed, remaining = check_rate_limit()
    if not allowed:
        return {'error': 'Rate limit exceeded'}, 429
    
    try:
        # Get inputs
        disease_id = request.form.get('disease_id')
        modality = request.form.get('modality')
        patient_id = request.form.get('patient_id')
        
        if not disease_id or not modality:
            return {'error': 'disease_id and modality required'}, 400
        
        # Validate disease
        disease = disease_registry.get_disease(disease_id)
        if not disease:
            return {'error': f'Disease not supported: {disease_id}'}, 400
        
        # Get image file
        if 'image' not in request.files:
            return {'error': 'Image file required'}, 400
        
        file = request.files['image']
        
        # Validate file
        is_valid, error = security_manager.validate_file_upload(file, disease.modalities)
        if not is_valid:
            return {'error': error}, 400
        
        # Read and preprocess image
        image_data = file.read()
        image_array = np.frombuffer(image_data, np.uint8)
        
        # Validate image content
        is_valid, error = image_validator.validate_image_content(image_array)
        if not is_valid:
            return {'error': f'Image validation failed: {error}'}, 400
        
        # Decode image
        import cv2
        image = cv2.imdecode(image_array, cv2.IMREAD_GRAYSCALE)
        
        # Modality-specific preprocessing
        modality_enum = Modality(modality)
        preprocess_fn = ModalityHandler.get_preprocessing_function(modality_enum)
        if preprocess_fn:
            image = preprocess_fn(image)
        
        # Resize for model
        image = cv2.resize(image, (256, 256))
        image = np.expand_dims(image, axis=-1)
        image = np.expand_dims(image, axis=0)
        
        # Load models and predict
        models = model_loader.load_ensemble_for_disease(disease_id)
        predictions = []
        
        for model in models:
            pred = model.predict(image, verbose=0)[0]
            predictions.append(pred)
        
        # Ensemble vote (average probabilities)
        ensemble_pred = np.mean(predictions, axis=0)
        predicted_class_idx = np.argmax(ensemble_pred)
        confidence = ensemble_pred[predicted_class_idx]
        predicted_class = disease.output_classes[predicted_class_idx]
        
        # Classify severity
        severity = classify_severity(confidence, disease_id)
        
        # Clinical decision support
        differential_diagnoses = cds_engine.generate_differential_diagnosis({
            'age': request.form.get('patient_age'),
            'sex': request.form.get('patient_sex'),
            'medical_history': request.form.get('medical_history', '').split(',')
        }, {'findings': predicted_class, 'confidence': confidence})
        
        # Urgency assessment
        urgency = cds_engine.assess_clinical_urgency({
            'finding': predicted_class,
            'confidence': confidence,
            'disease': disease_id
        })
        
        # Follow-up recommendations
        followup = disease_registry.get_recommended_follow_up(disease_id, severity)
        
        # Prepare response
        response = {
            'prediction': {
                'disease_id': disease_id,
                'disease_name': disease.name,
                'predicted_class': predicted_class,
                'confidence': float(confidence),
                'confidence_threshold_met': confidence >= disease.confidence_threshold,
                'severity': severity.name,
                'requires_specialist': disease.requires_specialist
            },
            'differential_diagnoses': differential_diagnoses,
            'urgency': urgency,
            'follow_up_recommendation': followup,
            'clinical_notes': f'Patient shows {severity.name} findings. Confidence: {confidence:.2%}',
            'timestamp': datetime.utcnow().isoformat(),
            'rate_limit_remaining': remaining,
            'all_class_probabilities': {
                disease.output_classes[i]: float(ensemble_pred[i])
                for i in range(len(disease.output_classes))
            }
        }
        
        # Log audit trail
        audit_logger.log_prediction(
            user_id=request.headers.get('X-User-ID', 'anonymous'),
            patient_id=patient_id,
            disease_id=disease_id,
            predicted_class=predicted_class,
            confidence=confidence,
            severity=severity.name,
            ip_address=get_client_ip()
        )
        
        # Encrypt PHI if patient_id provided
        if patient_id:
            response['patient_id_encrypted'] = hipaa_manager.encrypt_pii(patient_id.encode())
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return {'error': f'Prediction failed: {str(e)}'}, 500

# =====================================================
# API ENDPOINTS - CLINICAL SUPPORT
# =====================================================

@app.route('/api/v2/followup-recommendations', methods=['POST'])
def get_followup():
    """Get follow-up recommendations"""
    allowed, remaining = check_rate_limit()
    if not allowed:
        return {'error': 'Rate limit exceeded'}, 429
    
    data = request.json
    disease_id = data.get('disease_id')
    severity = data.get('severity')
    
    if not disease_id or not severity:
        return {'error': 'disease_id and severity required'}, 400
    
    severity_enum = SeverityLevel[severity]
    followup = disease_registry.get_recommended_follow_up(disease_id, severity_enum)
    
    response = {
        'disease_id': disease_id,
        'severity': severity,
        'followup': followup,
        'rate_limit_remaining': remaining
    }
    
    return jsonify(response), 200

@app.route('/api/v2/differential-diagnosis', methods=['POST'])
def get_differentials():
    """Get differential diagnoses"""
    allowed, remaining = check_rate_limit()
    if not allowed:
        return {'error': 'Rate limit exceeded'}, 429
    
    data = request.json
    patient_data = data.get('patient_data')
    clinical_findings = data.get('clinical_findings')
    
    differentials = cds_engine.generate_differential_diagnosis(
        patient_data,
        clinical_findings
    )
    
    response = {
        'differentials': differentials,
        'rate_limit_remaining': remaining
    }
    
    return jsonify(response), 200

# =====================================================
# API ENDPOINTS - HIPAA COMPLIANCE
# =====================================================

@app.route('/api/v2/audit-logs', methods=['GET'])
def get_audit_logs():
    """Get audit logs (admin only)"""
    allowed, remaining = check_rate_limit()
    if not allowed:
        return {'error': 'Rate limit exceeded'}, 429
    
    user_role = request.headers.get('X-User-Role', 'user')
    if user_role != 'admin':
        return {'error': 'Admin access required'}, 403
    
    logs = audit_logger.get_logs(limit=100)
    
    response = {
        'total_logs': len(logs),
        'logs': logs,
        'rate_limit_remaining': remaining
    }
    
    return jsonify(response), 200

# =====================================================
# HEALTH CHECK
# =====================================================

@app.route('/api/v2/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'diseases_supported': len(disease_registry.diseases),
        'modalities_supported': len(ModalityHandler.MODALITY_SPECS),
        'timestamp': datetime.utcnow().isoformat()
    }), 200

# =====================================================
# ERROR HANDLERS
# =====================================================

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File too large (max 16MB)'}), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

# =====================================================
# MAIN
# =====================================================

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║  Multi-Disease Medical AI Platform                   ║
    ║  Government-Grade Healthcare System                   ║
    ╚═══════════════════════════════════════════════════════╝
    
    📊 Diseases Supported: {}
    📸 Modalities Supported: {}
    🔒 HIPAA Compliance: Enabled
    📋 Audit Logging: Enabled
    
    Starting server on http://127.0.0.1:5000
    """.format(
        len(disease_registry.diseases),
        len(ModalityHandler.MODALITY_SPECS)
    ))
    
    app.run(debug=True, port=5000)
