from config.env import env


EMAIL_BACKEND = env.str("EMAIL_BACKEND", default="")

EMAIL_HOST = env.str("EMAIL_HOST", default="")

EMAIL_PORT = env.int("EMAIL_PORT", default=0)

EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)

EMAIL_HOST_USER = env.str("EMAIL_HOST_USER", default="")

EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", default="")

DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", default="")
