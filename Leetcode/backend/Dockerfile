FROM python:3.10

WORKDIR /app

# Copy only requirements to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

EXPOSE 5000

# Initialize DB and start app when container runs (if needed)
CMD ["sh", "-c", "python init_db.py && python app.py"]
