import requests


class MissingCompanyError(Exception):
    pass


class MissingNameError(Exception):
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

    def email_finder(self, domain=None, company=None, first_name=None,
                     last_name=None, full_name=None):
        if not domain and not company:
            raise MissingCompanyError(
                'You must supply at least a domain name or a company name'
            )

        if domain:
            payload = {'domain': domain, 'api_key': self.api_key}
        elif company:
            payload = {'company': company, 'api_key': self.api_key}

        if not(first_name and last_name) and not full_name:
            raise MissingNameError(
                'You must supply a first name AND a last name OR a full name'
            )

        if first_name and last_name:
            payload['first_name'] = first_name
            payload['last_name'] = last_name
        elif full_name:
            payload['full_name'] = full_name

        endpoint = self.base_endpoint.format('email-finder')

        res = self._query_hunter(endpoint, payload)
        email = res['email']
        score = res['score']

        return email, score
