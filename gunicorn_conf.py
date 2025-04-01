# Gunicorn configuration file
import multiprocessing

# Number of worker processes
workers = multiprocessing.cpu_count() * 2 + 1

# Socket to bind
bind = "0.0.0.0:$PORT"  # Render sets the PORT environment variable

# Worker timeout in seconds
timeout = 120

# Log level
loglevel = 'info'

# Access log format
accesslog = '-'  # stdout
errorlog = '-'   # stderr

# Enable threading for handling concurrent requests
threads = 2

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 50

# Process name
proc_name = 'gunicorn_heartdisease'
