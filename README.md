# Movie Genre Predictor

A web application that predicts movie genres from posters using a DenseNet169 model, deployed with Flask (backend) and React.js (frontend).

## Features
- Upload a movie poster and get the top-3 predicted genres with probabilities.
- Built with TensorFlow, Flask, and React.js.
- Custom weighted binary cross-entropy loss for multi-label classification.

## Setup
### Backend
1. `cd backEnd`
2. Install dependencies: `pip install -r requirements.txt`
3. Download the model file [here](<link-to-your-model-on-drive>) and place it in `backEnd/`.
4. Run: `python app.py`

### Frontend
1. `cd frontend`
2. Install dependencies: `npm install`
3. Run: `npm start`

## Deployment
- Backend: Hosted on [Render](#) (replace with actual link)
- Frontend: Hosted on [Netlify](#) (replace with actual link)

## Demo
Try it live at [your-app-url](#)!