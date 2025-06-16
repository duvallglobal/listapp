
#!/bin/bash

echo "Starting Price Intelligence Backend..."

# Navigate to API directory
cd api

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Start the FastAPI server
echo "Starting FastAPI server..."
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
