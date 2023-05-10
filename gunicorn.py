"""gunicorn WSGI server configuration."""
from multiprocessing import cpu_count
from os import environ


def max_workers():
    return cpu_count()


bind = '0.0.0.0:' + environ.get('PORT', '8000')
max_requests = 1
workers = max_workers()
threads = max_workers() * 2

# Max parallel requests per worker
worker_connections = 1000
