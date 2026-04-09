from unittest.mock import AsyncMock

import httpx
import pytest

from pyhunter import AsyncPyHunter
from pyhunter.exceptions import HunterApiError, MissingCompanyError, MissingNameError


@pytest.mark.asyncio
async def test_async_domain_search_requires_domain_or_company():
    hunter = AsyncPyHunter("key")
    with pytest.raises(MissingCompanyError):
        await hunter.domain_search()
    await hunter.aclose()


@pytest.mark.asyncio
async def test_async_email_finder_requires_name_when_no_linkedin():
    hunter = AsyncPyHunter("key")
    with pytest.raises(MissingNameError):
        await hunter.email_finder(domain="example.com")
    await hunter.aclose()


@pytest.mark.asyncio
async def test_async_email_finder_returns_tuple():
    hunter = AsyncPyHunter("key")
    hunter._query_hunter = AsyncMock(return_value={"email": "a@b.com", "score": 99})
    email, score = await hunter.email_finder(domain="example.com", full_name="A B")
    assert email == "a@b.com"
    assert score == 99
    await hunter.aclose()


@pytest.mark.asyncio
async def test_async_account_information_adds_calls_left():
    hunter = AsyncPyHunter("key")
    hunter._query_hunter = AsyncMock(
        return_value={"calls": {"available": 200, "used": 20}}
    )
    data = await hunter.account_information()
    assert data["calls"]["left"] == 180
    await hunter.aclose()


@pytest.mark.asyncio
async def test_async_invalid_payload_raises_api_error():
    transport = httpx.MockTransport(
        lambda _: httpx.Response(200, json={"meta": {"ok": True}})
    )
    client = httpx.AsyncClient(transport=transport, timeout=5)
    hunter = AsyncPyHunter("key", client=client, max_retries=0)
    with pytest.raises(HunterApiError):
        await hunter._query_hunter("https://api.hunter.io/v2/account", {"api_key": "key"})
    await hunter.aclose()


@pytest.mark.asyncio
async def test_async_logo_returns_content_bytes():
    transport = httpx.MockTransport(
        lambda _: httpx.Response(
            200,
            content=b"binary-logo",
            headers={"content-type": "image/png"},
        )
    )
    client = httpx.AsyncClient(transport=transport, timeout=5)
    hunter = AsyncPyHunter("key", client=client, max_retries=0)
    content = await hunter.logo("stripe.com")
    assert content == b"binary-logo"
    await hunter.aclose()
