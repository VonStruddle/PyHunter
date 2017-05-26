import requests


class MissingCompanyError(Exception):
    pass


class MissingNameError(Exception):
    pass


class PyHunter:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_endpoint = 'https://api.hunter.io/v2/{}'

    def _query_hunter(self, endpoint, params, request_type='get',
                      payload=None):
        if not payload:
            res = getattr(requests, request_type)(endpoint, params=params)
        else:
            res = getattr(requests, request_type)(endpoint, params=params,
                                                  json=payload)
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
            params = {'domain': domain, 'api_key': self.api_key}
        elif company:
            params = {'company': company, 'api_key': self.api_key}

        if limit:
            params['limit'] = limit

        if offset:
            params['offset'] = offset

        if emails_type:
            params['type'] = emails_type

        endpoint = self.base_endpoint.format('domain-search')

        return self._query_hunter(endpoint, params)

    def email_finder(self, domain=None, company=None, first_name=None,
                     last_name=None, full_name=None, raw=False):
        params = {'api_key': self.api_key}

        if not domain and not company:
            raise MissingCompanyError(
                'You must supply at least a domain name or a company name'
            )

        if domain:
            params['domain'] = domain
        elif company:
            params['company'] = company

        if not(first_name and last_name) and not full_name:
            raise MissingNameError(
                'You must supply a first name AND a last name OR a full name'
            )

        if first_name and last_name:
            params['first_name'] = first_name
            params['last_name'] = last_name
        elif full_name:
            params['full_name'] = full_name

        endpoint = self.base_endpoint.format('email-finder')

        res = self._query_hunter(endpoint, params)
        if raw:
            return res

        email = res['email']
        score = res['score']

        return email, score

    def email_verifier(self, email):
        params = {'email': email, 'api_key': self.api_key}

        endpoint = self.base_endpoint.format('email-verifier')

        return self._query_hunter(endpoint, params)

    def email_count(self, domain):
        params = {'domain': domain}

        endpoint = self.base_endpoint.format('email-count')

        return self._query_hunter(endpoint, params)

    def account_information(self):
        params = {'api_key': self.api_key}

        endpoint = self.base_endpoint.format('account')

        res = self._query_hunter(endpoint, params)
        res['calls']['left'] = res['calls']['available'] - res['calls']['used']

        return res

    def get_leads(self):
        params = {'api_key': self.api_key}

        endpoint = self.base_endpoint.format('leads')

        return self._query_hunter(endpoint, params)

    def get_lead(self, lead_id):
        params = {'api_key': self.api_key}

        endpoint = self.base_endpoint.format('leads/' + str(lead_id))

        return self._query_hunter(endpoint, params)

    def create_lead(self, first_name, last_name, email=None, position=None,
                    company=None, company_industry=None, company_size=None,
                    confidence_score=None, website=None, country_code=None,
                    postal_code=None, source=None, linkedin_url=None,
                    phone_number=None, twitter=None, leads_list_id=None):
        args = locals()
        payload = dict((key, value) for key, value in args.items() if value
                       is not None)
        payload.pop('self')

        params = {'api_key': self.api_key}

        endpoint = self.base_endpoint.format('leads')

        return self._query_hunter(endpoint, params, 'post', payload)

    def update_lead(self, first_name, last_name, email=None, position=None,
                    company=None, company_industry=None, company_size=None,
                    confidence_score=None, website=None, country_code=None,
                    postal_code=None, source=None, linkedin_url=None,
                    phone_number=None, twitter=None, leads_list_id=None):
        args = locals()
        payload = dict((key, value) for key, value in args.items() if value
                       is not None)
        payload.pop('self')

        params = {'api_key': self.api_key}

        endpoint = self.base_endpoint.format('leads')

        return self._query_hunter(endpoint, params, 'put', payload)

    def delete_lead(self, lead_id):
        params = {'api_key': self.api_key}

        endpoint = self.base_endpoint.format('leads/' + str(lead_id))

        return self._query_hunter(endpoint, params, 'delete')
