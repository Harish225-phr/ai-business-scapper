from urllib.parse import urlparse
import re

def normalize_url(url):
    if not url or url == "N/A":
        return "N/A"
    try:
        parsed = urlparse(url)
        # Strip trailing slash and www
        domain = parsed.netloc.lower().replace('www.', '')
        return f"{domain}{parsed.path}".rstrip('/')
    except:
        return url

def extract_domain(url):
    if not url or url == "N/A":
        return "N/A"
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower().replace('www.', '')
    except:
        return "N/A"

def extract_place_id_from_url(url):
    # E.g. https://www.google.com/maps/place/.../data=!4m7!3m6!1s0x...
    if not url or url == "N/A":
        return "N/A"
    try:
        match = re.search(r'1s(0x[0-9a-fA-F]+:0x[0-9a-fA-F]+)', url)
        if match:
            return match.group(1)
    except:
        pass
    return "N/A"

def extract_phone_digits(phone):
    if not phone or phone == "N/A":
        return "N/A"
    return re.sub(r'\D', '', phone)

def normalize_name(name):
    if not name or name == "N/A":
        return ""
    # Lowercase, remove non-alphanumeric, collapse whitespace
    name = name.lower()
    name = re.sub(r'[^a-z0-9]', ' ', name)
    return re.sub(r'\s+', ' ', name).strip()
