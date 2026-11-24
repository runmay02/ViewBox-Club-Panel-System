"""
Generate High-Resolution Visual PNG Diagrams for ViewBox Club System Design
- design/er_diagram.png (Complete Relational Database Architecture)
- design/user_flow.png (Three-Portal End-to-End User Journey)
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_er_diagram():
    fig, ax = plt.subplots(figsize=(24, 16), dpi=200)
    ax.set_facecolor('#0B0F19')
    fig.patch.set_facecolor('#0B0F19')

    # Title Banner
    ax.text(12, 15.4, "VIEWBOX CLUB — RELATIONAL DATABASE ARCHITECTURE (ER DIAGRAM)",
            color='#F8FAFC', fontsize=22, fontweight='bold', ha='center', va='center')
    ax.text(12, 14.9, "Concave Insights — Respondent Management & Survey Operations Platform | 3NF Schema",
            color='#94A3B8', fontsize=13, ha='center', va='center')

    # Color palette
    card_bg = '#1E293B'
    header_user = '#3B82F6'     # Blue
    header_source = '#8B5CF6'   # Purple
    header_survey = '#10B981'   # Green
    header_ops = '#F59E0B'      # Amber
    header_system = '#64748B'   # Slate
    border_color = '#334155'
    text_light = '#F1F5F9'
    text_muted = '#94A3B8'
    pk_color = '#F59E0B'
    fk_color = '#38BDF8'

    entities = [
        # (x, y, w, h, name, header_color, [fields])
        # Users & Auth
        (1.0, 11.2, 4.0, 2.8, "users", header_user, [
            ("PK", "id", "VARCHAR(36)"),
            ("UK", "phone", "VARCHAR(15)"),
            ("  ", "hashed_otp", "VARCHAR(255)"),
            ("  ", "role", "VARCHAR(20)"),
            ("  ", "is_active", "BOOLEAN"),
            ("  ", "created_at", "DATETIME"),
        ]),
        
        # Member Profiles
        (6.0, 10.5, 4.8, 3.8, "member_profiles", header_user, [
            ("PK", "id", "VARCHAR(36)"),
            ("UK", "member_id", "VARCHAR(20)"),
            ("FK", "user_id", "VARCHAR(36)"),
            ("  ", "full_name", "VARCHAR(100)"),
            ("UK", "phone", "VARCHAR(15)"),
            ("  ", "email", "VARCHAR(100)"),
            ("  ", "gender / dob", "VARCHAR / DATE"),
            ("  ", "city / income", "VARCHAR / VARCHAR"),
            ("  ", "interests", "TEXT"),
            ("FK", "acquisition_source_id", "VARCHAR(36)"),
            ("  ", "last_survey_completed_on", "DATE"),
        ]),

        # Dynamic Acquisition Sources
        (1.0, 6.8, 4.0, 3.2, "acquisition_sources", header_source, [
            ("PK", "id", "VARCHAR(36)"),
            ("UK", "name", "VARCHAR(100)"),
            ("  ", "channel_type", "VARCHAR(30)"),
            ("UK", "code", "VARCHAR(50)"),
            ("  ", "is_active", "BOOLEAN"),
            ("  ", "created_at", "DATETIME"),
        ]),

        # Source Links
        (1.0, 3.0, 4.0, 2.6, "source_links", header_source, [
            ("PK", "id", "VARCHAR(36)"),
            ("FK", "source_id", "VARCHAR(36)"),
            ("UK", "token", "VARCHAR(64)"),
            ("  ", "target_url", "VARCHAR(255)"),
            ("  ", "click_count", "INTEGER"),
        ]),

        # Attribution Events
        (1.0, 0.2, 4.0, 2.2, "attribution_events", header_source, [
            ("PK", "id", "VARCHAR(36)"),
            ("FK", "source_id", "VARCHAR(36)"),
            ("FK", "source_link_id", "VARCHAR(36)"),
            ("  ", "ip_address / user_agent", "VARCHAR"),
            ("  ", "created_at", "DATETIME"),
        ]),

        # Referrals
        (6.0, 6.0, 4.8, 3.6, "referrals", header_user, [
            ("PK", "id", "VARCHAR(36)"),
            ("FK", "referrer_member_id", "VARCHAR(36)"),
            ("FK", "referred_member_id", "VARCHAR(36)"),
            ("  ", "referral_token", "VARCHAR(64)"),
            ("  ", "stage", "LEAD | FIT | COMPL | FAIL"),
            ("  ", "failure_reason", "TEXT"),
            ("  ", "fit_verified_at", "DATETIME"),
            ("  ", "completion_verified_at", "DATETIME"),
        ]),

        # Surveys
        (12.0, 10.5, 4.8, 3.8, "surveys", header_survey, [
            ("PK", "id", "VARCHAR(36)"),
            ("  ", "title", "VARCHAR(200)"),
            ("  ", "start_date / deadline", "DATE (<= 15d)"),
            ("  ", "status", "ACTIVE | EXPIRED | QUOTA"),
            ("  ", "target_quota", "INTEGER"),
            ("  ", "completed_count", "INTEGER"),
            ("  ", "incentive_amount", "NUMERIC(10,2)"),
            ("  ", "referral_bonus_amount", "NUMERIC(10,2)"),
            ("FK", "created_by_user_id", "VARCHAR(36)"),
        ]),

        # Survey Eligibility Rules
        (18.0, 11.0, 4.8, 3.0, "survey_eligibility_rules", header_survey, [
            ("PK", "id", "VARCHAR(36)"),
            ("FK", "survey_id", "VARCHAR(36)"),
            ("  ", "rule_type", "AGE | CITY | GENDER | INC"),
            ("  ", "rule_value", "VARCHAR(100)"),
            ("  ", "strictness", "STRICT | FLEXIBLE"),
        ]),

        # Survey Applications
        (12.0, 6.4, 4.8, 2.6, "survey_applications", header_survey, [
            ("PK", "id", "VARCHAR(36)"),
            ("FK", "survey_id", "VARCHAR(36)"),
            ("FK", "member_id", "VARCHAR(36)"),
            ("  ", "status", "APPL | APPR | WAIT | REJ"),
            ("  ", "applied_at", "DATETIME"),
        ]),

        # Survey Participations
        (12.0, 2.8, 4.8, 2.8, "survey_participations", header_survey, [
            ("PK", "id", "VARCHAR(36)"),
            ("FK", "survey_id", "VARCHAR(36)"),
            ("FK", "member_id", "VARCHAR(36)"),
            ("  ", "status", "COMPLETED | REJECTED"),
            ("  ", "completed_at", "DATETIME"),
            ("FK", "verified_by_user_id", "VARCHAR(36)"),
        ]),

        # Payouts
        (6.0, 1.8, 4.8, 3.4, "payouts", header_ops, [
            ("PK", "id", "VARCHAR(36)"),
            ("FK", "member_id", "VARCHAR(36)"),
            ("FK", "survey_id", "VARCHAR(36)"),
            ("FK", "referral_id", "VARCHAR(36)"),
            ("  ", "payout_type", "SURVEY | REFERRAL"),
            ("  ", "amount / status", "NUMERIC / PENDING..PAID"),
            ("FK", "approved_by_user_id", "VARCHAR(36)"),
            ("  ", "payment_reference", "VARCHAR(100)"),
        ]),

        # Meta Leads
        (18.0, 6.8, 4.8, 3.0, "meta_leads", header_source, [
            ("PK", "id", "VARCHAR(36)"),
            ("UK", "leadgen_id", "VARCHAR(64)"),
            ("  ", "form_id / campaign_id", "VARCHAR"),
            ("  ", "ad_id", "VARCHAR"),
            ("FK", "member_id", "VARCHAR(36)"),
            ("  ", "raw_payload", "JSON"),
        ]),

        # Import Jobs & Errors
        (18.0, 2.8, 4.8, 3.2, "import_jobs & errors", header_system, [
            ("PK", "job_id", "VARCHAR(36)"),
            ("  ", "file_name / total_rows", "VARCHAR / INT"),
            ("  ", "valid / imported / skipped", "INT / INT / INT"),
            ("  ", "status", "PENDING | COMPLETED"),
            ("ERR", "import_row_errors", "TABLE (row, col, reason)"),
        ]),

        # Audit Logs & Fraud Flags
        (18.0, 0.2, 4.8, 2.2, "audit_logs & fraud_flags", header_system, [
            ("PK", "id", "VARCHAR(36)"),
            ("FK", "user_id / member_id", "VARCHAR(36)"),
            ("  ", "action / flag_type", "VARCHAR"),
            ("  ", "prev_state / new_state", "JSON"),
            ("  ", "created_at", "DATETIME"),
        ]),
    ]

    for x, y, w, h, name, header_col, fields in entities:
        # Card Background
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.15",
                                      facecolor=card_bg, edgecolor=border_color, linewidth=1.5)
        ax.add_patch(rect)
        # Header Box
        header_h = 0.55
        h_rect = patches.FancyBboxPatch((x, y + h - header_h), w, header_h,
                                        boxstyle="round,pad=0.08,rounding_size=0.15",
                                        facecolor=header_col, edgecolor=header_col, linewidth=0)
        ax.add_patch(h_rect)
        # Table Name
        ax.text(x + w / 2, y + h - header_h / 2, name.upper(), color='#FFFFFF',
                fontsize=11, fontweight='bold', ha='center', va='center')

        # Fields
        cur_y = y + h - header_h - 0.25
        for tag, f_name, f_type in fields:
            tag_color = pk_color if tag == "PK" else (fk_color if tag in ("FK", "UK") else text_muted)
            ax.text(x + 0.2, cur_y, tag, color=tag_color, fontsize=8.5, fontweight='bold', va='center')
            ax.text(x + 0.8, cur_y, f_name, color=text_light, fontsize=8.5, va='center')
            ax.text(x + w - 0.2, cur_y, f_type, color=text_muted, fontsize=7.5, ha='right', va='center')
            cur_y -= 0.26

    # Relationship connectors
    def draw_rel(x1, y1, x2, y2, label=""):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color='#60A5FA', lw=1.5,
                                    mutation_scale=12, shrinkA=4, shrinkB=4))
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mx, my + 0.1, label, color='#93C5FD', fontsize=7.5,
                    ha='center', va='bottom', bbox=dict(boxstyle="round,pad=0.1", fc='#0F172A', ec='#3B82F6', lw=0.5))

    # Connectors
    draw_rel(5.0, 12.5, 6.0, 12.5, "1:1 user_id")
    draw_rel(3.0, 6.8, 3.0, 5.6, "1:N source_links")
    draw_rel(3.0, 3.0, 3.0, 2.4, "1:N clicks")
    draw_rel(5.0, 8.4, 6.0, 11.0, "1:N acquisition_source")
    draw_rel(8.4, 10.5, 8.4, 9.6, "1:N referrals (referrer & candidate)")
    draw_rel(10.8, 12.0, 12.0, 12.0, "M:N applications")
    draw_rel(16.8, 12.5, 18.0, 12.5, "1:N rules")
    draw_rel(14.4, 10.5, 14.4, 9.0, "1:N applications")
    draw_rel(14.4, 6.4, 14.4, 5.6, "1:N participations")
    draw_rel(12.0, 4.2, 10.8, 3.5, "completion -> payout")
    draw_rel(8.4, 6.0, 8.4, 5.2, "completed referral -> payout")
    draw_rel(18.0, 8.3, 10.8, 11.2, "leads -> member")

    ax.set_xlim(0, 24)
    ax.set_ylim(0, 16)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig('design/er_diagram.png', dpi=200, facecolor='#0B0F19')
    plt.close()
    print("ER diagram generated successfully: design/er_diagram.png")

def generate_user_flow():
    fig, ax = plt.subplots(figsize=(24, 16), dpi=200)
    ax.set_facecolor('#0B0F19')
    fig.patch.set_facecolor('#0B0F19')

    # Title Banner
    ax.text(12, 15.4, "VIEWBOX CLUB — END-TO-END SYSTEM USER FLOWS",
            color='#F8FAFC', fontsize=22, fontweight='bold', ha='center', va='center')
    ax.text(12, 14.9, "Respondent Mobile Portal | Operations Triage Queues | Administrator BI & Management",
            color='#94A3B8', fontsize=13, ha='center', va='center')

    # Swimlanes
    swimlanes = [
        ("A. RESPONDENT PORTAL (Mobile-First)", 0.6, 10.2, 22.8, 4.2, '#1E293B', '#3B82F6'),
        ("B. OPERATIONS SPECIALIST PORTAL (Verification)", 0.6, 5.6, 22.8, 4.2, '#1E293B', '#F59E0B'),
        ("C. SYSTEM ADMINISTRATOR PORTAL (Governance & BI)", 0.6, 1.0, 22.8, 4.2, '#1E293B', '#10B981'),
    ]

    for title, sx, sy, sw, sh, bg, border in swimlanes:
        s_rect = patches.FancyBboxPatch((sx, sy), sw, sh, boxstyle="round,pad=0.1,rounding_size=0.15",
                                        facecolor=bg, edgecolor=border, linewidth=2.0)
        ax.add_patch(s_rect)
        # Lane Header Banner
        lh_rect = patches.FancyBboxPatch((sx, sy + sh - 0.45), sw, 0.45,
                                         boxstyle="round,pad=0.1,rounding_size=0.15",
                                         facecolor=border, edgecolor=border, linewidth=0)
        ax.add_patch(lh_rect)
        ax.text(sx + 0.3, sy + sh - 0.22, title, color='#FFFFFF', fontsize=11, fontweight='bold', va='center')

    def draw_card(x, y, w, h, title, subtitle, color='#2563EB'):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.12",
                                      facecolor='#0F172A', edgecolor=color, linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h - 0.25, title, color='#F8FAFC', fontsize=9, fontweight='bold', ha='center', va='center')
        ax.text(x + w / 2, y + h / 2 - 0.1, subtitle, color='#94A3B8', fontsize=7.5, ha='center', va='center')

    def draw_arrow(x1, y1, x2, y2, color='#60A5FA', label=""):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.5, mutation_scale=10, shrinkA=3, shrinkB=3))
        if label:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.1, label, color='#93C5FD', fontsize=7, ha='center')

    # Respondent Cards (Lane A)
    draw_card(1.0, 10.8, 2.8, 1.6, "1. Visit Link", "Source Token or\nReferral URL")
    draw_card(4.2, 10.8, 2.8, 1.6, "2. Mock OTP", "Phone Input +\nDev OTP Banner")
    draw_card(7.4, 10.8, 3.0, 1.6, "3. Onboarding", "Name, DOB, City,\nIncome, Interests")
    draw_card(10.8, 10.8, 3.0, 1.6, "4. Dashboard", "Survey Feed &\nInterest Matches")
    draw_card(14.2, 10.8, 3.0, 1.6, "5. Eligibility", "Human-Readable\nAppr / Wait / Rej")
    draw_card(17.6, 10.8, 2.6, 1.6, "6. Apply", "Transaction Safe\nQuota Lock")
    draw_card(20.6, 10.8, 2.4, 1.6, "7. Referrals", "Masked Friends:\n98XXXXXX21")

    draw_arrow(3.8, 11.6, 4.2, 11.6)
    draw_arrow(7.0, 11.6, 7.4, 11.6)
    draw_arrow(10.4, 11.6, 10.8, 11.6)
    draw_arrow(13.8, 11.6, 14.2, 11.6)
    draw_arrow(17.2, 11.6, 17.6, 11.6)
    draw_arrow(12.3, 10.8, 12.3, 10.5)
    draw_arrow(12.3, 10.5, 21.8, 10.5)
    draw_arrow(21.8, 10.5, 21.8, 10.8)

    # Operations Cards (Lane B)
    draw_card(1.0, 6.2, 3.2, 1.6, "Triage Queue", "Pending Tasks &\nVerification Feed", '#F59E0B')
    draw_card(5.0, 6.2, 3.8, 1.6, "Referral Fit Review", "Lead -> Fit or\nLead -> Failed (Reason)", '#F59E0B')
    draw_card(9.6, 6.2, 4.0, 1.6, "Survey Participation", "Ops verifies survey\ncompletion & quality", '#F59E0B')
    draw_card(14.4, 6.2, 4.0, 1.6, "Completion Audit", "Fit -> Completed\nReferrer Bonus Earned", '#F59E0B')
    draw_card(19.2, 6.2, 3.8, 1.6, "Payout Approval", "Two-step authorization\nPending -> Approved", '#F59E0B')

    draw_arrow(4.2, 7.0, 5.0, 7.0, color='#FBBF24')
    draw_arrow(8.8, 7.0, 9.6, 7.0, color='#FBBF24')
    draw_arrow(13.6, 7.0, 14.4, 7.0, color='#FBBF24')
    draw_arrow(18.4, 7.0, 19.2, 7.0, color='#FBBF24')

    # Cross-Lane Connectors
    draw_arrow(8.9, 10.8, 6.9, 7.8, color='#A855F7', label="New Lead")
    draw_arrow(18.9, 10.8, 11.6, 7.8, color='#A855F7', label="Survey Submitted")
    draw_arrow(16.4, 7.8, 21.8, 10.8, color='#34D399', label="Bonus Visible")

    # Admin Cards (Lane C)
    draw_card(1.0, 1.6, 3.6, 1.6, "Executive Dashboard", "Live KPIs & Funnel\nRecharts Visuals", '#10B981')
    draw_card(5.2, 1.6, 4.0, 1.6, "Respondent Grid", "Debounced Search,\nFilters, CSV/XLSX Export", '#10B981')
    draw_card(9.8, 1.6, 4.0, 1.6, "Survey Creator", "15-Day Lifespan Rule\nStrict/Flexible Config", '#10B981')
    draw_card(14.4, 1.6, 4.0, 1.6, "Dynamic Sources", "Tokenized URL Generator\nChannel Analytics", '#10B981')
    draw_card(19.0, 1.6, 4.0, 1.6, "Resilient CSV Import", "11-Step Preview, Error\nReport & Atomic Commit", '#10B981')

    draw_arrow(4.6, 2.4, 5.2, 2.4, color='#34D399')
    draw_arrow(9.2, 2.4, 9.8, 2.4, color='#34D399')
    draw_arrow(13.8, 2.4, 14.4, 2.4, color='#34D399')
    draw_arrow(18.4, 2.4, 19.0, 2.4, color='#34D399')

    # Cross-lane Admin to Respondent/Ops
    draw_arrow(16.4, 3.2, 2.4, 10.8, color='#38BDF8', label="Generates Link")
    draw_arrow(11.8, 3.2, 14.2, 10.8, color='#38BDF8', label="Feeds Rules")

    ax.set_xlim(0, 24)
    ax.set_ylim(0, 16)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig('design/user_flow.png', dpi=200, facecolor='#0B0F19')
    plt.close()
    print("User flow generated successfully: design/user_flow.png")

if __name__ == '__main__':
    generate_er_diagram()
    generate_user_flow()
