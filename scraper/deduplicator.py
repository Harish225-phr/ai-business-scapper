from .website_extractor import extract_domain, extract_place_id_from_url, extract_phone_digits, normalize_name

def remove_duplicates(businesses):
    unique_businesses = []
    seen = {
        'place_ids': set(),
        'domains': set(),
        'phones': set(),
        'names': set()
    }
    
    for b in businesses:
        is_duplicate = False
        
        # 1. Deduplicate by Place ID
        place_id = extract_place_id_from_url(b.get('google_maps_url'))
        if place_id != "N/A":
            if place_id in seen['place_ids']:
                is_duplicate = True
            seen['place_ids'].add(place_id)
            
        # 2. Deduplicate by Domain (if not already duplicate)
        if not is_duplicate:
            domain = extract_domain(b.get('website'))
            if domain != "N/A":
                if domain in seen['domains']:
                    is_duplicate = True
                seen['domains'].add(domain)
                
        # 3. Deduplicate by Phone
        if not is_duplicate:
            phone_digits = extract_phone_digits(b.get('phone'))
            if phone_digits != "N/A" and len(phone_digits) >= 7:
                if phone_digits in seen['phones']:
                    is_duplicate = True
                seen['phones'].add(phone_digits)
                
        # 4. Deduplicate by Name (Fuzzy/Normalized)
        if not is_duplicate:
            norm_name = normalize_name(b.get('business_name'))
            if norm_name:
                if norm_name in seen['names']:
                    is_duplicate = True
                seen['names'].add(norm_name)
                
        if not is_duplicate:
            unique_businesses.append(b)
            
    return unique_businesses
