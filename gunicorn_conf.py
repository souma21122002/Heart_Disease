# Gunicorn configuration file
import multiprocessing

# Number of worker processes
workers = multiprocessing.cpu_count() * 2 + 1

# Socket to bind
worker_class = "uvicorn.workers.UvicornWorker"  # Use Uvicorn worker for ASGI apps