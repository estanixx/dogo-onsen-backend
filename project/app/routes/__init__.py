from app.routes.service import ServiceRouter
from app.routes.employee import EmployeeRouter
from app.routes.banquet import BanquetRouter
from app.routes.reservation import ReservationRouter
from app.routes.spirit import SpiritRouter
from app.routes.spirit_type import SpiritTypeRouter
from app.routes.files import FileRouter
from app.routes.venue_account import VenueAccountRouter
from app.routes.item import ItemRouter
from app.routes.item_intake import ItemIntakeRouter
from app.routes.private_venue import PrivateVenueRouter
from app.routes.utils import UtilsRouter
from app.routes.deposit import DepositRouter

__all__ = [
    "ServiceRouter",
    "EmployeeRouter",
    "BanquetRouter",
    "ReservationRouter",
    "SpiritRouter",
    "SpiritTypeRouter",
    "FileRouter",
    "VenueAccountRouter",
    "ItemRouter",
    "ItemIntakeRouter",
    "PrivateVenueRouter",
    "UtilsRouter",
    "DepositRouter",
]
