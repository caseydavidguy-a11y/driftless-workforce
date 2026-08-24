from datetime import datetime, timezone
import json

from app.models import JobObservation
from app.pipeline import build_employers

# Demo-only records. Production connectors must never label unverified data as verified.
OBSERVATIONS = [
    JobObservation("Great Lakes Cheese", "Production Supervisor", "La Crosse, WI", "manufacturing", datetime.now(timezone.utc), "demo", "", "demo-glc-1", False),
    JobObservation("Great Lakes Cheese", "Production Operator", "West Salem, WI", "manufacturing", datetime.now(timezone.utc), "demo", "", "demo-glc-2", False),
    JobObservation("Great Lakes Cheese", "Maintenance Technician", "West Salem, WI", "skilled trades", datetime.now(timezone.utc), "demo", "", "demo-glc-3", False),
    JobObservation("Trane Technologies", "Operations Supervisor", "La Crosse, WI", "operations", datetime.now(timezone.utc), "demo", "", "demo-trane-1", False),
    JobObservation("Trane Technologies", "Manufacturing Engineer", "La Crosse, WI", "manufacturing", datetime.now(timezone.utc), "demo", "", "demo-trane-2", False),
]

for employer in build_employers(OBSERVATIONS):
    print(json.dumps({
        "employer": employer.name,
        "score": employer.score,
        "priority": employer.priority,
        "openings": employer.opening_count,
        "industries": sorted(employer.industries),
        "locations": sorted(employer.locations),
        "data_status": "DEMO",
    }))
