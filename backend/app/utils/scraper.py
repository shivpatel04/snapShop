import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import asyncio
import random
import time
import re


def scrape_amazon(query):
    url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    print("[Amazon] Searching URL:", url)
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        print("[Amazon] Status code:", resp.status_code)
        print("[Amazon] HTML length:", len(resp.text))
        
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
    
        product_containers = soup.select("div[data-component-type='s-search-result']")
        
        if not product_containers:
            product_containers = soup.select("div[data-asin]")
        
        print(f"[Amazon] Found {len(product_containers)} product containers")
        
        for div in product_containers:
            title_text = ""
            price_text = ""
            rating_text = "N/A"
            image_url = ""
            product_link = ""
            
            title_selectors = [
                "h2.a-size-mini span",
                "h2 span.a-size-medium",
                "h2 span.a-size-base-plus",
                "h2 a span",
                "h2 span",
                "[data-cy='title-recipe-title']",
                ".s-title-instructions-style span"
            ]
            
            for selector in title_selectors:
                title_elem = div.select_one(selector)
                if title_elem:
                    title_text = title_elem.get_text(strip=True)
                    break

            price_selectors = [
                ".a-price.a-text-price .a-offscreen",
                ".a-price .a-offscreen",
                ".a-price-whole",
                ".a-price.a-text-price",
                ".a-price",
                "[data-cy='price-recipe']",
                ".a-price-symbol + .a-price-whole"
            ]
            
            for selector in price_selectors:
                price_elem = div.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    if price_text:
                        break

            rating_selectors = [
                ".a-icon-alt",
                ".a-icon.a-icon-star-small .a-icon-alt",
                ".a-icon.a-icon-star .a-icon-alt",
                "[data-cy='reviews-ratings-slot'] .a-icon-alt",
                ".a-rating .a-icon-alt"
            ]
            
            for selector in rating_selectors:
                rating_elem = div.select_one(selector)
                if rating_elem:
                    rating_text = rating_elem.get_text(strip=True)
                    if rating_text and rating_text != "N/A":
                        rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                        if rating_match:
                            rating_text = rating_match.group(1)
                        break

            image_selectors = [
                "img.s-image",
                "img[data-image-latency]",
                ".s-product-image img",
                "img"
            ]
            
            for selector in image_selectors:
                image_elem = div.select_one(selector)
                if image_elem:
                    image_url = image_elem.get('src', '') or image_elem.get('data-src', '')
                    if image_url:
                        break
            
            link_selectors = [
                "h2 a",
                "a.a-link-normal",
                ".s-product-image a",
                "a[href*='/dp/']",
                "a[href*='/gp/product/']"
            ]
            
            for selector in link_selectors:
                link_elem = div.select_one(selector)
                if link_elem and link_elem.has_attr("href"):
                    href = link_elem["href"]
                    if href.startswith("/"):
                        product_link = "https://www.amazon.in" + href
                    elif href.startswith("https://"):
                        product_link = href
                    else:
                        product_link = "https://www.amazon.in/" + href
                    break

            if title_text:
                results.append({
                    "title": title_text,
                    "price": price_text if price_text else "N/A",
                    "rating": rating_text,
                    "source": "Amazon",
                    "image": image_url,
                    "link": product_link
                })
        
        print(f"[Amazon] Found {len(results)} results")
        return results
        
    except Exception as e:
        print(f"[Amazon] Error: {str(e)}")
        return []

