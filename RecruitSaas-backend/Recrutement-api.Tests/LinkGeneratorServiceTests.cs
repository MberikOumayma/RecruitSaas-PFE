using Microsoft.Extensions.Configuration;
using Recrutement_api.Services.Implementations;
using Xunit;

namespace Recrutement_api.Tests;

public class LinkGeneratorServiceTests
{
    [Fact]
    public void GenerateOfferLink_IncludesToken()
    {
        var config = new ConfigurationBuilder().Build();
        var service = new LinkGeneratorService(config);

        var link = service.GenerateOfferLink("abc123-token");

        Assert.Contains("abc123-token", link);
        Assert.StartsWith("http://localhost:5173/public/offres/", link);
    }
}
