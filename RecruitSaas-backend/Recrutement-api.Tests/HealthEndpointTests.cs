using System.Net;
using Xunit;

namespace Recrutement_api.Tests;

public class HealthEndpointTests : IClassFixture<RecruitSaasApiFactory>
{
    private readonly HttpClient _client;

    public HealthEndpointTests(RecruitSaasApiFactory factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task GetHealth_ReturnsHealthyStatus()
    {
        var response = await _client.GetAsync("/health");

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);

        var body = await response.Content.ReadAsStringAsync();
        Assert.Contains("Healthy", body, StringComparison.OrdinalIgnoreCase);
    }
}
