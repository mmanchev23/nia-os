from config.env import env


SALT_KEY = env.str("SALT_KEY", "change-me-if-you-want-secure-fernet-keys")
