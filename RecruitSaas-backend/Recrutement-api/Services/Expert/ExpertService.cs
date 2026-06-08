namespace Recrutement_api.Services.Expert;

using Recrutement_api.Configuration;
using Recrutement_api.DTOs.Email;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Recrutement_api.Data;
using Recrutement_api.DTOs.Expert;
using Recrutement_api.Models;
using Recrutement_api.Services.Shared;
using BC = BCrypt.Net.BCrypt;

public class ExpertService
{
    private readonly ApplicationDbContext _context;
    private readonly EmailService _emailService;
    private readonly EmailSettings _emailSettings;
    private readonly ILogger<ExpertService> _logger;

    public ExpertService(
        ApplicationDbContext context,
        EmailService emailService,
        IOptions<EmailSettings> emailSettings,
        ILogger<ExpertService> logger)
    {
        _context = context;
        _emailService = emailService;
        _emailSettings = emailSettings.Value;
        _logger = logger;
    }

    private async Task<Guid> ResolveTenantIdAsync(Guid userOrTenantId)
    {
        bool isTenant = await _context.Tenants.AnyAsync(t => t.Id == userOrTenantId);
        if (isTenant) return userOrTenantId;

        var tenant = await _context.Tenants
            .FirstOrDefaultAsync(t => t.UtilisateurId == userOrTenantId);

        if (tenant == null)
            throw new UnauthorizedAccessException("Tenant introuvable pour cet utilisateur.");

        return tenant.Id;
    }

    // 1. INVITER un expert
    public async Task<ExpertResponseDto> InviteExpertAsync(InviteExpertDto dto, Guid userOrTenantId)
    {
        var tenantId = await ResolveTenantIdAsync(userOrTenantId);

        var company = await _context.Companies
            .FirstOrDefaultAsync(c => c.Id == dto.CompanyId && c.TenantId == tenantId)
            ?? throw new KeyNotFoundException("Entreprise introuvable ou acces refuse.");

        var invitedByName = await GetInvitedByNameAsync(tenantId);

        // ✅ Vérification email dans Experts
        bool existe = await _context.Experts
            .AnyAsync(e => e.Email == dto.Email && e.CompanyId == dto.CompanyId);
        if (existe)
            throw new InvalidOperationException($"Un expert avec l'email {dto.Email} existe déjà dans cette entreprise.");

        // ✅ Vérification email dans Utilisateurs (contrainte unique globale)
        bool utilisateurExiste = await _context.Utilisateurs
            .AnyAsync(u => u.Email == dto.Email);
        if (utilisateurExiste)
            throw new InvalidOperationException($"Un compte avec l'email {dto.Email} existe déjà sur la plateforme.");

        var tempPassword = GenerateTempPassword();

        var utilisateur = new Utilisateur
        {
            Id             = Guid.NewGuid(),
            Email          = dto.Email,
            Nom            = dto.LastName,
            Prenom         = dto.FirstName,
            Role           = RoleUtilisateur.Expert,
            MotDePasseHash = BC.HashPassword(tempPassword),
            EstActif       = true,
            CreeLe         = DateTime.UtcNow,
            Telephone      = ""
        };

        _context.Utilisateurs.Add(utilisateur);

        var expert = new Expert
        {
            FirstName         = dto.FirstName,
            LastName          = dto.LastName,
            Email             = dto.Email,
            CompanyId         = dto.CompanyId,
            EntrepriseId      = dto.CompanyId,
            TenantId          = tenantId,
            IsInvited         = true,
            IsActive          = true,
            Poste             = dto.Poste,
            TemporaryPassword = BC.HashPassword(tempPassword),
            UtilisateurId     = utilisateur.Id
        };

        _context.Experts.Add(expert);
        await _context.SaveChangesAsync();

        await _context.Entry(expert).Reference(e => e.Company).LoadAsync();

        var invitationEmailSent = await TrySendInvitationEmailAsync(
            dto.Email,
            $"{dto.FirstName} {dto.LastName}",
            company.Nom,
            invitedByName,
            tempPassword);

        var response = ToDto(expert);
        response.InvitationEmailSent = invitationEmailSent;
        return response;
    }

