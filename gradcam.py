"""
Grad-CAM Heatmap Visualization Module
Generates visual explanations of CNN predictions using Gradient-weighted Class Activation Maps
"""

import numpy as np
import cv2
from tensorflow.keras.models import Model
import tensorflow as tf
from PIL import Image
import io
import base64

class GradCAM:
    """Gradient-weighted Class Activation Maps for model interpretability"""
    
    def __init__(self, model, layer_name):
        """
        Initialize Grad-CAM
        Args:
            model: Keras model
            layer_name: Name of the convolutional layer to visualize
        """
        self.model = model
        self.layer_name = layer_name
        
        # Create a model that returns layer outputs and model predictions
        self.grad_model = Model(
            [model.inputs],
            [model.get_layer(layer_name).output, model.output]
        )
    
    def generate_heatmap(self, img_array, pred_index=None):
        """
        Generate Grad-CAM heatmap
        Args:
            img_array: Input image array (1, height, width, channels)
            pred_index: Index of the predicted class
        Returns:
            heatmap: Normalized heatmap (0-255)
        """
        # Convert to tensor
        img_tensor = tf.convert_to_tensor(img_array, dtype=tf.float32)
        
        with tf.GradientTape() as tape:
            tape.watch(img_tensor)
            conv_outputs, predictions = self.grad_model(img_tensor)
            
            if pred_index is None:
                pred_index = tf.argmax(predictions[0])
            
            class_channel = predictions[:, pred_index]
        
        # Compute gradients
        grads = tape.gradient(class_channel, conv_outputs)
        
        # Pool the gradients spatially
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        
        # Multiply each filter in the feature map by "how important this filter is"
        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        
        # Normalize to 0-1
        heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
        
        return heatmap.numpy()
    
    def overlay_heatmap(self, original_img, heatmap, alpha=0.4):
        """
        Overlay heatmap on original image
        Args:
            original_img: Original image (PIL or numpy array)
            heatmap: Normalized heatmap (0-1)
            alpha: Transparency level
        Returns:
            combined: Image with heatmap overlay
        """
        # Convert PIL to numpy if needed
        if isinstance(original_img, Image.Image):
            original_img = np.array(original_img)
        
        # Resize heatmap to match image dimensions
        heatmap_resized = cv2.resize(heatmap, (original_img.shape[1], original_img.shape[0]))
        heatmap_resized = np.uint8(255 * heatmap_resized)
        
        # Apply colormap
        heatmap_colored = cv2.applyColorMap(heatmap_resized, cv2.COLORMAP_JET)
        
        # Convert BGR to RGB if needed
        if len(original_img.shape) == 3 and original_img.shape[2] == 3:
            # Ensure we have 3 channels
            if original_img.dtype != np.uint8:
                original_img = np.uint8(original_img * 255)
            
            # Convert grayscale to RGB if needed
            if len(original_img.shape) == 2:
                original_img = cv2.cvtColor(original_img, cv2.COLOR_GRAY2BGR)
            
            # Blend images
            combined = cv2.addWeighted(original_img, 1 - alpha, heatmap_colored, alpha, 0)
        else:
            combined = heatmap_colored
        
        return combined
    
    @staticmethod
    def image_to_base64(image):
        """Convert numpy image to base64 string for embedding in HTML"""
        # Convert to uint8 if needed
        if image.dtype != np.uint8:
            image = np.uint8(image)
        
        # Encode to PNG
        _, buffer = cv2.imencode('.png', image)
        img_b64 = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/png;base64,{img_b64}"

class AttentionVisualization:
    """Generate attention maps for different model layers"""
    
    def __init__(self, model):
        self.model = model
    
    def get_activation_maps(self, img_array, layer_index):
        """
        Get activation maps from intermediate layer
        Args:
            img_array: Input image
            layer_index: Index of layer to visualize
        Returns:
            activation: Activation maps
        """
        layer_model = Model(
            inputs=self.model.input,
            outputs=self.model.layers[layer_index].output
        )
        activations = layer_model.predict(img_array, verbose=0)
        return activations
    
    def visualize_filters(self, activations, max_filters=16):
        """
        Visualize activation maps as a grid
        Args:
            activations: Activation maps from network
            max_filters: Maximum number of filters to display
        Returns:
            grid_image: Grid visualization
        """
        # Normalize activations
        activations = np.maximum(activations, 0)
        activations = activations / (activations.max() + 1e-8)
        
        # Get dimensions
        n_filters = min(activations.shape[-1], max_filters)
        img_height = activations.shape[1]
        img_width = activations.shape[2]
        
        # Create grid
        grid_size = int(np.ceil(np.sqrt(n_filters)))
        grid = np.zeros((grid_size * img_height, grid_size * img_width))
        
        for i in range(n_filters):
            row = (i // grid_size) * img_height
            col = (i % grid_size) * img_width
            activation_map = activations[0, :, :, i]
            activation_map = np.uint8(255 * activation_map)
            grid[row:row+img_height, col:col+img_width] = activation_map
        
        return np.uint8(grid)

def generate_heatmap_report(model, image, layer_name="conv2d"):
    """
    Generate complete heatmap analysis report
    Args:
        model: Trained model
        image: Input image
        layer_name: Layer to analyze
    Returns:
        report: Dictionary with visualizations and explanations
    """
    try:
        # Initialize Grad-CAM
        grad_cam = GradCAM(model, layer_name)
        
        # Generate heatmap
        heatmap = grad_cam.generate_heatmap(image)
        
        # Overlay on original
        original_resized = cv2.resize(image[0], (image.shape[2], image.shape[1]))
        if len(original_resized.shape) == 2:
            original_resized = cv2.cvtColor(original_resized, cv2.COLOR_GRAY2BGR)
        
        combined = grad_cam.overlay_heatmap(original_resized, heatmap)
        
        # Convert to base64
        heatmap_b64 = GradCAM.image_to_base64(combined)
        
        return {
            "success": True,
            "heatmap_image": heatmap_b64,
            "explanation": "Red regions indicate areas the model considers as having tumor characteristics. Blue regions are normal."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "explanation": "Could not generate heatmap visualization"
        }

print("Grad-CAM module loaded successfully")
