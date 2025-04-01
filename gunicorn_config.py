import multiprocessing
import os

# Gunicorn configuration file

# Bind to the port provided by Render
port = int(os.environ.get("PORT", 8000))
bind = f"0.0.0.0:{port}"

# Worker configuration - use a reasonable number based on available CPUs
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 60  # Increased timeout for better handling of long requests
keepalive = 2

# Log configuration
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"

# Application configuration
wsgi_app = "wsgi:app"  # This references the 'app' variable in your wsgi.py file
