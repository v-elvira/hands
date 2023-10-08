import pytest
from phone_finder import find_phones


@pytest.mark.asyncio
async def test_text():
    data = {"REP": "https://repetitors.info/"}
    assert await find_phones(data) == {"REP": {"84955405676"}}


@pytest.mark.asyncio
async def test_text():
    data = {"REP": "https://repetitors.info/"}
    assert await find_phones(data) == {"REP": {"84955405676"}}


@pytest.mark.asyncio
async def test_show_phone():
    data = {"HANDS": "https://hands.ru/company/about/"}
    assert await find_phones(data) == {"HANDS": {"84951370720"}}


@pytest.mark.asyncio
async def test_more():
    data = {
        "REP": ["https://repetitors.info/", "https://profi.ru/"],
        "STIR": "https://stir-remont.ru/company.html/",
    }
    assert await find_phones(data) == {
        "REP": {"84955405676", "88003334545"},
        "STIR": {"84951281554", "84951281334"},
    }


@pytest.mark.asyncio
async def test_antibot():
    data = {"OKNA": "https://remont-okon-servis.ru/"}
    assert await find_phones(data) == {"OKNA": {"89857730093", "84957730093"}}


@pytest.mark.asyncio
async def mix():
    data = {
        "REP": ["https://repetitors.info/", "https://profi.ru/"],
        "OKNA": "https://remont-okon-servis.ru/contacts.html",
        "STIR": "https://stir-remont.ru/company.html",
        "RROFI": "https://profi.ru/",
        "HANDS": "https://hands.ru/company/about/",
        "NOTFOUND": "http/no/",
    }
    assert await find_phones(data) == {
        "REP": {"88003334545", "84955405676"},
        "STIR": {"84951281554", "84951281334"},
        "RROFI": {"88003334545"},
        "OKNA": {"89857730093", "84957730093"},
        "HANDS": {"84951370720"},
        "NOTFOUND": {},
    }
