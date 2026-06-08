using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Recrutement_api.Data;
using Recrutement_api.DTOs;
using Recrutement_api.Models;
using BC = BCrypt.Net.BCrypt;

namespace Recrutement_api.Services
{
    // =========================================================
    // INTERFACE
    // =========================================================
    public interface IAuthService
    {
        string HashPassword(string password);
        bool VerifyPassword(string password, string hash);

        Task<string> RegisterCandidateAsync(RegisterDto dto);
        Task<string> RegisterCompanyAsync(CompanyRegisterDto dto);
        Task<AuthResponseDto> LoginAsync(LoginDto dto);
        Task<AuthResponseDto> ExternalLoginAsync(string provider, string externalId, string email, string displayName);
        Task<CurrentUserDto?> GetCurrentUserAsync(Guid userId);
    }

    // =========================================================
    // SERVICE IMPLEMENTATION
    // =========================================================
    public class AuthService : IAuthService
    {
        private readonly ApplicationDbContext _context;
        private readonly IJwtService _jwtService;
        private readonly PasswordHasher<string> _passwordHasher;

        public AuthService(ApplicationDbContext context, IJwtService jwtService)
        {
            _context = context;
            _jwtService = jwtService;
            _passwordHasher = new PasswordHasher<string>();
        }

        // ============================
        // PASSWORD MANAGEMENT
        // ============================
        public string HashPassword(string password)
        {
            return _passwordHasher.HashPassword(null, password);
        }

        public bool VerifyPassword(string password, string hash)
        {
            // BCrypt — utilisé pour les experts invités
            if (!string.IsNullOrEmpty(hash) &&
                (hash.StartsWith("$2a$") || hash.StartsWith("$2b$") || hash.StartsWith("$2y$")))
            {
                try { return BC.Verify(password, hash); }
                catch { return false; }
            }

            // ASP.NET Identity PasswordHasher — utilisé pour candidats/tenants/admin
            try
            {
                var result = _passwordHasher.VerifyHashedPassword(null, hash, password);
                return result == PasswordVerificationResult.Success
                    || result == PasswordVerificationResult.SuccessRehashNeeded;
            }
            catch { return false; }
        }

        // ============================
        // REGISTER CANDIDATE
        // ============================
        public async Task<string> RegisterCandidateAsync(RegisterDto dto)
        {
            if (string.IsNullOrWhiteSpace(dto.Email) ||
                string.IsNullOrWhiteSpace(dto.MotDePasse))
                throw new Exception("Email and password are required.");

            var emailExists = await _context.Utilisateurs
                .AnyAsync(u => u.Email == dto.Email);

            if (emailExists)
                throw new Exception("A user with this email already exists.");

            var user = new Utilisateur
            {
                Id             = Guid.NewGuid(),
                Email          = dto.Email,
                Nom            = dto.Nom,
                Prenom         = string.Empty,
                MotDePasseHash = HashPassword(dto.MotDePasse),
                Role           = RoleUtilisateur.Candidat,
                CreeLe         = DateTime.UtcNow
            };
            await _context.Utilisateurs.AddAsync(user);
            await _context.SaveChangesAsync();

            var candidat = new Candidat
            {
                Id            = Guid.NewGuid(),
                UtilisateurId = user.Id,
                Telephone     = string.Empty,
                CreeLe        = DateTime.UtcNow
            };
            await _context.Candidats.AddAsync(candidat);
            await _context.SaveChangesAsync();

            return "Your account has been created successfully. Welcome aboard!";
        }

