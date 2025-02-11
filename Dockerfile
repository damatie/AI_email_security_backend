# Dockerfile
# Use the official Python image
FROM python:3.10

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# ✅ Upgrade pip first (to avoid the upgrade notice)
RUN python -m pip install --upgrade pip

# ✅ Copy only requirements.txt first (leveraging Docker cache)
COPY requirements.txt .

# ✅ Install dependencies before copying the full application
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copy the rest of the application files
COPY . .

# Expose FastAPI default port
EXPOSE 8000

# ✅ Run FastAPI in development mode with autoreload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

