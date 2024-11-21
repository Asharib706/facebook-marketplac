from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio

app = FastAPI()

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

        # Navigate to the webpage
        await page.goto(url)

        # Wait for the page content to load fully
        await page.wait_for_selector('div.x1ja2u2z.x78zum5.xl56j7k.xh8yej3', timeout=10000)

        # Get the page content
        html_content = await page.content()
        await browser.close()

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all img tags within the specific div
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

    return image_urls

@app.get("/")
def root():
    return {"message": "Welcome to Passivebot's Facebook Marketplace API."}

@app.get("/crawl_facebook_marketplace")
async def crawl_facebook_marketplace(city: str, query: str, max_price: int):
    marketplace_url = f"https://www.facebook.com/marketplace/{city}/search/?query={query}&maxPrice={max_price}"

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
                        "location": location
                    })

                except Exception as e:
                    print(f"Error parsing listing: {e}")
                    continue
            
            await browser.close()

            for parse in parsed:
                webpage_url = parse['post_url']  # Extract the URL from the listing
                print(f"Scraping images for: {parse['title']} ({webpage_url})")

                # Scrape the specific div
                image_urls = await scrape_specific_div(webpage_url)

                # Append the image URLs to the current listing
                parse['scraped_images'] = image_urls

                print("Scraping complete for this listing.")
                print("-" * 50)
            return {"listings": parsed}
        except Exception as e:
            print(f"Error during scraping: {e}")
            raise HTTPException(500, f"Error during scraping: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000)