        // ============================
        // REGISTER COMPANY (TENANT)
        // ============================
        public async Task<string> RegisterCompanyAsync(CompanyRegisterDto dto)
        {
            if (string.IsNullOrWhiteSpace(dto.WorkEmail) ||
                string.IsNullOrWhiteSpace(dto.Password) ||
                string.IsNullOrWhiteSpace(dto.TenantName))
                throw new Exception("Required fields are missing.");

            var emailExists = await _context.Utilisateurs
                .AnyAsync(u => u.Email == dto.WorkEmail);

            if (emailExists)
                throw new Exception("A user with this email already exists.");

            var user = new Utilisateur
            {
                Id             = Guid.NewGuid(),
                Email          = dto.WorkEmail,
                Nom            = dto.TenantName,
                Prenom         = string.Empty,
                Role           = RoleUtilisateur.Tenant,
                MotDePasseHash = HashPassword(dto.Password),
                CreeLe         = DateTime.UtcNow
            };
            await _context.Utilisateurs.AddAsync(user);
            await _context.SaveChangesAsync();

            var tenant = new Tenant
            {
                Id            = Guid.NewGuid(),
                UtilisateurId = user.Id,
                Statut        = TenantStatus.Pending,
                CreeLe        = DateTime.UtcNow
            };
            await _context.Tenants.AddAsync(tenant);
            await _context.SaveChangesAsync();

            var entreprise = new Entreprise
            {
                Id          = Guid.NewGuid(),
                Nom         = dto.CompanyName,
                RNE         = dto.RNE,
                Secteur     = dto.Industry,
                Description = string.Empty,
                LogoUrl     = string.Empty,
                TenantId    = tenant.Id,
                CreeLe      = DateTime.UtcNow
            };
            await _context.Entreprises.AddAsync(entreprise);
            await _context.SaveChangesAsync();

            return "Your company account has been registered successfully. It is currently under review — an administrator will confirm it shortly.";
        }

        // ============================
        // LOGIN
        // ============================
        public async Task<AuthResponseDto> LoginAsync(LoginDto dto)
        {
            if (string.IsNullOrWhiteSpace(dto.Email) ||
                string.IsNullOrWhiteSpace(dto.MotDePasse))
                throw new Exception("Email and password are required.");

            var user = await _context.Utilisateurs
                .FirstOrDefaultAsync(u => u.Email == dto.Email);

            if (user == null)
                throw new Exception("Incorrect email or password.");

            if (string.IsNullOrEmpty(user.MotDePasseHash))
                throw new Exception("This account uses social login. Please sign in with Google, Facebook or LinkedIn.");

            if (!VerifyPassword(dto.MotDePasse, user.MotDePasseHash))
                throw new Exception("Incorrect email or password.");

            return await BuildAuthResponseAsync(user);
        }

        // ============================
        // EXTERNAL LOGIN (Google / Facebook / LinkedIn)
        // ============================
        public async Task<AuthResponseDto> ExternalLoginAsync(
            string provider, string externalId, string email, string displayName)
        {
            if (string.IsNullOrWhiteSpace(provider) || string.IsNullOrWhiteSpace(externalId))
                throw new Exception("Invalid social login data.");

            if (string.IsNullOrWhiteSpace(email))
                throw new Exception("Email not provided by the social provider. Please allow email access.");

            provider = provider.ToLowerInvariant();
            email = email.Trim().ToLowerInvariant();

            var user = await _context.Utilisateurs
                .FirstOrDefaultAsync(u => u.AuthProvider == provider && u.ExternalId == externalId);

            if (user == null)
            {
                var existingByEmail = await _context.Utilisateurs
                    .FirstOrDefaultAsync(u => u.Email.ToLower() == email);

                if (existingByEmail != null)
                {
                    if (existingByEmail.AuthProvider == null && !string.IsNullOrEmpty(existingByEmail.MotDePasseHash))
                        throw new Exception("An account with this email already exists. Please log in with your password.");

                    existingByEmail.AuthProvider = provider;
                    existingByEmail.ExternalId = externalId;
                    user = existingByEmail;
                }
            }

            if (user == null)
            {
                var name = string.IsNullOrWhiteSpace(displayName)
                    ? email.Split('@')[0]
                    : displayName.Trim();

                user = new Utilisateur
                {
                    Id = Guid.NewGuid(),
                    Email = email,
                    Nom = name,
                    Prenom = string.Empty,
                    MotDePasseHash = null,
                    AuthProvider = provider,
                    ExternalId = externalId,
                    Role = RoleUtilisateur.Candidat,
                    CreeLe = DateTime.UtcNow
                };
                await _context.Utilisateurs.AddAsync(user);
                await _context.SaveChangesAsync();

                var candidat = new Candidat
                {
                    Id = Guid.NewGuid(),
                    UtilisateurId = user.Id,
                    Telephone = string.Empty,
                    CreeLe = DateTime.UtcNow
                };
                await _context.Candidats.AddAsync(candidat);
                await _context.SaveChangesAsync();
            }

            return await BuildAuthResponseAsync(user);
        }

