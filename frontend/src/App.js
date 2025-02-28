import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [file, setFile] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [allGenrePredictions, setAllGenrePredictions] = useState(null);

  // Handle file drop
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type.includes('image')) {
        setSelectedImage(URL.createObjectURL(droppedFile));
        setFile(droppedFile);
        setPrediction(null);
        setError(null);
      } else {
        setError("Please drop an image file");
      }
    }
  };

  // Handle image selection
  const handleImageChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setSelectedImage(URL.createObjectURL(selectedFile));
      setFile(selectedFile);
      setPrediction(null);
      setError(null);
    }
  };

  // Handle image upload and prediction
  const handleUpload = async () => {
    if (!file) {
      setError("Please select an image!");
      return;
    }

    const formData = new FormData();
    formData.append('image', file);

    try {
      setIsLoading(true);
      setError(null);
      const response = await axios.post('https://priyansu19-movie-genre-predictor.hf.space/predict', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setPrediction(response.data);
      
      // Store all genre predictions for visualization (if your backend supports it)
      if (response.data.all_predictions) {
        setAllGenrePredictions(response.data.all_predictions);
      }
    } catch (error) {
      console.error("Error during prediction:", error);
      setError("Failed to make prediction. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1>🎬 Movie Poster Genre Predictor</h1>
        <p className="subtitle">
          Upload a movie poster and our AI will predict its genre!
        </p>
      </header>

      <div 
        className={`upload-section ${dragActive ? "drag-active" : ""}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="upload-box">
          {!selectedImage ? (
            <>
              <div className="upload-icon">📁</div>
              <p>Drag & drop an image here or</p>
              <label className="file-input-label">
                <input 
                  type="file" 
                  accept="image/*" 
                  onChange={handleImageChange} 
                  className="file-input" 
                />
                Browse Files
              </label>
            </>
          ) : (
            <div className="image-preview-container">
              <img 
                src={selectedImage} 
                alt="Selected" 
                className={`image-preview ${isLoading ? 'scanning' : ''}`} 
              />
              <div className="preview-controls">
                <label className="file-input-label small">
                  <input 
                    type="file" 
                    accept="image/*" 
                    onChange={handleImageChange} 
                    className="file-input" 
                  />
                  Change
                </label>
              </div>
            </div>
          )}
        </div>
      </div>

      {error && <p className="error-message">{error}</p>}

      <button 
        onClick={handleUpload} 
        className="upload-btn" 
        disabled={isLoading || !selectedImage}
      >
        {isLoading ? "Analyzing..." : "Predict Genre"}
      </button>

      {isLoading && (
        <div className="loading-container">
          <div className="loader"></div>
          <p className="loading-text">AI is analyzing the poster...</p>
        </div>
      )}

      {prediction && prediction.top_3_genres && (
        <div className="result-section">
          <h2>Predicted Genres</h2>
          <div className="results-container">
            {prediction.top_3_genres.map((genre, index) => (
              <div key={index} className="result-card">
                <h3 className="genre-name">{genre}</h3>
                <div className="probability-bar-container">
                  <div 
                    className="probability-bar" 
                    style={{width: `${prediction.probabilities[index] * 100}%`}}
                  ></div>
                </div>
                <p className="genre-probability">
                  {(prediction.probabilities[index] * 100).toFixed(1)}%
                </p>
              </div>
            ))}
          </div>
          
          {allGenrePredictions && (
            <div className="all-genres-section">
              <h3>All Genre Probabilities</h3>
              <div className="genre-grid">
                {Object.entries(allGenrePredictions)
                  .filter(([genre, _]) => genre !== 'N/A')
                  .map(([genre, probability]) => (
                    <div key={genre} className="genre-item">
                      <span className="genre-label">{genre}</span>
                      <div className="mini-bar-container">
                        <div 
                          className="mini-bar" 
                          style={{width: `${probability * 100}%`}}
                        ></div>
                      </div>
                      <span className="mini-percentage">
                        {(probability * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))
                }
              </div>
            </div>
          )}
        </div>
      )}
      
      <footer>
        <p>Built with TensorFlow, DenseNet169, React, and Flask</p>
        <p className="footer-note">A project for internship application</p>
      </footer>
    </div>
  );
}

export default App;