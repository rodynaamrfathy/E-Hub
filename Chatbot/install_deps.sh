#!/bin/bash
# Install missing email-validator dependency

echo "Installing email-validator..."
uv pip install email-validator

echo ""
echo "Testing import..."
python -c "import email_validator; print('✅ email-validator installed successfully')"

echo ""
echo "You can now run: python backend/main.py"