def extract_flipkart_rating(div, debug=False):

    if debug:
        print(f"[Rating Debug] Processing product div: {div.get('class', 'No class')}")
    
    rating_strategies = [
        {
            "name": "Direct Rating Selectors",
            "selectors": [
                "div._3LWZlK",
                "div[class*='_3LWZlK']",
                "span._1lRcqv",
                "span[class*='_1lRcqv']",
                "div.hGSR34",
                "div[class*='hGSR34']",
                "span.hGSR34",
                "span[class*='hGSR34']",
                "div._3Ay6Sb",
                "div[class*='_3Ay6Sb']",
                "span._3Ay6Sb",
                "span[class*='_3Ay6Sb']",
                "div.XQDdHH",
                "div[class*='XQDdHH']",
                "span.XQDdHH",
                "span[class*='XQDdHH']",
                "div._1i2ddd",
                "div[class*='_1i2ddd']",
                "span._1i2ddd",
                "span[class*='_1i2ddd']",
                "div.col-7-12",
                "div[class*='col-7-12']",
                "span.col-7-12",
                "span[class*='col-7-12']"
            ]
        },
        
        {
            "name": "Star Symbol Search",
            "selectors": [] 
        },
        
        {
            "name": "Numerical Pattern Search",
            "selectors": []  
        },
        
        {
            "name": "Attribute Search",
            "selectors": [
                "[title*='rating']",
                "[title*='Rating']",
                "[title*='star']",
                "[title*='Star']",
                "[alt*='rating']",
                "[alt*='Rating']",
                "[alt*='star']",
                "[alt*='Star']"
            ]
        }
    ]
    
    for strategy in rating_strategies:
        if debug:
            print(f"[Rating Debug] Trying strategy: {strategy['name']}")
        
        if strategy['name'] == "Direct Rating Selectors":
            for selector in strategy['selectors']:
                rating_elem = div.select_one(selector)
                if rating_elem:
                    rating_text = rating_elem.get_text(strip=True)
                    if debug:
                        print(f"[Rating Debug] Found with selector '{selector}': {rating_text}")
                    
                    if rating_text and rating_text != "N/A":
                        rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                        if rating_match:
                            rating_value = rating_match.group(1)
                            try:
                                rating_float = float(rating_value)
                                if 1 <= rating_float <= 5:
                                    if debug:
                                        print(f"[Rating Debug] Valid rating found: {rating_value}")
                                    return rating_value
                            except ValueError:
                                continue
        
        elif strategy['name'] == "Star Symbol Search":
            star_patterns = ['★', '⭐', '✯', '✰', '☆']
            for pattern in star_patterns:
                star_elements = div.find_all(string=lambda text: text and pattern in text)
                for elem in star_elements:
                    parent = elem.parent if elem.parent else elem
                    rating_text = parent.get_text(strip=True) if hasattr(parent, 'get_text') else str(elem)
                    if debug:
                        print(f"[Rating Debug] Found star pattern '{pattern}': {rating_text}")
                    
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        rating_value = rating_match.group(1)
                        try:
                            rating_float = float(rating_value)
                            if 1 <= rating_float <= 5:
                                if debug:
                                    print(f"[Rating Debug] Valid star rating found: {rating_value}")
                                return rating_value
                        except ValueError:
                            continue
        
        elif strategy['name'] == "Numerical Pattern Search":
            text_content = div.get_text()
            rating_patterns = [
                r'(\d+\.\d+)\s*out\s*of\s*5',
                r'(\d+\.\d+)\s*\/\s*5',
                r'(\d+\.\d+)\s*stars?',
                r'(\d+\.\d+)\s*rating',
                r'rating:?\s*(\d+\.\d+)',
                r'(\d+\.\d+)\s*★',
                r'★\s*(\d+\.\d+)',
                r'(\d+\.\d+)\s*⭐',
                r'⭐\s*(\d+\.\d+)'
            ]
            
            for pattern in rating_patterns:
                rating_match = re.search(pattern, text_content, re.IGNORECASE)
                if rating_match:
                    rating_value = rating_match.group(1)
                    if debug:
                        print(f"[Rating Debug] Found with pattern '{pattern}': {rating_value}")
                    
                    try:
                        rating_float = float(rating_value)
                        if 1 <= rating_float <= 5:
                            if debug:
                                print(f"[Rating Debug] Valid pattern rating found: {rating_value}")
                            return rating_value
                    except ValueError:
                        continue
        
        elif strategy['name'] == "Attribute Search":
            for selector in strategy['selectors']:
                rating_elem = div.select_one(selector)
                if rating_elem:
                    rating_text = rating_elem.get_text(strip=True)
                    title_attr = rating_elem.get('title', '')
                    alt_attr = rating_elem.get('alt', '')
                    
                    for text_source in [rating_text, title_attr, alt_attr]:
                        if text_source:
                            if debug:
                                print(f"[Rating Debug] Checking attribute text: {text_source}")
                            
                            rating_match = re.search(r'(\d+\.?\d*)', text_source)
                            if rating_match:
                                rating_value = rating_match.group(1)
                                try:
                                    rating_float = float(rating_value)
                                    if 1 <= rating_float <= 5:
                                        if debug:
                                            print(f"[Rating Debug] Valid attribute rating found: {rating_value}")
                                        return rating_value
                                except ValueError:
                                    continue

    if debug:
        print("[Rating Debug] No rating found with standard methods, trying comprehensive search...")
    
    rating_elements = div.find_all(attrs={'class': re.compile(r'rating|star|review', re.I)})
    for elem in rating_elements:
        text = elem.get_text(strip=True)
        if text:
            rating_match = re.search(r'(\d+\.?\d*)', text)
            if rating_match:
                rating_value = rating_match.group(1)
                try:
                    rating_float = float(rating_value)
                    if 1 <= rating_float <= 5:
                        if debug:
                            print(f"[Rating Debug] Valid comprehensive rating found: {rating_value}")
                        return rating_value
                except ValueError:
                    continue
    
    if debug:
        print("[Rating Debug] No rating found after comprehensive search")
    
    return "N/A"

