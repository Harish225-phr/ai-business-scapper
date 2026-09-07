import threading

# In-memory storage to prevent any disk writing
_memory_store = {}
_store_lock = threading.Lock()

def save_job_progress(job_id, data):
    with _store_lock:
        if job_id not in _memory_store:
            _memory_store[job_id] = {}
        _memory_store[job_id].update(data)

def load_job_progress(job_id):
    with _store_lock:
        return _memory_store.get(job_id, None)

def save_job_results(job_id, results):
    with _store_lock:
        if job_id not in _memory_store:
            _memory_store[job_id] = {}
        _memory_store[job_id]['results'] = results

def get_job_results(job_id):
    with _store_lock:
        return _memory_store.get(job_id, {}).get('results', [])
