from dataclasses import dataclass
from datetime import datetime, timezone

STATUSES = ("NEW", "RESEARCHING", "CONTACT IDENTIFIED", "CONTACTED", "ENGAGED", "CLIENT")

@dataclass
class OutreachRecord:
    employer: str
    status: str = "NEW"
    contact_role: str = ""
    contact_name: str = ""
    contact_source_url: str = ""
    last_contacted_at: str = ""
    next_action: str = "Research decision-maker"
    notes: str = ""

    def advance(self, status: str, *, contact_name: str = "", contact_source_url: str = "") -> None:
        if status not in STATUSES:
            raise ValueError(f"Unknown status: {status}")
        if status in {"CONTACT IDENTIFIED", "CONTACTED", "ENGAGED", "CLIENT"} and not contact_name and not self.contact_name:
            raise ValueError("A named contact is required before advancing beyond RESEARCHING")
        if contact_source_url and not contact_source_url.startswith(("https://", "http://")):
            raise ValueError("Contact source must be a public HTTP(S) URL")
        self.status = status
        self.contact_name = contact_name or self.contact_name
        self.contact_source_url = contact_source_url or self.contact_source_url
        if status == "CONTACTED":
            self.last_contacted_at = datetime.now(timezone.utc).isoformat()
            self.next_action = "Follow up"
        elif status == "ENGAGED":
            self.next_action = "Qualify recruiting need"
        elif status == "CLIENT":
            self.next_action = "Deliver and expand account"
