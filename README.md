[![PyPI version](https://badge.fury.io/py/pyhunter.svg)](https://badge.fury.io/py/pyhunter)

# PyHunter

## A Python wrapper for the Hunter.io v2 API

### Installation

Requirements:

* Python 3 (no Python 2 version)


To install:

```bash
pip install pyhunter
```

For async support:

```bash
pip install "pyhunter[test]"
```

### Usage

Import the PyHunter and instantiate it:

```python
from pyhunter import PyHunter
```

```python
hunter = PyHunter('my_hunter_api_key')
```

You can configure transport behavior:

```python
hunter = PyHunter(
    'my_hunter_api_key',
    timeout=10,
    max_retries=2,
    retry_backoff=0.5,
)
```

### Async Usage

```python
from pyhunter import AsyncPyHunter

async with AsyncPyHunter('my_hunter_api_key') as hunter:
    result = await hunter.domain_search('instagram.com')
```

For long-lived clients:

```python
hunter = AsyncPyHunter('my_hunter_api_key')
try:
    data = await hunter.email_count('instagram.com')
finally:
    await hunter.aclose()
```

---

### Domain Search

Search all email addresses for a given domain:

```python
hunter.domain_search('instagram.com')
```

Pass the company name instead, along with optional filters:

```python
hunter.domain_search(
    company='Instagram',
    limit=5,
    offset=2,
    emails_type='personal',
    seniority='senior,executive',
    department='sales,marketing',
    required_field='full_name',
    verification_status='valid',
)
```

---

### Email Finder

Find a specific person's email address:

```python
email, confidence_score = hunter.email_finder('instagram.com', first_name='Kevin', last_name='Systrom')
```

Use the company name, full name, or LinkedIn handle instead:

```python
hunter.email_finder(company='Instagram', full_name='Kevin Systrom', raw=True)

hunter.email_finder(linkedin_handle='kevinsystrom', max_duration=15)
```

---

### Email Verifier

Check the deliverability of an email address:

```python
hunter.email_verifier('kevin@instagram.com')
```

---

### Email Count

Check how many email addresses Hunter has for a given domain:

```python
hunter.email_count('instagram.com')
# or by company name
hunter.email_count(company='Instagram')
```

---

### Account Information

Check your account information and remaining API calls:

```python
hunter.account_information()
```

PyHunter adds a `calls['left']` field to the response with the number of API calls still available.

---

**NOTE:** By default, all calls return the `data` element of the JSON response. Pass `raw=True` to get the full HTTP response object, including headers (e.g. `X-RateLimit-Remaining`) and the complete response body including `meta`.

Transport and HTTP failures raise typed exceptions:
- `HunterTransportError` for connectivity/timeouts
- `HunterApiError` for non-2xx and malformed API payloads

---

### Enrichment

Look up all information about a person from their email or LinkedIn handle:

```python
hunter.email_enrichment(email='kevin@instagram.com')
hunter.email_enrichment(linkedin_handle='kevinsystrom')
```

Look up all information about a company from its domain:

```python
hunter.company_enrichment('instagram.com')
```

Get combined person + company information in one call:

```python
hunter.combined_enrichment('kevin@instagram.com')
```

All enrichment methods accept a `clearbit_format=True` parameter to return data in Clearbit-compatible format.

---

### Discover

Find companies matching a set of criteria:

```python
hunter.discover(query='Tech companies in Europe')

hunter.discover(
    industry={'include': ['Technology', 'Software']},
    headcount=['51-200', '201-500'],
    headquarters_location={'include': [{'country': 'France'}]},
    limit=50,
)
```

---

### Leads

Get all leads:

```python
hunter.get_leads()
```

Filter leads:

```python
hunter.get_leads(
    offset=2,
    limit=10,
    lead_list_id=1,
    first_name='Kevin',
    last_name='Systrom',
    email='kevin@instagram.com',
    company='Instagram',
    phone_number='0102030405',
    twitter='kevin',
    position='CEO',
    sync_status='success',
    query='kevin',
)
```

Get a specific lead by id:

```python
hunter.get_lead(42)
```

Create a lead:

```python
hunter.create_lead(
    'Quentin', 'Durantay',
    email='quentin.durantay@unicorn.io',
    position='CEO',
    company='Unicorn Consulting',
    company_size=10,
    confidence_score=100,
    website='unicornsaregreat.io',
    country_code='FR',
    postal_code=75000,
    source='theinternet.com',
    linkedin_url='www.linkedin.com/in/masteroftheuniverse',
    phone_number='0102030405',
    twitter='quentindty',
    notes='Met at a conference',
    leads_list_id=1,
    leads_list_ids=[1, 2, 3],
)
```

Create or update a lead by email (upsert):

```python
hunter.upsert_lead('kevin@instagram.com', first_name='Kevin', last_name='Systrom')
```

Update a lead by id:

```python
hunter.update_lead(1, position='CEO in chief', notes='Updated notes')
```

Delete a lead by id:

```python
hunter.delete_lead(42)
```

---

### Leads Lists

Get all leads lists:

```python
hunter.get_leads_lists()
hunter.get_leads_lists(offset=3, limit=2)
```

Get a specific leads list by id:

```python
hunter.get_leads_list(42)
```

Create a leads list:

```python
hunter.create_leads_list('Ultra hot prospects')
```

Update a leads list:

```python
hunter.update_leads_list(42, 'Ultra mega hot prospects')
```

Delete a leads list:

```python
hunter.delete_leads_list(42)
```

---

### Custom Attributes

Manage custom attributes for your leads:

```python
# List all custom attributes
hunter.get_leads_custom_attributes()

# Get a specific custom attribute
hunter.get_leads_custom_attribute(1)

# Create a new custom attribute
hunter.create_leads_custom_attribute('Priority Level')

# Update a custom attribute
hunter.update_leads_custom_attribute(1, 'Deal Priority')

# Delete a custom attribute
hunter.delete_leads_custom_attribute(1)
```

---

### Campaigns (Email Sequences)

Manage your email sequences:

```python
# List all campaigns
hunter.get_campaigns()
hunter.get_campaigns(started=True, limit=10)

# Get recipients of a campaign
hunter.get_campaign_recipients(42)

# Add recipients to a campaign
hunter.add_campaign_recipients(42, emails=['kevin@instagram.com', 'jack@twitter.com'])
hunter.add_campaign_recipients(42, lead_ids=[1, 2, 3])

# Cancel scheduled emails to recipients
hunter.cancel_campaign_recipients(42, emails=['kevin@instagram.com'])

# Start a campaign
hunter.start_campaign(42)
```

---

### Logos

Get a company logo by domain (returns bytes):

```python
logo_bytes = hunter.logo('stripe.com')
```

Async:

```python
from pyhunter import AsyncPyHunter

async with AsyncPyHunter('my_hunter_api_key') as async_hunter:
    logo_bytes = await async_hunter.logo('stripe.com')
```

---

### Information

If you find a bug or something is missing, feel free to open an issue or a pull request on [GitHub](https://github.com/VonStruddle/PyHunter).

### Contribute

It's my first (ever) open-source library! So it can be improved. Feel very welcome to fork it and ask for pull requests if you find something buggy or lacking ;)

### Have a nice day scraping B2B emails with PyHunter!
