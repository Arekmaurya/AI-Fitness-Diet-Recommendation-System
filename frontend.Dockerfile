FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your frontend code into the container
COPY frontend.py .

# Expose the port Streamlit runs on
EXPOSE 8501

# Command to run the frontend
CMD ["streamlit", "run", "frontend.py", "--server.port=8501", "--server.address=0.0.0.0"]