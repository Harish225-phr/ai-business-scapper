from flask import Flask, render_template, request, jsonify, send_file
import os
import io
import csv
from scraper.job_manager import start_job, get_job_status
from scraper.storage import get_job_results

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def create_search():
    data = request.json
    keyword = data.get('keyword', '').strip()
    locations_text = data.get('locations', '').strip()
    websites_only = data.get('websites_only', False)
    headless = data.get('headless', True)
    
    if not keyword or not locations_text:
        return jsonify({"error": "Keyword and locations are required"}), 400
        
    locations = [loc.strip() for loc in locations_text.split(',') if loc.strip()]
    if not locations:
        return jsonify({"error": "At least one location is required"}), 400
        
    job_id = start_job(keyword, locations, websites_only, headless)
    return jsonify({"job_id": job_id, "status": "queued"})

@app.route('/api/search/status/<job_id>', methods=['GET'])
def search_status(job_id):
    status = get_job_status(job_id)
    if not status:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(status)

@app.route('/api/search/results/<job_id>', methods=['GET'])
def search_results(job_id):
    results = get_job_results(job_id)
    return jsonify({"results": results})

@app.route('/api/export/csv/<job_id>', methods=['GET'])
def export_csv(job_id):
    results = get_job_results(job_id)
    if not results:
        return "No results found", 404
        
    si = io.StringIO()
    keys = ['business_name', 'location_searched', 'website', 'phone', 'rating', 'review_count', 'address', 'category', 'google_maps_url']
    writer = csv.DictWriter(si, fieldnames=keys, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(results)
    
    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)
    
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'leads-{job_id[:8]}.csv'
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