async def scrape_flipkart_playwright(query):
    url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
    print("[Flipkart] Searching URL:", url)
    results = []
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--disable-gpu',
                    '--window-size=1920x1080',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            
            page = await context.new_page()
            
            print("[Flipkart] Navigating to URL...")
            await page.goto(url, wait_until='networkidle', timeout=60000)
            
            await asyncio.sleep(random.uniform(3, 5))
            
            login_popup_selectors = [
                "button._2KpZ6l._2doB4z",
                "button._2KpZ6l",
                "span._30XB9F",
                "button[class*='_2KpZ6l']",
                "button:has-text('✕')",
                ".close-button"
            ]
            
            for selector in login_popup_selectors:
                try:
                    await page.click(selector, timeout=3000)
                    print(f"[Flipkart] Closed login popup with selector: {selector}")
                    break
                except:
                    continue
            
            print("[Flipkart] Scrolling to load content...")
            for i in range(3):
                await page.evaluate("window.scrollBy(0, window.innerHeight)")
                await asyncio.sleep(random.uniform(1, 2))

            await asyncio.sleep(2)
            
            html = await page.content()
            await browser.close()

            soup = BeautifulSoup(html, "html.parser")
            
            product_selectors = [
                "div[data-id]",
                "div._1AtVbE",
                "div._13oc-S",
                "div[class*='_1AtVbE']",
                "div[class*='_13oc-S']",
                "div[class*='_2kHMtA']",
                "div[class*='_1fQZEK']",
                "div[class*='_25b18c']",
                "div[class*='_2B099V']",
                "div[class*='_1xHGtK']",
                "div[class*='_396cs4']"
            ]
            
            products = []
            for selector in product_selectors:
                products = soup.select(selector)
                if products:
                    print(f"[Flipkart] Found {len(products)} products with selector: {selector}")
                    break
            
            if not products:
                print("[Flipkart] No products found with any selector")
                return results
            
            for i, div in enumerate(products[:20]): 
                title_text = ""
                price_text = ""
                rating_text = "N/A"
                image_url = ""
                product_link = ""

                title_selectors = [
                    "a.s1Q9rs",
                    "div._4rR01T",
                    "a[class*='IRpwTa']",
                    "a[title]",
                    "div[class*='_4rR01T']",
                    ".s1Q9rs",
                    "._4rR01T",
                    "a[class*='s1Q9rs']",
                    "div[class*='KzDlHZ']",
                    "a[class*='_2rpwqI']",
                    "div[class*='_2rpwqI']"
                ]
                
                for selector in title_selectors:
                    title_elem = div.select_one(selector)
                    if title_elem:
                        title_text = title_elem.get_text(strip=True)
                        break
                
                if not title_text:
                    link_with_title = div.select_one("a[title]")
                    if link_with_title:
                        title_text = link_with_title.get("title", "")

                price_selectors = [
                    "div._30jeq3",
                    "div[class*='_30jeq3']",
                    "div._1_WHN1",
                    "div[class*='_1_WHN1']",
                    "div[class*='_25b18c']",
                    "div[class*='_16Jk6d']",
                    "div[class*='_3tbRL2']",
                    "div[class*='_1vC4OE']",
                    "span:contains('₹')",
                    "div:contains('₹')"
                ]
                
                for selector in price_selectors:
                    if selector.startswith("div:contains") or selector.startswith("span:contains"):
                        price_elem = div.find(selector.split(':')[0], string=lambda text: text and '₹' in text)
                    else:
                        price_elem = div.select_one(selector)
                    
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        if price_text:
                            break
                rating_text = extract_flipkart_rating(div, debug=(i < 5))  
                
                image_selectors = [
                    "img",
                    "img[class*='_396cs4']",
                    "img[class*='_2r_T1I']",
                    "img[class*='_53J4C-']"
                ]
                
                for selector in image_selectors:
                    image_elem = div.select_one(selector)
                    if image_elem:
                        image_url = image_elem.get("src", "") or image_elem.get("data-src", "")
                        if image_url:
                            break
                
                link_selectors = [
                    "a[href*='/p/']",
                    "a[href*='/product/']",
                    "a[href]"
                ]
                
                for selector in link_selectors:
                    link_elem = div.select_one(selector)
                    if link_elem and link_elem.has_attr("href"):
                        href = link_elem["href"]
                        if href.startswith("/"):
                            product_link = "https://www.flipkart.com" + href
                        elif href.startswith("https://"):
                            product_link = href
                        else:
                            product_link = "https://www.flipkart.com/" + href
                        break
                
                if title_text:
                    results.append({
                        "title": title_text,
                        "price": price_text if price_text else "N/A",
                        "rating": rating_text,
                        "source": "Flipkart",
                        "image": image_url,
                        "link": product_link
                    })
                    print(f"[Flipkart] Added product {i+1}: {title_text[:50]}... (Rating: {rating_text})")
            
        except Exception as e:
            print(f"[Flipkart] Error occurred: {str(e)}")
            try:
                await browser.close()
            except:
                pass
    
    print(f"[Flipkart] Found {len(results)} results")
    return results

