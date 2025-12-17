#!/usr/bin/env python3
"""
Startup script for the News Recommendation System backend
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        sys.exit(1)
    logger.info(f"Python version: {sys.version}")

def install_requirements():
    """Install required packages"""
    try:
        logger.info("Installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        logger.info("Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install requirements: {e}")
        sys.exit(1)

def check_environment():
    """Check environment variables"""
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("Please set these variables in your .env file")
        sys.exit(1)
    
    logger.info("Environment variables check passed")

def copy_model_files():
    """Copy ML model files to backend directory"""
    model_files = ["mtl_model.py", "mtl_model.pt", "X_inputs.pkl", "y_click_labels.pkl", "y_relevance_labels.pkl"]
    
    for file in model_files:
        if os.path.exists(file):
            # Copy to backend directory if it doesn't exist there
            backend_path = os.path.join("backend", file)
            if not os.path.exists(backend_path):
                import shutil
                shutil.copy2(file, backend_path)
                logger.info(f"Copied {file} to backend directory")
        else:
            logger.warning(f"Model file {file} not found in current directory")

def start_server():
    """Start the FastAPI server"""
    try:
        logger.info("Starting News Recommendation System backend...")
        logger.info("Server will be available at: https://vnls-press-backend.onrender.com")
        logger.info("API documentation: https://vnls-press-backend.onrender.com/docs")
        
        # Change to backend directory
        os.chdir("backend")
        
        # Start uvicorn server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

def main():
    """Main function"""
    logger.info("🚀 Starting News Recommendation System Backend")
    
    # Check Python version
    check_python_version()
    
    # Install requirements
    install_requirements()
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check environment
    check_environment()
    
    # Copy model files
    copy_model_files()
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()