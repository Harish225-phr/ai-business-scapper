import os

def get_env_bool(key, default):
    val = os.environ.get(key)
    if val is None:
        return default
    return val.lower() in ('true', '1', 'yes')

def get_env_int(key, default):
    val = os.environ.get(key)
    if val is None:
        return default
    try:
        return int(val)
    except ValueError:
        return default

def get_env_float(key, default):
    val = os.environ.get(key)
    if val is None:
        return default
    try:
        return float(val)
    except ValueError:
        return default

class Config:
    # Browser Mode
    BROWSER_HEADLESS = get_env_bool('BROWSER_HEADLESS', False)
    
    # Search Configuration
    MAX_RESULTS_PER_LOCATION = get_env_int('MAX_RESULTS_PER_LOCATION', 200)
    MAX_CONCURRENT_LOCATIONS = get_env_int('MAX_CONCURRENT_LOCATIONS', 1)
    
    # Scrolling Settings
    SCROLL_PAUSE = get_env_float('SCROLL_PAUSE', 1.5)
    MAX_NO_NEW_RESULTS = get_env_int('MAX_NO_NEW_RESULTS', 5)
    MAX_SCROLL_ATTEMPTS = get_env_int('MAX_SCROLL_ATTEMPTS', 100)
    
    # Storage
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    JOBS_DIR = os.path.join(DATA_DIR, 'jobs')

# Ensure directories exist
os.makedirs(Config.JOBS_DIR, exist_ok=True)
