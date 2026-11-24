"""Validación determinista, independiente del modelo."""
from typing import Literal
from pydantic import BaseModel, Field, field_validator
import re

class TicketProposal(BaseModel):
    title: str = Field(min_length=8, max_length=120)
    description: str = Field(min_length=12, max_length=2000)
    category: Literal['acceso','seguridad','hardware','software','otros']
    priority: Literal['baja','media','alta'] = 'media'

    @field_validator('title','description')
    @classmethod
    def no_control_characters(cls, v):
        if re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', v):
            raise ValueError('Texto contiene caracteres de control')
        return v.strip()

class ApprovedTicket(TicketProposal):
    request_id: str = Field(min_length=8, max_length=80)
    approved: bool


def require_approval(ticket: ApprovedTicket):
    if ticket.approved is not True:
        raise PermissionError('Confirmación obligatoria antes de escribir en Cosmos DB')
    return ticket
