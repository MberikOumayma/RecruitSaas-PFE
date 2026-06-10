using System.Net;
using Xunit;

namespace Recrutement_api.Tests;

[Collection("Integration")]
public class ProtectedEndpointTests
{
    private readonly HttpClient _client;

    public ProtectedEndpointTests(RecruitSaasApiFactory factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task GetMe_WithoutToken_ReturnsUnauthorized()
    {
        var response = await _client.GetAsync("/api/auth/me");
        Assert.Equal(HttpStatusCode.Unauthorized, response.StatusCode);
    }

    [Fact]
    public async Task GetCandidatures_WithoutToken_ReturnsUnauthorized()
    {
        var response = await _client.GetAsync("/api/candidatures");
        Assert.Equal(HttpStatusCode.Unauthorized, response.StatusCode);
    }
}
