using Microsoft.Extensions.Configuration;
using Recrutement_api.Extensions;
using Xunit;

namespace Recrutement_api.Tests;

public class ExternalAuthExtensionsTests
{
    [Theory]
    [InlineData("google")]
    [InlineData("facebook")]
    [InlineData("linkedin")]
    public void IsProviderConfigured_ReturnsFalse_WhenSecretsMissing(string provider)
    {
        var config = new ConfigurationBuilder().Build();
        Assert.False(ExternalAuthExtensions.IsProviderConfigured(config, provider));
    }

    [Fact]
    public void IsProviderConfigured_ReturnsTrue_WhenGoogleConfigured()
    {
        var config = new ConfigurationBuilder()
            .AddInMemoryCollection(new Dictionary<string, string?>
            {
                ["Authentication:Google:ClientId"] = "client-id",
                ["Authentication:Google:ClientSecret"] = "client-secret"
            })
            .Build();

        Assert.True(ExternalAuthExtensions.IsProviderConfigured(config, "google"));
    }
}
