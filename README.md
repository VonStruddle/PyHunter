# PyHunter

## A Python wrapper for the Hunter.io v2 API

### Installation

Requirements:

* Python 3 (no Python 2 version, c'mon, we're in 2017!)


To install:

```bash
pip install pyhunter
```

### Usage

PyHunter supports all the methods from the [Hunter.io](https://hunter.io/api/v2/docs) v2 API:

* `domain_search`
* `email_finder`
* `email_verifier`
* `email_count`
* `account_information`

PyHunter also supports new methods from the `Leads` and `Leads Lists` APIs.

### How to use PyHunter

Import the PyHunter and instantiate it:

```python
from pyhunter import PyHunter
```

```python
hunter = PyHunter('my_hunter_api_key')
```

You can search all the email adresses for a given domain:

```python
hunter.domain_search('instagram.com')
```

You can also pass the company name, along with optional parameters:

```python
hunter.domain_search(company='Instragram', limit=5, offset=2, emails_type='personal')
```

You can find a specific email adress:

```python
email, confidence_score = hunter.email_finder('instragram.com', first_name='Kevin', last_name='Systrom')
```

You can also use the company name and the full name instead, along with raw to get the full response:

```python
hunter.email_finder(company='Instragram', full_name='Kevin Systrom', raw=True)
```

You can check the deliverability of a given email adress:

```python
hunter.email_verifier('kevin@instagram.com')
```

You can check how many email addresses Hunter has for a given domain:

```python
hunter.email_count('instagram.com')
```

You can also use a company name if the domain is unknown::
```python
hunter.email_count(company='Instagram')
```

When both domain and company are passed, the domain will be used:
```python
hunter.email_count(domain='instagram.com', company='Instagram')
```

And you can finally check your account information (PyHunter adds the number of calls still available in the payload):

```python
hunter.account_information()
```


**NOTE:** By default, all of the calls (except `email_verifier()`) return the 'data' element
of the JSON response. You can get the "raw" response by passing `raw=True` to those calls.
This gives access to the response headers, e.g. `X-RateLimit-Remaining` returned for the
`domain_search()` call, and also the complete response body, including `meta`.


### But that's not all folks! As the v2 API added Leads and Leads Lists, these methods are also available on PyHunter

#### Leads methods

You can get all your leads:

```python
hunter.get_leads()
```

Or filter the leads you want using these arguments:

```python
hunter.get_leads(offset=2, limit=10, lead_list_id=1, first_name='Kevin', last_name='Systrom', email='kevin@instragram.com', company='Instagram', phone_number=0102030405, twitter='kevin')
```

You can also get a specific lead by giving its id:

```python
hunter.get_lead(42)
```

You can create a lead:

```python
hunter.create_lead('Quentin', 'Durantay', email='quentin.durantay@unicorn.io', position='CEO', company='Unicorn Consulting', company_size=10, confidence_score=100, website='unicornsaregreat.io', contry_code='FR', postal_code=75000, source='theinternet.com', linkedin_url='www.linkedin.com/in/masteroftheuniverse', phone_number=0102030405, twitter='quentindty', leads_list_id=1)
```

You can update a lead by giving its id and the parameters to change (same as creation):

```python
hunter.update_lead(1, position='CEO in chief')
```

And you can also delete a lead by giving its id:

```python
hunter.delete_lead(42)
```

#### Leads Lists methods

You can get all your Leads Lists:

```python
hunter.get_leads_lists()
```

And filter the results with these arguments:

```python
hunter.get_leads_lists(offset=3, limit=2)
```

You can get a specific Leads List by giving its id:

```python
hunter.get_leads_list(42)
```

You can create a Leads Lists:

```python
hunter.create_leads_list('Ultra hot prospects', team_id=1)
```

You can update a Leads List by giving its id:

```python
hunter.update_leads_list(42, 'Ultra mega hot prospects', team_id=2)
```

And you can finally delete a Leads Lists by giving its id:

```python
hunter.delete_leads_list(42)
```

### Information

This library is still in development, don't hesitate to share bugs if you find some (nomally it's good, but you never know :p ).

### Contribute

It's my first (ever) open-source library! So it can be improved. Feel very welcome to fork it and ask for pull requests if you find something buggy or lacking ;)

### Have a nice day scraping B2B emails with PyHunter!