    public async Task<ExpertResponseDto> ResendInvitationAsync(Guid expertId, Guid userOrTenantId)
    {
        var tenantId = await ResolveTenantIdAsync(userOrTenantId);

        var expert = await _context.Experts
            .Include(e => e.Company)
            .Include(e => e.Utilisateur)
            .FirstOrDefaultAsync(e => e.Id == expertId && e.TenantId == tenantId)
            ?? throw new KeyNotFoundException("Expert not found.");

        if (expert.Utilisateur == null)
            throw new InvalidOperationException("No user account linked to this expert.");

        var tempPassword = GenerateTempPassword();
        expert.TemporaryPassword = BC.HashPassword(tempPassword);
        expert.Utilisateur.MotDePasseHash = BC.HashPassword(tempPassword);
        expert.IsInvited = true;
        await _context.SaveChangesAsync();

        var invitationEmailSent = await TrySendInvitationEmailAsync(
            expert.Email,
            $"{expert.FirstName} {expert.LastName}".Trim(),
            expert.Company?.Nom ?? "your company",
            await GetInvitedByNameAsync(tenantId),
            tempPassword);

        var response = ToDto(expert);
        response.InvitationEmailSent = invitationEmailSent;
        return response;
    }

    private async Task<string> GetInvitedByNameAsync(Guid tenantId)
    {
        var tenant = await _context.Tenants
            .Include(t => t.Utilisateur)
            .FirstOrDefaultAsync(t => t.Id == tenantId);

        var invitedByName = tenant?.Utilisateur != null
            ? $"{tenant.Utilisateur.Prenom} {tenant.Utilisateur.Nom}".Trim()
            : "The HR team";

        return string.IsNullOrWhiteSpace(invitedByName) ? "The HR team" : invitedByName;
    }

    private async Task<bool> TrySendInvitationEmailAsync(
        string email,
        string fullName,
        string companyName,
        string invitedByName,
        string tempPassword)
    {
        var invitationUrl = $"{_emailSettings.FrontendBaseUrl.TrimEnd('/')}/login";
        try
        {
            await _emailService.SendExpertInvitationAsync(new ExpertInvitationEmailDto
            {
                ToEmail           = email,
                ToName            = fullName,
                CompanyName       = companyName,
                InvitedByName     = invitedByName,
                InvitationUrl     = invitationUrl,
                ExpiresAt         = DateTime.UtcNow.AddDays(7),
                TemporaryPassword = tempPassword
            });
            _logger.LogInformation("[EXPERT-INVITE] Invitation email sent to {Email}", email);
            return true;
        }
        catch (Exception emailEx)
        {
            _logger.LogError(emailEx, "[EXPERT-INVITE] Failed to send invitation email to {Email}", email);
            return false;
        }
    }

    // 2. LISTE des experts
    public async Task<ExpertListResponseDto> GetExpertsByCompanyAsync(
        Guid companyId, ExpertFilterDto filter, Guid userOrTenantId)
    {
        var tenantId = await ResolveTenantIdAsync(userOrTenantId);

        var company = await _context.Companies
            .FirstOrDefaultAsync(c => c.Id == companyId && c.TenantId == tenantId);

        if (company == null)
            throw new KeyNotFoundException("Entreprise introuvable ou accès refusé.");

        var query = _context.Experts
            .Include(e => e.Company)
            .Include(e => e.Utilisateur)
            .Include(e => e.Assignations)
                .ThenInclude(a => a.Offre)
            .Where(e => e.CompanyId == companyId && e.TenantId == tenantId);

        if (filter.IsActive.HasValue)
            query = query.Where(u => u.IsActive == filter.IsActive.Value);

        if (!string.IsNullOrWhiteSpace(filter.Search))
        {
            string s = filter.Search.ToLower();
            query = query.Where(u =>
                u.FirstName.ToLower().Contains(s) ||
                u.LastName.ToLower().Contains(s) ||
                u.Email.ToLower().Contains(s));
        }

        int total = await query.CountAsync();

        var expertsList = await query
            .OrderBy(u => u.LastName)
            .Skip((filter.Page - 1) * filter.PageSize)
            .Take(filter.PageSize)
            .ToListAsync();

        var items = expertsList.Select(u =>
        {
            var lastAssignation = u.Assignations
                .OrderByDescending(a => a.AssigneLe)
                .FirstOrDefault();
            return ToDto(u, lastAssignation);
        }).ToList();

        return new ExpertListResponseDto
        {
            Items      = items,
            Total      = total,
            Page       = filter.Page,
            PageSize   = filter.PageSize,
            TotalPages = (int)Math.Ceiling(total / (double)filter.PageSize)
        };
    }

    // 3. DETAIL
    public async Task<ExpertResponseDto> GetExpertByIdAsync(Guid id, Guid userOrTenantId)
    {
        var tenantId = await ResolveTenantIdAsync(userOrTenantId);

        var expert = await _context.Experts
            .Include(e => e.Company)
            .FirstOrDefaultAsync(e => e.Id == id && e.TenantId == tenantId)
            ?? throw new KeyNotFoundException("Expert introuvable");

        return ToDto(expert);
    }

