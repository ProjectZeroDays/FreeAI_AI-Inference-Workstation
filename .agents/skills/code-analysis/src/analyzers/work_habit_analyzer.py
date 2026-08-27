"""
Work Habit Analyzer - Aggregates Git commit timestamps into descriptive
work-time pattern statistics.

⚠️  IMPORTANT — INTENDED USE & LIMITATIONS

The metrics produced here (peak hour, weekend ratio, late-night ratio,
streaks, average gap between commits) are extracted from Git timestamps,
which only reflect *when commits were authored* — not when the developer
was working, resting, on call, in meetings, mentoring, or in pair sessions.
Time-zone misconfiguration, batched pushes, squash merges, automation, and
work-from-home patterns can all distort these signals heavily.

These metrics are intended for:
  - Self-reflection by the developer being analyzed (with their consent)
  - Aggregate, anonymized team-health diagnostics (e.g., is the team as a
    whole working unsustainable hours?)

They MUST NOT be used to:
  - Evaluate, rank, discipline, or compare individual employees
  - Infer effort, dedication, or "work-life balance" of a specific person
  - Drive performance reviews, promotions, or compensation decisions
  - Surveil employees without informed consent

By using this module you accept responsibility for ensuring informed consent
from every developer whose timestamps are analyzed, and for compliance with
applicable privacy and labor regulations.

Metrics include:
  - Preferred working hours distribution
  - Weekday vs weekend activity
  - Day-of-week distribution
  - Late night / early morning coding ratio (descriptive only)
  - Longest consecutive coding streaks
  - Average time between commits
"""

import logging
from collections import defaultdict, Counter
from datetime import timedelta
from typing import Dict

from src.analyzers.base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)


class WorkHabitAnalyzer(BaseAnalyzer):
    """Aggregates commit timestamps into descriptive cadence-of-the-week
    statistics per consented identity.

    The orchestrator restricts ``BaseAnalyzer._get_commits`` to either the
    local Git user (self-scope, default) or to authors who have given
    informed consent (``--multi-author-team-retro`` mode). This analyzer
    only operates on commits the orchestrator has already authorised.

    Output is intended for *self-reflection* ("is my own commit cadence
    what I want it to be?") — not for individual performance evaluation,
    attendance monitoring, or work-time auditing. Every result includes an
    ``interpretation_notice`` field that downstream renderers must surface
    to the reader.
    """

    # Time slot definitions
    EARLY_MORNING = range(5, 9)    # 05:00 - 08:59
    MORNING = range(9, 12)         # 09:00 - 11:59
    AFTERNOON = range(12, 18)      # 12:00 - 17:59
    EVENING = range(18, 22)        # 18:00 - 21:59
    LATE_NIGHT_1 = range(22, 24)   # 22:00 - 23:59
    LATE_NIGHT_2 = range(0, 5)     # 00:00 - 04:59

    WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    def analyze(self) -> Dict:
        """
        Compute descriptive cadence-of-the-week statistics on the
        *already-scoped* commit set.

        Returns:
            Dict keyed by the consented Git identity with descriptive
            cadence-of-the-week statistics. In self-scope mode this dict
            has at most one entry (the local Git user).
        """
        author_data = defaultdict(lambda: {
            "commit_times": [],
            "commit_dates": [],
        })

        for commit in self._get_commits():
            author = commit.author.name
            author_data[author]["commit_times"].append(commit.committer_date)
            author_data[author]["commit_dates"].append(commit.committer_date.date())

        result = {}
        for author, data in author_data.items():
            times = data["commit_times"]
            if not times:
                continue

            # Hour distribution
            hour_counts = Counter(t.hour for t in times)
            hour_distribution = {h: hour_counts.get(h, 0) for h in range(24)}

            # Day of week distribution
            dow_counts = Counter(t.weekday() for t in times)
            dow_distribution = {
                self.WEEKDAY_NAMES[d]: dow_counts.get(d, 0) for d in range(7)
            }

            # Weekday vs weekend
            weekday_commits = sum(1 for t in times if t.weekday() < 5)
            weekend_commits = len(times) - weekday_commits

            # Time slot classification
            slot_counts = self._classify_time_slots(times)

            # Late night ratio
            total = len(times)
            late_night_count = slot_counts.get("late_night", 0)
            late_night_ratio = round(late_night_count / total, 3) if total else 0

            # Consecutive coding streaks
            unique_dates = sorted(set(data["commit_dates"]))
            longest_streak = self._longest_streak(unique_dates)

            # Average gap between commits
            sorted_times = sorted(times)
            avg_gap = self._avg_time_gap(sorted_times)

            # Peak hour (most commits)
            peak_hour = max(hour_distribution, key=hour_distribution.get) if hour_distribution else None

            result[author] = {
                "total_commits": total,
                "hour_distribution": hour_distribution,
                "day_of_week_distribution": dow_distribution,
                "weekday_commits": weekday_commits,
                "weekend_commits": weekend_commits,
                "weekend_ratio": round(weekend_commits / total, 3) if total else 0,
                "time_slot_distribution": slot_counts,
                "late_night_ratio": late_night_ratio,
                "peak_hour": peak_hour,
                "longest_streak_days": longest_streak,
                "avg_gap_between_commits_hours": avg_gap,
                "interpretation_notice": (
                    "Descriptive Git-timestamp statistic only. Reflects when "
                    "commits were authored, NOT when the developer was working "
                    "or resting. Time-zone, batched pushes, squash merges, and "
                    "automation can distort it. Must not be used for performance "
                    "evaluation, ranking, or HR decisions."
                ),
            }

        return result

    def _classify_time_slots(self, times) -> Dict[str, int]:
        """Classify commit times into work time slots."""
        slots = Counter()
        for t in times:
            h = t.hour
            if h in self.MORNING:
                slots["morning"] += 1
            elif h in self.AFTERNOON:
                slots["afternoon"] += 1
            elif h in self.EVENING:
                slots["evening"] += 1
            elif h in self.EARLY_MORNING:
                slots["early_morning"] += 1
            else:
                slots["late_night"] += 1
        return dict(slots)

    @staticmethod
    def _longest_streak(dates) -> int:
        """Calculate the longest consecutive days streak."""
        if not dates:
            return 0
        if len(dates) == 1:
            return 1

        max_streak = 1
        current_streak = 1
        for i in range(1, len(dates)):
            if (dates[i] - dates[i - 1]).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        return max_streak

    @staticmethod
    def _avg_time_gap(sorted_times) -> float:
        """Calculate average time gap between consecutive commits in hours."""
        if len(sorted_times) < 2:
            return 0.0
        gaps = []
        for i in range(1, len(sorted_times)):
            delta = sorted_times[i] - sorted_times[i - 1]
            gaps.append(delta.total_seconds() / 3600.0)
        return round(sum(gaps) / len(gaps), 2)
