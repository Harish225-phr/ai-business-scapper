def extract_business_name(element):
    try:
        name_elem = element.query_selector('div.fontHeadlineSmall')
        if name_elem:
            return name_elem.inner_text().strip()
    except:
        pass
    return "N/A"

def extract_rating(element):
    try:
        # Looking for aria-label with rating text, e.g., "4.8 stars"
        span = element.query_selector('span[role="img"]')
        if span:
            aria_label = span.get_attribute('aria-label')
            if aria_label and 'stars' in aria_label:
                return aria_label.split(' ')[0]
    except:
        pass
    return "N/A"

def extract_review_count(element):
    try:
        span = element.query_selector('span[role="img"]')
        if span:
            aria_label = span.get_attribute('aria-label')
            if aria_label and 'Reviews' in aria_label:
                parts = aria_label.split(' ')
                # Usually "4.8 stars 120 Reviews"
                for i, part in enumerate(parts):
                    if 'Reviews' in part or 'Review' in part:
                        try:
                            # It could be the item before it
                            num = parts[i-1].replace(',', '')
                            if num.isdigit():
                                return int(num)
                        except:
                            pass
    except:
        pass
    
    try:
        # Alternative extraction from inner text if aria-label fails
        text = element.inner_text()
        if '(' in text and ')' in text:
            # Often review counts are in parenthesis like (120)
            import re
            match = re.search(r'\((\d+)\)', text.replace(',', ''))
            if match:
                return int(match.group(1))
    except:
        pass
    
    return 0

def extract_google_maps_url(element):
    try:
        link = element.query_selector('a')
        if link:
            return link.get_attribute('href')
    except:
        pass
    return "N/A"

def extract_website(element):
    try:
        # The website button is often an 'a' tag with 'Website' as inner text or aria-label
        # Alternative strategy is to find a link that doesn't go to google.com
        links = element.query_selector_all('a')
        for link in links:
            href = link.get_attribute('href')
            if href and 'google.com' not in href and 'maps.google.com' not in href:
                # Basic check to avoid share links, etc.
                text = link.inner_text().lower()
                if 'website' in text or link.get_attribute('data-value') == 'Website':
                    return href
    except:
        pass
    return "N/A"

def extract_category_address_phone(element):
    # This data is often grouped together in text blocks
    # We will try to parse it from the general inner_text or specific divs
    category, address, phone = "N/A", "N/A", "N/A"
    
    try:
        # One reliable way is looking for specific div structure, but they change often.
        # Let's extract all text lines and deduce.
        lines = element.inner_text().split('\n')
        # Typical structure:
        # Business Name
        # 4.8 (120) · Plumber
        # 123 Main St
        # (555) 123-4567
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if it looks like a phone number
            import re
            if re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', line):
                phone = line
                continue
                
            # Check for category (often combined with rating/reviews)
            if '·' in line:
                parts = line.split('·')
                if len(parts) > 1:
                    potential_category = parts[1].strip()
                    if potential_category and not potential_category.startswith('Closed') and not potential_category.startswith('Open'):
                        category = potential_category
                        
            # Address can be hard to reliably extract this way without breaking changes.
            # We will use a regex to see if it starts with digits or looks like an address
            if re.match(r'^\d+\s+[A-Za-z]+', line):
                address = line
                
    except:
        pass
        
    return category, address, phone

def extract_all_data(element, location):
    name = extract_business_name(element)
    if not name or name == "N/A":
        return None # Skip empty
        
    category, address, phone = extract_category_address_phone(element)
    website = extract_website(element)
    
    return {
        "business_name": name,
        "location_searched": location,
        "website": website,
        "phone": phone,
        "rating": extract_rating(element),
        "review_count": extract_review_count(element),
        "address": address,
        "category": category,
        "google_maps_url": extract_google_maps_url(element)
    }
