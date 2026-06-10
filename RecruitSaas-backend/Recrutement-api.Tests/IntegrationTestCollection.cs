using Xunit;

namespace Recrutement_api.Tests;

[CollectionDefinition("Integration")]
public class IntegrationTestCollection : ICollectionFixture<RecruitSaasApiFactory>;
