"""
Ensemble Model Module
Combines multiple model architectures for improved accuracy and robustness
"""

import numpy as np
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, BatchNormalization, Dropout, Flatten, Dense, Input, concatenate
from tensorflow.keras.applications import ResNet50, VGG16, EfficientNetB0
from tensorflow.keras.preprocessing import image as keras_image

class EnsembleModel:
    """Ensemble of multiple models for voting/averaging predictions"""
    
    def __init__(self):
        self.models = {}
        self.weights = {}
    
    def add_model(self, name, model_path, weight=1.0):
        """
        Add a model to the ensemble
        Args:
            name: Model name/identifier
            model_path: Path to trained model
            weight: Weight for this model in voting
        """
        from tensorflow.keras.models import load_model
        try:
            model = load_model(model_path)
            self.models[name] = model
            self.weights[name] = weight
            return {"success": True, "message": f"Model {name} added"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def predict_ensemble(self, image_array, method='voting'):
        """
        Get prediction from ensemble
        Args:
            image_array: Preprocessed image
            method: 'voting' (hard voting), 'averaging' (soft voting)
        Returns:
            prediction: Ensemble prediction
            confidence: Confidence score
        """
        if len(self.models) == 0:
            return {"error": "No models in ensemble"}
        
        predictions = []
        confidences = []
        
        # Get predictions from all models
        for name, model in self.models.items():
            try:
                pred = model.predict(image_array, verbose=0)
                predictions.append(pred[0])
                confidences.append(self.weights.get(name, 1.0))
            except Exception as e:
                print(f"Error in model {name}: {e}")
                continue
        
        if len(predictions) == 0:
            return {"error": "No valid predictions from ensemble"}
        
        # Aggregate predictions
        if method == 'averaging':
            # Weighted average
            weighted_sum = np.average(predictions, axis=0, weights=confidences)
            ensemble_pred = weighted_sum
        else:  # voting
            # Hard voting
            class_votes = np.zeros(predictions[0].shape)
            for i, pred in enumerate(predictions):
                if pred[1] > pred[0]:  # Tumor detected
                    class_votes[1] += confidences[i]
                else:
                    class_votes[0] += confidences[i]
            ensemble_pred = class_votes / np.sum(confidences)
        
        # Get final class and confidence
        final_class = np.argmax(ensemble_pred)
        final_confidence = ensemble_pred[final_class] * 100
        
        return {
            "class": int(final_class),
            "confidence": f"{final_confidence:.2f}%",
            "tumor_prob": f"{ensemble_pred[1]*100:.2f}%",
            "normal_prob": f"{ensemble_pred[0]*100:.2f}%",
            "num_models": len(self.models)
        }

class TransferLearningModel:
    """Transfer learning models using pre-trained architectures"""
    
    @staticmethod
    def create_resnet_model(input_shape=(64, 64, 3), num_classes=2):
        """
        Create ResNet50 transfer learning model
        Args:
            input_shape: Input image shape
            num_classes: Number of output classes
        Returns:
            model: Compiled model
        """
        # Load pre-trained ResNet50
        base_model = ResNet50(
            weights='imagenet',
            include_top=False,
            input_shape=input_shape
        )
        
        # Freeze base model layers
        for layer in base_model.layers:
            layer.trainable = False
        
        # Add custom top layers
        model = Sequential([
            Input(shape=input_shape),
            base_model,
            Flatten(),
            Dense(512, activation='relu'),
            Dropout(0.5),
            Dense(256, activation='relu'),
            Dropout(0.3),
            Dense(num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    @staticmethod
    def create_vgg_model(input_shape=(64, 64, 3), num_classes=2):
        """
        Create VGG16 transfer learning model
        Args:
            input_shape: Input image shape
            num_classes: Number of output classes
        Returns:
            model: Compiled model
        """
        # Load pre-trained VGG16
        base_model = VGG16(
            weights='imagenet',
            include_top=False,
            input_shape=input_shape
        )
        
        # Freeze base model layers
        for layer in base_model.layers:
            layer.trainable = False
        
        # Add custom top layers
        model = Sequential([
            Input(shape=input_shape),
            base_model,
            Flatten(),
            Dense(512, activation='relu'),
            BatchNormalization(),
            Dropout(0.5),
            Dense(256, activation='relu'),
            BatchNormalization(),
            Dropout(0.3),
            Dense(num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    @staticmethod
    def create_efficientnet_model(input_shape=(64, 64, 3), num_classes=2):
        """
        Create EfficientNetB0 transfer learning model
        Args:
            input_shape: Input image shape
            num_classes: Number of output classes
        Returns:
            model: Compiled model
        """
        # Load pre-trained EfficientNetB0
        base_model = EfficientNetB0(
            weights='imagenet',
            include_top=False,
            input_shape=input_shape
        )
        
        # Freeze base model layers
        for layer in base_model.layers:
            layer.trainable = False
        
        # Add custom top layers
        model = Sequential([
            Input(shape=input_shape),
            base_model,
            Flatten(),
            Dense(256, activation='relu'),
            BatchNormalization(),
            Dropout(0.4),
            Dense(num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model

class ModelMetrics:
    """Calculate detailed model performance metrics"""
    
    @staticmethod
    def calculate_confidence_intervals(predictions, confidence_level=0.95):
        """
        Calculate confidence intervals for predictions
        Args:
            predictions: Model predictions
            confidence_level: Confidence level (0-1)
        Returns:
            ci: Confidence intervals
        """
        from scipy import stats
        
        # Convert to probabilities
        probs = predictions[:, 1]  # Tumor probability
        
        # Calculate mean and SEM
        mean = np.mean(probs)
        sem = stats.sem(probs)
        ci = sem * stats.t.ppf((1 + confidence_level) / 2., len(probs) - 1)
        
        return {
            "mean": mean,
            "ci_lower": mean - ci,
            "ci_upper": mean + ci,
            "confidence_level": confidence_level
        }
    
    @staticmethod
    def get_prediction_uncertainty(prediction_scores):
        """
        Quantify uncertainty in predictions
        Args:
            prediction_scores: Raw model scores
        Returns:
            uncertainty: Uncertainty metrics
        """
        tumor_score = prediction_scores[1]
        normal_score = prediction_scores[0]
        
        # Calculate prediction entropy (uncertainty)
        probs = np.array([normal_score, tumor_score]) / (normal_score + tumor_score)
        entropy = -np.sum(probs * np.log(probs + 1e-10))
        
        # Margin (confidence in prediction)
        margin = abs(tumor_score - normal_score)
        
        return {
            "entropy": float(entropy),
            "margin": float(margin),
            "high_confidence": entropy < 0.3 and margin > 0.4,
            "uncertain": entropy > 0.6 or margin < 0.2
        }

print("Ensemble model module loaded successfully")
