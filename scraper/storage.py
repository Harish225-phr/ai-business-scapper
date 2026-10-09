import json
import os
from .config import Config

def _get_job_file(job_id):
    return os.path.join(Config.JOBS_DIR, f"{job_id}.json")

def save_job_progress(job_id, data):
    job_file = _get_job_file(job_id)
    # Read existing data to not overwrite results when saving progress
    current_data = {}
    if os.path.exists(job_file):
        try:
            with open(job_file, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
        except:
            pass
            
    current_data.update(data)
    
    with open(job_file, 'w', encoding='utf-8') as f:
        json.dump(current_data, f)

def load_job_progress(job_id):
    job_file = _get_job_file(job_id)
    if os.path.exists(job_file):
        try:
            with open(job_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return None

def save_job_results(job_id, results):
    job_file = _get_job_file(job_id)
    current_data = {}
    if os.path.exists(job_file):
        try:
            with open(job_file, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
        except:
            pass
            
    current_data['results'] = results
    
    with open(job_file, 'w', encoding='utf-8') as f:
        json.dump(current_data, f)

def get_job_results(job_id):
    data = load_job_progress(job_id)
    if data and 'results' in data:
        return data['results']
    return []
