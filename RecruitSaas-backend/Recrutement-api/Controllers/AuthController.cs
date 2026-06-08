using System.Security.Claims;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Recrutement_api.Data;
using Recrutement_api.DTOs;
using Recrutement_api.Extensions;
using Recrutement_api.Models;
using Recrutement_api.Services;
using Recrutement_api.Services.Auth;

namespace Recrutement_api.Controllers
{
    [ApiController]
    [Route("api/auth")]
    public class AuthController : ControllerBase
    {
        private readonly IAuthService _authService;
        private readonly ApplicationDbContext _context;
        private readonly IConfiguration _configuration;

        public AuthController(
            IAuthService authService,
            ApplicationDbContext context,
            IConfiguration configuration)
        {
            _authService = authService;
            _context = context;
            _configuration = configuration;
        }

        [HttpPost("register")]
        public async Task<IActionResult> RegisterCandidate([FromBody] RegisterDto dto)
        {
            try
            {
                var message = await _authService.RegisterCandidateAsync(dto);
                return Ok(new { Message = message });
            }
            catch (Exception ex)
            {
                return BadRequest(new { Message = ex.Message });
            }
        }

        [HttpPost("company/register")]
        public async Task<IActionResult> RegisterCompany([FromBody] CompanyRegisterDto dto)
        {
            try
            {
                var message = await _authService.RegisterCompanyAsync(dto);
                return Ok(new { Message = message });
            }
            catch (Exception ex)
            {
                return BadRequest(new { Message = ex.Message });
            }
        }

        [HttpPost("login")]
        public async Task<IActionResult> Login([FromBody] LoginDto dto)
        {
            try
            {
                var response = await _authService.LoginAsync(dto);
                return Ok(response);
            }
            catch (Exception ex)
            {
                return Unauthorized(new { message = ex.Message });
            }
        }

        [HttpGet("me")]
        [Authorize]
        public async Task<IActionResult> GetCurrentUser()
        {
            var userIdStr = User.FindFirstValue("userId")
                ?? User.FindFirstValue("sub")
                ?? User.FindFirstValue(ClaimTypes.NameIdentifier);

            if (string.IsNullOrEmpty(userIdStr) || !Guid.TryParse(userIdStr, out var userId))
                return Unauthorized(new { message = "Token invalide." });

            var profile = await _authService.GetCurrentUserAsync(userId);
            if (profile == null)
                return NotFound(new { message = "Utilisateur introuvable." });

            return Ok(profile);
        }

        // ── Changer le mot de passe (Expert + tous les rôles) ──────────
        [HttpPost("change-password")]
        [Authorize]
        public async Task<IActionResult> ChangePassword([FromBody] ChangePasswordDto dto)
        {
            try
            {
                // Lire l'userId depuis le token JWT
                var userIdStr = User.FindFirstValue("userId")
                             ?? User.FindFirstValue("sub")
                             ?? User.FindFirstValue(ClaimTypes.NameIdentifier);

                if (string.IsNullOrEmpty(userIdStr))
                    return Unauthorized(new { message = "Token invalide." });

                var userId = Guid.Parse(userIdStr);

                var user = await _context.Utilisateurs.FindAsync(userId);
                if (user == null)
                    return NotFound(new { message = "Utilisateur introuvable." });

                // Vérifier l'ancien mot de passe
                if (string.IsNullOrEmpty(user.MotDePasseHash))
                    return BadRequest(new { message = "Ce compte utilise une connexion sociale. Le mot de passe ne peut pas être modifié ici." });

                if (!_authService.VerifyPassword(dto.AncienMotDePasse, user.MotDePasseHash))
                    return BadRequest(new { message = "Mot de passe actuel incorrect." });

                // Mettre à jour
                user.MotDePasseHash = _authService.HashPassword(dto.NouveauMotDePasse);
                await _context.SaveChangesAsync();

                return Ok(new { message = "Mot de passe mis à jour avec succès." });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { message = ex.Message });
            }
        }

