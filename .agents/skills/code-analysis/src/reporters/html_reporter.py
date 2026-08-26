"""
HTML Reporter - Renders the per-developer Git-history reflection narrative
as styled HTML.

⚠️  STRUCTURAL SAFEGUARDS

This reporter intentionally:

  * Does NOT render any composite 0-100 score, grade band, score circle,
    score bar, or verdict.
  * Does NOT emit any cross-author comparison table or leaderboard.
  * Always opens with an explicit usage notice.
  * Stamps a SCOPE banner inside every repository section (self-scope vs.
    consented multi-author retrospective) so readers cannot lose track of
    what they are looking at.
"""

from typing import Dict

from jinja2 import Template

from src.reporters.base_reporter import BaseReporter

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Git-History Reflection Report</title>
    <style>
        :root {
            --primary: #4f46e5;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --warning: #f59e0b;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 2rem;
        }
        .container { max-width: 1024px; margin: 0 auto; }
        h1 {
            font-size: 1.8rem;
            color: var(--primary);
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid var(--primary);
        }
        h2 {
            font-size: 1.35rem;
            margin: 2rem 0 1rem;
            padding: 0.5rem 1rem;
            background: var(--primary);
            color: white;
            border-radius: 8px;
        }
        h3 { font-size: 1.15rem; color: var(--primary); margin: 1.5rem 0 0.5rem; }
        h4 {
            font-size: 0.95rem;
            color: var(--text-muted);
            margin: 1rem 0 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1.25rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        table { width: 100%; border-collapse: collapse; margin: 0.5rem 0 1rem; }
        th, td {
            padding: 0.5rem 0.85rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }
        th {
            background: var(--bg);
            font-weight: 600;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
        }
        .scope-banner {
            background: #f1f5f9;
            border-left: 4px solid var(--primary);
            padding: 0.65rem 1rem;
            border-radius: 0 8px 8px 0;
            margin: 0.5rem 0 1.25rem;
            color: var(--text);
            font-size: 0.9rem;
        }
        .obs-item   { color: #166534; margin: 0.3rem 0; }
        .point-item { color: #991b1b; margin: 0.3rem 0; }
        .prompt-item { color: #1e40af; margin: 0.3rem 0; }
        .obs-item::before    { content: "✅ "; }
        .point-item::before  { content: "🔎 "; }
        .prompt-item::before { content: "💡 "; }
        .interpretation-notice {
            color: var(--text-muted);
            font-size: 0.8rem;
            margin-top: 0.75rem;
            font-style: italic;
        }
        footer {
            text-align: center;
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
            color: var(--text-muted);
            font-size: 0.85rem;
        }
        @media print {
            body { padding: 0.5rem; }
            .card { break-inside: avoid; }
            h2 { break-before: page; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🪞 Git-History Reflection Report</h1>

        <div class="card" style="border-left: 6px solid var(--warning); background: #fffbeb;">
            <h3 style="color: #92400e; margin-top: 0">⚠️ Usage notice — please read first</h3>
            <p>
                This report is a <strong>descriptive summary of Git history only</strong>.
                It does <strong>not</strong> measure productivity, engagement, or the value
                of any individual's contribution. Code review, design, mentoring, on-call,
                ops, and many other contributions are invisible to Git history.
            </p>
            <p>
                <strong>Do not</strong> use this report for performance evaluation, ranking,
                compensation, promotion, discipline, or any HR decision. Run it only with the
                <strong>informed consent</strong> of every analyzed developer, and treat
                findings as <strong>personal reflection prompts, not verdicts</strong>.
            </p>
        </div>

        {% for repo_name, repo_metrics in metrics.items() %}
        <h2>📁 {{ repo_name }}</h2>

        {% set scope = repo_metrics.get('_scope', {}) %}
        {% if scope.get('mode') == 'self_scope' %}
        <div class="scope-banner">
            🔒 <strong>Scope: self-reflection only.</strong> Analysis is locked to the
            local Git user (<code>{{ scope.filters | join(' / ') }}</code>). Other authors
            in the repository are not analysed.
        </div>
        {% elif scope.get('mode') == 'team_retro' %}
        <div class="scope-banner">
            👥 <strong>Scope: consented team retrospective.</strong> Caller has explicitly
            asserted informed consent from every listed author:
            {% for a in scope.filters %}<code>{{ a }}</code>{% if not loop.last %}, {% endif %}{% endfor %}.
        </div>
        {% else %}
        <div class="scope-banner">
            ℹ️ <strong>Scope: unspecified.</strong> Treat this report with extra caution
            and verify the consent basis before sharing.
        </div>
        {% endif %}

        {% set all_authors = [] %}
        {% for key, analyzer_data in repo_metrics.items() %}
            {% if key not in ('evaluations', '_scope') and analyzer_data is mapping %}
                {% for author in analyzer_data.keys() %}
                    {% if author not in all_authors %}
                        {% if all_authors.append(author) %}{% endif %}
                    {% endif %}
                {% endfor %}
            {% endif %}
        {% endfor %}

        {% for author in all_authors | sort %}
        <div class="card">
            <h3>👤 {{ author }}</h3>

            {# ── Personal Reflection Narrative ── #}
            {% set ev = repo_metrics.get('evaluations', {}).get(author, {}) %}
            {% if ev %}
            <h4>🪞 Personal Reflection Narrative</h4>
            <p style="color: var(--text-muted); font-size: 0.85rem; margin: 0.25rem 0 0.75rem;">
                Descriptive observations only. Not a score, not a grade, not a verdict.
            </p>

            {% if ev.strengths %}
            <h4 style="color: #166534">Supportive observations</h4>
            {% for s in ev.strengths %}<div class="obs-item">{{ s }}</div>{% endfor %}
            {% endif %}

            {% if ev.weaknesses %}
            <h4 style="color: #991b1b; margin-top: 1rem">Points to consider (with context)</h4>
            {% for w in ev.weaknesses %}<div class="point-item">{{ w }}</div>{% endfor %}
            {% endif %}

            {% if ev.suggestions %}
            <h4 style="color: #1e40af; margin-top: 1rem">Reflection prompts</h4>
            {% for sg in ev.suggestions %}<div class="prompt-item">{{ sg }}</div>{% endfor %}
            {% endif %}

            {% if ev.interpretation_notice %}
            <p class="interpretation-notice">ℹ️ {{ ev.interpretation_notice }}</p>
            {% endif %}
            {% endif %}

            {# ── Commit-cadence component values (descriptive only) ── #}
            {% set sl = repo_metrics.get('slacking', {}).get(author, {}) %}
            {% if sl %}
            <h4>📉 Commit-cadence component values (descriptive only)</h4>
            <p style="color: var(--text-muted); font-size: 0.85rem; margin: 0.25rem 0 0.5rem;">
                How sparse / bursty / low-volume the Git activity looks. <strong>Not</strong>
                a productivity or engagement measure. Many legitimate work patterns produce
                sparse cadence (architecture, code review, on-call, time-off). No single
                composite score is rendered; consider each component on its own.
            </p>
            <table>
                <tr><th>Component</th><th>Value</th></tr>
                <tr><td>Activity ratio</td><td>{{ "%.1f%%" | format(sl.activity_ratio * 100) }}</td></tr>
                <tr><td>Trivial-change ratio</td><td>{{ "%.1f%%" | format(sl.trivial_commit_ratio * 100) }}</td></tr>
                <tr><td>Long-gap ratio (&gt;72h)</td><td>{{ "%.1f%%" | format(sl.large_gap_ratio * 100) }}</td></tr>
                <tr><td>Avg gap (hours)</td><td>{{ sl.avg_gap_hours }}</td></tr>
                <tr><td>Lines / active day</td><td>{{ sl.lines_per_active_day }}</td></tr>
                <tr><td>Non-code-only commit ratio</td><td>{{ "%.1f%%" | format(sl.non_code_commit_ratio * 100) }}</td></tr>
            </table>
            {% if sl.interpretation_notice %}
            <p class="interpretation-notice">ℹ️ {{ sl.interpretation_notice }}</p>
            {% endif %}
            {% endif %}

            {# ── Commit Patterns ── #}
            {% set cd = repo_metrics.get('commit_patterns', {}).get(author, {}) %}
            {% if cd %}
            <h4>📝 Commit Patterns</h4>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Total commits</td><td>{{ cd.total_commits }}</td></tr>
                <tr><td>Merge ratio</td><td>{{ "%.1f%%" | format(cd.merge_ratio * 100) }}</td></tr>
                <tr><td>Active span</td><td>{{ cd.active_span_days }} days</td></tr>
                <tr><td>Avg commits / active day</td><td>{{ cd.avg_commits_per_active_day }}</td></tr>
                <tr><td>Avg lines added</td><td>{{ cd.avg_lines_added }}</td></tr>
                <tr><td>Avg lines deleted</td><td>{{ cd.avg_lines_deleted }}</td></tr>
                <tr><td>Total lines added</td><td>{{ "{:,}".format(cd.total_lines_added) }}</td></tr>
                <tr><td>Total lines deleted</td><td>{{ "{:,}".format(cd.total_lines_deleted) }}</td></tr>
            </table>
            {% endif %}

            {# ── Commit timestamp distribution ── #}
            {% set hd = repo_metrics.get('work_habits', {}).get(author, {}) %}
            {% if hd %}
            <h4>⏰ Commit timestamp distribution</h4>
            <p style="color: var(--text-muted); font-size: 0.85rem; margin: 0.25rem 0 0.5rem;">
                Reflects when commits were authored, not when the developer was working /
                resting. Time-zone settings, batched pushes, and squash merges can distort
                these numbers.
            </p>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Peak hour</td><td>{{ hd.peak_hour }}:00</td></tr>
                <tr><td>Weekend ratio</td><td>{{ "%.1f%%" | format(hd.weekend_ratio * 100) }}</td></tr>
                <tr><td>Late-night ratio</td><td>{{ "%.1f%%" | format(hd.late_night_ratio * 100) }}</td></tr>
                <tr><td>Longest streak</td><td>{{ hd.longest_streak_days }} days</td></tr>
                <tr><td>Avg gap</td><td>{{ hd.avg_gap_between_commits_hours }} hrs</td></tr>
            </table>
            {% if hd.interpretation_notice %}
            <p class="interpretation-notice">ℹ️ {{ hd.interpretation_notice }}</p>
            {% endif %}
            {% endif %}

            {# ── Change patterns ── #}
            {% set ed = repo_metrics.get('efficiency', {}).get(author, {}) %}
            {% if ed %}
            <h4>🚀 Change patterns (descriptive)</h4>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Churn rate</td><td>{{ "%.1f%%" | format(ed.churn_rate * 100) }}</td></tr>
                <tr><td>Rework ratio</td><td>{{ "%.1f%%" | format(ed.rework_ratio * 100) }}</td></tr>
                <tr><td>Lines / commit</td><td>{{ ed.lines_per_commit }}</td></tr>
                <tr><td>Files touched</td><td>{{ ed.unique_files_touched }}</td></tr>
                <tr><td>Ownership ratio</td><td>{{ "%.1f%%" | format(ed.ownership_ratio * 100) }}</td></tr>
                <tr><td>Repo-level avg bus factor</td><td>{{ ed.repo_avg_bus_factor }}</td></tr>
            </table>
            {% if ed.interpretation_notice %}
            <p class="interpretation-notice">ℹ️ {{ ed.interpretation_notice }}</p>
            {% endif %}
            {% endif %}

            {# ── Code-style markers ── #}
            {% set sd = repo_metrics.get('code_style', {}).get(author, {}) %}
            {% if sd %}
            <h4>🎨 Code-style markers</h4>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Conventional Commits ratio</td><td>{{ "%.1f%%" | format(sd.conventional_commit_ratio * 100) }}</td></tr>
                <tr><td>Issue-reference ratio</td><td>{{ "%.1f%%" | format(sd.issue_reference_ratio * 100) }}</td></tr>
                <tr><td>Avg change size</td><td>{{ sd.avg_change_size_lines }} lines</td></tr>
            </table>
            {% endif %}

            {# ── Code-quality artefacts ── #}
            {% set qd = repo_metrics.get('code_quality', {}).get(author, {}) %}
            {% if qd %}
            <h4>🔍 Code-quality artefacts</h4>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Bug-fix ratio</td><td>{{ "%.1f%%" | format(qd.bug_fix_ratio * 100) }}</td></tr>
                <tr><td>Revert ratio</td><td>{{ "%.1f%%" | format(qd.revert_ratio * 100) }}</td></tr>
                <tr><td>Large-commit ratio</td><td>{{ "%.1f%%" | format(qd.large_commit_ratio * 100) }}</td></tr>
                <tr><td>Test-modification ratio</td><td>{{ "%.1f%%" | format(qd.test_modification_ratio * 100) }}</td></tr>
                <tr><td>Avg commit size</td><td>{{ qd.avg_commit_size }} lines</td></tr>
                {% if qd.avg_python_complexity > 0 %}
                <tr><td>Avg Python complexity</td><td>{{ qd.avg_python_complexity }}</td></tr>
                {% endif %}
            </table>
            {% endif %}
        </div>
        {% endfor %}
        {% endfor %}

        <footer>
            Generated by <strong>Code Analysis Skills</strong> &middot; Git-history reflection only
            &middot; Not for HR / ranking / surveillance use
        </footer>
    </div>
</body>
</html>
"""


class HtmlReporter(BaseReporter):
    """Generates styled HTML reports from analysis metrics."""

    def generate(self, metrics: Dict) -> str:
        """Generate an HTML report using Jinja2 template."""
        template = Template(HTML_TEMPLATE)
        return template.render(metrics=metrics)