def scrape_flipkart_requests(query):
    url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    print("[Flipkart Requests] Searching URL:", url)
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            results = []
           
            product_selectors = [
                "div[data-id]",
                "div._1AtVbE",
                "div._13oc-S",
                "div[class*='_1AtVbE']",
                "div[class*='_13oc-S']",
                "div[class*='_2kHMtA']",
                "div[class*='_1fQZEK']",
                "div[class*='_25b18c']"
            ]
            
            products = []
            for selector in product_selectors:
                products = soup.select(selector)
                if products:
                    print(f"[Flipkart Requests] Found {len(products)} products with selector: {selector}")
                    break
            
            for i, div in enumerate(products[:20]):
                title_text = ""
                price_text = ""
                rating_text = "N/A"
                image_url = ""
                product_link = ""
                
                title_selectors = [
                    "a.s1Q9rs",
                    "div._4rR01T",
                    "a[title]",
                    "div[class*='_4rR01T']",
                    "a[class*='s1Q9rs']",
                    "a[class*='_2rpwqI']"
                ]
                
                for selector in title_selectors:
                    title_elem = div.select_one(selector)
                    if title_elem:
                        title_text = title_elem.get_text(strip=True) if hasattr(title_elem, 'get_text') else title_elem.get('title', '')
                        break
                
                price_selectors = [
                    "div._30jeq3",
                    "div._1_WHN1",
                    "div[class*='_30jeq3']",
                    "div[class*='_1_WHN1']",
                    "div[class*='_25b18c']",
                    "div[class*='_16Jk6d']"
                ]
                
                for selector in price_selectors:
                    price_elem = div.select_one(selector)
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        break
                
                rating_text = extract_flipkart_rating(div, debug=(i < 5))  
                
                image_elem = div.select_one("img")
                if image_elem:
                    image_url = image_elem.get("src", "") or image_elem.get("data-src", "")
                
                link_elem = div.select_one("a[href]")
                if link_elem and link_elem.has_attr("href"):
                    href = link_elem["href"]
                    if href.startswith("/"):
                        product_link = "https://www.flipkart.com" + href
                    elif href.startswith("https://"):
                        product_link = href
                    else:
                        product_link = "https://www.flipkart.com/" + href
                
                if title_text:
                    results.append({
                        "title": title_text,
                        "price": price_text if price_text else "N/A",
                        "rating": rating_text,
                        "source": "Flipkart",
                        "image": image_url,
                        "link": product_link
                    })
                    print(f"[Flipkart Requests] Added product {i+1}: {title_text[:50]}... (Rating: {rating_text})")
            
            print(f"[Flipkart Requests] Found {len(results)} results")
            return results
        else:
            print(f"[Flipkart Requests] Failed with status code: {resp.status_code}")
            return []
    
    except Exception as e:
        print(f"[Flipkart Requests] Error: {str(e)}")
        return []

