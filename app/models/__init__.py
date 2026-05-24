from app.models.appointment import Appointment
from app.models.house import House, HouseImage
from app.models.lease import Contract, Payment
from app.models.log import SystemLog
from app.models.maintenance import Complaint, RepairRequest
from app.models.message import Message
from app.models.news import News
from app.models.user import User

__all__ = [
    "Appointment",
    "Complaint",
    "Contract",
    "House",
    "HouseImage",
    "Message",
    "News",
    "Payment",
    "RepairRequest",
    "SystemLog",
    "User",
]

