import os
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
from PIL import Image
import cv2
from tensorflow.keras.models import load_model
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from tensorflow.keras.utils import normalize


app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


model = load_model('BrainTumor10EpochsCategorical.h5')
print('Model loaded. Check http://127.0.0.1:5000/')


def get_className(classNo):
	if classNo==0:
		return "No Brain Tumor"
	elif classNo==1:
		return "Yes Brain Tumor"


def getResult(img):
    image=cv2.imread(img)
    image = Image.fromarray(image, 'RGB')
    image = image.resize((64, 64))
    image=np.array(image)
    input_img = np.expand_dims(image, axis=0)
    input_img=normalize(input_img, axis=1)
    prediction = model.predict(input_img, verbose=0)
    confidence = float(np.max(prediction) * 100)
    result_class = np.argmax(prediction)
    return result_class, confidence, prediction


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files['file']

        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)
        result_class, confidence, prediction = getResult(file_path)
        result_text = get_className(result_class)
        
        response_data = {
            'prediction': result_text,
            'confidence': f'{confidence:.2f}%',
            'class': int(result_class),
            'tumor_probability': f'{float(prediction[0][1])*100:.2f}%',
            'no_tumor_probability': f'{float(prediction[0][0])*100:.2f}%'
        }
        return jsonify(response_data)
    return None


if __name__ == '__main__':
    app.run(debug=True)