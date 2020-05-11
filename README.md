# git-wild-hunt
A tool to hunt for credentials in the Github wild AKA git*hunt
![](static/wildhunt.jpg)


### Usage

```
usage: git-wild-hunt.py [-h] -s SEARCH [-c CONFIG] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -s SEARCH, --search SEARCH
                        search to execute
  -c CONFIG, --config CONFIG
                        config file path
  -v, --version         shows current git-wild-hunt version
```

### Installation 

* requirements:     `virtualenv, python3`

1. `git clone https://github.com/d1vious/git-wild-hunt && cd git-wild-hunt` clone project and cd into the project dir
2. `pip install virtualenv && virtualenv -p python3 venv && source venv/bin/activate && pip install -r requirements.txt` create virtualenv and install requirements

Continue to [configuring](#configuration) a github API key

### Configuration [`git-wild-hunt.conf`]()

Make sure you set a Github token if you need to create one for your account follow [these](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line) instructions. 

```
[global]
github_token = ''
# github token for searching

output = results.json
# stores matches in JSON here

log_path = git-wild-hunt.log
# Sets the log_path for the logging file

log_level = INFO
# Sets the log level for the logging
# Possible values: INFO, ERROR

regexes = regexes.json
# regexes to check the git wild hunt search against
```

### Github search examples

* Searching for Jenkins credentials
* Find GCP JWT token files
* Find secrets in .circleci 
* Find AWS secrets
* Find ...


### [`regexes.json`]()
This file contains all the regexes that will be used to check against the raw content filed returned for a [search](#github-search-examples). Feel free to add/modify and include any specific ones that match the credential you are trying to find. 

List of checked credentials via regex:

*   AWS API Key
*   Amazon AWS Access Key ID
*   Amazon MWS Auth Token
*   Facebook Access Token
*   Facebook OAuth
*   Generic API Key
*   Generic Secret
*   GitHub
*   Google (GCP) Service-account
*   Google API Key
*   Google Cloud Platform API Key
*   Google Cloud Platform OAuth
*   Google Drive API Key
*   Google Drive OAuth
*   Google Gmail API Key
*   Google Gmail OAuth
*   Google OAuth Access Token
*   Google YouTube API Key
*   Google YouTube OAuth
*   Heroku API Key
*   MailChimp API Key
*   Mailgun API Key
*   PGP private key block
*   Password in URL
*   PayPal Braintree Access Token
*   Picatic API Key
*   RSA private key
*   SSH (DSA) private key
*   SSH (EC) private key
*   Slack Token
*   Slack Webhook
*   Square Access Token
*   Square OAuth Secret
*   Stripe API Key
*   Stripe Restricted API Key
*   Twilio API Key
*   Twitter Access Token
*   Twitter OAuth

### Author

Jose Hernandez [@d1vious]()
Rod Soto [@rsoto]()

### Credits & References

Inspiration [shhgit](https://github.com/eth0izzle/shhgit/)