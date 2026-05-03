import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# HTML Email Templates
# ---------------------------------------------------------------------------

_BASE_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{subject}</title>
  <style>
    body {{
      margin: 0; padding: 0;
      background-color: #0f0f0f;
      font-family: 'Segoe UI', Arial, sans-serif;
      color: #e0e0e0;
    }}
    .wrapper {{
      max-width: 600px;
      margin: 32px auto;
      background: #1a1a1a;
      border-radius: 12px;
      overflow: hidden;
      border: 1px solid #2a2a2a;
    }}
    .header {{
      background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
      padding: 32px 40px 24px;
      border-bottom: 1px solid #30363d;
      text-align: center;
    }}
    .logo {{
      font-size: 28px;
      font-weight: 800;
      letter-spacing: -1px;
      color: #ffffff;
    }}
    .logo span {{ color: #3b82f6; }}
    .tagline {{
      font-size: 12px;
      color: #7d8590;
      margin-top: 4px;
      letter-spacing: 1.5px;
      text-transform: uppercase;
    }}
    .body {{ padding: 36px 40px; }}
    h2 {{
      margin: 0 0 8px;
      font-size: 22px;
      font-weight: 700;
      color: #f0f6fc;
    }}
    p {{
      margin: 0 0 16px;
      font-size: 15px;
      line-height: 1.65;
      color: #c9d1d9;
    }}
    .case-badge {{
      display: inline-block;
      background: #21262d;
      border: 1px solid #30363d;
      border-radius: 6px;
      padding: 8px 16px;
      font-family: monospace;
      font-size: 14px;
      color: #58a6ff;
      letter-spacing: 0.5px;
      margin: 8px 0 20px;
    }}
    .info-table {{
      width: 100%;
      border-collapse: collapse;
      margin: 16px 0 24px;
      font-size: 14px;
    }}
    .info-table td {{
      padding: 10px 14px;
      border-bottom: 1px solid #21262d;
    }}
    .info-table td:first-child {{ color: #7d8590; white-space: nowrap; }}
    .info-table td:last-child   {{ color: #e6edf3; font-weight: 500; }}
    .urgency-badge {{
      display: inline-block;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.5px;
      text-transform: uppercase;
    }}
    .urgency-CRITICAL {{ background: #3d1515; color: #f85149; border: 1px solid #6e1a1a; }}
    .urgency-HIGH     {{ background: #3d2b00; color: #f0883e; border: 1px solid #6b4500; }}
    .urgency-MEDIUM   {{ background: #2f2a00; color: #e3b341; border: 1px solid #5a4e00; }}
    .urgency-LOW      {{ background: #0d2119; color: #3fb950; border: 1px solid #1a4530; }}
    .actions-list {{
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 8px;
      padding: 16px 20px;
      margin: 16px 0 24px;
    }}
    .actions-list p {{
      font-size: 13px;
      font-weight: 600;
      color: #7d8590;
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 12px;
    }}
    .actions-list ol {{
      margin: 0;
      padding-left: 20px;
      font-size: 14px;
      color: #c9d1d9;
    }}
    .actions-list ol li {{ margin-bottom: 8px; line-height: 1.5; }}
    .actions-list ol li:last-child {{ margin-bottom: 0; }}
    .cta-button {{
      display: inline-block;
      background: #1f6feb;
      color: #ffffff !important;
      text-decoration: none;
      padding: 12px 28px;
      border-radius: 8px;
      font-size: 15px;
      font-weight: 600;
      margin: 8px 0 24px;
    }}
    .helpline-box {{
      background: #0d1117;
      border: 1px solid #1f6feb;
      border-radius: 8px;
      padding: 14px 20px;
      text-align: center;
      margin: 20px 0;
    }}
    .helpline-box p {{ margin: 0; font-size: 13px; color: #7d8590; }}
    .helpline-number {{
      font-size: 28px;
      font-weight: 800;
      color: #58a6ff;
      display: block;
      margin: 4px 0;
      letter-spacing: 2px;
    }}
    .footer {{
      background: #161b22;
      border-top: 1px solid #21262d;
      padding: 20px 40px;
      text-align: center;
      font-size: 12px;
      color: #484f58;
      line-height: 1.8;
    }}
    .footer a {{ color: #58a6ff; text-decoration: none; }}
    .divider {{
      height: 1px;
      background: #21262d;
      margin: 24px 0;
    }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <div class="logo">Trace<span>Back</span></div>
      <div class="tagline">India's Cybercrime Recovery Platform</div>
    </div>
    <div class="body">
      {body_content}
    </div>
    <div class="footer">
      TraceBack &nbsp;|&nbsp; <a href="https://traceback.in">traceback.in</a><br/>
      National Cybercrime Helpline: <strong>1930</strong> &nbsp;|&nbsp;
      <a href="https://cybercrime.gov.in">cybercrime.gov.in</a><br/><br/>
      You received this because you filed a complaint with TraceBack.<br/>
      Do not reply to this email — it is sent from an automated system.
    </div>
  </div>
</body>
</html>
"""


def _render_email(subject: str, body_content: str) -> str:
    return _BASE_HTML.format(subject=subject, body_content=body_content)


def _urgency_badge_html(urgency_score: str) -> str:
    score = (urgency_score or "MEDIUM").upper()
    return f'<span class="urgency-badge urgency-{score}">{score}</span>'


def _actions_html(immediate_actions: list) -> str:
    if not immediate_actions:
        return ""
    items = "".join(f"<li>{action}</li>" for action in immediate_actions)
    return f"""
    <div class="actions-list">
      <p>Immediate Actions</p>
      <ol>{items}</ol>
    </div>
    """


# ---------------------------------------------------------------------------
# EmailService
# ---------------------------------------------------------------------------

class EmailService:
    """
    Sends transactional emails for TraceBack.
    Requires Flask-Mail (or compatible) config dict.
    Falls back to console logging if the mail server is unavailable.
    """

    def __init__(
        self,
        mail_server: str = "smtp.gmail.com",
        mail_port: int = 587,
        mail_username: str = "",
        mail_password: str = "",
        mail_use_tls: bool = True,
        sender_name: str = "TraceBack",
        sender_email: str = "no-reply@traceback.in",
    ):
        self.mail_server   = mail_server
        self.mail_port     = mail_port
        self.mail_username = mail_username
        self.mail_password = mail_password
        self.mail_use_tls  = mail_use_tls
        self.sender        = f"{sender_name} <{sender_email}>"

    # ------------------------------------------------------------------
    # Public send methods
    # ------------------------------------------------------------------

    def send_complaint_confirmation(
        self,
        victim_email: str,
        victim_name: str,
        case_id: str,
        triage_result: dict,
    ) -> bool:
        """Send case confirmation + triage summary to the victim."""
        urgency       = triage_result.get("urgency_score", "MEDIUM")
        tier          = triage_result.get("recommended_tier", "trace").capitalize()
        summary       = triage_result.get("analysis_summary", "")
        actions       = triage_result.get("immediate_actions", [])
        hours_rem     = triage_result.get("hours_remaining", "—")
        fraud_type    = triage_result.get("fraud_type_detected", "unknown").replace("_", " ").title()
        confidence    = triage_result.get("confidence_score", 0)

        subject = f"TraceBack Case #{case_id} — Your Complaint Has Been Received"
        body = f"""
        <h2>Your complaint has been registered, {victim_name}.</h2>
        <p>We've analysed your case and our AI triage system has assessed it as follows.
           Please take the immediate actions listed below — time is critical.</p>
        <div class="case-badge">Case ID: {case_id}</div>

        <table class="info-table">
          <tr><td>Fraud Type</td>      <td>{fraud_type}</td></tr>
          <tr><td>Urgency Level</td>   <td>{_urgency_badge_html(urgency)}</td></tr>
          <tr><td>Recommended Plan</td><td><strong>{tier} Tier</strong></td></tr>
          <tr><td>Hours Remaining</td> <td>{hours_rem} hrs to act</td></tr>
          <tr><td>AI Confidence</td>   <td>{int(confidence * 100)}%</td></tr>
        </table>

        <p><em>"{summary}"</em></p>

        {_actions_html(actions)}

        <div class="helpline-box">
          <p>National Cybercrime Helpline</p>
          <span class="helpline-number">1930</span>
          <p>Available 24×7 — Call Now</p>
        </div>

        <p>Our team will be in touch shortly. Log in to TraceBack to track your case progress
           and upload additional evidence.</p>
        """
        return self._send(to_email=victim_email, subject=subject, html_body=_render_email(subject, body))

    def send_expert_assignment(
        self,
        expert_email: str,
        expert_name: str,
        case_id: str,
        complaint_summary: dict,
    ) -> bool:
        """Notify an assigned TraceBack expert about a new case."""
        victim_name  = complaint_summary.get("victim_name", "Victim")
        fraud_type   = complaint_summary.get("fraud_type", "unknown").replace("_", " ").title()
        amount       = complaint_summary.get("amount_lost", 0)
        urgency      = complaint_summary.get("urgency_score", "HIGH")
        description  = str(complaint_summary.get("description", ""))[:300]

        subject = f"[TraceBack] New Case Assigned: #{case_id} — {_urgency_badge_html(urgency).replace('<', '').replace('>', '')}"
        body = f"""
        <h2>New Case Assigned to You</h2>
        <p>Hello {expert_name}, a new complaint has been assigned to you on TraceBack.</p>
        <div class="case-badge">Case ID: {case_id}</div>

        <table class="info-table">
          <tr><td>Victim</td>       <td>{victim_name}</td></tr>
          <tr><td>Fraud Type</td>   <td>{fraud_type}</td></tr>
          <tr><td>Amount Lost</td>  <td>₹{float(amount):,.0f}</td></tr>
          <tr><td>Urgency</td>      <td>{_urgency_badge_html(urgency)}</td></tr>
        </table>

        <p><strong>Complaint Excerpt:</strong><br/>
        <em>{description}{"…" if len(str(complaint_summary.get("description",""))) > 300 else ""}</em></p>

        <div class="divider"></div>
        <p>Please log in to the TraceBack Expert Dashboard to review the full case and begin recovery action.</p>
        <a class="cta-button" href="https://app.traceback.in/expert/cases/{case_id}">Open Case Dashboard</a>
        """
        return self._send(to_email=expert_email, subject=subject, html_body=_render_email(subject, body))

    def send_status_update(
        self,
        victim_email: str,
        case_id: str,
        new_status: str,
        notes: str = "",
    ) -> bool:
        """Notify a victim that their case status has changed."""
        status_display = new_status.replace("_", " ").title()
        subject = f"TraceBack Case #{case_id} — Status Update: {status_display}"
        body = f"""
        <h2>Case Status Update</h2>
        <p>There has been an update to your TraceBack case.</p>
        <div class="case-badge">Case ID: {case_id}</div>

        <table class="info-table">
          <tr><td>New Status</td><td><strong>{status_display}</strong></td></tr>
        </table>

        {"<p><strong>Notes from your case expert:</strong><br/>" + notes + "</p>" if notes else ""}

        <div class="divider"></div>
        <p>Log in to TraceBack to view the full update history and communicate with your assigned expert.</p>
        <a class="cta-button" href="https://app.traceback.in/cases/{case_id}">View Case</a>

        <div class="helpline-box">
          <p>Need urgent help? Call the Cybercrime Helpline</p>
          <span class="helpline-number">1930</span>
        </div>
        """
        return self._send(to_email=victim_email, subject=subject, html_body=_render_email(subject, body))

    def send_verification(
        self,
        email: str,
        token: str,
        name: str,
    ) -> bool:
        """Send an email-verification link to a newly registered user."""
        verify_url = f"https://app.traceback.in/verify-email?token={token}"
        subject = "Verify your TraceBack account"
        body = f"""
        <h2>Welcome to TraceBack, {name}!</h2>
        <p>You're one step away from accessing India's most advanced cybercrime recovery platform.
           Please verify your email address to activate your account.</p>

        <a class="cta-button" href="{verify_url}">Verify Email Address</a>

        <p>Or copy and paste this link into your browser:</p>
        <div class="case-badge">{verify_url}</div>

        <div class="divider"></div>
        <p style="font-size:13px; color:#484f58;">
          This link expires in 24 hours. If you didn't create a TraceBack account, please ignore this email.
        </p>
        """
        return self._send(to_email=email, subject=subject, html_body=_render_email(subject, body))

    # ------------------------------------------------------------------
    # Internal SMTP sender with graceful fallback
    # ------------------------------------------------------------------

    def _send(self, to_email: str, subject: str, html_body: str) -> bool:
        """
        Attempt to send via SMTP. On any failure, log to console and
        return False (graceful degradation — the app continues working).
        """
        if not to_email:
            logger.error("Email send failed: recipient address is empty.")
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = self.sender
        msg["To"]      = to_email
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        # Plain-text fallback (strip tags naïvely for now)
        import re as _re
        plain = _re.sub(r"<[^>]+>", "", html_body)
        plain = _re.sub(r"\n{3,}", "\n\n", plain).strip()
        msg.attach(MIMEText(plain, "plain", "utf-8"))

        if not self.mail_username or not self.mail_password:
            self._console_fallback(to_email, subject, html_body)
            return False

        try:
            if self.mail_use_tls:
                server = smtplib.SMTP(self.mail_server, self.mail_port, timeout=10)
                server.ehlo()
                server.starttls()
                server.ehlo()
            else:
                server = smtplib.SMTP_SSL(self.mail_server, self.mail_port, timeout=10)

            server.login(self.mail_username, self.mail_password)
            server.sendmail(self.sender, [to_email], msg.as_string())
            server.quit()
            logger.info(f"Email sent to {to_email} | subject='{subject}'")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error(f"SMTP auth failed for user '{self.mail_username}'. Check credentials.")
            self._console_fallback(to_email, subject, html_body)
        except smtplib.SMTPConnectError:
            logger.error(f"Cannot connect to mail server {self.mail_server}:{self.mail_port}.")
            self._console_fallback(to_email, subject, html_body)
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error while sending to {to_email}: {e}")
            self._console_fallback(to_email, subject, html_body)
        except OSError as e:
            logger.error(f"Network error sending email: {e}")
            self._console_fallback(to_email, subject, html_body)

        return False

    def _console_fallback(self, to_email: str, subject: str, html_body: str) -> None:
        """Log email content to the console when SMTP is unavailable."""
        logger.warning(
            "\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  [TraceBack EmailService] SMTP unavailable — console log\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  To      : {to_email}\n"
            f"  Subject : {subject}\n"
            f"  Body    : {html_body[:400]}...\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
