"""
PDF Reporter - Renders the per-developer Git-history reflection narrative
as a styled PDF.

Falls back to HTML-to-PDF conversion via weasyprint / pdfkit / xhtml2pdf
when available; otherwise uses reportlab directly.

⚠️  STRUCTURAL SAFEGUARDS

This reporter intentionally:

  * Does NOT render any composite 0-100 score, grade band, score circle,
    or verdict.
  * Does NOT emit any cross-author comparison table or leaderboard.
  * Always opens with an explicit usage notice page.
  * Stamps a SCOPE banner inside every repository section (self-scope vs.
    consented multi-author retrospective).
"""

import logging
from typing import Dict, List

from src.reporters.base_reporter import BaseReporter

logger = logging.getLogger(__name__)


class PdfReporter(BaseReporter):
    """Generates PDF reports from analysis metrics."""

    def generate(self, metrics: Dict) -> str:
        """
        Generate report content (returns HTML for compatibility).
        Use generate_to_file() for actual PDF output.
        """
        from src.reporters.html_reporter import HtmlReporter
        return HtmlReporter().generate(metrics)

    def generate_to_file(self, metrics: Dict, output_path: str) -> str:
        """
        Generate a PDF report and write it to a file.

        Args:
            metrics: Analysis metrics dict.
            output_path: Path to write the PDF file.

        Returns:
            The output file path.
        """
        # Try HTML-to-PDF engines first for best visual quality
        html_content = self.generate(metrics)
        for method in [
            self._try_weasyprint,
            self._try_pdfkit,
            self._try_xhtml2pdf,
        ]:
            try:
                return method(html_content, output_path)
            except (ImportError, Exception) as e:
                logger.debug("PDF method failed: %s", e)
                continue

        # Fall back to reportlab (always available)
        logger.info("Using reportlab for PDF generation")
        return self._generate_with_reportlab(metrics, output_path)

    # ─── HTML-to-PDF methods ──────────────────────────────────────────────

    @staticmethod
    def _try_weasyprint(html_content: str, output_path: str) -> str:
        from weasyprint import HTML
        HTML(string=html_content).write_pdf(output_path)
        logger.info("PDF generated with weasyprint: %s", output_path)
        return output_path

    @staticmethod
    def _try_pdfkit(html_content: str, output_path: str) -> str:
        import pdfkit
        pdfkit.from_string(html_content, output_path, options={
            "encoding": "UTF-8", "page-size": "A4",
            "margin-top": "15mm", "margin-bottom": "15mm",
        })
        logger.info("PDF generated with pdfkit: %s", output_path)
        return output_path

    @staticmethod
    def _try_xhtml2pdf(html_content: str, output_path: str) -> str:
        from xhtml2pdf import pisa
        with open(output_path, "wb") as f:
            pisa.CreatePDF(html_content, dest=f)
        logger.info("PDF generated with xhtml2pdf: %s", output_path)
        return output_path

    # ─── reportlab PDF generation ─────────────────────────────────────────

    def _generate_with_reportlab(self, metrics: Dict, output_path: str) -> str:
        """Generate PDF using reportlab (always available).

        Renders narrative + per-component-value tables only. NO composite
        score, NO grade band, NO leaderboard, NO cross-author comparison.
        """
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
        )
        from reportlab.lib import colors

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=15 * mm,
            leftMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle", parent=styles["Title"], fontSize=22,
            textColor=HexColor("#4f46e5"), spaceAfter=12,
        )
        h2_style = ParagraphStyle(
            "CustomH2", parent=styles["Heading2"], fontSize=16,
            textColor=HexColor("#4f46e5"), spaceBefore=16, spaceAfter=8,
        )
        h3_style = ParagraphStyle(
            "CustomH3", parent=styles["Heading3"], fontSize=13,
            textColor=HexColor("#1e293b"), spaceBefore=12, spaceAfter=6,
        )
        h4_style = ParagraphStyle(
            "CustomH4", parent=styles["Heading4"], fontSize=11,
            textColor=HexColor("#64748b"), spaceBefore=8, spaceAfter=4,
        )
        body_style = styles["Normal"]
        observation_style = ParagraphStyle(
            "Observation", parent=body_style, textColor=HexColor("#166534"),
            fontSize=9, spaceBefore=2,
        )
        consideration_style = ParagraphStyle(
            "Consideration", parent=body_style, textColor=HexColor("#991b1b"),
            fontSize=9, spaceBefore=2,
        )
        prompt_style = ParagraphStyle(
            "Prompt", parent=body_style, textColor=HexColor("#1e40af"),
            fontSize=9, spaceBefore=2,
        )
        notice_style = ParagraphStyle(
            "Notice", parent=body_style, textColor=HexColor("#64748b"),
            fontSize=9, fontName="Helvetica-Oblique",
            spaceBefore=4, spaceAfter=8, leftIndent=10, borderPadding=5,
        )
        scope_style = ParagraphStyle(
            "Scope", parent=body_style, textColor=HexColor("#1e293b"),
            fontSize=10, backColor=HexColor("#f1f5f9"),
            borderPadding=6, leftIndent=4, rightIndent=4,
            spaceBefore=4, spaceAfter=10,
        )
        usage_notice_style = ParagraphStyle(
            "UsageNotice", parent=styles["Normal"], fontSize=9,
            textColor=HexColor("#92400e"), backColor=HexColor("#fffbeb"),
            borderColor=HexColor("#f59e0b"), borderPadding=8, borderWidth=1,
            leftIndent=4, rightIndent=4, spaceBefore=4, spaceAfter=10,
        )

        elements = []
        elements.append(Paragraph("🪞 Git-History Reflection Report", title_style))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(
            "<b>⚠ Usage notice — please read first.</b> This report is a "
            "<b>descriptive summary of Git history only</b>. It does <b>not</b> measure "
            "productivity, engagement, or the value of any individual's contribution. "
            "Code review, design, mentoring, on-call, ops, and many other contributions "
            "are invisible to Git history. <b>Do not</b> use this report for performance "
            "evaluation, ranking, compensation, promotion, discipline, or any HR decision. "
            "Run it only with the <b>informed consent</b> of every analyzed developer, "
            "and treat findings as <b>personal reflection prompts, not verdicts</b>.",
            usage_notice_style,
        ))

        primary_color = HexColor("#4f46e5")
        header_bg = HexColor("#f1f5f9")

        def make_table(headers: List[str], rows: List[List[str]]) -> Table:
            data = [headers] + rows
            t = Table(data, repeatRows=1)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), primary_color),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#e2e8f0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, header_bg]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            return t

        for repo_name, repo_metrics in metrics.items():
            elements.append(Paragraph(f"📁 Repository: {repo_name}", h2_style))

            scope = repo_metrics.get("_scope") or {}
            mode = scope.get("mode")
            filters = scope.get("filters") or []
            if mode == "self_scope":
                elements.append(Paragraph(
                    "🔒 <b>Scope: self-reflection only.</b> Analysis is locked to "
                    f"the local Git user (<font face='Courier'>{' / '.join(filters)}"
                    "</font>). Other authors in the repository are not analysed.",
                    scope_style,
                ))
            elif mode == "team_retro":
                elements.append(Paragraph(
                    "👥 <b>Scope: consented team retrospective.</b> Caller has "
                    "explicitly asserted informed consent from every listed author: "
                    + ", ".join(f"<font face='Courier'>{a}</font>" for a in filters)
                    + ".",
                    scope_style,
                ))
            else:
                elements.append(Paragraph(
                    "ℹ <b>Scope: unspecified.</b> Treat this report with extra "
                    "caution and verify the consent basis before sharing.",
                    scope_style,
                ))

            all_authors = set()
            for key, analyzer_data in repo_metrics.items():
                if (
                    isinstance(analyzer_data, dict)
                    and key not in ("evaluations", "_scope")
                ):
                    all_authors.update(analyzer_data.keys())

            for author in sorted(all_authors):
                elements.append(Paragraph(f"👤 {author}", h3_style))

                # ── Personal Reflection Narrative ──
                ev = repo_metrics.get("evaluations", {}).get(author, {})
                if ev:
                    elements.append(Paragraph(
                        "🪞 Personal Reflection Narrative", h4_style
                    ))
                    elements.append(Paragraph(
                        "<i>Descriptive observations only. Not a score, not a "
                        "grade, not a verdict.</i>",
                        notice_style,
                    ))
                    for s in ev.get("strengths", []):
                        elements.append(Paragraph(f"✅ {s}", observation_style))
                    if ev.get("strengths"):
                        elements.append(Spacer(1, 4))
                    for w in ev.get("weaknesses", []):
                        elements.append(Paragraph(f"🔎 {w}", consideration_style))
                    if ev.get("weaknesses"):
                        elements.append(Spacer(1, 4))
                    for sg in ev.get("suggestions", []):
                        elements.append(Paragraph(f"💡 {sg}", prompt_style))
                    if ev.get("interpretation_notice"):
                        elements.append(Paragraph(
                            f"ℹ {ev['interpretation_notice']}", notice_style,
                        ))
                    elements.append(Spacer(1, 6))

                # ── Commit-cadence component values (descriptive only) ──
                sl = repo_metrics.get("slacking", {}).get(author, {})
                if sl:
                    elements.append(Paragraph(
                        "📉 Commit-cadence component values (descriptive only)",
                        h4_style,
                    ))
                    elements.append(Paragraph(
                        "<i>How sparse / bursty / low-volume the Git activity "
                        "looks. Not a productivity or engagement measure. "
                        "No single composite score is rendered; consider each "
                        "component on its own.</i>",
                        notice_style,
                    ))
                    sl_rows = [
                        ["Activity ratio", f"{sl.get('activity_ratio', 0):.1%}"],
                        ["Trivial-change ratio", f"{sl.get('trivial_commit_ratio', 0):.1%}"],
                        ["Long-gap ratio (>72h)", f"{sl.get('large_gap_ratio', 0):.1%}"],
                        ["Avg gap (hours)", str(sl.get("avg_gap_hours", 0))],
                        ["Lines / active day", str(sl.get("lines_per_active_day", 0))],
                        ["Non-code-only commit ratio", f"{sl.get('non_code_commit_ratio', 0):.1%}"],
                    ]
                    elements.append(make_table(["Component", "Value"], sl_rows))
                    if sl.get("interpretation_notice"):
                        elements.append(Paragraph(
                            f"ℹ {sl['interpretation_notice']}", notice_style,
                        ))

                # ── Commit Patterns ──
                cd = repo_metrics.get("commit_patterns", {}).get(author, {})
                if cd:
                    elements.append(Paragraph("📝 Commit Patterns", h4_style))
                    rows = [
                        ["Total commits", str(cd.get("total_commits", 0))],
                        ["Merge ratio", f"{cd.get('merge_ratio', 0):.1%}"],
                        ["Active span", f"{cd.get('active_span_days', 0)} days"],
                        ["Avg commits / active day", str(cd.get("avg_commits_per_active_day", 0))],
                        ["Avg lines added", str(cd.get("avg_lines_added", 0))],
                        ["Avg lines deleted", str(cd.get("avg_lines_deleted", 0))],
                        ["Total lines added", f"{cd.get('total_lines_added', 0):,}"],
                        ["Total lines deleted", f"{cd.get('total_lines_deleted', 0):,}"],
                    ]
                    elements.append(make_table(["Metric", "Value"], rows))

                # ── Commit timestamp distribution ──
                hd = repo_metrics.get("work_habits", {}).get(author, {})
                if hd:
                    elements.append(Paragraph(
                        "⏰ Commit timestamp distribution", h4_style
                    ))
                    elements.append(Paragraph(
                        "<i>Reflects when commits were authored, not when the "
                        "developer was working / resting.</i>",
                        notice_style,
                    ))
                    rows = [
                        ["Peak hour", f"{hd.get('peak_hour', 'N/A')}:00"],
                        ["Weekend ratio", f"{hd.get('weekend_ratio', 0):.1%}"],
                        ["Late-night ratio", f"{hd.get('late_night_ratio', 0):.1%}"],
                        ["Longest streak", f"{hd.get('longest_streak_days', 0)} days"],
                        ["Avg gap", f"{hd.get('avg_gap_between_commits_hours', 0)} hrs"],
                    ]
                    elements.append(make_table(["Metric", "Value"], rows))

                # ── Change patterns ──
                ed = repo_metrics.get("efficiency", {}).get(author, {})
                if ed:
                    elements.append(Paragraph("🚀 Change patterns (descriptive)", h4_style))
                    rows = [
                        ["Churn rate", f"{ed.get('churn_rate', 0):.1%}"],
                        ["Rework ratio", f"{ed.get('rework_ratio', 0):.1%}"],
                        ["Lines / commit", str(ed.get("lines_per_commit", 0))],
                        ["Files touched", str(ed.get("unique_files_touched", 0))],
                        ["Ownership ratio", f"{ed.get('ownership_ratio', 0):.1%}"],
                        ["Repo-level avg bus factor", str(ed.get("repo_avg_bus_factor", 0))],
                    ]
                    elements.append(make_table(["Metric", "Value"], rows))

                # ── Code-quality artefacts ──
                qd = repo_metrics.get("code_quality", {}).get(author, {})
                if qd:
                    elements.append(Paragraph("🔍 Code-quality artefacts", h4_style))
                    rows = [
                        ["Bug-fix ratio", f"{qd.get('bug_fix_ratio', 0):.1%}"],
                        ["Revert ratio", f"{qd.get('revert_ratio', 0):.1%}"],
                        ["Large-commit ratio", f"{qd.get('large_commit_ratio', 0):.1%}"],
                        ["Test-modification ratio", f"{qd.get('test_modification_ratio', 0):.1%}"],
                        ["Avg commit size", f"{qd.get('avg_commit_size', 0)} lines"],
                    ]
                    if qd.get("avg_python_complexity", 0) > 0:
                        rows.append(["Avg Python complexity", str(qd["avg_python_complexity"])])
                    elements.append(make_table(["Metric", "Value"], rows))

                elements.append(HRFlowable(
                    width="100%", thickness=1, color=HexColor("#e2e8f0"),
                    spaceBefore=8, spaceAfter=8,
                ))

            # NOTE: Composite-Indicator Overview / Cadence-Density Overview
            # leaderboards are intentionally NOT rendered.

        doc.build(elements)
        logger.info("PDF generated with reportlab: %s", output_path)
        return output_path