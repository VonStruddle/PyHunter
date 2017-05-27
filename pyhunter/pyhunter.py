import requests

from .exceptions import MissingCompanyError, MissingNameError


class PyHunter:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_params = {'api_key': api_key}
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
        """
        Return all the email addresses found for a given domain.

        :param domain: The domain on which to search for emails. Must be
        defined if company is not.

        :param company: The name of the company on which to search for emails.
        Must be defined if domain is not.

        :param limit: The maximum number of emails to give back. Default is 10.

        :param offset: The number of emails to skip. Default is 0.

        :param emails_type: The type of emails to give back. Can be one of
        'personal' or 'generic'.

        :return: Full payload of the query as a dict, with email addresses
        found.
        """
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
        """
        Find the email address of a person given its name and company's domain.

        :param domain: The domain of the company where the person works. Must
        be defined if company is not.

        :param company: The name of the company where the person works. Must
        be defined if domain is not.

        :param first_name: The first name of the person. Must be defined if
        full_name is not.

        :param last_name: The last name of the person. Must be defined if
        full_name is not.

        :param full_name: The full name of the person. Must be defined if
        first_name AND last_name are not.

        :param raw: Gives back the entire response instead of just email and score.

        :return: email and score as a tuple.
        """
        params = self.base_params

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
        """
        Verify the deliverability of a given email adress.abs

        :param email: The email adress to check.

        :return: Full payload of the query as a dict.
        """
        params = {'email': email, 'api_key': self.api_key}

        endpoint = self.base_endpoint.format('email-verifier')

        return self._query_hunter(endpoint, params)

    def email_count(self, domain):
        """
        Give back the number of email adresses Hunter has for this domain.

        :param domain: The domain to check.

        :return: Full payload of the query as a dict.
        """
        params = {'domain': domain}

        endpoint = self.base_endpoint.format('email-count')

        return self._query_hunter(endpoint, params)

    def account_information(self):
        """
        Gives the information about the account associated with the api_key.

        :return: Full payload of the query as a dict.
        """
        params = self.base_params

        endpoint = self.base_endpoint.format('account')

        res = self._query_hunter(endpoint, params)
        res['calls']['left'] = res['calls']['available'] - res['calls']['used']

        return res

    def get_leads(self, offset=None, limit=None, lead_list_id=None,
                  first_name=None, last_name=None, email=None, company=None,
                  phone_number=None, twitter=None):
        """
        Gives back all the leads saved in your account.

        :param offset: Number of leads to skip.

        :param limit: Maximum number of leads to return.

        :param lead_list_id: Id of a lead list to query leads on.

        :param first_name: First name to filter on.

        :param last_name: Last name to filter on.

        :param email: Email to filter on.

        :param company: Company to filter on.

        :param phone_number: Phone number to filter on.

        :param twitter: Twitter account to filter on.

        :return: All leads found as a dict.
        """
        args = locals()
        args_params = dict((key, value) for key, value in args.items() if value
                           is not None)
        args_params.pop('self')

        params = self.base_params
        params.update(args_params)

        endpoint = self.base_endpoint.format('leads')

        return self._query_hunter(endpoint, params)

    def get_lead(self, lead_id):
        """
        Get a specific lead saved on your account.

        :param lead_id: Id of the lead to search. Must be defined.

        :return: Lead found as a dict.
        """
        params = self.base_params

        endpoint = self.base_endpoint.format('leads/' + str(lead_id))

        return self._query_hunter(endpoint, params)

    def create_lead(self, first_name, last_name, email=None, position=None,
                    company=None, company_industry=None, company_size=None,
                    confidence_score=None, website=None, country_code=None,
                    postal_code=None, source=None, linkedin_url=None,
                    phone_number=None, twitter=None, leads_list_id=None):
        """
        Create a lead on your account.

        :param first_name: The first name of the lead to create. Must be
        defined.

        :param last_name: The last name of the lead to create. Must be defined.

        :param email: The email of the lead to create.

        :param position: The professional position of the lead to create.

        :param company: The company of the lead to create.

        :param company_industry: The type of industry of the company where the
        lead works.

        :param company_size: The size of the company where the lead works.

        :param confidence_score: The confidence score of the lead's email.

        :param website: The website of the lead's company.

        :param country_code: The country code of the lead's company.

        :param postal_code: The postal code of the lead's company.

        :param source: The source of the lead's email.

        :param linkedin_url: The URL of the lead's LinkedIn profile.

        :param phone_number: The phone number of the lead to create.

        :param twitter: The lead's Twitter account.

        :param leads_list_id: The id of the leads list where to save the new
        lead.

        :return: The newly created lead as a dict.
        """
        args = locals()
        payload = dict((key, value) for key, value in args.items() if value
                       is not None)
        payload.pop('self')

        params = self.base_params

        endpoint = self.base_endpoint.format('leads')

        return self._query_hunter(endpoint, params, 'post', payload)

    def update_lead(self, lead_id, first_name, last_name, email=None, position=None,
                    company=None, company_industry=None, company_size=None,
                    confidence_score=None, website=None, country_code=None,
                    postal_code=None, source=None, linkedin_url=None,
                    phone_number=None, twitter=None, leads_list_id=None):
        """
        Update a lead on your account.

        :param lead_id: The id of the lead to update. Must be defined.

        :param first_name: The first name of the lead to update. Must be
        defined.

        :param last_name: The last name of the lead to update. Must be defined.

        :param email: The email of the lead to update.

        :param position: The professional position of the lead to update.

        :param company: The company of the lead to update.

        :param company_industry: The type of industry of the company where the
        lead works.

        :param company_size: The size of the company where the lead works.

        :param confidence_score: The confidence score of the lead's email.

        :param website: The website of the lead's company.

        :param country_code: The country code of the lead's company.

        :param postal_code: The postal code of the lead's company.

        :param source: The source of the lead's email.

        :param linkedin_url: The URL of the lead's LinkedIn profile.

        :param phone_number: The phone number of the lead to update.

        :param twitter: The lead's Twitter account.

        :param leads_list_id: The id of the leads list where to save the new
        lead.

        :return: The newly updated lead as a dict.
        """
        args = locals()
        payload = dict((key, value) for key, value in args.items() if value
                       is not None)
        payload.pop('self')
        payload.pop('lead_id')

        params = self.base_params

        endpoint = self.base_endpoint.format('leads/' + str(lead_id))

        return self._query_hunter(endpoint, params, 'put', payload)

    def delete_lead(self, lead_id):
        """
        Delete a specific lead saved on your account.

        :param lead_id: Id of the lead to delete. Must be defined.

        :return: 204 Response.
        """
        params = self.base_params

        endpoint = self.base_endpoint.format('leads/' + str(lead_id))

        return self._query_hunter(endpoint, params, 'delete')

    def get_leads_lists(self, offset=None, limit=None):
        """
        Gives back all the leads lists saved on your account.

        :param offset: Number of lists to skip.

        :param limit: Maximum number of lists to return.

        :return: Leads lists found as a dict.
        """
        params = self.base_params

        if offset:
            params['offset'] = offset
        if limit:
            params['limit'] = limit

        endpoint = self.base_endpoint.format('leads_lists')

        return self._query_hunter(endpoint, params)

    def get_leads_list(self, leads_list_id):
        """
        Gives back a specific leads list saved on your account.

        :param leads_list_id: The id of the list to return.

        :return: Leads list found as a dict.
        """
        params = self.base_params

        endpoint = self.base_endpoint.format(
            'leads_lists/' +
            str(leads_list_id)
        )

        return self._query_hunter(endpoint, params)

    def create_leads_list(self, name, team_id=None):
        """
        Create a leads list.

        :param name: Name of the list to create. Must be defined.

        :param team_id: The id of the list to share this list with.

        :return: The created leads list as a dict.
        """
        params = self.base_params

        payload = {'name': name}
        if team_id:
            payload['team_id'] = team_id

        endpoint = self.base_endpoint.format('leads_lists')

        return self._query_hunter(endpoint, params, 'post', payload)

    def update_leads_list(self, name, team_id=None):
        """
        Update a leads list.

        :param name: Name of the list to update. Must be defined.

        :param team_id: The id of the list to share this list with.

        :return: 204 Response.
        """
        params = self.base_params

        payload = {'name': name}
        if team_id:
            payload['team_id'] = team_id

        endpoint = self.base_endpoint.format('leads_lists')

        return self._query_hunter(endpoint, params, 'put', payload)

    def delete_leads_list(self, leads_list_id):
        """
        Delete a leads list.

        :param leads_list_id: The id of the list to delete.

        :return: 204 Response.
        """
        params = self.base_params

        endpoint = self.base_endpoint.format(
            'leads_lists/' +
            str(leads_list_id)
        )

        return self._query_hunter(endpoint, params, 'delete')
