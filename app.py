import os
import logging
from flask import Flask, render_template, request, jsonify
from transformers import pipeline

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variable for QA pipeline
qa_pipeline = None

def load_model():
    """Load the fine-tuned BERT model using HuggingFace pipeline"""
    global qa_pipeline
    
    try:
        model_path = "./my_awesome_qa_model"
        
        # Check if model directory exists
        if not os.path.exists(model_path):
            logger.error(f"Model directory not found: {model_path}")
            print(f"\n❌ ERROR: Model directory not found at: {os.path.abspath(model_path)}")
            print("Please ensure 'my_awesome_qa_model' folder exists with these files:")
            print("  - config.json")
            print("  - model.safetensors or pytorch_model.bin")
            print("  - tokenizer.json")
            print("  - tokenizer_config.json")
            print("  - vocab.txt")
            return False
        
        print("Loading BERT model...")
        logger.info("Loading QA pipeline...")
        
        # Use device=-1 for CPU, 0 for GPU
        qa_pipeline = pipeline(
            "question-answering",
            model=model_path,
            tokenizer=model_path,
            device=-1  # Use CPU
        )
        
        print("✅ Model loaded successfully!")
        logger.info("Model loaded successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        print(f"❌ Error loading model: {str(e)}")
        return False

@app.route('/')
def home():
    """Render the main page"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """API endpoint for question answering"""
    try:
        # Get JSON data
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        context = data.get('context', '').strip()
        question = data.get('question', '').strip()
        
        if not context:
            return jsonify({"error": "Context is required"}), 400
        if not question:
            return jsonify({"error": "Question is required"}), 400
        
        # Load model if not loaded
        if qa_pipeline is None:
            if not load_model():
                return jsonify({"error": "Failed to load model"}), 500
        
        # Get prediction
        try:
            result = qa_pipeline(question=question, context=context)
            answer = result['answer'].strip()
            confidence = round(result['score'] * 100, 2)
            
            if not answer:
                answer = "Sorry, I couldn't find an answer in the given context."
                confidence = 0
                
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            answer = f"Error during prediction: {str(e)}"
            confidence = 0
        
        # Return response
        return jsonify({
            "answer": answer,
            "confidence": confidence,
            "status": "success",
            "context_length": len(context),
            "question_length": len(question)
        })
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    if qa_pipeline is not None:
        return jsonify({
            "status": "healthy",
            "model_loaded": True,
            "service": "BERT QA System"
        })
    return jsonify({
        "status": "starting",
        "model_loaded": False,
        "service": "BERT QA System"
    })

@app.route('/example')
def example():
    """Example data endpoint - returns SIMPLE structure"""
    example_context = """The Mars 2020 mission is part of NASA's Mars Exploration Program. 
    The Perseverance rover landed on Mars on February 18, 2021, in Jezero Crater. 
    Its mission is to search for signs of ancient life and collect rock and soil samples 
    for possible return to Earth. The rover carries the Ingenuity helicopter, 
    which became the first aircraft to make a powered, controlled flight on another planet."""
    
    example_question = "When did Perseverance land on Mars?"
    
    # Return SIMPLE structure that matches what JavaScript expects
    return jsonify({
        "example_context": example_context,
        "example_question": example_question
    })

if __name__ == '__main__':
    print("=" * 60)
    print("           BERT Question Answering System")
    print("=" * 60)
    
    # Try to load model at startup
    load_model()
    
    print("\n🌐 Starting Flask server...")
    print("📡 Open your browser and go to: http://localhost:5000")
    print("📋 Test endpoint: http://localhost:5000/health")
    print("📚 Example data: http://localhost:5000/example")
    print("=" * 60)
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)