    // 4. UPDATE
    public async Task<ExpertResponseDto> ExpertUpdateAsync(Guid id, ExpertUpdateDto dto, Guid userOrTenantId)
    {
        var tenantId = await ResolveTenantIdAsync(userOrTenantId);

        var expert = await _context.Experts
            .Include(e => e.Company)
            .FirstOrDefaultAsync(e => e.Id == id && e.TenantId == tenantId)
            ?? throw new KeyNotFoundException("Expert introuvable");

        expert.Poste = dto.Poste;

        await _context.SaveChangesAsync();
        return ToDto(expert);
    }

    // 5. DESACTIVER
    public async Task DeactivateExpertAsync(Guid id, Guid userOrTenantId)
    {
        var tenantId = await ResolveTenantIdAsync(userOrTenantId);

        var expert = await _context.Experts
            .FirstOrDefaultAsync(e => e.Id == id && e.TenantId == tenantId)
            ?? throw new KeyNotFoundException("Expert introuvable");

        expert.IsActive = false;
        await _context.SaveChangesAsync();
    }

    // 6. REACTIVER
    public async Task ReactivateExpertAsync(Guid id, Guid userOrTenantId)
    {
        var tenantId = await ResolveTenantIdAsync(userOrTenantId);

        var expert = await _context.Experts
            .FirstOrDefaultAsync(e => e.Id == id && e.TenantId == tenantId)
            ?? throw new KeyNotFoundException("Expert introuvable");

        expert.IsActive = true;
        await _context.SaveChangesAsync();
    }

    // 7. DELETE
    public async Task DeleteExpertAsync(Guid id, Guid userOrTenantId)
    {
        var tenantId = await ResolveTenantIdAsync(userOrTenantId);

        Console.WriteLine($"[DELETE-EXPERT] id={id} tenantId={tenantId}");

        var expert = await _context.Experts
            .Include(e => e.Assignations)
            .Include(e => e.Avis)
            .FirstOrDefaultAsync(e => e.Id == id && e.TenantId == tenantId);

        if (expert == null)
        {
            Console.WriteLine($"[DELETE-EXPERT] Expert introuvable pour tenant {tenantId}");
            throw new KeyNotFoundException("Expert introuvable");
        }

        Console.WriteLine($"[DELETE-EXPERT] Trouvé : {expert.Email} | Assignations={expert.Assignations.Count} | Avis={expert.Avis.Count}");

        if (expert.Avis.Count > 0)
            _context.AvisExperts.RemoveRange(expert.Avis);

        if (expert.Assignations.Count > 0)
            _context.AssignationsExperts.RemoveRange(expert.Assignations);

        var notifs = await _context.Set<Notification>()
            .Where(n => n.ExpertId == id)
            .ToListAsync();
        if (notifs.Count > 0)
            _context.Set<Notification>().RemoveRange(notifs);

        _context.Experts.Remove(expert);

        if (expert.UtilisateurId.HasValue)
        {
            var utilisateur = await _context.Utilisateurs.FindAsync(expert.UtilisateurId.Value);
            if (utilisateur != null)
                _context.Utilisateurs.Remove(utilisateur);
        }

        try
        {
            var affected = await _context.SaveChangesAsync();
            Console.WriteLine($"[DELETE-EXPERT] OK — {affected} lignes affectées");
        }
        catch (DbUpdateException ex)
        {
            Console.WriteLine($"[DELETE-EXPERT] ÉCHEC SaveChanges : {ex.GetBaseException().Message}");
            throw new InvalidOperationException(
                $"Impossible de supprimer cet expert : {ex.GetBaseException().Message}", ex);
        }
    }

