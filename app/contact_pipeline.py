"""Contact verification and prospect lifecycle primitives.

The engine intentionally stores research targets and public evidence, not guessed
personal data. A contact becomes verified only when a public source is attached.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum

class ProspectStatus(StrEnum):
    NEW = "new"
    RESEARCHING = "researching"
    CONTACT_IDENTIFIED = "contact_identified"
    CONTACTED = "contacted"
    ENGAGED = "engaged"
    CLIENT = "client"
    DISQUALIFIED = "disqualified"

@dataclass
class PublicContact:
    employer: str
    role: str
    name: str = ""
    source_url: str = ""
    source_type: str = ""
    verified: bool = False
    notes: str = ""
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class ProspectRecord:
    employer: str
    status: ProspectStatus = ProspectStatus.NEW
    contacts: list[PublicContact] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    last_action: str = ""
    next_action: str = "Research decision-maker"

    def add_contact(self, contact: PublicContact) -> None:
        if not contact.source_url:
            raise ValueError("A contact cannot be verified without a public source URL")
        contact.verified = True
        self.contacts.append(contact)
        self.status = ProspectStatus.CONTACT_IDENTIFIED
        self.next_action = "Review evidence and prepare outreach"

    def mark_contacted(self, channel: str) -> None:
        self.status = ProspectStatus.CONTACTED
        self.last_action = f"contacted via {channel}"
        self.next_action = "Follow up or record response"

    def mark_engaged(self, note: str = "") -> None:
        self.status = ProspectStatus.ENGAGED
        if note:
            self.notes.append(note)
        self.next_action = "Qualify recruiting need and schedule next step"
