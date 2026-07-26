"""Email Template Renderer for GraphEin AI Enterprise Platform.

Supports responsive HTML, plain text fallbacks, dark mode styling, and French / English localizations.
"""

from typing import Any


class EmailTemplateRenderer:
    """Renders responsive HTML and Plain Text email templates for all GraphEin AI notification types."""

    BASE_HTML_WRAPPER = """<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="color-scheme" content="light dark">
  <meta name="supported-color-schemes" content="light dark">
  <title>{subject}</title>
  <style>
    :root {{
      --bg: #0F172A;
      --card-bg: #1E293B;
      --text-main: #F8FAFC;
      --text-muted: #94A3B8;
      --primary: #6366F1;
      --primary-hover: #4F46E5;
      --border: #334155;
    }}
    body {{
      margin: 0;
      padding: 0;
      background-color: #0F172A;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: #F8FAFC;
      -webkit-font-smoothing: antialiased;
    }}
    .email-container {{
      max-width: 580px;
      margin: 40px auto;
      background: #1E293B;
      border-radius: 12px;
      border: 1px solid #334155;
      overflow: hidden;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }}
    .email-header {{
      padding: 24px 32px;
      border-bottom: 1px solid #334155;
      background: #0F172A;
      display: flex;
      align-items: center;
    }}
    .brand-logo {{
      font-size: 20px;
      font-weight: 800;
      color: #FFFFFF;
      letter-spacing: -0.5px;
      text-decoration: none;
    }}
    .brand-logo span {{
      color: #6366F1;
    }}
    .email-body {{
      padding: 32px;
    }}
    h1 {{
      font-size: 22px;
      font-weight: 700;
      color: #FFFFFF;
      margin-top: 0;
      margin-bottom: 16px;
      line-height: 1.3;
    }}
    p {{
      font-size: 15px;
      line-height: 1.6;
      color: #94A3B8;
      margin-top: 0;
      margin-bottom: 20px;
    }}
    .btn-primary {{
      display: inline-block;
      padding: 12px 28px;
      background-color: #6366F1;
      color: #FFFFFF !important;
      font-weight: 600;
      font-size: 14px;
      border-radius: 8px;
      text-decoration: none;
      margin: 16px 0;
      text-align: center;
      transition: background-color 0.2s ease;
    }}
    .info-box {{
      background: #0F172A;
      border-radius: 8px;
      border: 1px solid #334155;
      padding: 16px;
      margin: 20px 0;
      font-size: 14px;
      color: #CBD5E1;
    }}
    .otp-code {{
      font-family: monospace;
      font-size: 28px;
      font-weight: 800;
      letter-spacing: 6px;
      color: #6366F1;
      text-align: center;
      padding: 16px;
      background: #0F172A;
      border-radius: 8px;
      border: 1px dashed #6366F1;
      margin: 20px 0;
    }}
    .email-footer {{
      padding: 20px 32px;
      background: #0F172A;
      border-top: 1px solid #334155;
      text-align: center;
      font-size: 12px;
      color: #64748B;
    }}
    .email-footer a {{
      color: #94A3B8;
      text-decoration: underline;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="email-header">
      <a href="https://graphein.ai" class="brand-logo">Graphein<span>AI</span></a>
    </div>
    <div class="email-body">
      {content_html}
    </div>
    <div class="email-footer">
      <p style="margin-bottom: 4px; font-size: 12px; color: #64748B;">
        &copy; 2026 GraphEin AI Enterprise. Tous droits réservés.
      </p>
      <p style="margin: 0; font-size: 11px; color: #475569;">
        Plateforme SaaS d'Intelligence Graphique VLM, AST & Data Analytics.
      </p>
    </div>
  </div>
</body>
</html>"""

    @classmethod
    def render(
        cls,
        template_name: str,
        lang: str = "fr",
        context: dict[str, Any] | None = None,
    ) -> tuple[str, str, str]:
        """Renders (subject, html_body, text_body) for a given template_name and locale language."""
        ctx = context or {}
        lang_code = lang.lower() if lang in ("fr", "en") else "fr"
        is_fr = lang_code == "fr"

        user_name = ctx.get("user_name", "Utilisateur" if is_fr else "User")
        action_url = ctx.get("action_url", "http://localhost:8088")
        workspace_name = ctx.get("workspace_name", "GraphEin Workspace")
        chart_title = ctx.get("chart_title", "Graphique VLM")
        otp_code = ctx.get("otp_code", "123456")

        if template_name == "welcome":
            subject = "Bienvenue sur GraphEin AI Enterprise 🎉" if is_fr else "Welcome to GraphEin AI Enterprise 🎉"
            html_content = f"""
              <h1>{"Bienvenue sur GraphEin AI" if is_fr else "Welcome to GraphEin AI"}, {user_name} !</h1>
              <p>{"Votre compte Enterprise a été créé avec succès. Vous avez désormais accès à notre suite d'intelligence graphique propulsée par Gemini Flash Vision, OpenCV et AST." if is_fr else "Your Enterprise account has been successfully created. You now have access to our graph intelligence suite powered by Gemini Flash Vision, OpenCV, and AST."}</p>
              <div class="info-box">
                <strong>{"Détails de votre accès :" if is_fr else "Access Details:"}</strong><br>
                • {"Entreprise :" if is_fr else "Company:"} {ctx.get("company", "Graphein Corp")}<br>
                • {"Rôle :" if is_fr else "Role:"} {ctx.get("role", "Standard User")}<br>
                • {"Module d'explicabilité & AST actif" if is_fr else "Explainability & AST module active"}
              </div>
              <a href="{action_url}" class="btn-primary">{"Accéder au Studio d'Analyse" if is_fr else "Access Analysis Studio"}</a>
            """
            text_body = f"Bienvenue sur GraphEin AI, {user_name}!\nAccédez à votre espace: {action_url}"

        elif template_name in ("verify_email", "verification"):
            subject = "Vérification de votre adresse e-mail" if is_fr else "Verify your email address"
            html_content = f"""
              <h1>{"Vérification E-mail" if is_fr else "Email Verification"}</h1>
              <p>{"Bonjour" if is_fr else "Hello"} {user_name}, {"veuillez confirmer votre adresse e-mail en cliquant sur le bouton ci-dessous :" if is_fr else "please confirm your email address by clicking the button below:"}</p>
              <a href="{action_url}" class="btn-primary">{"Vérifier mon E-mail" if is_fr else "Verify My Email"}</a>
              <p style="font-size: 12px; color: #64748B;">{"Ce lien expirera dans 24 heures." if is_fr else "This link expires in 24 hours."}</p>
            """
            text_body = f"Vérifiez votre e-mail: {action_url}"

        elif template_name == "reset_password":
            subject = "Réinitialisation de votre mot de passe" if is_fr else "Password Reset Request"
            html_content = f"""
              <h1>{"Réinitialisation de Mot de Passe" if is_fr else "Reset Password"}</h1>
              <p>{"Bonjour" if is_fr else "Hello"} {user_name}, {"nous avons reçu une demande de réinitialisation de mot de passe pour votre compte." if is_fr else "we received a request to reset your password for your account."}</p>
              <a href="{action_url}" class="btn-primary">{"Réinitialiser le mot de passe" if is_fr else "Reset Password"}</a>
              <p style="font-size: 12px; color: #64748B;">{"Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer cet e-mail en toute sécurité." if is_fr else "If you did not request this, you can safely ignore this email."}</p>
            """
            text_body = f"Réinitialisez votre mot de passe ici: {action_url}"

        elif template_name in ("workspace_invitation", "collaborator_invitation"):
            inviter = ctx.get("inviter_name", "Un administrateur" if is_fr else "An administrator")
            subject = f"Invitation à rejoindre le Workspace {workspace_name}" if is_fr else f"Invitation to join Workspace {workspace_name}"
            html_content = f"""
              <h1>{"Invitation Workspace GraphEin AI" if is_fr else "GraphEin AI Workspace Invitation"}</h1>
              <p>{inviter} {"vous a invité à collaborer sur le workspace" if is_fr else "invited you to collaborate on workspace"} <strong>{workspace_name}</strong> {"avec le rôle" if is_fr else "with the role"} <strong>{ctx.get("role", "Editeur")}</strong>.</p>
              <a href="{action_url}" class="btn-primary">{"Accepter l'Invitation" if is_fr else "Accept Invitation"}</a>
            """
            text_body = f"Rejoignez le workspace {workspace_name}: {action_url}"

        elif template_name == "analysis_shared":
            subject = f"Analyse partagée : {chart_title}" if is_fr else f"Shared Analysis: {chart_title}"
            html_content = f"""
              <h1>{"Nouveau Graphique Partagé" if is_fr else "New Shared Chart"}</h1>
              <p>{user_name} {"a partagé une nouvelle analyse graphique avec vous :" if is_fr else "shared a new chart analysis with you:"} <strong>{chart_title}</strong>.</p>
              <a href="{action_url}" class="btn-primary">{"Consulter l'Analyse" if is_fr else "View Analysis"}</a>
            """
            text_body = f"Consultez l'analyse {chart_title}: {action_url}"

        elif template_name == "analysis_finished":
            subject = f"Analyse VLM & AST terminée : {chart_title}" if is_fr else f"VLM & AST Analysis Finished: {chart_title}"
            html_content = f"""
              <h1>{"Analyse Graphique Terminée" if is_fr else "Chart Analysis Completed"}</h1>
              <p>{"L'extraction visuelle et le calcul déterministe AST pour le graphique" if is_fr else "Visual extraction and AST calculation for chart"} <strong>{chart_title}</strong> {"sont désormais disponibles." if is_fr else "are now available."}</p>
              <div class="info-box">
                • {"Score de confiance :" if is_fr else "Confidence Score:"} {ctx.get("confidence", "98%")}<br>
                • {"Temps d'exécution :" if is_fr else "Execution Latency:"} {ctx.get("latency", "1.2s")}
              </div>
              <a href="{action_url}" class="btn-primary">{"Voir le Rapport Complet" if is_fr else "View Full Report"}</a>
            """
            text_body = f"Analyse terminée pour {chart_title}: {action_url}"

        elif template_name == "otp":
            subject = f"Code de sécurité OTP : {otp_code}" if is_fr else f"Security OTP Code: {otp_code}"
            html_content = f"""
              <h1>{"Code de Sécurité OTP" if is_fr else "Security OTP Code"}</h1>
              <p>{"Voici votre code de vérification temporaire :" if is_fr else "Here is your temporary verification code:"}</p>
              <div class="otp-code">{otp_code}</div>
              <p style="font-size: 12px; color: #64748B;">{"Ce code expire dans 15 minutes." if is_fr else "This code expires in 15 minutes."}</p>
            """
            text_body = f"Votre code OTP GraphEin AI: {otp_code}"

        elif template_name == "profile_updated":
            subject = "Mise à jour de votre profil GraphEin AI" if is_fr else "GraphEin AI Profile Updated"
            html_content = f"""
              <h1>{"Profil Mis à Jour" if is_fr else "Profile Updated"}</h1>
              <p>{"Bonjour" if is_fr else "Hello"} {user_name}, {"les informations de votre profil professionnel ont été mises à jour avec succès." if is_fr else "your professional profile details have been successfully updated."}</p>
            """
            text_body = f"Profil mis à jour pour {user_name}."

        elif template_name == "account_created":
            subject = "Nouveau compte créé" if is_fr else "New Account Created"
            html_content = f"<h1>{"Compte Créé" if is_fr else "Account Created"}</h1><p>{"Bonjour" if is_fr else "Hello"} {user_name}, {"votre compte SaaS a été créé avec succès." if is_fr else "your SaaS account has been successfully created."}</p>"
            text_body = f"Compte créé pour {user_name}."

        elif template_name == "account_deleted":
            subject = "Confirmation de suppression de compte" if is_fr else "Account Deletion Confirmation"
            html_content = f"<h1>{"Compte Supprimé" if is_fr else "Account Deleted"}</h1><p>{"Votre compte GraphEin AI a été définitivement supprimé." if is_fr else "Your GraphEin AI account has been permanently deleted."}</p>"
            text_body = "Votre compte a été supprimé."

        elif template_name == "workspace_created":
            subject = f"Nouveau Workspace créé : {workspace_name}" if is_fr else f"New Workspace Created: {workspace_name}"
            html_content = f"<h1>{"Workspace Créé" if is_fr else "Workspace Created"}</h1><p>{"Le workspace" if is_fr else "The workspace"} <strong>{workspace_name}</strong> {"a été créé." if is_fr else "has been created."}</p>"
            text_body = f"Workspace {workspace_name} créé."

        elif template_name == "workspace_deleted":
            subject = f"Suppression du Workspace : {workspace_name}" if is_fr else f"Workspace Deleted: {workspace_name}"
            html_content = f"<h1>{"Workspace Supprimé" if is_fr else "Workspace Deleted"}</h1><p>{"Le workspace" if is_fr else "The workspace"} <strong>{workspace_name}</strong> {"a été supprimé." if is_fr else "has been deleted."}</p>"
            text_body = f"Workspace {workspace_name} supprimé."

        else:
            subject = ctx.get("subject", "Notification GraphEin AI")
            msg_text = ctx.get("message", "Nouvelle notification disponible.")
            html_content = f"<h1>Notification</h1><p>{msg_text}</p><a href='{action_url}' class='btn-primary'>Ouvrir l'application</a>"
            text_body = msg_text

        final_html = cls.BASE_HTML_WRAPPER.format(
            lang=lang_code,
            subject=subject,
            content_html=html_content,
        )
        return subject, final_html, text_body
