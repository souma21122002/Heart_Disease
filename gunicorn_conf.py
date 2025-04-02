# Gunicorn configuration file
import multiprocessing

# Number of worker processes
workers = multiprocessing.cpu_count() * 2 + 1

# Socket to bind
bind = "0.0.0.0:10000"

# Worker class - using Uvicorn's worker
worker_class = "uvicorn.workers.UvicornWorker"

# Application object - point to the ASGI app
wsgi_app = "main:asgi_app"

# Timeout settings
timeout = 120

# Log settings
loglevel = "info"
accesslog = "-"
errorlog = "-"