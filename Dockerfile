# Use Python 3.9 AWS Lambda base image
FROM public.ecr.aws/lambda/python:3.9

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements.txt (Python dependencies configuration file)
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Set Lambda function entry point
# Assuming your main function is the handler function in handler.py
CMD ["handler.handler"]