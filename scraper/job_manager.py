import threading
import uuid
import time
from datetime import datetime
from .storage import save_job_progress, load_job_progress, save_job_results, get_job_results
from .browser import BrowserManager
from .maps_search import MapsScraper
from .deduplicator import remove_duplicates

jobs = {}

def start_job(keyword, locations, websites_only=False, headless=None):
    job_id = str(uuid.uuid4())
    
    initial_state = {
        "job_id": job_id,
        "status": "queued",
        "keyword": keyword,
        "locations": locations,
        "locations_total": len(locations),
        "locations_completed": 0,
        "current_location": None,
        "businesses_found": 0,
        "websites_found": 0,
        "websites_only": websites_only,
        "message": "Initializing...",
        "start_time": datetime.now().isoformat(),
        "end_time": None
    }
    
    jobs[job_id] = initial_state
    save_job_progress(job_id, initial_state)
    
    thread = threading.Thread(target=_run_job, args=(job_id, keyword, locations, websites_only, headless))
    thread.daemon = True
    thread.start()
    
    return job_id

def _run_job(job_id, keyword, locations, websites_only, headless):
    state = jobs[job_id]
    state["status"] = "running"
    save_job_progress(job_id, state)
    
    all_businesses = []
    
    try:
        with BrowserManager() as bm:
            bm.start(headless=headless)
            page = bm.get_new_page()
            scraper = MapsScraper(page)
            
            for location in locations:
                state["current_location"] = location
                state["message"] = f"Searching {location}..."
                save_job_progress(job_id, state)
                
                # Callback to update progress dynamically
                def progress_cb(msg, current_businesses=None):
                    state["message"] = msg
                    if current_businesses is not None:
                        temp_total = len(all_businesses) + len(current_businesses)
                        temp_websites = sum(1 for b in all_businesses if b.get('website') and b.get('website') != "N/A")
                        temp_websites += sum(1 for b in current_businesses if b.get('website') and b.get('website') != "N/A")
                        
                        state["businesses_found"] = temp_total
                        state["websites_found"] = temp_websites
                    save_job_progress(job_id, state)

                businesses = scraper.search_location(keyword, location, update_progress_cb=progress_cb)
                
                all_businesses.extend(businesses)
                
                state["locations_completed"] += 1
                state["businesses_found"] = len(all_businesses)
                state["websites_found"] = sum(1 for b in all_businesses if b.get('website') and b.get('website') != "N/A")
                state["message"] = f"Completed {location}"
                
                save_job_results(job_id, all_businesses)
                save_job_progress(job_id, state)
                
                time.sleep(2)
                
        state["message"] = "Deduplicating results..."
        save_job_progress(job_id, state)
        
        unique_businesses = remove_duplicates(all_businesses)
        
        if websites_only:
            unique_businesses = [b for b in unique_businesses if b.get('website') and b.get('website') != "N/A"]
            
        save_job_results(job_id, unique_businesses)
        
        state["status"] = "completed"
        state["message"] = "Search completed successfully."
        state["end_time"] = datetime.now().isoformat()
        state["businesses_found"] = len(unique_businesses)
        state["websites_found"] = sum(1 for b in unique_businesses if b.get('website') and b.get('website') != "N/A")
        save_job_progress(job_id, state)
        
    except Exception as e:
        print(f"Job {job_id} failed: {e}")
        state["status"] = "failed"
        state["message"] = f"Error: {str(e)}"
        state["end_time"] = datetime.now().isoformat()
        save_job_progress(job_id, state)

def get_job_status(job_id):
    if job_id in jobs:
        return jobs[job_id]
    state = load_job_progress(job_id)
    if state:
        jobs[job_id] = state
        return state
    return None
