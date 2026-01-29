from crewai.tools import tool
from playwright.sync_api import sync_playwright

@tool("Search Flights on Kayak")
def search_flights(url: str) -> list:
    """
    Visit Kayak URL and return top 5 flights.
    """
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(10000)

        # Grab top 5 flight cards
        cards = page.locator(".resultWrapper").all()[:5]

        for card in cards:
            results.append({
                "airline": card.locator(".codeshares-airline-names").inner_text(),
                "price": card.locator(".price-text").inner_text(),
                "duration": card.locator(".duration-text").inner_text(),
                "stops": card.locator(".stops-text").inner_text(),
            })

        browser.close()

    return results
