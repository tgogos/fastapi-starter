FROM python:3.12-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the current directory contents (app code) into the container at /app
COPY ./app /code/app

# Expose the port that FastAPI will run on
EXPOSE 8000

# Define the environment variable for running in production mode
ENV PYTHONUNBUFFERED=1

CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
