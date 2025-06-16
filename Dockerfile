# 1. Base Image: Use a specific and recent version of Python for reproducibility.
FROM python:3.10-slim-buster

# 2. Environment Variables: For better logging and to avoid .pyc files.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set Working Directory
WORKDIR /app

# 4. System Dependencies: Install essential build tools needed by some Python packages.
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
  && rm -rf /var/lib/apt/lists/*

# 5. Caching Optimization: Copy only the requirements file first.
# This leverages Docker's layer caching. The dependencies will only be re-installed
# if the requirements.txt file changes, making subsequent builds much faster.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Security: Create a non-root user to run the application.
# Running as a non-root user is a critical security best practice.
RUN addgroup --system app && adduser --system --group app

# 7. Copy Application Code: Now copy the rest of your application source code.
COPY . .

# 8. Ownership: Change the ownership of the application directory to the new user.
RUN chown -R app:app /app

# 9. Switch User: Switch to the non-root user for running the app.
USER app

# 10. Expose Port: Inform Docker that the container listens on port 8000.
EXPOSE 8000

# 11. Run Command: The command to start the Uvicorn server for FastAPI.
# This will be the default command for the container.
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]