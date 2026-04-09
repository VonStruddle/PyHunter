from time import sleep

import requests

from ._core import parse_data_payload
from .exceptions import (
    HunterApiError,
    HunterTransportError,
    MissingCompanyError,
    MissingNameError,
)


class PyHunter:
    def __init__(self, api_key, timeout=10, max_retries=2, retry_backoff=0.5,
                 session=None):
        self.api_key = api_key
        self.base_endpoint = 'https://api.hunter.io/v2/{}'
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.session = session or requests.Session()

    @property
    def base_params(self):
        return {'api_key': self.api_key}

    def _query_hunter(self, endpoint, params, request_type='get',
                      payload=None, headers=None, raw=False):
        request_kwargs = dict(
            params=params,
            json=payload,
            headers=headers,
            timeout=self.timeout,
        )
        attempt = 0
        last_error = None
        while attempt <= self.max_retries:
            try:
                res = getattr(self.session, request_type)(endpoint, **request_kwargs)
                res.raise_for_status()
                break
            except requests.exceptions.HTTPError as exc:
                status_code = exc.response.status_code if exc.response else None
                should_retry = status_code in (429, 500, 502, 503, 504)
                if should_retry and attempt < self.max_retries:
                    sleep(self.retry_backoff * (2 ** attempt))
                    attempt += 1
                    continue
                message = 'Hunter API returned an error response'
                payload_data = None
                if exc.response is not None:
                    try:
                        payload_data = exc.response.json()
                    except ValueError:
                        payload_data = {'body': exc.response.text}
                raise HunterApiError(
                    message=message,
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
            except requests.exceptions.RequestException as exc:
                last_error = exc
                if attempt < self.max_retries:
                    sleep(self.retry_backoff * (2 ** attempt))
                    attempt += 1
                    continue
                raise HunterTransportError(
                    message='Failed to reach Hunter API',
                    endpoint=endpoint,
                    method=request_type.upper(),
                ) from exc
        else:
            raise HunterTransportError(
                message='Failed to reach Hunter API',
                endpoint=endpoint,
                method=request_type.upper(),
            ) from last_error

        if raw:
            return res

        return parse_data_payload(res, endpoint, request_type.upper())

    def domain_search(self, domain=None, company=None, limit=None, offset=None,
                      seniority=None, department=None, emails_type=None,
                      required_field=None, verification_status=None, raw=False):
        """
        Return all the email addresses found for a given domain.

        :param domain: The domain on which to search for emails. Must be
        defined if company is not.

        :param company: The name of the company on which to search for emails.
        Must be defined if domain is not.

        :param limit: The maximum number of emails to give back. Default is 10.

        :param offset: The number of emails to skip. Default is 0.

        :param seniority: The seniority level of the owners of emails to give back. Can be 'junior', 'senior',
        'executive' or a combination of them delimited by a comma.

        :param department: The department where the owners of the emails to give back work. Can be 'executive', 'it',
        'finance', 'management', 'sales', 'legal', 'support', 'hr', 'marketing', 'communication' or a combination of
        them delimited by a comma.

        :param emails_type: The type of emails to give back. Can be one of
        'personal' or 'generic'.

        :param required_field: Only return emails with this field present. Can be
        'full_name', 'position', or 'phone_number'.

        :param verification_status: Only return emails with this verification status.
        Can be 'valid', 'accept_all', or 'unknown'.

        :param raw: Gives back the entire response instead of just the 'data'.

        :return: Full payload of the query as a dict, with email addresses
        found.
        """
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

        return self._query_hunter(endpoint, params, raw=raw)

    def email_finder(self, domain=None, company=None, first_name=None,
                     last_name=None, full_name=None, linkedin_handle=None,
                     max_duration=None, raw=False):
        """
        Find the email address of a person given its name and company's domain.

        :param domain: The domain of the company where the person works. Must
        be defined if company and linkedin_handle are not.

        :param company: The name of the company where the person works. Must
        be defined if domain and linkedin_handle are not.

        :param first_name: The first name of the person. Must be defined if
        full_name is not.

        :param last_name: The last name of the person. Must be defined if
        full_name is not.

        :param full_name: The full name of the person. Must be defined if
        first_name AND last_name are not.

        :param linkedin_handle: The LinkedIn handle of the person (e.g.
        'johnsmith'). Can be used instead of domain/company + name.

        :param max_duration: Maximum duration of the request in seconds (3-20,
        default 10).

        :param raw: Gives back the entire response instead of just email and score.

        :return: email and score as a tuple.
        """
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

        if not linkedin_handle:
            if not(first_name and last_name) and not full_name:
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

        res = self._query_hunter(endpoint, params, raw=raw)
        if raw:
            return res

        email = res['email']
        score = res['score']

        return email, score

    def email_verifier(self, email, raw=False):
        """
        Verify the deliverability of a given email address.

        :param email: The email address to check.

        :param raw: Gives back the entire response instead of just the 'data'.

        :return: Full payload of the query as a dict.
        """
        params = {'email': email, 'api_key': self.api_key}

        endpoint = self.base_endpoint.format('email-verifier')

        return self._query_hunter(endpoint, params, raw=raw)

    def email_count(self, domain=None, company=None, raw=False):
        """
        Give back the number of email addresses Hunter has for this domain/company.

        :param domain: The domain of the company where the person works. Must
        be defined if company is not. If both 'domain' and 'company' are given,
        the 'domain' will be used.

        :param company: The name of the company where the person works. Must
        be defined if domain is not.

        :param raw: Gives back the entire response instead of just the 'data'.

        :return: Full payload of the query as a dict.
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

        endpoint = self.base_endpoint.format('email-count')

        return self._query_hunter(endpoint, params, raw=raw)

    def account_information(self, raw=False):
        """
        Gives the information about the account associated with the api_key.

        :param raw: Gives back the entire response instead of just the 'data'.

        :return: Full payload of the query as a dict.
        """
        params = self.base_params

        endpoint = self.base_endpoint.format('account')

        res = self._query_hunter(endpoint, params, raw=raw)
        if raw:
            return res

        res['calls']['left'] = res['calls']['available'] - res['calls']['used']

        return res

    # ---------------------------------------------------------------------------
    # Enrichment
    # ---------------------------------------------------------------------------

    def email_enrichment(self, email=None, linkedin_handle=None,
                         clearbit_format=None, raw=False):
        """
        Returns all information about a person given their email or LinkedIn handle.

        :param email: The person's email address. Must be defined if
        linkedin_handle is not.

        :param linkedin_handle: The person's LinkedIn profile handle. Must be
        defined if email is not.

        :param clearbit_format: If True, returns the response in Clearbit format.

        :param raw: Gives back the entire response instead of just the 'data'.

        :return: Full payload of the query as a dict.
        """
        params = {'api_key': self.api_key}

        if email:
            params['email'] = email
        elif linkedin_handle:
            params['linkedin_handle'] = linkedin_handle
        else:
            raise MissingCompanyError(
                'You must supply at least an email or a LinkedIn handle'
            )

        if clearbit_format is not None:
            params['clearbit_format'] = clearbit_format

        endpoint = self.base_endpoint.format('people/find')

        return self._query_hunter(endpoint, params, raw=raw)

    def company_enrichment(self, domain, clearbit_format=None, raw=False):
        """
        Returns all information about a company given its domain.

        :param domain: The company's domain name. Must be defined.

        :param clearbit_format: If True, returns the response in Clearbit format.

        :param raw: Gives back the entire response instead of just the 'data'.

        :return: Full payload of the query as a dict.
        """
        params = {'domain': domain, 'api_key': self.api_key}

        if clearbit_format is not None:
            params['clearbit_format'] = clearbit_format

        endpoint = self.base_endpoint.format('companies/find')

        return self._query_hunter(endpoint, params, raw=raw)

    def combined_enrichment(self, email, clearbit_format=None, raw=False):
        """
        Returns information about both a person and their company given the
        person's email address.

        :param email: The person's email address. Must be defined.

        :param clearbit_format: If True, returns the response in Clearbit format.

        :param raw: Gives back the entire response instead of just the 'data'.

        :return: Full payload of the query as a dict with 'person' and
        'company' keys.
        """
        params = {'email': email, 'api_key': self.api_key}

        if clearbit_format is not None:
            params['clearbit_format'] = clearbit_format

        endpoint = self.base_endpoint.format('combined/find')

        return self._query_hunter(endpoint, params, raw=raw)

    # ---------------------------------------------------------------------------
    # Discover
    # ---------------------------------------------------------------------------

    def discover(self, query=None, organization=None, similar_to=None,
                 headquarters_location=None, industry=None, headcount=None,
                 company_type=None, year_founded=None, keywords=None,
                 technology=None, funding=None, limit=None, offset=None,
                 raw=False):
        """
        Returns companies matching a set of criteria.

        :param query: Natural language search query (e.g. 'Tech companies in Europe').

        :param organization: Filter by domain and/or company name. Dict with
        optional 'domain' (list) and 'name' (list) keys.

        :param similar_to: Find companies similar to this one (Premium). Dict
        with 'domain' or 'name' key.

        :param headquarters_location: Filter by location. Dict with 'include'
        and/or 'exclude' lists, each containing dicts with optional 'continent',
        'country', 'state', 'city' keys.

        :param industry: Filter by industry. Dict with 'include' and/or
        'exclude' lists.

        :param headcount: Filter by company size. List of ranges such as
        '1-10', '11-50', '51-200', etc.

        :param company_type: Filter by company type. Dict with 'include'
        and/or 'exclude' lists.

        :param year_founded: Filter by founding year (Premium). Dict with
        optional 'from', 'to', 'include', 'exclude' keys.

        :param keywords: Filter by keywords (Premium). Dict with 'include'
        and/or 'exclude' lists and optional 'match' ('any'/'all').

        :param technology: Filter by technologies used (Premium). Dict with
        'include' and/or 'exclude' lists and optional 'match' ('any'/'all').

        :param funding: Filter by funding (Premium). Dict with optional
        'series', 'amount', and 'date' keys.

        :param limit: Maximum number of companies to return (default 100).

        :param offset: Number of companies to skip (default 0).

        :param raw: Gives back the entire response instead of just the 'data'.

        :return: Full payload of the query as a dict with a list of companies.
        """
        params = {'api_key': self.api_key}

        payload = {}
        if query is not None:
            payload['query'] = query
        if organization is not None:
            payload['organization'] = organization
        if similar_to is not None:
            payload['similar_to'] = similar_to
        if headquarters_location is not None:
            payload['headquarters_location'] = headquarters_location
        if industry is not None:
            payload['industry'] = industry
        if headcount is not None:
            payload['headcount'] = headcount
        if company_type is not None:
            payload['company_type'] = company_type
        if year_founded is not None:
            payload['year_founded'] = year_founded
        if keywords is not None:
            payload['keywords'] = keywords
        if technology is not None:
            payload['technology'] = technology
        if funding is not None:
            payload['funding'] = funding
        if limit is not None:
            payload['limit'] = limit
        if offset is not None:
            payload['offset'] = offset

        endpoint = self.base_endpoint.format('discover')

        return self._query_hunter(endpoint, params, 'post', payload, raw=raw)

    # ---------------------------------------------------------------------------
    # Leads
    # ---------------------------------------------------------------------------

    def get_leads(self, offset=None, limit=None, lead_list_id=None,
                  first_name=None, last_name=None, email=None, company=None,
                  phone_number=None, twitter=None, position=None,
                  industry=None, website=None, country_code=None,
                  company_size=None, source=None, linkedin_url=None,
                  sync_status=None, sending_status=None,
                  verification_status=None, last_activity_at=None,
                  last_contacted_at=None, custom_attributes=None, query=None):
        """
        Gives back all the leads saved in your account.

        :param offset: Number of leads to skip.

        :param limit: Maximum number of leads to return (1-1000, default 20).

        :param lead_list_id: Id of a lead list to query leads on.

        :param first_name: First name to filter on.

        :param last_name: Last name to filter on.

        :param email: Email to filter on.

        :param company: Company to filter on.

        :param phone_number: Phone number to filter on.

        :param twitter: Twitter account to filter on.

        :param position: Job position to filter on.

        :param industry: Industry to filter on.

        :param website: Website to filter on.

        :param country_code: Country code to filter on.

        :param company_size: Company size to filter on.

        :param source: Lead source to filter on.

        :param linkedin_url: LinkedIn URL to filter on.

        :param sync_status: Filter by sync status ('pending', 'error', 'success').

        :param sending_status: Filter by sending status. Can be a list of values
        ('clicked', 'opened', 'sent', 'pending', 'error', 'bounced',
        'unsubscribed', 'replied').

        :param verification_status: Filter by verification status. Can be a list
        of values ('accept_all', 'disposable', 'invalid', 'unknown', 'valid',
        'webmail', 'pending').

        :param last_activity_at: Filter by last activity date.

        :param last_contacted_at: Filter by last contacted date.

        :param custom_attributes: Dict of custom attribute slugs and values to
        filter on.

        :param query: Search query matching first_name, last_name, or email.

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
                    phone_number=None, twitter=None, notes=None,
                    leads_list_id=None, leads_list_ids=None):
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

        :param notes: Notes about the lead.

        :param leads_list_id: The id of the leads list where to save the new
        lead.

        :param leads_list_ids: A list of leads list ids to assign the lead to
        multiple lists at once.

        :return: The newly created lead as a dict.
        """
        args = locals()
        payload = dict((key, value) for key, value in args.items() if value
                       is not None)
        payload.pop('self')

        params = self.base_params

        endpoint = self.base_endpoint.format('leads')

        return self._query_hunter(endpoint, params, 'post', payload)

    def upsert_lead(self, email, first_name=None, last_name=None,
                    position=None, company=None, company_industry=None,
                    company_size=None, confidence_score=None, website=None,
                    country_code=None, postal_code=None, source=None,
                    linkedin_url=None, phone_number=None, twitter=None,
                    notes=None, leads_list_id=None, leads_list_ids=None):
        """
        Create or update a lead based on their email address (upsert).
        If a lead with the given email already exists, it is updated; otherwise
        a new lead is created.

        :param email: The email of the lead. Must be defined.

        :param first_name: The first name of the lead.

        :param last_name: The last name of the lead.

        :param position: The professional position of the lead.

        :param company: The company of the lead.

        :param company_industry: The type of industry of the company where the
        lead works.

        :param company_size: The size of the company where the lead works.

        :param confidence_score: The confidence score of the lead's email.

        :param website: The website of the lead's company.

        :param country_code: The country code of the lead's company.

        :param postal_code: The postal code of the lead's company.

        :param source: The source of the lead's email.

        :param linkedin_url: The URL of the lead's LinkedIn profile.

        :param phone_number: The phone number of the lead.

        :param twitter: The lead's Twitter account.

        :param notes: Notes about the lead.

        :param leads_list_id: The id of the leads list to save the lead to.

        :param leads_list_ids: A list of leads list ids to assign the lead to
        multiple lists at once.

        :return: The created or updated lead as a dict.
        """
        args = locals()
        payload = dict((key, value) for key, value in args.items() if value
                       is not None)
        payload.pop('self')

        params = self.base_params

        endpoint = self.base_endpoint.format('leads')

        return self._query_hunter(endpoint, params, 'put', payload)

    def update_lead(self, lead_id, first_name=None, last_name=None, email=None,
                    position=None, company=None, company_industry=None,
                    company_size=None, confidence_score=None, website=None,
                    country_code=None, postal_code=None, source=None,
                    linkedin_url=None, phone_number=None, twitter=None,
                    notes=None, leads_list_id=None, leads_list_ids=None):
        """
        Update a lead on your account.

        :param lead_id: The id of the lead to update. Must be defined.

        :param first_name: The first name of the lead to update.

        :param last_name: The last name of the lead to update.

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

        :param notes: Notes about the lead.

        :param leads_list_id: The id of the leads list where to save the
        lead.

        :param leads_list_ids: A list of leads list ids to assign the lead to
        multiple lists at once.

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

    # ---------------------------------------------------------------------------
    # Leads Lists
    # ---------------------------------------------------------------------------

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

    def update_leads_list(self, leads_list_id, name, team_id=None):
        """
        Update a leads list.

        :param leads_list_id: The id of the list to update.

        :param name: Name of the list to update. Must be defined.

        :param team_id: The id of the list to share this list with.

        :return: 204 Response.
        """
        params = self.base_params

        payload = {'name': name}
        if team_id:
            payload['team_id'] = team_id

        endpoint = self.base_endpoint.format(
            'leads_lists/' + str(leads_list_id))

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

    # ---------------------------------------------------------------------------
    # Custom Attributes
    # ---------------------------------------------------------------------------

    def get_leads_custom_attributes(self, raw=False):
        """
        Returns all custom attributes defined on your account.

        :param raw: Gives back the entire response instead of just the 'data'.

        :return: All custom attributes as a dict.
        """
        params = self.base_params

        endpoint = self.base_endpoint.format('leads_custom_attributes')

        return self._query_hunter(endpoint, params, raw=raw)

    def get_leads_custom_attribute(self, attribute_id, raw=False):
        """
        Returns a specific custom attribute.

        :param attribute_id: The id of the custom attribute. Must be defined.

        :param raw: Gives back the entire response instead of just the 'data'.

        :return: The custom attribute as a dict.
        """
        params = self.base_params

        endpoint = self.base_endpoint.format(
            'leads_custom_attributes/' + str(attribute_id)
        )

        return self._query_hunter(endpoint, params, raw=raw)

    def create_leads_custom_attribute(self, label, raw=False):
        """
        Creates a new custom attribute.

        :param label: The name of the custom attribute. Must be unique and
        defined.

        :param raw: Gives back the entire response instead of just the 'data'.

        :return: The newly created custom attribute as a dict.
        """
        params = self.base_params
        payload = {'label': label}

        endpoint = self.base_endpoint.format('leads_custom_attributes')

        return self._query_hunter(endpoint, params, 'post', payload, raw=raw)

    def update_leads_custom_attribute(self, attribute_id, label, raw=False):
        """
        Updates a custom attribute.

        :param attribute_id: The id of the custom attribute to update. Must be
        defined.

        :param label: The new name for the custom attribute. Must be defined.

        :param raw: Gives back the entire response instead of just the 'data'.

        :return: 204 Response.
        """
        params = self.base_params
        payload = {'label': label}

        endpoint = self.base_endpoint.format(
            'leads_custom_attributes/' + str(attribute_id)
        )

        return self._query_hunter(endpoint, params, 'put', payload, raw=raw)

    def delete_leads_custom_attribute(self, attribute_id):
        """
        Deletes a custom attribute.

        :param attribute_id: The id of the custom attribute to delete. Must be
        defined.

        :return: 204 Response.
        """
        params = self.base_params

        endpoint = self.base_endpoint.format(
            'leads_custom_attributes/' + str(attribute_id)
        )

        return self._query_hunter(endpoint, params, 'delete')

    # ---------------------------------------------------------------------------
    # Campaigns (Email Sequences)
    # ---------------------------------------------------------------------------

    def get_campaigns(self, started=None, archived=None, limit=None,
                      offset=None, raw=False):
        """
        Returns all email sequences (campaigns) on your account.

        :param started: If True, only return started sequences.

        :param archived: If True, only return archived sequences.

        :param limit: Maximum number of sequences to return (1-100, default 20).

        :param offset: Number of sequences to skip.

        :param raw: Gives back the entire response instead of just the 'data'.

        :return: All campaigns as a dict.
        """
        params = self.base_params

        if started is not None:
            params['started'] = started
        if archived is not None:
            params['archived'] = archived
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset

        endpoint = self.base_endpoint.format('campaigns')

        return self._query_hunter(endpoint, params, raw=raw)

    def get_campaign_recipients(self, campaign_id, limit=None, offset=None,
                                raw=False):
        """
        Returns all recipients of a specific email sequence.

        :param campaign_id: The id of the campaign. Must be defined.

        :param limit: Maximum number of recipients to return (1-100, default 20).

        :param offset: Number of recipients to skip.

        :param raw: Gives back the entire response instead of just the 'data'.

        :return: All recipients as a dict.
        """
        params = self.base_params

        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset

        endpoint = self.base_endpoint.format(
            'campaigns/' + str(campaign_id) + '/recipients'
        )

        return self._query_hunter(endpoint, params, raw=raw)

    def add_campaign_recipients(self, campaign_id, emails=None,
                                lead_ids=None, raw=False):
        """
        Adds recipients to an email sequence.

        :param campaign_id: The id of the campaign. Must be defined.

        :param emails: A single email string or a list of up to 50 email
        addresses to add.

        :param lead_ids: A list of up to 50 lead ids to add.

        :param raw: Gives back the entire response instead of just the 'data'.

        :return: Number of recipients added and any skipped recipients.
        """
        params = self.base_params
        payload = {}

        if emails is not None:
            payload['emails'] = emails
        if lead_ids is not None:
            payload['lead_ids'] = lead_ids

        endpoint = self.base_endpoint.format(
            'campaigns/' + str(campaign_id) + '/recipients'
        )

        return self._query_hunter(endpoint, params, 'post', payload, raw=raw)

    def cancel_campaign_recipients(self, campaign_id, emails, raw=False):
        """
        Cancels scheduled emails to recipients of a campaign.

        :param campaign_id: The id of the campaign. Must be defined.

        :param emails: A single email string or a list of up to 50 email
        addresses whose scheduled emails should be cancelled.

        :param raw: Gives back the entire response instead of just the 'data'.

        :return: Dict with cancelled recipients and message count.
        """
        params = self.base_params
        payload = {'emails': emails}

        endpoint = self.base_endpoint.format(
            'campaigns/' + str(campaign_id) + '/recipients'
        )

        return self._query_hunter(endpoint, params, 'delete', payload, raw=raw)

    def start_campaign(self, campaign_id, raw=False):
        """
        Starts a draft email sequence.

        :param campaign_id: The id of the campaign to start. Must be defined.

        :param raw: Gives back the entire response instead of just the 'data'.

        :return: Dict with a confirmation message and recipient count.
        """
        params = self.base_params

        endpoint = self.base_endpoint.format(
            'campaigns/' + str(campaign_id) + '/start'
        )

        return self._query_hunter(endpoint, params, 'post', raw=raw)

    # ---------------------------------------------------------------------------
    # Logos
    # ---------------------------------------------------------------------------

    def logo(self, domain, raw=False):
        """
        Returns company logo bytes for a given domain.

        :param domain: The company's domain name. Must be defined.

        :param raw: Gives back the entire response instead of just image bytes.

        :return: Binary logo content (bytes) or a raw response object.
        """
        endpoint = 'https://logos.hunter.io/{}'.format(domain)
        try:
            res = self.session.get(endpoint, timeout=self.timeout)
            res.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            status_code = exc.response.status_code if exc.response else None
            raise HunterApiError(
                message='Hunter logos endpoint returned an error response',
                status_code=status_code,
                payload={'body': exc.response.text} if exc.response is not None else None,
                endpoint=endpoint,
                method='GET',
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise HunterTransportError(
                message='Failed to reach Hunter logos endpoint',
                endpoint=endpoint,
                method='GET',
            ) from exc

        if raw:
            return res
        return res.content
