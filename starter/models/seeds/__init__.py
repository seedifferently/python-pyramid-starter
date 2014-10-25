# Load seeders
from .users import seed_users

def seed_all():
    """Helper method for running all seeds."""
    seed_users()
