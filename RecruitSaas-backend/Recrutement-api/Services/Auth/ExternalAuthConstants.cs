namespace Recrutement_api.Services.Auth
{
    public static class ExternalAuthConstants
    {
        public const string ExternalCookieScheme = "External";
        public const string LinkedInScheme = "LinkedIn";

        public static readonly IReadOnlyDictionary<string, string> ProviderSchemes =
            new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
            {
                ["google"] = "Google",
                ["facebook"] = "Facebook",
                ["linkedin"] = LinkedInScheme
            };
    }
}
