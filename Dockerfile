# Use official Python image
FROM python:3.10

# Create a user to match HF's env
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:${PATH}"

# Set the working directory
WORKDIR /app

# Copy requirements and install
# We use --user to install in the user's home directory
COPY --chown=user ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --user --upgrade -r /app/requirements.txt

# Copy all files 
COPY --chown=user . .

# Expose the port
EXPOSE 7860

# Start uvicorn
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]