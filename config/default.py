# Flask Config
SECRET_KEY = '' # flask secret key for session encryption
DEBUG = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///data/evechem.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# EVE SSO Config
EVESSO_CLIENT_KEY = '' # EVE single sign-on application client key
EVESSO_CLIENT_SECRET = '' # EVE single sign-on application client secret
EVESSO_API_URL = 'https://esi.tech.ccp.is/latest/'
EVESSO_TOKEN_URL = 'https://login.eveonline.com/oauth/token/'
EVESSO_AUTH_URL = 'https://login.eveonline.com/oauth/authorize/'
EVESSO_VERIFY_URL = 'https://login.eveonline.com/oauth/verify/'
EVESSO_ACCESS_TOKEN_METHOD = 'POST'
EVESSO_REQUEST_TOKEN_METHOD = 'GET'
EVESSO_SCOPES = '' # EVE single sign-on application requested scopes

# EVE Chem API Config
EVECHEM_API_URL = 'https://api.evechem.com/' # Url for the API
