using System.IdentityModel.Tokens.Jwt;
using System.Text;
using Microsoft.Extensions.Configuration;
using Recrutement_api.Models;
using Recrutement_api.Services;
using Xunit;

namespace Recrutement_api.Tests;

public class JwtServiceTests
{
    private static JwtService CreateService()
    {
        var config = new ConfigurationBuilder()
            .AddInMemoryCollection(new Dictionary<string, string?>
            {
                ["Jwt:Secret"] = "test-secret-key-minimum-32-characters",
                ["Jwt:Issuer"] = "RecruitSaas-Test",
                ["Jwt:Audience"] = "RecruitSaas-Test-Users"
            })
            .Build();

        return new JwtService(config);
    }

    [Fact]
    public void GenerateToken_ContainsExpectedClaims()
    {
        var userId = Guid.NewGuid();
        var tenantId = Guid.NewGuid();
        var user = new Utilisateur
        {
            Id = userId,
            Email = "test@example.com",
            Nom = "Test User",
            Role = RoleUtilisateur.Tenant
        };

        var token = CreateService().GenerateToken(user, tenantId);
        var jwt = new JwtSecurityTokenHandler().ReadJwtToken(token);

        Assert.Equal(userId.ToString(), jwt.Claims.First(c => c.Type == "userId").Value);
        Assert.Equal("Tenant", jwt.Claims.First(c => c.Type == "role").Value);
        Assert.Equal(tenantId.ToString(), jwt.Claims.First(c => c.Type == "tenantId").Value);
        Assert.Equal("RecruitSaas-Test", jwt.Issuer);
        Assert.Contains(jwt.Audiences, a => a == "RecruitSaas-Test-Users");
    }

    [Fact]
    public void GenerateToken_ExpiresInAboutThreeHours()
    {
        var user = new Utilisateur
        {
            Id = Guid.NewGuid(),
            Email = "candidat@example.com",
            Nom = "Candidat",
            Role = RoleUtilisateur.Candidat
        };

        var before = DateTime.UtcNow.AddHours(2.9);
        var token = CreateService().GenerateToken(user, candidatId: Guid.NewGuid());
        var jwt = new JwtSecurityTokenHandler().ReadJwtToken(token);
        var after = DateTime.UtcNow.AddHours(3.1);

        Assert.InRange(jwt.ValidTo, before, after);
    }
}
