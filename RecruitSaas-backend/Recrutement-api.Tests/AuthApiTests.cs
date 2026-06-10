using System.Net;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using Recrutement_api.DTOs;
using Xunit;

namespace Recrutement_api.Tests;

[Collection("Integration")]
public class AuthApiTests
{
    private readonly RecruitSaasApiFactory _factory;
    private readonly HttpClient _client;

    public AuthApiTests(RecruitSaasApiFactory factory)
    {
        _factory = factory;
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task GetExternalProviders_ReturnsOk()
    {
        var response = await _client.GetAsync("/api/auth/external/providers");

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        var body = await response.Content.ReadAsStringAsync();
        Assert.Contains("providers", body, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public async Task Login_WithInvalidCredentials_ReturnsUnauthorized()
    {
        var response = await _client.PostAsJsonAsync("/api/auth/login", new
        {
            email = "unknown@example.com",
            motDePasse = "WrongPassword123!"
        });

        Assert.Equal(HttpStatusCode.Unauthorized, response.StatusCode);
    }

    [Fact]
    public async Task RegisterCandidate_ThenLogin_ReturnsToken()
    {
        var email = $"candidat-{Guid.NewGuid():N}@test.com";
        var password = "Password123!";

        var registerResponse = await _client.PostAsJsonAsync("/api/auth/register", new
        {
            nom = "Test Candidat",
            email,
            motDePasse = password,
            confirmMotDePasse = password
        });

        Assert.Equal(HttpStatusCode.OK, registerResponse.StatusCode);

        var loginResponse = await _client.PostAsJsonAsync("/api/auth/login", new
        {
            email,
            motDePasse = password
        });

        Assert.Equal(HttpStatusCode.OK, loginResponse.StatusCode);

        var auth = await loginResponse.Content.ReadFromJsonAsync<AuthResponseDto>();
        Assert.NotNull(auth);
        Assert.False(string.IsNullOrWhiteSpace(auth!.Token));
        Assert.Equal("Candidat", auth.Role);
    }

    [Fact]
    public async Task RegisterCandidate_WithDuplicateEmail_ReturnsBadRequest()
    {
        var email = $"dup-{Guid.NewGuid():N}@test.com";
        var payload = new
        {
            nom = "Dup User",
            email,
            motDePasse = "Password123!",
            confirmMotDePasse = "Password123!"
        };

        var first = await _client.PostAsJsonAsync("/api/auth/register", payload);
        Assert.Equal(HttpStatusCode.OK, first.StatusCode);

        var second = await _client.PostAsJsonAsync("/api/auth/register", payload);
        Assert.Equal(HttpStatusCode.BadRequest, second.StatusCode);
    }

    [Fact]
    public async Task GetMe_WithValidToken_ReturnsCurrentUser()
    {
        var email = $"me-{Guid.NewGuid():N}@test.com";
        var password = "Password123!";

        await _client.PostAsJsonAsync("/api/auth/register", new
        {
            nom = "Me Test",
            email,
            motDePasse = password,
            confirmMotDePasse = password
        });

        var loginResponse = await _client.PostAsJsonAsync("/api/auth/login", new
        {
            email,
            motDePasse = password
        });

        var auth = await loginResponse.Content.ReadFromJsonAsync<AuthResponseDto>();
        Assert.NotNull(auth);

        var authedClient = _factory.CreateClient();
        authedClient.DefaultRequestHeaders.Authorization =
            new AuthenticationHeaderValue("Bearer", auth!.Token);

        var meResponse = await authedClient.GetAsync("/api/auth/me");
        Assert.Equal(HttpStatusCode.OK, meResponse.StatusCode);

        var body = await meResponse.Content.ReadAsStringAsync();
        Assert.Contains(email, body, StringComparison.OrdinalIgnoreCase);
    }
}
