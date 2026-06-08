using System.Net;
using System.Net.Mail;
using Microsoft.Extensions.Options;
using Recrutement_api.Configuration;
using Recrutement_api.DTOs.Email;
using Recrutement_api.Templates;

namespace Recrutement_api.Services.Shared;

public class EmailService
{
    private readonly EmailSettings _settings;
    private readonly ILogger<EmailService> _logger;

    public EmailService(IOptions<EmailSettings> settings, ILogger<EmailService> logger)
    {
        _settings = settings.Value;
        _logger = logger;
    }

    public async Task SendInvitationEmail(string email) =>
        await SendExpertInvitationAsync(new ExpertInvitationEmailDto
        {
            ToEmail = email,
            ToName = email,
            CompanyName = "votre entreprise",
            InvitedByName = "L'équipe RH",
            InvitationUrl = $"{_settings.FrontendBaseUrl}/login",
            ExpiresAt = DateTime.UtcNow.AddHours(48),
            TemporaryPassword = "changeme123"
        });

    public async Task SendExpertInvitationAsync(ExpertInvitationEmailDto dto)
    {
        var html = EmailTemplates.ExpertInvitation(
            dto.ToName, dto.CompanyName, dto.InvitedByName,
            dto.InvitationUrl, dto.ExpiresAt, dto.TemporaryPassword, dto.ToEmail);
        await SendAsync(dto.ToEmail, dto.ToName,
            $"Vos accès RecruitSaaS - {dto.CompanyName}", html);
        _logger.LogInformation("Invitation sent to {Email}", dto.ToEmail);
    }

    public async Task SendWelcomeEmailAsync(WelcomeEmailDto dto)
    {
        var html = EmailTemplates.Welcome(dto.ToName, dto.LoginUrl);
        await SendAsync(dto.ToEmail, dto.ToName, "Bienvenue sur RecruitSaaS !", html);
    }

    public async Task SendPasswordResetAsync(PasswordResetEmailDto dto)
    {
        var html = EmailTemplates.PasswordReset(dto.ToName, dto.ResetUrl, dto.ExpiresAt);
        await SendAsync(dto.ToEmail, dto.ToName, "Réinitialisation de mot de passe", html);
    }

    public async Task SendGenericAsync(GenericEmailDto dto)
    {
        await SendAsync(dto.ToEmail, dto.ToName, dto.Subject, dto.HtmlBody);
    }

    // ── Interview Invite ──────────────────────────────────────────────────────
    public async Task SendInterviewInviteAsync(
        string toEmail,
        string toName,
        string titreOffre,
        string nomEntreprise,
        string schedulingUrl,
        string? messagePersonnalise = null)
    {
        // Email simple texte → arrive dans Principal au lieu de Promotions
        var messageBlock = string.IsNullOrEmpty(messagePersonnalise)
            ? ""
            : $@"<p style=""margin:16px 0;padding:12px 16px;background:#f9f9f9;border-left:3px solid #333;font-size:14px;color:#333;"">
                    {messagePersonnalise}
               </p>";

        var html = $@"<!DOCTYPE html>
<html>
<head><meta charset=""UTF-8""/></head>
<body style=""font-family:Arial,sans-serif;font-size:15px;color:#222;max-width:600px;margin:0 auto;padding:24px;"">

  <p>Bonjour {toName},</p>

  <p>Félicitations ! Votre candidature pour le poste de <strong>{titreOffre}</strong> chez <strong>{nomEntreprise}</strong> a retenu notre attention.</p>

  <p>Nous souhaitons vous rencontrer lors d'un entretien virtuel avec notre recruteur IA.</p>

  {messageBlock}

  <p>Pour planifier votre entretien, cliquez sur le lien ci-dessous et choisissez le créneau qui vous convient parmi les disponibilités proposées :</p>

  <p><a href=""{schedulingUrl}"" style=""color:#1A2B4C;font-weight:bold;font-size:16px;"">Choisir mon créneau d'entretien</a></p>

  <p style=""font-size:13px;color:#666;"">Durée : 30 min · Format : entretien virtuel · Poste : {titreOffre}</p>

  <p style=""font-size:12px;color:#999;"">Ce lien est personnel, merci de ne pas le partager.</p>

  <p>Cordialement,<br/>L'équipe RH — {nomEntreprise}</p>

</body>
</html>";

        await SendAsync(
            toEmail, toName,
            $"Vous êtes retenu(e) pour un entretien — {titreOffre}",
            html);

        _logger.LogInformation(
            "[EMAIL] Interview invite sent to {Email} for {Poste}",
            toEmail, titreOffre);
    }

