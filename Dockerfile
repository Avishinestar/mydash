FROM python:3.10-slim

# Install system dependencies needed for compiling packages and network fetching
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up user 1000 required by Hugging Face Spaces security
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

WORKDIR $HOME/app

# Copy requirements and install Python dependencies
COPY --chown=user requirements.txt $HOME/app/
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy all project code and data files
COPY --chown=user . $HOME/app

# Hugging Face Spaces listens on port 7860
EXPOSE 7860

# Run the 10-module pro dashboard
CMD ["streamlit", "run", "pro_dashboard.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=false", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
