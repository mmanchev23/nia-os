from config.env import env


AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_URL = "/account/login/"

LOGIN_REDIRECT_URL = "/"

ACCOUNT_FORMS = {"signup": "apps.authentication.forms.SignupForm"}

ACCOUNT_LOGIN_METHODS = {"username", "email"}

ACCOUNT_EMAIL_VERIFICATION = "mandatory"

ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = "/account/login"

ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = "/"

ACCOUNT_SIGNUP_FIELDS = ["username*", "email*", "password1*", "password2*"]

SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

SOCIALACCOUNT_CONFIRM_REDIRECT = False

SOCIALACCOUNT_STORE_TOKENS = True

SOCIALACCOUNT_LOGIN_ON_GET = True

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "EMAIL_AUTHENTICATION": True,
        "FETCH_USERINFO": True,
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
        "OAUTH_PKCE_ENABLED": True,
        "APP": {
            "client_id": env.str("GOOGLE_CLIENT_ID"),
            "secret": env.str("GOOGLE_CLIENT_SECRET"),
            "key": "",
        },
    }
}