        /// <summary>Redirect to Google, Facebook or LinkedIn OAuth.</summary>
        [HttpGet("external/{provider}")]
        public async Task<IActionResult> ExternalLogin(string provider, [FromQuery] string? returnUrl = null)
        {
            var frontendUrl = _configuration["Frontend:Url"] ?? "http://localhost:5173";
            var normalized = provider.ToLowerInvariant();

            if (!ExternalAuthConstants.ProviderSchemes.TryGetValue(normalized, out var scheme))
            {
                return Redirect($"{frontendUrl}/login?error={Uri.EscapeDataString("Fournisseur inconnu.")}");
            }

            if (!ExternalAuthExtensions.IsProviderConfigured(_configuration, normalized))
            {
                var msg = $"Connexion {provider} non configurée. Copiez appsettings.SocialAuth.json.example vers appsettings.SocialAuth.json et ajoutez vos clés API.";
                return Redirect($"{frontendUrl}/login?error={Uri.EscapeDataString(msg)}");
            }

            var schemeProvider = HttpContext.RequestServices.GetRequiredService<IAuthenticationSchemeProvider>();
            if (await schemeProvider.GetSchemeAsync(scheme) == null)
            {
                var msg = $"Le serveur n'a pas chargé le fournisseur {provider}. Redémarrez l'API après avoir configuré appsettings.SocialAuth.json.";
                return Redirect($"{frontendUrl}/login?error={Uri.EscapeDataString(msg)}");
            }

            var callbackUrl = Url.Action(nameof(ExternalLoginCallback), "Auth", null, Request.Scheme)!;
            var properties = new AuthenticationProperties { RedirectUri = callbackUrl };
            properties.Items["returnUrl"] = string.IsNullOrWhiteSpace(returnUrl) ? "/dashboard" : returnUrl;
            properties.Items["provider"] = normalized;

            return Challenge(properties, scheme);
        }

        [HttpGet("external/callback")]
        public async Task<IActionResult> ExternalLoginCallback()
        {
            var frontendUrl = _configuration["Frontend:Url"] ?? "http://localhost:5173";

            var result = await HttpContext.AuthenticateAsync(ExternalAuthConstants.ExternalCookieScheme);
            if (!result.Succeeded)
            {
                return Redirect($"{frontendUrl}/login?error=oauth_failed");
            }

            try
            {
                var principal = result.Principal!;
                var provider = MapSchemeToProvider(result.Ticket?.AuthenticationScheme)
                    ?? (result.Properties?.Items.TryGetValue("provider", out var p) == true && !string.IsNullOrEmpty(p) ? p : null)
                    ?? DetectProviderFromPrincipal(principal);

                var externalId = principal.FindFirstValue(ClaimTypes.NameIdentifier)
                    ?? principal.FindFirstValue("sub")
                    ?? throw new Exception("Identifiant externe manquant.");

                var email = principal.FindFirstValue(ClaimTypes.Email)
                    ?? principal.FindFirstValue("email");

                var displayName = principal.FindFirstValue(ClaimTypes.Name)
                    ?? principal.Identity?.Name
                    ?? BuildNameFromClaims(principal);

                var authResponse = await _authService.ExternalLoginAsync(
                    provider, externalId, email ?? "", displayName ?? "");

                await HttpContext.SignOutAsync(ExternalAuthConstants.ExternalCookieScheme);

                var returnUrl = result.Properties?.Items.TryGetValue("returnUrl", out var ru) == true ? ru : "/dashboard";
                var token = Uri.EscapeDataString(authResponse.Token);
                var userName = Uri.EscapeDataString(authResponse.UserName ?? "User");

                return Redirect($"{frontendUrl}/auth/callback?token={token}&userName={userName}&returnUrl={Uri.EscapeDataString(returnUrl)}");
            }
            catch (Exception ex)
            {
                await HttpContext.SignOutAsync(ExternalAuthConstants.ExternalCookieScheme);
                var msg = Uri.EscapeDataString(ex.Message);
                return Redirect($"{frontendUrl}/login?error={msg}");
            }
        }

        [HttpGet("external/providers")]
        public IActionResult GetConfiguredProviders()
        {
            var providers = new[] { "google", "facebook", "linkedin" }
                .Where(p => ExternalAuthExtensions.IsProviderConfigured(_configuration, p))
                .ToList();
            return Ok(new { providers });
        }

        private static string Capitalize(string s) =>
            s.Length > 0 ? char.ToUpper(s[0]) + s[1..] : s;

        private static string? MapSchemeToProvider(string? scheme) =>
            scheme?.ToLowerInvariant() switch
            {
                "google" => "google",
                "facebook" => "facebook",
                "linkedin" => "linkedin",
                _ => null
            };

        private static string DetectProviderFromPrincipal(ClaimsPrincipal principal)
        {
            var issuer = principal.FindFirst("iss")?.Value ?? "";
            if (issuer.Contains("google", StringComparison.OrdinalIgnoreCase)) return "google";
            if (issuer.Contains("facebook", StringComparison.OrdinalIgnoreCase)) return "facebook";
            if (issuer.Contains("linkedin", StringComparison.OrdinalIgnoreCase)) return "linkedin";
            return "google";
        }

        private static string BuildNameFromClaims(ClaimsPrincipal principal)
        {
            var given = principal.FindFirstValue(ClaimTypes.GivenName);
            var family = principal.FindFirstValue(ClaimTypes.Surname);
            if (!string.IsNullOrWhiteSpace(given) && !string.IsNullOrWhiteSpace(family))
                return $"{given} {family}".Trim();
            return given ?? family ?? "";
        }
    }
}