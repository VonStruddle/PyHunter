import asyncio

import httpx

from ._core import parse_data_payload
from .exceptions import (
    HunterApiError,
    HunterTransportError,
    MissingCompanyError,
    MissingNameError,
)


class AsyncPyHunter:
    def __init__(self, api_key, timeout=10, max_retries=2, retry_backoff=0.5,
                 client=None):
        self.api_key = api_key
        self.base_endpoint = 'https://api.hunter.io/v2/{}'
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.client = client or httpx.AsyncClient(timeout=timeout)
        self._owns_client = client is None

    @property
    def base_params(self):
        return {'api_key': self.api_key}

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.aclose()

    async def aclose(self):
        if self._owns_client:
            await self.client.aclose()

    async def _query_hunter(self, endpoint, params, request_type='get',
                            payload=None, headers=None, raw=False):
        request_kwargs = dict(params=params, json=payload, headers=headers)
        attempt = 0
        while attempt <= self.max_retries:
            try:
                res = await self.client.request(
                    request_type.upper(),
                    endpoint,
                    **request_kwargs
                )
                res.raise_for_status()
                break
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code if exc.response else None
                should_retry = status_code in (429, 500, 502, 503, 504)
                if should_retry and attempt < self.max_retries:
                    await asyncio.sleep(self.retry_backoff * (2 ** attempt))
                    attempt += 1
                    continue
                payload_data = None
                if exc.response is not None:
                    try:
                        payload_data = exc.response.json()
                    except ValueError:
                        payload_data = {'body': exc.response.text}
                raise HunterApiError(
                    message='Hunter API returned an error response',
                    status_code=status_code,
                    error=(
                        payload_data.get('errors')
                        if isinstance(payload_data, dict)
                        else None
                    ),
                    payload=payload_data,
                    endpoint=endpoint,
                    method=request_type.upper(),
                ) from exc
            except httpx.HTTPError as exc:
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_backoff * (2 ** attempt))
                    attempt += 1
                    continue
                raise HunterTransportError(
                    message='Failed to reach Hunter API',
                    endpoint=endpoint,
                    method=request_type.upper(),
                ) from exc

        if raw:
            return res

        return parse_data_payload(res, endpoint, request_type.upper())

    async def domain_search(self, domain=None, company=None, limit=None,
                            offset=None, seniority=None, department=None,
                            emails_type=None, required_field=None,
                            verification_status=None, raw=False):
        if domain:
            params = {'domain': domain, 'api_key': self.api_key}
        elif company:
            params = {'company': company, 'api_key': self.api_key}
        else:
            raise MissingCompanyError(
                'You must supply at least a domain name or a company name'
            )
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset
        if seniority:
            params['seniority'] = seniority
        if department:
            params['department'] = department
        if emails_type:
            params['type'] = emails_type
        if required_field:
            params['required_field'] = required_field
        if verification_status:
            params['verification_status'] = verification_status
        endpoint = self.base_endpoint.format('domain-search')
        return await self._query_hunter(endpoint, params, raw=raw)

    async def email_finder(self, domain=None, company=None, first_name=None,
                           last_name=None, full_name=None,
                           linkedin_handle=None, max_duration=None, raw=False):
        params = self.base_params
        if not domain and not company and not linkedin_handle:
            raise MissingCompanyError(
                'You must supply at least a domain name, a company name, or a LinkedIn handle'
            )
        if domain:
            params['domain'] = domain
        elif company:
            params['company'] = company
        if linkedin_handle:
            params['linkedin_handle'] = linkedin_handle
        if not linkedin_handle and not (first_name and last_name) and not full_name:
            raise MissingNameError(
                'You must supply a first name AND a last name OR a full name'
            )
        if first_name and last_name:
            params['first_name'] = first_name
            params['last_name'] = last_name
        elif full_name:
            params['full_name'] = full_name
        if max_duration:
            params['max_duration'] = max_duration
        endpoint = self.base_endpoint.format('email-finder')
        res = await self._query_hunter(endpoint, params, raw=raw)
        if raw:
            return res
        return res['email'], res['score']

    async def email_verifier(self, email, raw=False):
        params = {'email': email, 'api_key': self.api_key}
        endpoint = self.base_endpoint.format('email-verifier')
        return await self._query_hunter(endpoint, params, raw=raw)

    async def email_count(self, domain=None, company=None, raw=False):
        params = self.base_params
        if not domain and not company:
            raise MissingCompanyError(
                'You must supply at least a domain name or a company name'
            )
        if domain:
            params['domain'] = domain
        elif company:
            params['company'] = company
        endpoint = self.base_endpoint.format('email-count')
        return await self._query_hunter(endpoint, params, raw=raw)

    async def account_information(self, raw=False):
        params = self.base_params
        endpoint = self.base_endpoint.format('account')
        res = await self._query_hunter(endpoint, params, raw=raw)
        if raw:
            return res
        res['calls']['left'] = res['calls']['available'] - res['calls']['used']
        return res

    async def logo(self, domain, raw=False):
        """
        Returns company logo bytes for a given domain.

        :param domain: The company's domain name. Must be defined.

        :param raw: Gives back the entire response instead of just image bytes.

        :return: Binary logo content (bytes) or a raw response object.
        """
        endpoint = 'https://logos.hunter.io/{}'.format(domain)
        try:
            res = await self.client.get(endpoint)
            res.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code if exc.response else None
            raise HunterApiError(
                message='Hunter logos endpoint returned an error response',
                status_code=status_code,
                payload={'body': exc.response.text} if exc.response is not None else None,
                endpoint=endpoint,
                method='GET',
            ) from exc
        except httpx.HTTPError as exc:
            raise HunterTransportError(
                message='Failed to reach Hunter logos endpoint',
                endpoint=endpoint,
                method='GET',
            ) from exc

        if raw:
            return res
        return res.content
