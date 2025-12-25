import os

import environ


# Initialize environment variables
env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = environ.Path(__file__) - 2

# Load environment variables from .env file
env.read_env(os.path.join(BASE_DIR, ".env"))
