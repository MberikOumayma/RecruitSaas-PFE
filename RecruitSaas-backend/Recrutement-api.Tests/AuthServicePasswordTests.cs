using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Recrutement_api.Data;
using Recrutement_api.Services;
using Xunit;

namespace Recrutement_api.Tests;

public class AuthServicePasswordTests
{
    private static AuthService CreateService()
    {
        var options = new DbContextOptionsBuilder<ApplicationDbContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;

        var config = new ConfigurationBuilder()
            .AddInMemoryCollection(new Dictionary<string, string?>
            {
                ["Jwt:Secret"] = "test-secret-key-minimum-32-characters",
                ["Jwt:Issuer"] = "RecruitSaas-Test",
                ["Jwt:Audience"] = "RecruitSaas-Test-Users"
            })
            .Build();

        var context = new ApplicationDbContext(options);
        var jwtService = new JwtService(config);
        return new AuthService(context, jwtService);
    }

    [Fact]
    public void HashPassword_AndVerifyPassword_RoundTripSucceeds()
    {
        var service = CreateService();
        var hash = service.HashPassword("MySecurePassword123!");

        Assert.False(string.IsNullOrWhiteSpace(hash));
        Assert.True(service.VerifyPassword("MySecurePassword123!", hash));
        Assert.False(service.VerifyPassword("WrongPassword!", hash));
    }

    [Fact]
    public void VerifyPassword_AcceptsBcryptHash()
    {
        var service = CreateService();
        var bcryptHash = BCrypt.Net.BCrypt.HashPassword("ExpertPass123!");

        Assert.True(service.VerifyPassword("ExpertPass123!", bcryptHash));
        Assert.False(service.VerifyPassword("bad", bcryptHash));
    }
}
