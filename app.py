from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
from dotenv import load_dotenv
import os
import pymongo
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()
load_dotenv()

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI is not set in the environment.")
try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client['test']
    collection = db['fbproducts']
    logger.info("Successfully connected to MongoDB.")
except Exception as e:
    logger.error(f"Error connecting to MongoDB: {e}")
    raise RuntimeError("Failed to connect to MongoDB.")


# Predefined city URLs
city_urls = {
    "Dar-es-Salaam": "https://www.facebook.com/marketplace/110639715625917",
    "Mwanza": "https://www.facebook.com/marketplace/103124899728422",
    "Ubungo": "https://www.facebook.com/marketplace/110639715625917",
    "Mbeya": "https://www.facebook.com/marketplace/109476795738265",
    "Arusha": "https://www.facebook.com/marketplace/108741502491358",
    "Uvinza": "https://www.facebook.com/marketplace/110529672306370",
    "Geita": "https://www.facebook.com/marketplace/114585741885219",
    "Sumbawanga": "https://www.facebook.com/marketplace/108265579201898",
    "Kibaha": "https://www.facebook.com/marketplace/112247685458078",
    "Bariadi": "https://www.facebook.com/marketplace/106503279384083",
    "Kahama": "https://www.facebook.com/marketplace/108844469136684",
    "Kasulu": "https://www.facebook.com/marketplace/104705376234884",
    "Tabora": "https://www.facebook.com/marketplace/108198842540951",
    "Zanzibar": "https://www.facebook.com/marketplace/114769771872451",
    "Morogoro": "https://www.facebook.com/marketplace/103827289656637",
    "Ifakara": "https://www.facebook.com/marketplace/106477752719638",
    "Mpanda": "https://www.facebook.com/marketplace/109462835747378",
    "Iringa": "https://www.facebook.com/marketplace/107790559250455",
    "Singida": "https://www.facebook.com/marketplace/116526658361203",
    "Bukoba": "https://www.facebook.com/marketplace/113087255368763",
    "Moshi": "https://www.facebook.com/marketplace/108600849164250",
    "Kigoma": "https://www.facebook.com/marketplace/103942789641859",
    "Tarime": "https://www.facebook.com/marketplace/107137829317739",
    "Nzega": "https://www.facebook.com/marketplace/105002816204347",
    "Handeni": "https://www.facebook.com/marketplace/107067705992178",
    "Shinyanga": "https://www.facebook.com/marketplace/104062256296524",
    "Musoma": "https://www.facebook.com/marketplace/107936332567487",
    "Tanga": "https://www.facebook.com/marketplace/103998859635600",
    "Songea": "https://www.facebook.com/marketplace/108080835882005",
    "Mtwara": "https://www.facebook.com/marketplace/111937615488752",
    "Tukuyu": "https://www.facebook.com/marketplace/109564735736071",
    "Chake Chake": "https://www.facebook.com/marketplace/111333898887352",
    "Dodoma": "https://www.facebook.com/marketplace/112132262145989",
    "Kilosa": "https://www.facebook.com/marketplace/113607785318940",
    "Lindi": "https://www.facebook.com/marketplace/113657601977591",
    "Njombe": "https://www.facebook.com/marketplace/108766065811770",
    "Tunduma": "https://www.facebook.com/marketplace/113144172035080",
    "Masasi": "https://www.facebook.com/marketplace/107034915995289",
    "Magu": "https://www.facebook.com/marketplace/109098402451352",
    "Babati": "https://www.facebook.com/marketplace/108509759173550",
    "Chato": "https://www.facebook.com/marketplace/109139659106089",
    "Wete": "https://www.facebook.com/marketplace/112240375458861",
    "Biharamulo": "https://www.facebook.com/marketplace/113109858704990",
    "Itigi": "https://www.facebook.com/marketplace/108205602541561",
    "Mkokotoni": "https://www.facebook.com/marketplace/112026278813138",
    "Mahonda": "https://www.facebook.com/marketplace/112026278813138",
    "Vwawa": "https://www.facebook.com/marketplace/109023859125108",
    "Koani": "https://www.facebook.com/marketplace/114769771872451"
}


# Default marketplace URL
DEFAULT_URL = "https://www.facebook.com/marketplace"

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

