import re
import uuid
from typing import Dict, Any, List, Optional, Tuple
from app.services.cricket.normalizer import CricketNormalizer

class CricketScorecardExtractor:
    def extract_match_metadata(self, text: str) -> Dict[str, Any]:
        meta: Dict[str, Any] = {
            "team_1": "Team 1",
            "team_2": "Team 2",
            "venue": None,
            "city": None,
            "match_date": None,
            "tournament": None,
            "match_number": None,
            "format": "T20",
            "toss_winner": None,
            "toss_decision": None,
            "winner": None,
            "result_text": None,
            "player_of_match": None,
        }

        vs_match = re.search(r"([A-Za-z\s]+?)\s+(?:vs|v)\s+([A-Za-z\s]+?)(?:,|-|\n|\(|at|$)", text, re.IGNORECASE)
        if vs_match:
            t1 = vs_match.group(1).strip()
            t2 = vs_match.group(2).strip()
            if len(t1) > 2 and len(t2) > 2 and not t1.lower().startswith("match"):
                meta["team_1"] = t1[:90]
                meta["team_2"] = t2[:90]

        venue_match = re.search(r"(?:venue|stadium|ground|at):?\s*([A-Za-z0-9\s,]+?)(?:\n|date|match|$)", text, re.IGNORECASE)
        if venue_match:
            meta["venue"] = venue_match.group(1).strip()[:250]

        date_match = re.search(r"(?:date|played on):?\s*([A-Za-z0-9\s,-]+?)(?:\n|time|venue|$)", text, re.IGNORECASE)
        if date_match:
            meta["match_date"] = date_match.group(1).strip()[:50]

        tourn_match = re.search(r"(?:tournament|series|competition|league):?\s*([A-Za-z0-9\s,-]+?)(?:\n|$)", text, re.IGNORECASE)
        if tourn_match:
            meta["tournament"] = tourn_match.group(1).strip()[:250]
        elif "ipl" in text.lower():
            meta["tournament"] = "Indian Premier League"
        elif "world cup" in text.lower():
            meta["tournament"] = "ICC World Cup"

        if re.search(r"\b(t20i?|twenty20)\b", text, re.IGNORECASE):
            meta["format"] = "T20"
        elif re.search(r"\b(odi|one day)\b", text, re.IGNORECASE):
            meta["format"] = "ODI"
        elif re.search(r"\b(test|first class)\b", text, re.IGNORECASE):
            meta["format"] = "TEST"

        toss_match = re.search(r"([A-Za-z\s]+?)\s+won the toss and (?:elected|opted|chose) to\s+(bat|bowl|field)", text, re.IGNORECASE)
        if toss_match:
            meta["toss_winner"] = toss_match.group(1).strip()[:100]
            dec = toss_match.group(2).lower()
            meta["toss_decision"] = "bat" if "bat" in dec else "bowl"

        result_match = re.search(r"(?:^|\n|[\.\;]\s*)([A-Za-z0-9 ]+?\s+won by\s+[0-9]+?\s+(?:runs|wickets)|match tied|no result|[A-Za-z0-9 ]+?\s+won the match)", text, re.IGNORECASE)
        if result_match:
            meta["result_text"] = result_match.group(1).strip()[:250]
            winner_m = re.search(r"^([A-Za-z0-9 ]+?)\s+won", meta["result_text"], re.IGNORECASE)
            if winner_m:
                meta["winner"] = winner_m.group(1).strip()[:100]

        pom_match = re.search(r"(?:player|man) of the match:?\s*([A-Za-z\s\.]+?)(?:\n|\(|$|,)", text, re.IGNORECASE)
        if pom_match:
            meta["player_of_match"] = pom_match.group(1).strip()[:100]

        return meta

    def extract(
        self,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
        extracted_text: Optional[str] = None,
        extracted_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        text = extracted_text or ""
        metadata = self.extract_match_metadata(text)
        innings_list: List[Dict[str, Any]] = []

        tables: List[Dict[str, Any]] = []
        if extracted_metadata and "pages" in extracted_metadata:
            for page_idx, page in enumerate(extracted_metadata["pages"], 1):
                for t in page.get("tables", []):
                    t_copy = dict(t)
                    t_copy["page"] = page.get("page_number", page_idx)
                    tables.append(t_copy)

        if tables:
            innings_list = self._extract_from_tables(tables, metadata, text)

        if not innings_list:
            innings_list = self._extract_from_text(text, metadata)

        if not innings_list:
            innings_list = [
                {
                    "innings_number": 1,
                    "team": metadata.get("team_1") or "Team 1",
                    "total_runs": 0,
                    "wickets": 0,
                    "overs": 20.0,
                    "run_rate": 0.0,
                    "extras_total": 0,
                    "extras_wides": 0,
                    "extras_no_balls": 0,
                    "extras_byes": 0,
                    "extras_leg_byes": 0,
                    "extras_penalty": 0,
                    "batting_performances": [],
                    "bowling_performances": [],
                }
            ]

        if len(innings_list) >= 1:
            metadata["team_1"] = innings_list[0]["team"]
        if len(innings_list) >= 2:
            metadata["team_2"] = innings_list[1]["team"]

        return {
            "match_id": uuid.uuid4(),
            "document_id": document_id,
            "user_id": user_id,
            "metadata": metadata,
            "innings": innings_list
        }

    def _extract_from_tables(
        self,
        tables: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        raw_text: str
    ) -> List[Dict[str, Any]]:
        innings_list: List[Dict[str, Any]] = []
        current_innings: Optional[Dict[str, Any]] = None

        for table in tables:
            headers = [str(h).strip().lower() for h in table.get("headers", [])]
            rows = table.get("rows", [])
            page_num = table.get("page", 1)

            header_str = " ".join(headers)
            is_batting = any(k in header_str for k in ["r", "runs", "strike rate", "sr", "4s", "6s"]) and not ("econ" in header_str or "maidens" in header_str)
            is_bowling = any(k in header_str for k in ["econ", "economy", "maidens", "overs", "w"]) and ("o" in headers or "overs" in header_str)

            if is_batting:
                team_name = metadata["team_1"] if len(innings_list) == 0 else metadata["team_2"]
                current_innings = {
                    "innings_number": len(innings_list) + 1,
                    "team": team_name,
                    "total_runs": 0,
                    "wickets": 0,
                    "overs": 20.0,
                    "run_rate": 0.0,
                    "extras_total": 0,
                    "extras_wides": 0,
                    "extras_no_balls": 0,
                    "extras_byes": 0,
                    "extras_leg_byes": 0,
                    "extras_penalty": 0,
                    "batting_performances": [],
                    "bowling_performances": [],
                }
                innings_list.append(current_innings)

                col_map = self._map_batting_cols(headers)
                pos = 1
                for row in rows:
                    if not row:
                        continue
                    first_cell = str(row[0]).strip()
                    if any(ig in first_cell.lower() for ig in ["extras", "total", "did not bat", "fall of wickets"]):
                        if "extras" in first_cell.lower():
                            current_innings["extras_total"] = CricketNormalizer.safe_int(" ".join(str(c) for c in row))
                        if "total" in first_cell.lower():
                            totals = self._parse_total_cell(" ".join(str(c) for c in row))
                            if totals:
                                current_innings["total_runs"] = totals[0]
                                current_innings["wickets"] = totals[1]
                                current_innings["overs"] = totals[2]
                        continue

                    name = first_cell
                    if not name or len(name) < 2:
                        continue

                    dismissal = str(row[col_map["dismissal"]]).strip() if "dismissal" in col_map and col_map["dismissal"] < len(row) else "not out"
                    runs = CricketNormalizer.safe_int(row[col_map["r"]]) if "r" in col_map and col_map["r"] < len(row) else 0
                    balls = CricketNormalizer.safe_int(row[col_map["b"]]) if "b" in col_map and col_map["b"] < len(row) else runs
                    fours = CricketNormalizer.safe_int(row[col_map["4s"]]) if "4s" in col_map and col_map["4s"] < len(row) else 0
                    sixes = CricketNormalizer.safe_int(row[col_map["6s"]]) if "6s" in col_map and col_map["6s"] < len(row) else 0
                    sr = CricketNormalizer.calculate_strike_rate(runs, balls)

                    current_innings["batting_performances"].append({
                        "player_name": name,
                        "runs": runs,
                        "balls": balls,
                        "fours": fours,
                        "sixes": sixes,
                        "strike_rate": sr,
                        "dismissal": dismissal,
                        "batting_position": pos,
                        "source_page": page_num,
                        "source_text": " | ".join(str(c) for c in row),
                    })
                    pos += 1

            elif is_bowling and current_innings:
                col_map = self._map_bowling_cols(headers)
                for row in rows:
                    if not row:
                        continue
                    first_cell = str(row[0]).strip()
                    if any(ig in first_cell.lower() for ig in ["total", "extras"]):
                        continue

                    name = first_cell
                    if not name or len(name) < 2:
                        continue

                    overs = CricketNormalizer.safe_float(row[col_map["o"]]) if "o" in col_map and col_map["o"] < len(row) else 0.0
                    maidens = CricketNormalizer.safe_int(row[col_map["m"]]) if "m" in col_map and col_map["m"] < len(row) else 0
                    runs = CricketNormalizer.safe_int(row[col_map["r"]]) if "r" in col_map and col_map["r"] < len(row) else 0
                    wickets = CricketNormalizer.safe_int(row[col_map["w"]]) if "w" in col_map and col_map["w"] < len(row) else 0
                    econ = CricketNormalizer.calculate_economy(runs, overs)

                    current_innings["bowling_performances"].append({
                        "player_name": name,
                        "overs": overs,
                        "maidens": maidens,
                        "runs_conceded": runs,
                        "wickets": wickets,
                        "economy": econ,
                        "wides": 0,
                        "no_balls": 0,
                        "source_page": page_num,
                        "source_text": " | ".join(str(c) for c in row),
                    })

        for inn in innings_list:
            if inn["total_runs"] == 0 and inn["batting_performances"]:
                bat_runs = sum(b["runs"] for b in inn["batting_performances"])
                inn["total_runs"] = bat_runs + inn["extras_total"]
            if inn["wickets"] == 0 and inn["batting_performances"]:
                w_count = sum(1 for b in inn["batting_performances"] if not CricketNormalizer.is_not_out(b["dismissal"]))
                inn["wickets"] = min(w_count, 10)
            if inn["overs"] > 0:
                inn["run_rate"] = CricketNormalizer.calculate_run_rate(inn["total_runs"], inn["overs"])

        return innings_list

    def _extract_from_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        innings_list: List[Dict[str, Any]] = []
        inn_blocks = re.split(r"(?:Innings\s*([12]|One|Two)|([A-Za-z\s]+?)\s+Innings)", text, flags=re.IGNORECASE)

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        inn_1 = {
            "innings_number": 1,
            "team": metadata["team_1"],
            "total_runs": 0,
            "wickets": 0,
            "overs": 20.0,
            "run_rate": 0.0,
            "extras_total": 0,
            "extras_wides": 0,
            "extras_no_balls": 0,
            "extras_byes": 0,
            "extras_leg_byes": 0,
            "extras_penalty": 0,
            "batting_performances": [],
            "bowling_performances": [],
        }

        pos = 1
        for line in lines:
            bat_match = re.search(r"^([A-Za-z\s\.]+?)\s+(c\s+[A-Za-z\s]+|b\s+[A-Za-z\s]+|lbw\s+b\s+[A-Za-z\s]+|not out|run out|st\s+[A-Za-z\s]+)?\s*(\d+)\s+(\d+)(?:\s+(\d+))?(?:\s+(\d+))?", line, re.IGNORECASE)
            if bat_match:
                name = bat_match.group(1).strip()
                if name.lower() in ["extras", "total", "did not bat", "fall of wickets", "bowling"]:
                    continue
                dism = bat_match.group(2).strip() if bat_match.group(2) else "not out"
                r = CricketNormalizer.safe_int(bat_match.group(3))
                b = CricketNormalizer.safe_int(bat_match.group(4))
                fours = CricketNormalizer.safe_int(bat_match.group(5)) if bat_match.group(5) else 0
                sixes = CricketNormalizer.safe_int(bat_match.group(6)) if bat_match.group(6) else 0
                sr = CricketNormalizer.calculate_strike_rate(r, b)

                inn_1["batting_performances"].append({
                    "player_name": name,
                    "runs": r,
                    "balls": b,
                    "fours": fours,
                    "sixes": sixes,
                    "strike_rate": sr,
                    "dismissal": dism,
                    "batting_position": pos,
                    "source_page": 1,
                    "source_text": line,
                })
                pos += 1

            bowl_match = re.search(r"^([A-Za-z\s\.]+?)\s+(\d+\.?\d*)\s+(\d+)\s+(\d+)\s+(\d+)", line)
            if bowl_match and "batting" not in line.lower():
                name = bowl_match.group(1).strip()
                if name.lower() not in ["extras", "total", "target"]:
                    overs = CricketNormalizer.safe_float(bowl_match.group(2))
                    m = CricketNormalizer.safe_int(bowl_match.group(3))
                    r = CricketNormalizer.safe_int(bowl_match.group(4))
                    w = CricketNormalizer.safe_int(bowl_match.group(5))
                    econ = CricketNormalizer.calculate_economy(r, overs)

                    inn_1["bowling_performances"].append({
                        "player_name": name,
                        "overs": overs,
                        "maidens": m,
                        "runs_conceded": r,
                        "wickets": w,
                        "economy": econ,
                        "wides": 0,
                        "no_balls": 0,
                        "source_page": 1,
                        "source_text": line,
                    })

            total_m = re.search(r"(?:total|score):?\s*(\d+)(?:/|-)(\d+)\s*(?:\(?([0-9\.]+)\s*ov(?:ers)?\)?)?", line, re.IGNORECASE)
            if total_m:
                inn_1["total_runs"] = CricketNormalizer.safe_int(total_m.group(1))
                inn_1["wickets"] = CricketNormalizer.safe_int(total_m.group(2))
                if total_m.group(3):
                    inn_1["overs"] = CricketNormalizer.safe_float(total_m.group(3))

        if inn_1["batting_performances"] or inn_1["bowling_performances"]:
            if inn_1["total_runs"] == 0 and inn_1["batting_performances"]:
                inn_1["total_runs"] = sum(b["runs"] for b in inn_1["batting_performances"])
            if inn_1["overs"] > 0:
                inn_1["run_rate"] = CricketNormalizer.calculate_run_rate(inn_1["total_runs"], inn_1["overs"])
            innings_list.append(inn_1)

        return innings_list

    def _map_batting_cols(self, headers: List[str]) -> Dict[str, int]:
        mapping = {}
        for idx, h in enumerate(headers):
            h_clean = h.lower().strip()
            if h_clean in ["r", "runs", "run"]:
                mapping["r"] = idx
            elif h_clean in ["b", "balls", "bf"]:
                mapping["b"] = idx
            elif h_clean in ["4s", "4", "fours"]:
                mapping["4s"] = idx
            elif h_clean in ["6s", "6", "sixes"]:
                mapping["6s"] = idx
            elif h_clean in ["sr", "s/r", "strike rate"]:
                mapping["sr"] = idx
            elif h_clean in ["dismissal", "how out", "wicket", "status"]:
                mapping["dismissal"] = idx
        return mapping

    def _map_bowling_cols(self, headers: List[str]) -> Dict[str, int]:
        mapping = {}
        for idx, h in enumerate(headers):
            h_clean = h.lower().strip()
            if h_clean in ["o", "overs", "ov"]:
                mapping["o"] = idx
            elif h_clean in ["m", "maidens", "maid"]:
                mapping["m"] = idx
            elif h_clean in ["r", "runs", "rc"]:
                mapping["r"] = idx
            elif h_clean in ["w", "wickets", "wkts"]:
                mapping["w"] = idx
            elif h_clean in ["econ", "economy", "er"]:
                mapping["econ"] = idx
        return mapping

    def _parse_total_cell(self, cell_text: str) -> Optional[Tuple[int, int, float]]:
        m = re.search(r"(\d+)(?:/|-)(\d+)(?:\s*\(?([0-9\.]+)\s*ov\)?)?", cell_text, re.IGNORECASE)
        if m:
            r = CricketNormalizer.safe_int(m.group(1))
            w = CricketNormalizer.safe_int(m.group(2))
            o = CricketNormalizer.safe_float(m.group(3)) if m.group(3) else 20.0
            return (r, w, o)
        return None

cricket_extractor = CricketScorecardExtractor()
