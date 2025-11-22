import smtplib
from email.message import EmailMessage

# 🟢 CONFIGURATION
EMAIL_ADDRESS = "bouye1978saturnin@gmail.com"          # ton adresse Gmail complète
EMAIL_PASSWORD = "fenwtxqxjngqcyt"        # ton mot de passe d'application Gmail
DESTINATAIRE = "bouyesaturnin@yahoo.fr"     # l'adresse du destinataire

# 🟢 CONTENU DU MAIL
msg = EmailMessage()
msg['Subject'] = "Test SMTP avec Gmail"
msg['From'] = EMAIL_ADDRESS
msg['To'] = DESTINATAIRE
msg.set_content("Ceci est un test d'envoi de mail via Gmail SMTP avec mot de passe d'application.")

# 🟢 ENVOI DU MAIL
try:
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()                # se présenter au serveur
        smtp.starttls()            # activer TLS
        smtp.ehlo()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # login avec mot de passe d'application
        smtp.send_message(msg)
    print("✅ Email envoyé avec succès !")
except smtplib.SMTPAuthenticationError as auth_error:
    print("❌ Erreur d'authentification : vérifie ton email et ton mot de passe d'application.")
except Exception as e:
    print(f"❌ Une erreur est survenue : {e}")