async def scrape_specific_div(url):
    async with async_playwright() as p:
        # Launch a headless browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # Navigate to the webpage
            print(f"Navigating to {url}")
            await page.goto(url, timeout=60000)  # Increase page load timeout

            # Scroll down to ensure dynamic content loads
            print("Scrolling to load dynamic content...")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(3)  # Wait for content to load

            # Wait for the specific div to appear
            print("Waiting for selector to appear...")
            await page.wait_for_selector('div.x1ja2u2z.x78zum5.xl56j7k.xh8yej3', timeout=30000)

            # Get the page content
            print("Fetching page content...")
            html_content = await page.content()

        except Exception as e:
            print(f"Error during scraping: {e}")
            # Capture a screenshot for debugging
            await page.screenshot(path="debug_screenshot.png")
            await browser.close()
            return []

        finally:
            # Close the browser
            await browser.close()

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all img tags within the specific div
        print("Parsing images...")
        img_tags = soup.find_all('img', class_='x5yr21d')  # The image class

        if not img_tags:
            print(f"No images found for URL: {url}")
            return []

        # Collect unique image URLs
        image_urls = []
        for img in img_tags:
            if 'src' in img.attrs:
                img_url = img['src']
                if img_url not in image_urls:  # Avoid duplicates
                    image_urls.append(img_url)

        print(f"Found {len(image_urls)} images.")
        return image_urls

@app.get("/")
def root():
    return {"message": "Welcome to the Facebook Marketplace API."}

@app.get("/crawl_facebook_marketplace")
async def crawl_facebook_marketplace(city: str, query: str, max_price: int):
    category = query.lower()
    # Determine the base URL
    base_url = city_urls.get(city, DEFAULT_URL)

    # Construct the full URL with query parameters
    if base_url == DEFAULT_URL:
        marketplace_url = f"{base_url}/{city}/search/?query={query}&maxPrice={max_price}"
    else:
        marketplace_url = f"{base_url}/search/?query={query}&maxPrice={max_price}"

    async with async_playwright() as p:
        try:
            # Launch a headless browser
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Navigate to the marketplace URL
            await page.goto(marketplace_url, wait_until="networkidle")

            # Scroll and load more content
            await asyncio.sleep(1)
            await page.keyboard.press("End")
            await asyncio.sleep(1)

            # Get the page content
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            listings = soup.find_all("div", class_="x9f619 x78zum5 x1r8uery xdt5ytf x1iyjqo2 xs83m0k x1e558r4 x150jy0e x1iorvi4 xjkvuk6 xnpuxes x291uyu x1uepa24")

            # Parse listings
            parsed = []
            for listing in listings:
                try:
                    image_tag = listing.find("img")
                    image = image_tag["src"] if image_tag else None

                    title_tag = listing.find("span", class_="x1lliihq x6ikm8r x10wlt62 x1n2onr6")
                    title = title_tag.text if title_tag else "No title available"

                    price_div = listing.find("div", class_="x78zum5 x1q0g3np x1iorvi4 x4uap5 xjkvuk6 xkhd6sd")
                    price_tag = price_div.find("span", class_="x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x676frb x1lkfr7t x1lbecb7 x1s688f xzsf02u")
                    price = price_tag.text if price_tag else "No price available"

                    post_link_tag = listing.find("a")
                    post_url = "https://www.facebook.com" + post_link_tag["href"] if post_link_tag else None

                    location_tag = listing.find("span", class_="x1lliihq x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft x1j85h84")
                    location = location_tag.text if location_tag else "Location not specified"

                    # Append parsed data
                    parsed.append({
                        "image": image,
                        "title": title,
                        "price": price,
                        "post_url": post_url,
                        "category":category,
                        "location": location
                    })

                except Exception as e:
                    print(f"Error parsing listing: {e}")
                    continue
            
            if parsed:
                for item in parsed:
                    result = collection.update_one({'post_url': item['post_url']}, {'$set': item}, upsert=True)
                    action = "Updated" if result.matched_count else "Inserted"
                    logger.info(f"{action} listing with URL: {item['post_url']}")
                logger.info(f"{len(parsed)} listings processed and added/updated in the database.")
            else:
                logger.info("No listings found.")
            
            return {"listings": parsed}

        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            raise HTTPException(500, f"Error during scraping: {str(e)}")
        finally:
            browser.close()

if _name_ == "_main_":
    uvicorn.run("app:app", host="127.0.0.1", port=8000)