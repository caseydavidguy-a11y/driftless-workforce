import re
import unicodedata


def canonicalize_employer(name: str) -> str:
    """Create a stable matching key for employer names."""
    value = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    value = value.lower().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    value = re.sub(r"\b(incorporated|inc|llc|ltd|corp|corporation|company|co)\b", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def normalize_industry(industry: str) -> str:
    value = industry.strip().lower()
    aliases = {
        "manufacturing": "manufacturing",
        "production": "manufacturing",
        "warehouse": "warehouse",
        "warehousing": "warehouse",
        "operations": "operations",
        "operations management": "operations",
        "skilled trades": "skilled trades",
        "trades": "skilled trades",
        "hospitality": "hospitality",
        "hotel": "hospitality",
        "restaurant": "hospitality",
        "leadership": "leadership",
        "management": "leadership",
    }
    return aliases.get(value, value)