        private async Task<AuthResponseDto> BuildAuthResponseAsync(Utilisateur user)
        {
            Guid? tenantId = null;
            Guid? expertId = null;
            Guid? candidatId = null;

            if (user.Role == RoleUtilisateur.Admin)
            {
                var adminProfile = await BuildUserProfileAsync(user);
                return new AuthResponseDto
                {
                    Token = _jwtService.GenerateToken(user, null, null, null),
                    UserName = adminProfile.FullName,
                    FullName = adminProfile.FullName,
                    Email = adminProfile.Email,
                    PhotoUrl = adminProfile.PhotoUrl,
                    Role = adminProfile.Role,
                };
            }

            if (user.Role == RoleUtilisateur.Tenant)
            {
                var tenant = await _context.Tenants.FirstOrDefaultAsync(t => t.UtilisateurId == user.Id);
                if (tenant == null) throw new Exception("Tenant account not found.");
                if (tenant.Statut != TenantStatus.Approved)
                    throw new Exception("Your company account has not been approved yet.");
                tenantId = tenant.Id;
            }

            if (user.Role == RoleUtilisateur.Expert)
            {
                var expert = await _context.Experts.FirstOrDefaultAsync(e => e.UtilisateurId == user.Id);
                if (expert == null) throw new Exception("Expert account not found.");
                expertId = expert.Id;
            }

            if (user.Role == RoleUtilisateur.Candidat)
            {
                var candidat = await _context.Candidats.FirstOrDefaultAsync(c => c.UtilisateurId == user.Id);
                if (candidat == null) throw new Exception("Candidate account not found.");
                candidatId = candidat.Id;
            }

            var token = _jwtService.GenerateToken(user, tenantId, expertId, candidatId);
            var profile = await BuildUserProfileAsync(user);
            return new AuthResponseDto
            {
                Token = token,
                UserName = profile.FullName,
                FullName = profile.FullName,
                Email = profile.Email,
                PhotoUrl = profile.PhotoUrl,
                Role = profile.Role,
            };
        }

        public async Task<CurrentUserDto?> GetCurrentUserAsync(Guid userId)
        {
            var user = await _context.Utilisateurs.FindAsync(userId);
            if (user == null) return null;
            return await BuildUserProfileAsync(user);
        }

        private static string FormatFullName(string? prenom, string? nom)
        {
            var parts = new[] { prenom, nom }
                .Where(s => !string.IsNullOrWhiteSpace(s))
                .Select(s => s!.Trim());
            return string.Join(" ", parts);
        }

        private async Task<CurrentUserDto> BuildUserProfileAsync(Utilisateur user)
        {
            var dto = new CurrentUserDto
            {
                Email = user.Email ?? "",
                Role = user.Role.ToString(),
                FullName = FormatFullName(user.Prenom, user.Nom),
            };
            if (string.IsNullOrWhiteSpace(dto.FullName))
                dto.FullName = user.Nom ?? user.Email ?? "";

            if (user.Role == RoleUtilisateur.Tenant)
            {
                var tenant = await _context.Tenants
                    .FirstOrDefaultAsync(t => t.UtilisateurId == user.Id);
                if (tenant != null)
                {
                    var tp = await _context.TenantProfiles
                        .FirstOrDefaultAsync(p => p.TenantId == tenant.Id);
                    if (!string.IsNullOrWhiteSpace(tp?.LogoUrl))
                        dto.PhotoUrl = tp.LogoUrl;
                }
            }
            else if (user.Role == RoleUtilisateur.Candidat)
            {
                var candidat = await _context.Candidats
                    .FirstOrDefaultAsync(c => c.UtilisateurId == user.Id);
                if (candidat != null)
                {
                    var cp = await _context.CandidateProfiles
                        .FirstOrDefaultAsync(p => p.CandidatId == candidat.Id);
                    if (!string.IsNullOrWhiteSpace(cp?.AvatarUrl))
                        dto.PhotoUrl = cp.AvatarUrl;
                }
            }
            else if (user.Role == RoleUtilisateur.Expert)
            {
                var expert = await _context.Experts
                    .FirstOrDefaultAsync(e => e.UtilisateurId == user.Id);
                if (expert != null)
                {
                    var name = FormatFullName(expert.FirstName, expert.LastName);
                    if (!string.IsNullOrWhiteSpace(name))
                        dto.FullName = name;
                }
            }

            return dto;
        }
    }
}