# Import every model here so SQLAlchemy registers the tables.
from app.models.tickets import Ticket
from app.models.user import User

__all__ = ["User", "Ticket"]
