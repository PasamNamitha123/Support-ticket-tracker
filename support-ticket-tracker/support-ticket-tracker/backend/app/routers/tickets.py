from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models import Ticket, User
from app.schemas.ticket import TicketCreate, TicketOut, TicketStatusUpdate
from app.services.triage import triage_ticket

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


def _get_own_ticket(db: Session, ticket_id: int, user: User) -> Ticket:
    """Every lookup filters by owner, so users can only reach their own tickets."""
    ticket = db.scalar(select(Ticket).where(Ticket.id == ticket_id, Ticket.owner_id == user.id))
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.post("", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
def create_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    triage = triage_ticket(payload.title, payload.description)  # AI, or fallback
    ticket = Ticket(
        title=payload.title,
        description=payload.description,
        owner_id=current_user.id,
        **triage,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("", response_model=list[TicketOut])
def list_tickets(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    stmt = (
        select(Ticket)
        .where(Ticket.owner_id == current_user.id)
        .order_by(Ticket.created_at.desc(), Ticket.id.desc())
    )
    return list(db.scalars(stmt))


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _get_own_ticket(db, ticket_id, current_user)


@router.patch("/{ticket_id}/status", response_model=TicketOut)
def update_status(
    ticket_id: int,
    payload: TicketStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = _get_own_ticket(db, ticket_id, current_user)
    ticket.status = payload.status
    db.commit()
    db.refresh(ticket)
    return ticket
