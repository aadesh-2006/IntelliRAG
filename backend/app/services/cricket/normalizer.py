import re
import math
from typing import Optional, Tuple, Any

class CricketNormalizer:
    @staticmethod
    def parse_overs_to_balls(overs_val: float | str | int) -> int:
        if isinstance(overs_val, (int, float)):
            val_str = str(overs_val)
        else:
            val_str = str(overs_val).strip()

        if "." in val_str:
            parts = val_str.split(".")
            try:
                overs = int(parts[0])
                balls = int(parts[1]) if parts[1] else 0
                if balls > 5:
                    balls = min(balls, 5)
                return (overs * 6) + balls
            except ValueError:
                return 0
        else:
            try:
                return int(val_str) * 6
            except ValueError:
                return 0

    @staticmethod
    def balls_to_overs_float(balls: int) -> float:
        overs = balls // 6
        rem = balls % 6
        return float(f"{overs}.{rem}")

    @staticmethod
    def calculate_economy(runs_conceded: int, overs_val: float | str | int) -> Optional[float]:
        balls = CricketNormalizer.parse_overs_to_balls(overs_val)
        if balls <= 0:
            return 0.0
        econ = (runs_conceded / balls) * 6.0
        return round(econ, 2)

    @staticmethod
    def calculate_strike_rate(runs: int, balls: int) -> Optional[float]:
        if balls <= 0:
            return 0.0
        sr = (runs / balls) * 100.0
        return round(sr, 2)

    @staticmethod
    def calculate_run_rate(total_runs: int, overs_val: float | str | int) -> Optional[float]:
        balls = CricketNormalizer.parse_overs_to_balls(overs_val)
        if balls <= 0:
            return 0.0
        rr = (total_runs / balls) * 6.0
        return round(rr, 2)

    @staticmethod
    def is_not_out(dismissal: Optional[str]) -> bool:
        if not dismissal:
            return True
        d = dismissal.strip().lower()
        if d in ("not out", "dnb", "did not bat", "retired hurt", "absent hurt", "batting", "*", "-"):
            return True
        if d.endswith("*") or d.startswith("*"):
            return True
        return False

    @staticmethod
    def clean_player_name(name: str) -> str:
        cleaned = re.sub(r"[\*\(c\)\(wk\)\(c & wk\)\(w\)]", "", name, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned if cleaned else name.strip()

    @staticmethod
    def safe_int(val: Any, default: int = 0) -> int:
        if val is None:
            return default
        try:
            s = str(val).strip()
            digits = re.search(r"-?\d+", s)
            if digits:
                return int(digits.group(0))
            return default
        except Exception:
            return default

    @staticmethod
    def safe_float(val: Any, default: float = 0.0) -> float:
        if val is None:
            return default
        try:
            s = str(val).strip()
            digits = re.search(r"-?\d+(\.\d+)?", s)
            if digits:
                return float(digits.group(0))
            return default
        except Exception:
            return default
