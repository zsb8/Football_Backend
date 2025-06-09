import os
import sys

# Check if we're running in AWS Lambda environment
is_lambda = os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None

if not is_lambda:
    # Add the src directory to the Python path only in local development
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 