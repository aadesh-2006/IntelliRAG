from typing import Dict, Any, List
from app.schemas.cricket import CricketValidationResponse
from app.services.cricket.normalizer import CricketNormalizer

class CricketScorecardValidator:
    def validate(self, match_data: Dict[str, Any]) -> CricketValidationResponse:
        warnings: List[str] = []
        errors: List[str] = []

        innings_list = match_data.get("innings", [])
        if not innings_list:
            errors.append("No innings data found in the scorecard.")

        for inn in innings_list:
            inn_no = inn.get("innings_number", 1)
            team = inn.get("team", "Unknown")

            tot_runs = inn.get("total_runs", 0)
            if tot_runs < 0:
                errors.append(f"Innings {inn_no} ({team}): Total runs cannot be negative ({tot_runs}).")

            wickets = inn.get("wickets", 0)
            if wickets < 0 or wickets > 10:
                errors.append(f"Innings {inn_no} ({team}): Wickets count {wickets} is outside standard limit (0-10).")

            overs = inn.get("overs", 0.0)
            overs_str = str(overs)
            if "." in overs_str:
                parts = overs_str.split(".")
                if len(parts) > 1 and int(parts[1]) > 5:
                    warnings.append(f"Innings {inn_no} ({team}): Overs decimal fraction {parts[1]} is greater than 5 balls.")

            batting = inn.get("batting_performances", [])
            bat_runs_sum = sum(b.get("runs", 0) for b in batting)
            extras_total = inn.get("extras_total", 0)

            for b in batting:
                p_name = b.get("player_name", "Batsman")
                r = b.get("runs", 0)
                bls = b.get("balls", 0)
                fours = b.get("fours", 0)
                sixes = b.get("sixes", 0)

                if r < 0:
                    errors.append(f"Innings {inn_no}: {p_name} runs cannot be negative ({r}).")
                if bls < 0:
                    errors.append(f"Innings {inn_no}: {p_name} balls cannot be negative ({bls}).")

                boundary_runs = (fours * 4) + (sixes * 6)
                if boundary_runs > r:
                    warnings.append(f"Innings {inn_no}: {p_name} boundary runs ({boundary_runs}) exceed total runs ({r}).")

            if batting and tot_runs > 0:
                diff = abs(tot_runs - (bat_runs_sum + extras_total))
                if diff > 15:
                    warnings.append(f"Innings {inn_no} ({team}): Innings total ({tot_runs}) deviates from batsmen sum + extras ({bat_runs_sum + extras_total}) by {diff} runs.")

            bowling = inn.get("bowling_performances", [])
            for bowl in bowling:
                b_name = bowl.get("player_name", "Bowler")
                w = bowl.get("wickets", 0)
                rc = bowl.get("runs_conceded", 0)
                if w < 0 or w > 10:
                    errors.append(f"Innings {inn_no}: {b_name} wickets count ({w}) is invalid.")
                if rc < 0:
                    errors.append(f"Innings {inn_no}: {b_name} runs conceded cannot be negative ({rc}).")

        is_valid = len(errors) == 0
        return CricketValidationResponse(
            is_valid=is_valid,
            warnings=warnings,
            errors=errors
        )

cricket_validator = CricketScorecardValidator()
