#!/usr/bin/env python3
"""Optional web search and live-page inspection for Cenere coding sessions."""

import argparse
from urllib.parse import quote_plus

from playwright.sync_api import sync_playwright


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="Open a page or local development server")
    group.add_argument("--search", help="Search the web with DuckDuckGo")
    parser.add_argument("--screenshot", help="Save a screenshot to this path")
    parser.add_argument("--cdp", help="Attach to an existing browser via its local CDP endpoint")
    parser.add_argument("--max-chars", type=int, default=12000)
    args = parser.parse_args()

    target = args.url or f"https://r.jina.ai/http://www.bing.com/search?q={quote_plus(args.search)}"
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(args.cdp) if args.cdp else playwright.chromium.launch(headless=True)
        context = browser.contexts[0] if args.cdp and browser.contexts else browser.new_context()
        page = context.pages[0] if args.cdp and context.pages else context.new_page()
        errors: list[str] = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        response = page.goto(target, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1000)

        if args.search:
            print(page.locator("body").inner_text()[: args.max_chars])
        else:
            print(f"URL: {page.url}\nTitle: {page.title()}\nHTTP: {response.status if response else 'unknown'}")
            print("\nVisible page text:\n" + page.locator("body").inner_text()[: args.max_chars])

        if args.screenshot:
            page.screenshot(path=args.screenshot, full_page=True)
            print(f"\nScreenshot saved: {args.screenshot}")
        if errors:
            print("\nPage errors:")
            for error in errors[:20]:
                print(f"- {error}")
        if not args.cdp:
            browser.close()


if __name__ == "__main__":
    main()
