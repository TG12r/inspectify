import multiprocessing
import os

# Binding
bind = "0.0.0.0:8000"
backlog = 2048

# Worker Processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 360
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process Naming
proc_name = "inspectify"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (configure if needed)
keyfile = None
certfile = None
ssl_version = None
cert_reqs = 0
ca_certs = None
ciphers = "TLSv1"

# Server hooks
def post_fork(server, worker):
    pass

def pre_fork(server, worker):
    pass

def pre_exec(server):
    pass

def when_ready(server):
    pass

def on_exit(server):
    pass

def child_exit(server, worker):
    pass
