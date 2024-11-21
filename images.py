from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
# Sample listings
listings = [
    {
        "image": "https://scontent.fkhi22-1.fna.fbcdn.net/v/t45.5328-4/467200071_556555560466650_2088783252713888803_n.jpg",
        "title": "Samsung galaxy A32",
        "price": "₹7,500",
        "post_url": "https://www.facebook.com/marketplace/item/559469880061677/?ref=search",
        "location": "Mumbai، MH"
    },
    {
        "image": "https://scontent.fkhi22-1.fna.fbcdn.net/v/t45.5328-4/467401959_445839331884575_4138786006205954082_n.jpg",
        "title": "Samsung galaxy Note 10 lite only mobile",
        "price": "₹4,000",
        "post_url": "https://www.facebook.com/marketplace/item/581183857927415/?ref=search",
        "location": "Mumbai، MH"
    },
    {
        "image": "https://scontent.fkhi22-1.fna.fbcdn.net/v/t45.5328-4/467051087_1234528671183948_5695407214691708116_n.jpg",
        "title": "iPhone 12 Pro 256gb",
        "price": "₹26,500",
        "post_url": "https://www.facebook.com/marketplace/item/920004886224493/?ref=search",
        "location": "Mumbai، MH"
    },
    # Add more listings if needed
]

# Function to scrape a specific div
def scrape_specific_div(url):
    with sync_playwright() as p:
        # Launch a headless browser
        browser = p.chromium.launch(headless=True)  # Set headless=False to see the browser actions
        page = browser.new_page()

        # Navigate to the webpage
        page.goto(url)

        # Wait for the page content to load fully
        page.wait_for_selector('div.x1ja2u2z.x78zum5.xl56j7k.xh8yej3', timeout=10000)  # Adjust the timeout if needed

        # Get the page content
        html_content = page.content()
        browser.close()

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

# Iterate through the listings and scrape images
for listing in listings:
    webpage_url = listing['post_url']  # Extract the URL from the listing
    print(f"Scraping images for: {listing['title']} ({webpage_url})")

    # Scrape the specific div
    image_urls = scrape_specific_div(webpage_url)

    # Append the image URLs to the current listing
    listing['scraped_images'] = image_urls

    print("Scraping complete for this listing.")
    print("-" * 50)

# Print the updated listings with appended image URLs

json_string = json.dumps(listings, indent=4)
print(json_string)