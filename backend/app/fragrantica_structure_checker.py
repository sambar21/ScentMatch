#!/usr/bin/env python3
"""
Simple script to check Fragrantica's current site structure
"""

import requests
from bs4 import BeautifulSoup
import ssl
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_fragrantica_structure():
    """Check the current structure of Fragrantica pages"""
    
    # Test URLs to check
    test_urls = [
        "https://www.fragrantica.com/designers/",
        "https://www.fragrantica.com/perfume/Tom-Ford/Black-Orchid-1018.html",  # Example fragrance
        "https://www.fragrantica.com/"  # Homepage
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing URL: {url}")
        print('='*60)
        
        try:
            # Make request with SSL verification disabled for testing
            response = requests.get(url, headers=headers, verify=False, timeout=30)
            
            print(f"Status Code: {response.status_code}")
            print(f"Content Length: {len(response.text)} characters")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check page title
                title = soup.find('title')
                print(f"Page Title: {title.text.strip() if title else 'No title found'}")
                
                # Check for common fragrance-related elements
                print("\n--- Looking for fragrance links ---")
                
                # Try different selectors that might contain fragrance links
                selectors_to_check = [
                    'a[href*="/perfume/"]',
                    'a[href*="/designers/"]', 
                    '.fragrance-link',
                    '.perfume-link',
                    '.grid-item a',
                    '.product-item a'
                ]
                
                found_links = []
                for selector in selectors_to_check:
                    links = soup.select(selector)
                    if links:
                        print(f"✅ Found {len(links)} links with selector: {selector}")
                        # Show first few examples
                        for i, link in enumerate(links[:3]):
                            href = link.get('href', 'No href')
                            text = link.get_text().strip()[:50]  # First 50 chars
                            found_links.append((href, text))
                            print(f"   Example {i+1}: {href} -> {text}")
                    else:
                        print(f"❌ No links found with selector: {selector}")
                
                # Check for notes structure on fragrance pages
                if "/perfume/" in url:
                    print("\n--- Looking for fragrance notes ---")
                    note_selectors = [
                        '.notes',
                        '.top-notes', '.middle-notes', '.base-notes',
                        '[data-note-type]',
                        '.pyramid',
                        '.fragrance-notes'
                    ]
                    
                    for selector in note_selectors:
                        elements = soup.select(selector)
                        if elements:
                            print(f"✅ Found notes with selector: {selector}")
                            for elem in elements[:2]:
                                print(f"   Content: {elem.get_text().strip()[:100]}")
                        else:
                            print(f"❌ No notes found with selector: {selector}")
                
                # Check for rating/review structure
                print("\n--- Looking for ratings/reviews ---")
                rating_selectors = [
                    '.rating', '.stars', '.average-rating',
                    '[data-rating]', '.review', '.user-review'
                ]
                
                for selector in rating_selectors:
                    elements = soup.select(selector)
                    if elements:
                        print(f"✅ Found {len(elements)} rating/review elements with: {selector}")
                        for elem in elements[:2]:
                            print(f"   Content: {elem.get_text().strip()[:100]}")
                    else:
                        print(f"❌ No rating/review elements found with: {selector}")
                
                # Save a sample of the HTML for manual inspection
                if url == test_urls[0]:  # Save the designers page
                    with open('fragrantica_sample.html', 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    print(f"\n💾 Saved full HTML to 'fragrantica_sample.html' for manual inspection")
                
            else:
                print(f"❌ Request failed with status code: {response.status_code}")
                print(f"Response text (first 500 chars): {response.text[:500]}")
                
        except Exception as e:
            print(f"❌ Error accessing {url}: {e}")
    
    print(f"\n{'='*60}")
    print("Structure check complete!")
    print("Check the 'fragrantica_sample.html' file to manually inspect the page structure.")
    print('='*60)

if __name__ == "__main__":
    check_fragrantica_structure()