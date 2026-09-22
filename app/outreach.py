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

from app.outreach import build_outreach_draft


def build_outreach_draft(prospect: dict, contact: dict, sender_name: str = "Casey") -> dict:
    """Create a personalized draft from verified evidence; never send it."""
    if not contact or not contact.get("name") or not contact.get("source_url"):
        raise ValueError("A verified contact with a source URL is required before drafting outreach")
    employer = prospect.get("employer") or "your company"
    openings = int(prospect.get("opening_count", 0) or 0)
    roles = prospect.get("target_roles") or []
    role_text = ", ".join(str(r) for r in roles[:3]) if roles else "the roles you are hiring for"
    opening_text = f"{openings} current opening{'s' if openings != 1 else ''}" if openings else "current hiring activity"
    angle = (prospect.get("outreach_angle") or "supporting local hiring needs").rstrip(".")
    first_name = str(contact["name"]).split()[0]
    body = (f"Hi {first_name},\\n\\nI’m reaching out because I noticed {employer} has {opening_text}, "
            f"including activity around {role_text}. {angle}.\\n\\n"
            f"Driftless Workforce Group helps employers with recruiting for operations, manufacturing, warehouse, "
            f"skilled trades, hospitality, and leadership roles. If hiring support is useful, I’d be glad to "
            f"compare notes and see where we could help.\\n\\nBest,\\n{sender_name}")
    return {"channel":"email","state":"draft","recipient_name":contact["name"],"recipient_title":contact.get("title", ""),
            "recipient_source_url":contact["source_url"],"subject":f"Recruiting support for {employer}","body":body,
            "approval_required":True,"auto_send":False}
