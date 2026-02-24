FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy main.py to root
COPY main.py .

# Create the schema folder and copy the file into it
# This ensures "from schema.schema import..." still works!
COPY schema/schema.py ./schema/

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]