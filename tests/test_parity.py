from unittest.mock import AsyncMock, Mock

import pytest

from pyhunter import AsyncPyHunter, PyHunter
from pyhunter.exceptions import MissingCompanyError


@pytest.mark.asyncio
async def test_sync_async_domain_search_parity():
    expected = {"domain": "example.com", "emails": []}

    sync_client = PyHunter("key")
    sync_client._query_hunter = Mock(return_value=expected)

    async_client = AsyncPyHunter("key")
    async_client._query_hunter = AsyncMock(return_value=expected)

    sync_data = sync_client.domain_search(domain="example.com")
    async_data = await async_client.domain_search(domain="example.com")

    assert sync_data == async_data
    await async_client.aclose()


@pytest.mark.asyncio
async def test_sync_async_errors_match_for_missing_company():
    sync_client = PyHunter("key")
    async_client = AsyncPyHunter("key")

    with pytest.raises(MissingCompanyError):
        sync_client.email_count()
    with pytest.raises(MissingCompanyError):
        await async_client.email_count()

    await async_client.aclose()
