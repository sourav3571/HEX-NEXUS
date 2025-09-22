echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
echo "Installing required Python packages..."
pip install -r requirements.txt