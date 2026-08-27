"""
Reflection Narrator.

⚠️  IMPORTANT — INTENDED USE & STRUCTURAL SAFEGUARDS

This module produces *self-reflection narrative text* from Git history
component values. The output:

  - Is a NARROW, BIASED proxy. Git history misses code review, design,
    mentoring, on-call, ops, security work, pair programming, refactor
    planning, and many other forms of contribution.
  - MUST NOT be used to evaluate, rank, discipline, promote, demote, fire,
    or compensate any employee or contributor.
  - MUST NOT be used to compare individuals against each other for any
    workplace decision.
  - MUST be used only with informed consent of the analyzed developer, and
    in a non-punitive context (e.g., a developer running it on their own
    repository, or an opt-in team retrospective).

Structural safeguards:
  * No composite 0-100 score is produced.
  * No S/A/B/C/D/E/F letter band is produced.
  * No "verdict" sentence is produced.
  * Output fields are deliberately neutral:
    ``supportive_observations`` / ``points_to_consider`` /
    ``reflection_prompts``. Field names that frame the output as a personal
    evaluation (e.g., ``strengths`` / ``weaknesses``) are not emitted.
    journal-style reflection prompt.
  * Every per-identity entry carries a mandatory ``interpretation_notice``
    field that downstream renderers MUST surface alongside the data.

The input dictionary is keyed by *consented Git identity* — either the
local Git user (default self-scope) or one of the explicitly listed
``consented_authors``. The orchestrator is responsible for that scoping;
this narrator never decides on its own which identities to summarise.
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


# Per-dimension component weights — kept only so each dimension's narrative
# can mention which axes a developer might want to reflect on first. They are
# deliberately NOT combined into a single composite score.
DIMENSION_LABELS = {
    "commit_discipline": "Commit discipline (frequency, message length, conventions)",
    "work_consistency":  "Cadence consistency (timestamp distribution)",
    "efficiency":        "Change patterns (churn, rework, change volume)",
    "code_quality":      "Code-quality artefacts (bug-fix ratio, reverts, tests, complexity)",
    "code_style":        "Style markers (Conventional Commits, issue references)",
    "engagement":        "Cadence density (inverse of long-gap signals)",
}


# Always-attached interpretive guard. Every per-developer result carries this
# field so downstream renderers cannot accidentally drop the disclaimer.
_INTERPRETATION_NOTICE = (
    "This narrative is a DESCRIPTIVE summary of Git-history signals only. It "
    "is not a performance review, not a measure of an individual's value, and "
    "not a basis for HR, compensation, ranking, or disciplinary decisions. "
    "Many important contributions (design, code review, mentoring, on-call, "
    "operations, pair programming) are invisible to Git history. Read the "
    "findings as personal reflection prompts, not verdicts."
)


class ReflectionNarrator:
    """
    Generates a *self-reflection* narrative from analyzer component values
    for each consented Git identity. Output is intentionally framed as
    journal-style reflection prompts, never as evaluation, score, grade,
    verdict, or comparison between people.

    Each entry contains:
      - ``supportive_observations``: items each backed by a concrete component
        value, written so the reader can self-introspect (no comparison to
        other developers, no personal judgement language)
      - ``points_to_consider``: neutral, contextualised items where the
        reader may want to ask themselves *why* a Git pattern looks the way
        it does. Every item includes the most common alternative
        explanations, so the entry cannot be read as a deficiency list.
      - ``reflection_prompts``: questions phrased for personal reflection
        only ("would smaller commits help future me?"), never as managerial
        directives.
      - ``interpretation_notice``: a mandatory disclaimer downstream
        renderers must surface.

    This class deliberately does NOT emit any of the following: a composite
    overall score, a dimension-score table, a letter grade, a "verdict"
    sentence, or fields named ``strengths`` / ``weaknesses`` / ``suggestions``.
    Downstream consumers must use the journal-style fields above.
    """

    def narrate(
        self,
        repo_metrics: Dict,
        consented_identities: Optional[List[str]] = None,
    ) -> Dict:
        """
        Build the per-identity self-reflection narrative.

        Args:
            repo_metrics: Dict with keys like 'commit_patterns', 'work_habits',
                          'efficiency', 'code_style', 'code_quality',
                          'cadence_signals'. Each is keyed by the *already
                          consent-scoped* Git identity, as enforced upstream
                          by the orchestrator.
            consented_identities: Optional defence-in-depth allow-list of
                          Git identities the orchestrator has confirmed are
                          consent-scoped for this run. When provided, this
                          method silently drops any identity present in
                          ``repo_metrics`` that is *not* in the allow-list
                          and logs a warning, even if upstream filtering
                          missed it. ``None`` (the default) preserves the
                          historical behaviour of trusting the upstream
                          consent gate.

        Returns:
            Dict keyed by Git identity with journal-style reflection results.
        """
        discovered = set()
        for analyzer_data in repo_metrics.values():
            if isinstance(analyzer_data, dict):
                discovered.update(analyzer_data.keys())

        if consented_identities is not None:
            allow_lower = {ci.lower() for ci in consented_identities}
            allow_lower.update(
                ci.split("<")[0].strip().lower() for ci in consented_identities if "<" in ci
            )
            allowed = set()
            for identity in discovered:
                ident_lower = identity.lower()
                # Match either by full name/email or by substring against
                # the consented entries — mirrors BaseAnalyzer._author_matches.
                if any(a in ident_lower or ident_lower in a for a in allow_lower):
                    allowed.add(identity)
            dropped = discovered - allowed
            if dropped:
                logger.warning(
                    "ReflectionNarrator dropped %d unconsented identity/identities "
                    "that slipped past the upstream gate: %s",
                    len(dropped), sorted(dropped),
                )
            discovered = allowed

        results = {}
        for author in sorted(discovered):
            commit = repo_metrics.get("commit_patterns", {}).get(author, {})
            habit = repo_metrics.get("work_habits", {}).get(author, {})
            eff = repo_metrics.get("efficiency", {}).get(author, {})
            style = repo_metrics.get("code_style", {}).get(author, {})
            quality = repo_metrics.get("code_quality", {}).get(author, {})
            cadence = repo_metrics.get("cadence_signals", {}).get(author, {})

            if not commit:
                continue

            observations = self._supportive_observations(
                commit, habit, eff, style, quality, cadence
            )
            considerations = self._points_to_consider(
                commit, habit, eff, style, quality, cadence
            )
            prompts = self._reflection_prompts(
                commit, habit, eff, style, quality, cadence
            )

            results[author] = {
                # Journal-style outputs only. NO composite score, NO grade
                # band, NO verdict, NO strengths/weaknesses framing.
                "supportive_observations": observations,
                "points_to_consider": considerations,
                "reflection_prompts": prompts,
                "interpretation_notice": _INTERPRETATION_NOTICE,
            }

        return results

    # Backwards-compatible alias — the orchestrator already calls
    # ``narrate``; this thin alias keeps third-party imports of
    # ``ReflectionNarrator().evaluate(...)`` from breaking, while logging a
    # deprecation warning so legacy callers know to migrate.
    def evaluate(self, repo_metrics: Dict) -> Dict:
        logger.warning(
            "ReflectionNarrator.evaluate() is a deprecated alias for "
            "narrate(). The word 'evaluate' implies personal evaluation, "
            "which this skill explicitly forbids."
        )
        return self.narrate(repo_metrics)

    # ─── Observation / Consideration / Reflection-Prompt Generators ───

    def _supportive_observations(
        self, commit, habit, eff, style, quality, cadence
    ) -> List[str]:
        """Surface evidence-based, non-comparative observations."""
        observations = []

        if commit.get("avg_commits_per_active_day", 0) >= 3:
            observations.append("Steady commit cadence on the days they are active.")

        if commit.get("avg_message_length", 0) >= 40:
            observations.append("Commit messages tend to be descriptive — helpful for traceability.")

        if habit.get("weekend_ratio", 1) < 0.05:
            observations.append("Most commits land on weekdays, suggesting commits stay inside regular hours.")

        if habit.get("longest_streak_days", 0) >= 7:
            observations.append(
                f"At one point sustained a {habit['longest_streak_days']}-day commit streak."
            )

        if eff.get("churn_rate", 1) < 0.3:
            observations.append("Low code churn — added lines tend to stay in the codebase.")

        if eff.get("rework_ratio", 1) < 0.15:
            observations.append("Low rework ratio — files tend not to be re-edited within a week.")

        if quality.get("test_modification_ratio", 0) > 0.2:
            observations.append("Test files are touched alongside code changes regularly.")

        if quality.get("bug_fix_ratio", 1) < 0.15:
            observations.append("Few commits are tagged as bug-fixes (in this Git history sample).")

        if quality.get("revert_ratio", 1) < 0.02:
            observations.append("Reverts are rare in this history.")

        if style.get("conventional_commit_ratio", 0) > 0.7:
            observations.append("Conventional Commits format is followed consistently.")

        if style.get("issue_reference_ratio", 0) > 0.5:
            observations.append("Commits frequently reference issue / ticket numbers.")

        if eff.get("ownership_ratio", 0) > 0.5:
            observations.append("Holds majority authorship on a notable share of touched files.")

        return observations[:8]

    def _points_to_consider(
        self, commit, habit, eff, style, quality, cadence
    ) -> List[str]:
        """Surface points worth a personal reflection — neutral, specific."""
        considerations = []

        if commit.get("avg_message_length", 999) < 20:
            considerations.append(
                "Commit messages average under 20 chars — longer messages would "
                "help future readers (and the author) understand the *why* "
                "behind a change."
            )

        if commit.get("merge_ratio", 0) > 0.5:
            considerations.append(
                f"Merge commits make up {commit['merge_ratio']:.0%} of activity. "
                "This may simply reflect a merge-only role; worth confirming "
                "with the author."
            )

        if habit.get("late_night_ratio", 0) > 0.2:
            considerations.append(
                f"{habit['late_night_ratio']:.0%} of commits land in late-night "
                "hours. This may reflect time-zone settings, batched pushes, "
                "on-call work, or a preferred schedule — context from the "
                "author is needed before drawing conclusions."
            )

        if habit.get("weekend_ratio", 0) > 0.25:
            considerations.append(
                f"Weekend commits are {habit['weekend_ratio']:.0%} of the total. "
                "Consider whether this matches the author's intended work "
                "pattern, or whether workload / time-zone settings are the "
                "cause."
            )

        if eff.get("churn_rate", 0) > 0.6:
            considerations.append(
                f"Churn rate is {eff['churn_rate']:.0%} — a large share of "
                "added lines are later removed. Common causes include "
                "exploratory prototyping, scope changes, or refactoring "
                "sweeps; not necessarily a problem."
            )

        if eff.get("rework_ratio", 0) > 0.3:
            considerations.append(
                f"Rework ratio is {eff['rework_ratio']:.0%} — files are "
                "revisited within a week. May reflect iterative review "
                "feedback, evolving requirements, or shared-ownership work."
            )

        if quality.get("bug_fix_ratio", 0) > 0.4:
            considerations.append(
                f"{quality['bug_fix_ratio']:.0%} of commits are tagged as fixes. "
                "Could indicate fix-heavy work assignment, or an opportunity "
                "for more tests / earlier review."
            )

        if quality.get("revert_ratio", 0) > 0.05:
            considerations.append(
                f"Reverts are {quality['revert_ratio']:.0%} of commits — "
                "slightly elevated. Worth checking whether CI / pre-merge "
                "checks could catch issues earlier."
            )

        if quality.get("large_commit_ratio", 0) > 0.2:
            considerations.append(
                f"{quality['large_commit_ratio']:.0%} of commits are large "
                "(>500 lines). Smaller commits are usually easier to review."
            )

        if quality.get("test_modification_ratio", 0) < 0.05:
            considerations.append(
                "Test files are rarely touched alongside code changes. This "
                "might be fine (e.g., docs / infra work), or may suggest a "
                "gap in test coverage."
            )

        if style.get("conventional_commit_ratio", 0) < 0.2:
            considerations.append(
                "Conventional Commits format is rarely used. Adopting it "
                "makes automated changelogs and release tooling easier."
            )

        if eff.get("lines_per_commit", 0) < 10 and commit.get("total_commits", 0) > 20:
            considerations.append(
                "Commits average under 10 lines each. Very granular commits "
                "can be useful, but consider whether some of them could be "
                "squashed for clearer history."
            )

        return considerations[:8]

    def _reflection_prompts(
        self, commit, habit, eff, style, quality, cadence
    ) -> List[str]:
        """Generate neutral, practical reflection prompts."""
        suggestions = []

        if style.get("conventional_commit_ratio", 0) < 0.5:
            suggestions.append(
                "📝 Consider adopting Conventional Commits (feat/fix/docs…) "
                "and writing messages that explain the *why* of a change."
            )

        if habit.get("avg_gap_between_commits_hours", 0) > 72:
            suggestions.append(
                "⏰ Smaller, more frequent commits tend to make review and "
                "rollback easier than infrequent large batches."
            )

        if eff.get("churn_rate", 0) > 0.5 or eff.get("rework_ratio", 0) > 0.3:
            suggestions.append(
                "🚀 If churn or rework feels high, a brief design sketch or "
                "a quick review-before-implementation pass can sometimes "
                "reduce iteration cost."
            )

        if quality.get("test_modification_ratio", 0) < 0.1:
            suggestions.append(
                "🔍 Pairing each behavioural change with a test (where it "
                "fits the codebase culture) tends to reduce the bug-fix "
                "follow-up rate."
            )

        if quality.get("large_commit_ratio", 0) > 0.15:
            suggestions.append(
                "✂️ Where it doesn't break the change's logical unit, smaller "
                "commits (roughly under ~200 lines) are easier to review."
            )

        if habit.get("late_night_ratio", 0) > 0.15:
            suggestions.append(
                "🌙 If late-night commits don't match your preferred schedule, "
                "this is a useful self-reflection prompt — but Git timestamps "
                "alone are not enough to draw firm conclusions."
            )

        if style.get("issue_reference_ratio", 0) < 0.3:
            suggestions.append(
                "🔗 Linking commits to issue / ticket numbers improves "
                "traceability and audit trails."
            )

        if eff.get("ownership_ratio", 0) > 0.8:
            suggestions.append(
                "🤝 Authorship is highly concentrated. Pair-programming or "
                "rotating ownership reduces bus-factor risk for the team."
            )

        return suggestions[:6]