    // ── Core send ─────────────────────────────────────────────────────────────
    private async Task SendAsync(string toEmail, string toName, string subject, string htmlBody)
    {
        Exception? lastError = null;
        var viaApi = !string.IsNullOrWhiteSpace(_settings.ApiKey);
        var viaSmtp = HasSmtpConfig();
        _logger.LogInformation(
            "[EMAIL] Sending to {Email} (api={ViaApi}, smtp={ViaSmtp}, port={Port})",
            toEmail, viaApi, viaSmtp, _settings.SmtpPort);

        if (viaApi)
        {
            try
            {
                await SendViaBrevoApiAsync(toEmail, toName, subject, htmlBody);
                return;
            }
            catch (Exception ex)
            {
                lastError = ex;
                _logger.LogWarning(ex, "[EMAIL] Brevo API failed for {Email}, trying SMTP", toEmail);
            }
        }

        if (HasSmtpConfig())
        {
            try
            {
                await SendViaSmtpAsync(toEmail, toName, subject, htmlBody);
                return;
            }
            catch (Exception ex)
            {
                lastError = ex;
                _logger.LogError(ex, "[EMAIL] SMTP failed for {Email}", toEmail);
            }
        }

        if (lastError != null)
            throw new InvalidOperationException($"Unable to send email: {lastError.Message}", lastError);

        throw new InvalidOperationException("Email is not configured. Set EmailSettings:SmtpHost or EmailSettings:ApiKey.");
    }

    private bool HasSmtpConfig() =>
        !string.IsNullOrWhiteSpace(_settings.SmtpHost) &&
        !string.IsNullOrWhiteSpace(_settings.SmtpUsername) &&
        !string.IsNullOrWhiteSpace(_settings.SmtpPassword);

    private async Task SendViaBrevoApiAsync(string toEmail, string toName, string subject, string htmlBody)
    {
        using var http = new HttpClient();
        http.DefaultRequestHeaders.Add("api-key", _settings.ApiKey);

        var payload = new
        {
            sender = new { name = _settings.FromName, email = _settings.FromEmail },
            to = new[] { new { email = toEmail, name = toName } },
            subject,
            htmlContent = htmlBody
        };

        var response = await http.PostAsJsonAsync("https://api.brevo.com/v3/smtp/email", payload);
        if (response.IsSuccessStatusCode)
        {
            _logger.LogInformation("[EMAIL] Sent via Brevo API to {Email}", toEmail);
            return;
        }

        var err = await response.Content.ReadAsStringAsync();
        throw new InvalidOperationException($"Brevo API error: {err}");
    }

    private async Task SendViaSmtpAsync(string toEmail, string toName, string subject, string htmlBody)
    {
        // System.Net.Mail.SmtpClient only supports STARTTLS (port 587), not implicit SSL (465).
        var port = _settings.SmtpPort == 465 ? 587 : _settings.SmtpPort;
        if (_settings.SmtpPort == 465)
            _logger.LogWarning("[EMAIL] Port 465 is not supported by SmtpClient; using 587 (STARTTLS) instead.");

        var useSsl = port == 587 || _settings.SmtpUseSsl;

        using var client = new SmtpClient(_settings.SmtpHost, port)
        {
            EnableSsl = useSsl,
            DeliveryMethod = SmtpDeliveryMethod.Network,
            UseDefaultCredentials = false,
            Credentials = new NetworkCredential(_settings.SmtpUsername, _settings.SmtpPassword)
        };

        using var message = new MailMessage
        {
            From = new MailAddress(_settings.FromEmail, _settings.FromName),
            Subject = subject,
            IsBodyHtml = true,
            Body = htmlBody
        };
        message.To.Add(new MailAddress(toEmail, toName));

        await client.SendMailAsync(message);
        _logger.LogInformation("[EMAIL] Sent via SMTP to {Email}", toEmail);
    }
}