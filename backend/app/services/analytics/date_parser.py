import re
import datetime
from typing import Tuple, Optional

class DateParser:
    def parse_expression(self, text: str) -> Tuple[Optional[datetime.datetime], Optional[datetime.datetime], Optional[str]]:
        if not text:
            return None, None, None

        q = text.lower()
        now = datetime.datetime.now(datetime.timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + datetime.timedelta(days=1)

        if "today" in q:
            return today_start, today_end, "today"

        if "yesterday" in q:
            yesterday_start = today_start - datetime.timedelta(days=1)
            return yesterday_start, today_start, "yesterday"

        next_days_match = re.search(r'next\s+(\d+)\s+days?', q)
        if next_days_match:
            days = int(next_days_match.group(1))
            days = max(1, min(days, 365))
            return now, now + datetime.timedelta(days=days), f"next {days} days"

        last_days_match = re.search(r'(?:last|past|in the last)\s+(\d+)\s+days?', q)
        if last_days_match:
            days = int(last_days_match.group(1))
            days = max(1, min(days, 365))
            return now - datetime.timedelta(days=days), now, f"last {days} days"

        if "this week" in q:
            weekday = today_start.weekday()
            week_start = today_start - datetime.timedelta(days=weekday)
            week_end = week_start + datetime.timedelta(days=7)
            return week_start, week_end, "this week"

        if "last week" in q:
            weekday = today_start.weekday()
            this_week_start = today_start - datetime.timedelta(days=weekday)
            last_week_start = this_week_start - datetime.timedelta(days=7)
            return last_week_start, this_week_start, "last week"

        if "this month" in q:
            month_start = today_start.replace(day=1)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1)
            return month_start, month_end, "this month"

        if "last month" in q:
            this_month_start = today_start.replace(day=1)
            if this_month_start.month == 1:
                last_month_start = this_month_start.replace(year=this_month_start.year - 1, month=12, day=1)
            else:
                last_month_start = this_month_start.replace(month=this_month_start.month - 1, day=1)
            return last_month_start, this_month_start, "last month"

        if "this year" in q:
            year_start = today_start.replace(month=1, day=1)
            year_end = year_start.replace(year=year_start.year + 1, month=1, day=1)
            return year_start, year_end, "this year"

        if "last year" in q:
            this_year_start = today_start.replace(month=1, day=1)
            last_year_start = this_year_start.replace(year=this_year_start.year - 1, month=1, day=1)
            return last_year_start, this_year_start, "last year"

        if "overdue" in q or "expired" in q:
            return None, now, "overdue"

        if "upcoming" in q or "soon" in q:
            return now, now + datetime.timedelta(days=30), "upcoming 30 days"

        return None, None, None

date_parser = DateParser()
