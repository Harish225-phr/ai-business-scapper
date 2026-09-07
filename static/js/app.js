document.addEventListener('DOMContentLoaded', () => {
    
    const form = document.getElementById('search-form');
    const setupSection = document.getElementById('setup-section');
    const progressSection = document.getElementById('progress-section');
    const resultsSection = document.getElementById('results-section');
    
    let currentJobId = null;
    let pollInterval = null;
    let cachedResults = [];

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const keyword = document.getElementById('keyword').value;
        const locations = document.getElementById('locations').value;
        const websitesOnly = document.getElementById('websites-only').checked;
        const headless = document.getElementById('headless').checked;
        
        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ keyword, locations, websites_only: websitesOnly, headless })
            });
            
            const data = await response.json();
            if (data.error) {
                alert(data.error);
                return;
            }
            
            currentJobId = data.job_id;
            
            setupSection.classList.add('hidden');
            progressSection.classList.remove('hidden');
            
            pollInterval = setInterval(pollStatus, 2000);
            
        } catch (error) {
            console.error('Search error:', error);
            alert('Failed to start search');
        }
    });

    async function pollStatus() {
        if (!currentJobId) return;
        
        try {
            const response = await fetch(`/api/search/status/${currentJobId}`);
            const data = await response.json();
            
            document.getElementById('job-message').innerText = data.message || 'Running...';
            document.getElementById('loc-completed').innerText = `${data.locations_completed} / ${data.locations_total}`;
            document.getElementById('businesses-found').innerText = data.businesses_found;
            document.getElementById('websites-found').innerText = data.websites_found;
            
            if (data.status === 'completed' || data.status === 'failed') {
                clearInterval(pollInterval);
                document.querySelector('.spinner').style.display = 'none';
                
                if (data.status === 'completed') {
                    document.getElementById('job-message').innerText = 'Search Completed. Loading Results...';
                    setTimeout(() => loadResults(currentJobId), 1000);
                } else {
                    document.getElementById('job-message').innerText = 'Search Failed: ' + data.message;
                }
            }
        } catch (error) {
            console.error('Polling error:', error);
        }
    }

    async function loadResults(jobId) {
        try {
            const response = await fetch(`/api/search/results/${jobId}`);
            const data = await response.json();
            cachedResults = (data.results || []).map(b => {
                if (b.website && b.website !== 'N/A') {
                    b.website = cleanUrl(b.website);
                }
                return b;
            });
            
            // Saving to localStorage for persistence on the frontend as per user request
            localStorage.setItem('lastSearchResults', JSON.stringify(cachedResults));
            
            renderTable(cachedResults);
            
            const total = cachedResults.length;
            const websites = cachedResults.filter(b => b.website && b.website !== 'N/A').length;
            document.getElementById('final-summary').innerText = `Found ${total} unique businesses (${websites} with websites).`;
            
            document.getElementById('download-csv-btn').href = `/api/export/csv/${jobId}`;
            
            progressSection.classList.add('hidden');
            resultsSection.classList.remove('hidden');
            
        } catch (error) {
            console.error('Error loading results:', error);
        }
    }

    function cleanUrl(urlStr) {
        if (!urlStr || urlStr === 'N/A') return urlStr;
        try {
            const url = new URL(urlStr);
            const params = new URLSearchParams(url.search);
            const keysToRemove = Array.from(params.keys()).filter(k => k.startsWith('utm_') || k === 'gclid' || k === 'fbclid');
            keysToRemove.forEach(k => params.delete(k));
            url.search = params.toString();
            return url.toString();
        } catch(e) {
            return urlStr;
        }
    }

    function getDomain(url) {
        try {
            return new URL(url).hostname.replace(/^www\./, '');
        } catch (e) {
            return url;
        }
    }

    function renderTable(results) {
        const tbody = document.querySelector('#results-table tbody');
        tbody.innerHTML = '';
        
        results.forEach((b, index) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${index + 1}</td>
                <td><strong>${b.business_name}</strong><br><small>${b.category}</small></td>
                <td>${b.location_searched}</td>
                <td>${b.website !== 'N/A' ? `
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <a href="${b.website}" target="_blank" rel="noopener">${getDomain(b.website)}</a>
                        <button class="btn btn-outline btn-sm copy-website-btn" data-website="${b.website}" style="padding: 2px 6px; font-size: 11px; height: auto; min-width: auto; line-height: 1;" title="Copy Website">Copy</button>
                    </div>
                ` : 'N/A'}</td>
                <td>${b.rating !== 'N/A' ? b.rating : ''}</td>
                <td>${b.review_count || 0}</td>
                <td>${b.google_maps_url !== 'N/A' ? `<a href="${b.google_maps_url}" target="_blank">Map</a>` : ''}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    document.getElementById('results-table').addEventListener('click', (e) => {
        const copyBtn = e.target.closest('.copy-website-btn');
        if (copyBtn) {
            const website = copyBtn.getAttribute('data-website');
            navigator.clipboard.writeText(website).then(() => {
                const originalText = copyBtn.innerText;
                copyBtn.innerText = 'Copied!';
                setTimeout(() => {
                    copyBtn.innerText = originalText;
                }, 1500);
            }).catch(err => {
                console.error('Failed to copy: ', err);
            });
        }
    });

    document.getElementById('new-search-btn').addEventListener('click', () => {
        resultsSection.classList.add('hidden');
        progressSection.classList.add('hidden');
        setupSection.classList.remove('hidden');
        document.querySelector('.spinner').style.display = 'block';
        currentJobId = null;
    });

    document.getElementById('copy-all-btn').addEventListener('click', () => {
        const websites = cachedResults
            .filter(b => b.website && b.website !== 'N/A')
            .map(b => b.website)
            .join('\n');
            
        if (websites) {
            navigator.clipboard.writeText(websites).then(() => alert('Websites copied to clipboard!'));
        } else {
            alert('No websites to copy.');
        }
    });

    function generateTSV(resultsData) {
        const headers = ['Business Name', 'Location', 'Website', 'Phone', 'Rating', 'Reviews', 'Category', 'Address', 'Google Maps'];
        let tsv = headers.join('\t') + '\n';
        
        resultsData.forEach(b => {
            const row = [
                b.business_name,
                b.location_searched,
                b.website,
                b.phone,
                b.rating,
                b.review_count,
                b.category,
                b.address,
                b.google_maps_url
            ].map(val => {
                let str = String(val || '');
                return str.replace(/\t/g, ' ').replace(/\n/g, ' ');
            });
            tsv += row.join('\t') + '\n';
        });
        return tsv;
    }

    document.getElementById('copy-full-btn').addEventListener('click', () => {
        if (cachedResults.length === 0) return;
        const tsv = generateTSV(cachedResults);
        navigator.clipboard.writeText(tsv).then(() => alert('Full data copied to clipboard! (Ready to paste in Excel)'));
    });

    document.getElementById('download-json-btn').addEventListener('click', () => {
        if (cachedResults.length === 0) return;
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(cachedResults, null, 2));
        const a = document.createElement('a');
        a.href = dataStr;
        a.download = `leads-${currentJobId ? currentJobId.substring(0,8) : 'export'}.json`;
        a.click();
    });

    // If local storage is populated, load it silently to persist
    const stored = localStorage.getItem('lastSearchResults');
    if (stored) {
        try {
            const results = JSON.parse(stored);
            if (results && results.length > 0) {
                // We keep it cached so if they click export it exports the last cached memory
                cachedResults = results;
            }
        } catch(e) {}
    }
});
