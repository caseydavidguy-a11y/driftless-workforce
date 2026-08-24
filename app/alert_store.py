import json
from pathlib import Path
from .signals import HiringSignal


def serialize_signals(signals_by_employer: dict[str, list[HiringSignal]]) -> dict:
    return {
        "signals": [
            {"employer": employer, **signal.__dict__}
            for employer, signals in signals_by_employer.items()
            for signal in signals
        ]
    }


def write_signals(path: str | Path, signals_by_employer: dict[str, list[HiringSignal]]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(serialize_signals(signals_by_employer), indent=2), encoding="utf-8")
