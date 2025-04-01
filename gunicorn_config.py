import multiprocessing

# Gunicorn configuration file

# Bind address
bind = "0.0.0.0:8000"

# Worker configuration
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Process naming
proc_name = "heart_disease_app"

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# Prevent server fingerprinting
server_header = False
x_forwarded_for_header = True

# Security settings
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Detect file changes
reload = True

# Run in the background (daemon mode)
daemon = False
