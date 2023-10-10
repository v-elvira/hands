import asyncio
import time
import re
from collections import defaultdict
import aiohttp
from aiohttp.client_exceptions import ClientConnectorError
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc


phone_regex = re.compile(
    r"""
        (?<!(?:\w|\.|=|\[|{|")|(?:= ))                                  # not preceded by letter, digits, ., = 
        ((?:(?:8|(?:\+7)) {0,2}(?:(?:\(|-)?\d\d\d(?:\)|-)?)?\s{0,2})?   # code
        \d\d\d(?:-|\s)?\d\d(?:-|\s)?\d\d)                               # number
        (?!(?:\w|\.|;|]|}|"))                                           # not followed by letter, digits, ., ;
        """,
    re.VERBOSE,
)


def phones_re(text):
    found = phone_regex.findall(text)
    cleaned = [re.sub(r"\(|\)|\s*|-", "", s) for s in found]
    phones = {"8" + x if len(x) == 10 else "8495" + x for x in cleaned}
    return phones


async def page_search(session, key, url, found, not_found):
    phones = set()
    try:
        async with session.get(url) as response:
            page_text = await response.text()
            phones = phones_re(page_text)
    except ClientConnectorError:
        pass
    if phones:
        found[key].update(phones)
    else:
        not_found[key].add(url)


def get_browser():
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    return uc.Chrome(headless=True, use_subprocess=False, options=options)


def browser_page_search(browser, key, url, found, not_found):
    print(f"{key} {url}:")
    phones = set()
    try:
        browser.get(url)
        showers = browser.find_elements(
            By.XPATH,
            "//*[contains(text(), 'Показать телефон') or contains(text(), 'Я не робот')]",
        )
        for shower in showers:
            if shower.is_displayed():
                shower.click()
        time.sleep(0.3)
        body_text = browser.find_element(By.TAG_NAME, "body").text
        phones = phones_re(body_text)
    except WebDriverException:
        pass
    if phones:
        print(*phones)
        found[key].update(phones)
    else:
        not_found[key].add(url)
        print("Not found")


async def fast_search(emails):
    found = defaultdict(set)
    not_found = defaultdict(set)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for key, val in emails.items():
            if isinstance(val, (list, set, tuple)):
                [
                    tasks.append(
                        asyncio.create_task(
                            page_search(session, key, url, found, not_found)
                        )
                    )
                    for url in val
                ]
            else:
                tasks.append(
                    asyncio.create_task(
                        page_search(session, key, val, found, not_found)
                    )
                )
        await asyncio.gather(*tasks)
    return found, not_found


def slow_search(emails, found=None):
    if found is None:
        found = defaultdict(set)
    not_found = defaultdict(set)
    browser = get_browser()
    with browser:
        for key, val in emails.items():
            if isinstance(val, (list, set, tuple)):
                [
                    browser_page_search(browser, key, url, found, not_found)
                    for url in val
                ]
            else:
                browser_page_search(browser, key, val, found, not_found)
    return found, not_found


async def find_phones(emails):
    found, not_found = await fast_search(emails)
    print("Fast search. Found:")
    for key in found:
        print(f"{key} {emails[key]}:")
        print(*found[key])

    if not_found:
        print("_" * 100)
        print("Slow search:")
        _, not_found = slow_search(not_found, found)
    print("_" * 100)
    print(f"Found phones for {len(found)} organisations")
    print(f"Nothing found for: {len(not_found)}")
    return dict(found)


if __name__ == "__main__":
    asyncio.run(
        find_phones(
            {
                "REP": ["https://repetitors.info/", "https://profi.ru/"],
                "OKNA": "https://remont-okon-servis.ru/contacts.html",
                "STIR": "https://stir-remont.ru/company.html",
                "RROFI": "https://profi.ru/",
                "HANDS": "https://hands.ru/company/about/",
            }
        )
    )
