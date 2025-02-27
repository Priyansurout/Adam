from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os
import time

app = Flask(__name__, static_folder='frontend/build')
CORS(app)


# Define the custom loss function from your training code
def create_weighted_loss():
    def weighted_binary_crossentropy(y_true, y_pred):
        genre_counts = tf.reduce_sum(y_true, axis=0)
        weights = 1.0 / (genre_counts + 1e-5)
        weights = weights / tf.reduce_sum(weights)
        bce = tf.keras.losses.binary_crossentropy(y_true, y_pred)
        weighted_bce = bce * tf.reduce_sum(y_true * weights, axis=1)
        return tf.reduce_mean(weighted_bce)
    return weighted_binary_crossentropy

# Download model from Google Drive
MODEL_URL = "https://drive.google.com/uc?id=1zSIkdkh2nwTl_dRFzfuaMHPNZ4PSaaJN"  # Replace with your Google Drive file ID 
MODEL_PATH = "movie_genre_model_with_generator_DenseNet169.h5"

if not os.path.exists(MODEL_PATH):
    print("Downloading model from Google Drive...")
    gdown.download(MODEL_URL, MODEL_PATH, quiet=False)

try:
    model = tf.keras.models.load_model(
        MODEL_PATH,
        custom_objects={'weighted_binary_crossentropy': create_weighted_loss()}
    )
except Exception as e:
    print(f"Error loading model: {e}")
    raise

genres = [
    'Action', 'Adventure', 'Animation', 'Biography', 'Comedy',
    'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy',
    'History', 'Horror', 'Music', 'Musical', 'Mystery',
    'N/A', 'News', 'Reality-TV', 'Romance', 'Sci-Fi',
    'Short', 'Sport', 'Thriller', 'War', 'Western'
]

# Store recent predictions for demo purposes
recent_predictions = []
MAX_RECENT = 5

def preprocess_image(image):
    """Preprocess the image for prediction"""
    # Handle different image formats (RGB vs RGBA)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    image = image.resize((350, 350))  # Resize to match model input size
    image = np.array(image) / 255.0  # Normalize pixel values
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    return image

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['image']
    
    try:
        # Open and preprocess the image
        image = Image.open(io.BytesIO(file.read()))
        processed_image = preprocess_image(image)

        # Add artificial delay for demo effect (can remove in production)
        time.sleep(0.5)
        
        # Make prediction
        predictions = model.predict(processed_image)[0]
        
        # Get all genre probabilities for visualization
        all_genres_probs = [(genre, float(prob)) for genre, prob in zip(genres, predictions)]
        all_genres_probs.sort(key=lambda x: x[1], reverse=True)
        
        # Get top 3 predictions
        top_3_indices = np.argsort(predictions)[-3:][::-1]
        top_3_genres = [genres[i] for i in top_3_indices]
        top_3_probs = [float(predictions[i]) for i in top_3_indices]

        result = {
            "top_3_genres": top_3_genres,
            "probabilities": top_3_probs,
            "all_predictions": dict(all_genres_probs)
        }
        
        # Store this prediction (for recent predictions feature)
        global recent_predictions
        recent_predictions.insert(0, result)
        recent_predictions = recent_predictions[:MAX_RECENT]
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error processing prediction: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/recent', methods=['GET'])
def get_recent():
    """Return recent predictions for demo purposes"""
    return jsonify({"recent": recent_predictions})

# Serve React app in production
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)