    // 8. ASSIGNER / DÉSASSIGNER une offre
    public async Task<ExpertResponseDto> AssignOffreAsync(Guid expertId, AssignOffreDto dto, Guid userOrTenantId)
    {
        var tenantId = await ResolveTenantIdAsync(userOrTenantId);

        var expert = await _context.Experts
            .Include(e => e.Company)
            .Include(e => e.Assignations)
                .ThenInclude(a => a.Offre)
            .FirstOrDefaultAsync(e => e.Id == expertId && e.TenantId == tenantId)
            ?? throw new KeyNotFoundException("Expert introuvable");

        if (!string.IsNullOrWhiteSpace(dto.Poste))
            expert.Poste = dto.Poste;

        if (dto.OffreId.HasValue)
        {
            var offre = await _context.OffresEmploi
                .Include(o => o.Entreprise)
                .FirstOrDefaultAsync(o => o.Id == dto.OffreId.Value && o.Entreprise.TenantId == tenantId)
                ?? throw new KeyNotFoundException("Offre introuvable ou accès refusé.");

            bool dejaAssigne = expert.Assignations.Any(a => a.OffreId == dto.OffreId.Value);
            if (!dejaAssigne)
            {
                var assignation = new AssignationExpert
                {
                    Id        = Guid.NewGuid(),
                    ExpertId  = expertId,
                    OffreId   = dto.OffreId.Value,
                    AssigneLe = DateTime.UtcNow
                };
                _context.AssignationsExperts.Add(assignation);
            }
        }
        else
        {
            var assignations = expert.Assignations.ToList();
            _context.AssignationsExperts.RemoveRange(assignations);
        }

        await _context.SaveChangesAsync();

        await _context.Entry(expert).Collection(e => e.Assignations).LoadAsync();
        foreach (var a in expert.Assignations)
            await _context.Entry(a).Reference(x => x.Offre).LoadAsync();

        var lastAssignation = expert.Assignations
            .OrderByDescending(a => a.AssigneLe)
            .FirstOrDefault();

        return ToDto(expert, lastAssignation);
    }

    // 9. SOUMETTRE AVIS
    public async Task SoumettreAvisAsync(Guid expertId, SoumettreAvisDto dto)
    {
        bool estAssigne = await _context.AssignationsExperts
            .AnyAsync(a => a.ExpertId == expertId &&
                           _context.Candidatures
                               .Any(c => c.Id == dto.CandidatureId && c.OffreId == a.OffreId));

        if (!estAssigne)
            throw new UnauthorizedAccessException("Accès refusé à cette candidature.");

        var avisExistant = await _context.AvisExperts
            .FirstOrDefaultAsync(a => a.ExpertId == expertId && a.CandidatureId == dto.CandidatureId);

        if (avisExistant != null)
        {
            avisExistant.Score       = dto.Score;
            avisExistant.Commentaire = dto.Commentaire;
        }
        else
        {
            _context.AvisExperts.Add(new AvisExpert
            {
                Id            = Guid.NewGuid(),
                ExpertId      = expertId,
                CandidatureId = dto.CandidatureId,
                Score         = dto.Score,
                Commentaire   = dto.Commentaire,
                CreeLe        = DateTime.UtcNow
            });
        }

        await _context.SaveChangesAsync();

        var candidature = await _context.Candidatures
            .Include(c => c.Candidat).ThenInclude(c => c.Utilisateur)
            .Include(c => c.Offre)
            .FirstOrDefaultAsync(c => c.Id == dto.CandidatureId);

        if (candidature != null)
        {
            var autresExperts = await _context.AssignationsExperts
                .Where(a => a.OffreId == candidature.OffreId && a.ExpertId != expertId)
                .Select(a => a.ExpertId)
                .ToListAsync();

            var nom = candidature.Candidat?.Utilisateur != null
                ? $"{candidature.Candidat.Utilisateur.Prenom} {candidature.Candidat.Utilisateur.Nom}".Trim()
                : "A candidate";

            var scoreLabel = $"{dto.Score:0.0}/5 ({Math.Round(dto.Score * 20)}% match)";

            foreach (var expId in autresExperts)
            {
                _context.Notifications.Add(new Notification
                {
                    ExpertId   = expId,
                    Type       = "status_updates",
                    Title      = "Candidate evaluated by colleague",
                    Body       = $"{nom} was rated {scoreLabel} on \"{candidature.Offre?.Titre}\"",
                    OffreId    = candidature.OffreId,
                    CandidatId = dto.CandidatureId,
                    CreeLe     = DateTime.UtcNow,
                    Read       = false
                });
            }

            await _context.SaveChangesAsync();
        }
    }

    private static ExpertResponseDto ToDto(Expert e, AssignationExpert? assignation = null) => new()
    {
        Id          = e.Id,
        FullName    = $"{e.FirstName} {e.LastName}",
        Email       = e.Email,
        IsActive    = e.IsActive,
        IsInvited   = e.IsInvited,
        CompanyName = e.Company?.Nom ?? "",
        Poste       = e.Poste,
        OffreId     = assignation?.OffreId,
        OffreTitre  = assignation?.Offre?.Titre
    };

    private static string GenerateTempPassword()
    {
        var chars  = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789!@#$";
        var random = new Random();
        return new string(Enumerable.Range(0, 10)
            .Select(_ => chars[random.Next(chars.Length)])
            .ToArray());
    }
}