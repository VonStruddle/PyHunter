from unittest.mock import Mock

import pytest
import requests

from pyhunter import PyHunter
from pyhunter.exceptions import HunterApiError, MissingCompanyError, MissingNameError


def _mock_response(payload, status_code=200):
    response = Mock()
    response.status_code = status_code
    response.json.return_value = payload
    response.text = str(payload)
    response.raise_for_status.return_value = None
    return response


def test_domain_search_requires_domain_or_company():
    hunter = PyHunter("key")
    with pytest.raises(MissingCompanyError):
        hunter.domain_search()


def test_email_finder_requires_name_when_no_linkedin():
    hunter = PyHunter("key")
    with pytest.raises(MissingNameError):
        hunter.email_finder(domain="example.com")


def test_domain_search_includes_offset_zero():
    hunter = PyHunter("key")
    hunter._query_hunter = Mock(return_value={"emails": []})
    hunter.domain_search(domain="example.com", offset=0, limit=0)
    args = hunter._query_hunter.call_args[0]
    params = args[1]
    assert params["offset"] == 0
    assert params["limit"] == 0


def test_email_finder_returns_tuple():
    hunter = PyHunter("key")
    hunter._query_hunter = Mock(return_value={"email": "a@b.com", "score": 92})
    email, score = hunter.email_finder(domain="example.com", full_name="A B")
    assert email == "a@b.com"
    assert score == 92


def test_account_information_adds_calls_left():
    hunter = PyHunter("key")
    hunter._query_hunter = Mock(
        return_value={"calls": {"available": 100, "used": 10}}
    )
    data = hunter.account_information()
    assert data["calls"]["left"] == 90


def test_query_hunter_raises_hunter_api_error_on_invalid_payload():
    hunter = PyHunter("key")
    bad = _mock_response({"meta": {}}, 200)
    hunter.session = Mock()
    hunter.session.get.return_value = bad
    with pytest.raises(HunterApiError):
        hunter._query_hunter("https://api.hunter.io/v2/account", {"api_key": "key"})


def test_query_hunter_wraps_http_error():
    hunter = PyHunter("key", max_retries=0)
    err_response = _mock_response({"errors": [{"id": "bad"}]}, status_code=400)
    err_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=err_response
    )
    hunter.session = Mock()
    hunter.session.get.return_value = err_response

    with pytest.raises(HunterApiError) as exc:
        hunter._query_hunter("https://api.hunter.io/v2/account", {"api_key": "key"})
    assert exc.value.status_code == 400


def test_major_categories_call_query_hunter():
    hunter = PyHunter("key")
    hunter._query_hunter = Mock(return_value={"ok": True})

    hunter.email_enrichment(email="a@b.com")
    hunter.discover(query="tech")
    hunter.get_leads(limit=5)
    hunter.get_campaigns(limit=5)

    assert hunter._query_hunter.call_count == 4


def test_logo_returns_content_bytes():
    hunter = PyHunter("key")
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.content = b"binary-logo"
    hunter.session = Mock()
    hunter.session.get.return_value = mock_response

    logo = hunter.logo("stripe.com")

    assert logo == b"binary-logo"
