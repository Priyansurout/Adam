from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os
import gdown

app = Flask(__name__)
CORS(app)

def create_weighted_loss():
    def weighted_binary_crossentropy(y_true, y_pred):
        genre_counts = tf.reduce_sum(y_true, axis=0)
        weights = 1.0 / (genre_counts + 1e-5)
        weights = weights / tf.reduce_sum(weights)
        bce = tf.keras.losses.binary_crossentropy(y_true, y_pred)
        weighted_bce = bce * tf.reduce_sum(y_true * weights, axis=1)
        return tf.reduce_mean(weighted_bce)
    return weighted_binary_crossentropy

# MODEL_URL = "https://drive.google.com/uc?id=1zSIkdkh2nwTl_dRFzfuaMHPNZ4PSaaJN"
# MODEL_PATH = "movie_genre_model_with_generator_DenseNet169.h5"

# if not os.path.exists(MODEL_PATH):
#     print("Downloading model from Google Drive...")
#     gdown.download(MODEL_URL, MODEL_PATH, quiet=False)

# try:
#     model = tf.keras.models.load_model(
#         MODEL_PATH,
#         custom_objects={'weighted_binary_crossentropy': create_weighted_loss()}
#     )
# except Exception as e:
#     print(f"Error loading model: {e}")
#     raise
model = tf.keras.models.load_model("movie_genre_model_with_generator_DenseNet169.h5")

genres = [
    'Action', 'Adventure', 'Animation', 'Biography', 'Comedy',
    'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy',
    'History', 'Horror', 'Music', 'Musical', 'Mystery',
    'N/A', 'News', 'Reality-TV', 'Romance', 'Sci-Fi',
    'Short', 'Sport', 'Thriller', 'War', 'Western'
]

def preprocess_image(image):
    try:
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image = image.resize((350, 350))
        image = np.array(image) / 255.0
        image = np.expand_dims(image, axis=0)
        return image
    except Exception as e:
        raise ValueError(f"Image preprocessing failed: {str(e)}")

@app.route('/')
def home():
    return jsonify({"message": "Movie Genre Predictor API is running"})

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    file = request.files['image']
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400
    if not file.content_type.startswith('image/'):
        return jsonify({"error": "Uploaded file is not an image"}), 400
    try:
        image = Image.open(io.BytesIO(file.read()))
        processed_image = preprocess_image(image)
        
        # First make predictions
        predictions = model.predict(processed_image)[0]
        
        # Then use the predictions for all_genres_probs
        all_genres_probs = [(genre, float(prob)) for genre, prob in zip(genres, predictions)]
        all_genres_probs.sort(key=lambda x: x[1], reverse=True)
        
        top_3_indices = np.argsort(predictions)[-3:][::-1]
        top_3_genres = [genres[i] for i in top_3_indices]
        top_3_probs = [float(predictions[i]) for i in top_3_indices]
        return jsonify({
            "top_3_genres": top_3_genres,
            "probabilities": top_3_probs,
            "all_predictions": dict(all_genres_probs),
            "message": "Prediction successful"
        })
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))  # Use 7860 for Spaces
    app.run(debug=False, host='0.0.0.0', port=port)