async def scrape_flipkart_robust(query):
    print("[Flipkart] Starting robust scraping...")
    
    try:
        results = await scrape_flipkart_playwright(query)
        if results:
            return results
    except Exception as e:
        print(f"[Flipkart] Playwright method failed: {str(e)}")
    
    print("[Flipkart] Falling back to requests method...")
    return scrape_flipkart_requests(query)

def test_flipkart_rating_extraction(query, max_products=5):
    print(f"[Rating Test] Testing rating extraction for query: {query}")
    
    url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")

            product_selectors = [
                "div[data-id]",
                "div._1AtVbE",
                "div._13oc-S",
                "div[class*='_1AtVbE']",
                "div[class*='_13oc-S']"
            ]
            
            products = []
            for selector in product_selectors:
                products = soup.select(selector)
                if products:
                    print(f"[Rating Test] Found {len(products)} products with selector: {selector}")
                    break
            
            if not products:
                print("[Rating Test] No products found")
                return
            
            for i, div in enumerate(products[:max_products]):
                print(f"\n[Rating Test] ========== PRODUCT {i+1} ==========")
                
                title_elem = div.select_one("a.s1Q9rs") or div.select_one("div._4rR01T") or div.select_one("a[title]")
                title = title_elem.get_text(strip=True) if title_elem else "Unknown Product"
                print(f"[Rating Test] Product: {title[:60]}...")

                rating = extract_flipkart_rating(div, debug=True)
                print(f"[Rating Test] Final Rating: {rating}")
                
                print(f"[Rating Test] HTML Classes: {div.get('class', 'No classes')}")
                
                all_text = div.get_text(strip=True)
                print(f"[Rating Test] All text content: {all_text[:200]}...")
                
        else:
            print(f"[Rating Test] Failed with status code: {resp.status_code}")
    
    except Exception as e:
        print(f"[Rating Test] Error: {str(e)}")

def save_flipkart_html_for_debugging(query, filename="flipkart_debug.html"):

    url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(resp.text)
            print(f"[Debug] HTML saved to {filename}")
            print(f"[Debug] You can now inspect the HTML structure manually")
        else:
            print(f"[Debug] Failed to fetch HTML: {resp.status_code}")
    except Exception as e:
        print(f"[Debug] Error saving HTML: {str(e)}")
