using System.Net.Http.Headers;
using System.Security.Claims;
using System.Text.Json;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Facebook;
using Microsoft.AspNetCore.Authentication.Google;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Authentication.OAuth;
using Microsoft.IdentityModel.Tokens;
using Recrutement_api.Services.Auth;
using System.Text;

namespace Recrutement_api.Extensions
{
    public static class ExternalAuthExtensions
    {
        public static IServiceCollection AddTalentFlowAuthentication(
            this IServiceCollection services, IConfiguration config)
        {
            var secret = config["Jwt:Secret"]
                ?? throw new Exception("JWT Secret is not configured in appsettings.json");
            var issuer = config["Jwt:Issuer"];
            var audience = config["Jwt:Audience"];
            var frontendUrl = config["Frontend:Url"] ?? "http://localhost:5173";

            var authBuilder = services.AddAuthentication(options =>
            {
                options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
                options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
                options.DefaultSignInScheme = ExternalAuthConstants.ExternalCookieScheme;
            })
            .AddJwtBearer(options =>
            {
                options.TokenValidationParameters = new TokenValidationParameters
                {
                    ValidateIssuer = true,
                    ValidateAudience = true,
                    ValidateLifetime = true,
                    ValidateIssuerSigningKey = true,
                    ValidIssuer = issuer,
                    ValidAudience = audience,
                    IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secret)),
                    RoleClaimType = "role"
                };
            })
            .AddCookie(ExternalAuthConstants.ExternalCookieScheme, options =>
            {
                options.Cookie.Name = "TalentFlow.ExternalAuth";
                options.Cookie.HttpOnly = true;
                options.Cookie.SameSite = SameSiteMode.Lax;
                options.Cookie.SecurePolicy = CookieSecurePolicy.SameAsRequest;
                options.ExpireTimeSpan = TimeSpan.FromMinutes(15);
            });

            var googleClientId = config["Authentication:Google:ClientId"];
            var googleClientSecret = config["Authentication:Google:ClientSecret"];
            if (!string.IsNullOrWhiteSpace(googleClientId) && !string.IsNullOrWhiteSpace(googleClientSecret))
            {
                authBuilder.AddGoogle(GoogleDefaults.AuthenticationScheme, options =>
                {
                    options.ClientId = googleClientId;
                    options.ClientSecret = googleClientSecret;
                    options.SignInScheme = ExternalAuthConstants.ExternalCookieScheme;
                    options.CallbackPath = "/api/auth/signin-google";
                    options.SaveTokens = true;
                    ConfigureRemoteFailure(options.Events, frontendUrl);
                });
            }

            var facebookAppId = config["Authentication:Facebook:AppId"];
            var facebookAppSecret = config["Authentication:Facebook:AppSecret"];
            if (!string.IsNullOrWhiteSpace(facebookAppId) && !string.IsNullOrWhiteSpace(facebookAppSecret))
            {
                authBuilder.AddFacebook(FacebookDefaults.AuthenticationScheme, options =>
                {
                    options.AppId = facebookAppId;
                    options.AppSecret = facebookAppSecret;
                    options.SignInScheme = ExternalAuthConstants.ExternalCookieScheme;
                    options.CallbackPath = "/api/auth/signin-facebook";
                    options.SaveTokens = true;
                    options.Fields.Add("email");
                    options.Fields.Add("name");
                    ConfigureRemoteFailure(options.Events, frontendUrl);
                });
            }

            var linkedInClientId = config["Authentication:LinkedIn:ClientId"];
            var linkedInClientSecret = config["Authentication:LinkedIn:ClientSecret"];
            if (!string.IsNullOrWhiteSpace(linkedInClientId) && !string.IsNullOrWhiteSpace(linkedInClientSecret))
            {
                authBuilder.AddOAuth(ExternalAuthConstants.LinkedInScheme, options =>
                {
                    options.ClientId = linkedInClientId;
                    options.ClientSecret = linkedInClientSecret;
                    options.SignInScheme = ExternalAuthConstants.ExternalCookieScheme;
                    options.CallbackPath = "/api/auth/signin-linkedin";
                    options.AuthorizationEndpoint = "https://www.linkedin.com/oauth/v2/authorization";
                    options.TokenEndpoint = "https://www.linkedin.com/oauth/v2/accessToken";
                    options.UserInformationEndpoint = "https://api.linkedin.com/v2/userinfo";
                    options.Scope.Clear();
                    options.Scope.Add("openid");
                    options.Scope.Add("profile");
                    options.Scope.Add("email");
                    options.SaveTokens = true;
                    options.ClaimActions.MapJsonKey(ClaimTypes.NameIdentifier, "sub");
                    options.ClaimActions.MapJsonKey(ClaimTypes.Email, "email");
                    options.ClaimActions.MapJsonKey(ClaimTypes.Name, "name");
                    options.ClaimActions.MapJsonKey(ClaimTypes.GivenName, "given_name");
                    options.ClaimActions.MapJsonKey(ClaimTypes.Surname, "family_name");

                    ConfigureRemoteFailure(options.Events, frontendUrl);

                    // LinkedIn OpenID Connect : récupération explicite du profil
                    options.Events.OnCreatingTicket = async context =>
                    {
                        var request = new HttpRequestMessage(
                            HttpMethod.Get,
                            context.Options.UserInformationEndpoint);
                        request.Headers.Authorization =
                            new AuthenticationHeaderValue("Bearer", context.AccessToken);

                        var response = await context.Backchannel.SendAsync(
                            request,
                            context.HttpContext.RequestAborted);

                        if (!response.IsSuccessStatusCode)
                        {
                            var body = await response.Content.ReadAsStringAsync(context.HttpContext.RequestAborted);
                            throw new InvalidOperationException(
                                $"LinkedIn userinfo error ({(int)response.StatusCode}): {body}");
                        }

                        await using var stream = await response.Content.ReadAsStreamAsync(
                            context.HttpContext.RequestAborted);
                        using var doc = await JsonDocument.ParseAsync(stream, cancellationToken: context.HttpContext.RequestAborted);
                        context.RunClaimActions(doc.RootElement);
                    };
                });
            }

            services.AddAuthorization();
            return services;
        }

        private static void ConfigureRemoteFailure(OAuthEvents events, string frontendUrl)
        {
            events.OnRemoteFailure = context =>
            {
                var error = context.Failure?.Message ?? "Connexion sociale annulée ou échouée.";
                context.Response.Redirect(
                    $"{frontendUrl}/login?error={Uri.EscapeDataString(error)}");
                context.HandleResponse();
                return Task.CompletedTask;
            };
        }

        public static bool IsProviderConfigured(IConfiguration config, string provider)
        {
            return provider.ToLowerInvariant() switch
            {
                "google" => !string.IsNullOrWhiteSpace(config["Authentication:Google:ClientId"])
                    && !string.IsNullOrWhiteSpace(config["Authentication:Google:ClientSecret"]),
                "facebook" => !string.IsNullOrWhiteSpace(config["Authentication:Facebook:AppId"])
                    && !string.IsNullOrWhiteSpace(config["Authentication:Facebook:AppSecret"]),
                "linkedin" => !string.IsNullOrWhiteSpace(config["Authentication:LinkedIn:ClientId"])
                    && !string.IsNullOrWhiteSpace(config["Authentication:LinkedIn:ClientSecret"]),
                _ => false
            };
        }

    }
}
