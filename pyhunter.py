import requests


class MissingCompanyError(Exception):
    pass


class PyHunter:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_endpoint = 'https://api.hunter.io/v2/{}'

    def _query_hunter(self, url, payload):
        res = requests.get(url, params=payload)
        res.raise_for_status()

        data = res.json()['data']

        return data

    def domain_search(self, domain=None, company=None, limit=None, offset=None,
                      emails_type=None):
        if not domain and not company:
            raise MissingCompanyError(
                'You must supply at least a domain name or a company name'
            )

        if domain:
            payload = {'domain': domain, 'api_key': self.api_key}
        elif company:
            payload = {'company': company, 'api_key': self.api_key}

        if limit:
            payload['limit'] = limit

        if offset:
            payload['offset'] = offset

        if emails_type:
            payload['type'] = emails_type

        endpoint = self.base_endpoint.format('domain-search')

        return self._query_hunter(endpoint, payload)['emails']
