using System.Net.Http.Headers;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace Recrutement_api.Services.CvExtraction
{
    /// <summary>
    /// Extracts CV text via recruit-ai-service (PyMuPDF + Tesseract OCR).
    /// </summary>
    public class AiCvTextExtractor
    {
        private readonly HttpClient _http;
        private readonly ILogger<AiCvTextExtractor> _logger;
        private readonly string _extractUrl;

        private static readonly JsonSerializerOptions _json = new()
        {
            PropertyNameCaseInsensitive = true,
        };

        public AiCvTextExtractor(HttpClient http, IConfiguration config, ILogger<AiCvTextExtractor> logger)
        {
            _http = http;
            _logger = logger;
            var baseUrl = config["AiService:BaseUrl"]?.TrimEnd('/') ?? "http://127.0.0.1:8000";
            _extractUrl = $"{baseUrl}/ai/extract-cv-text";
        }

        public async Task<string?> ExtractFromBytesAsync(byte[] fileBytes, string fileName)
        {
            if (fileBytes == null || fileBytes.Length == 0)
                return null;

            try
            {
                using var content = new MultipartFormDataContent();
                var fileContent = new ByteArrayContent(fileBytes);
                var mime = GuessMime(fileName);
                fileContent.Headers.ContentType = new MediaTypeHeaderValue(mime);
                content.Add(fileContent, "file", fileName);

                var response = await _http.PostAsync(_extractUrl, content);
                var body = await response.Content.ReadAsStringAsync();

                if (!response.IsSuccessStatusCode)
                {
                    _logger.LogWarning("[AiCvText] extract-cv-text → {Status}: {Body}",
                        (int)response.StatusCode, body.Length > 500 ? body[..500] : body);
                    return null;
                }

                var parsed = JsonSerializer.Deserialize<ExtractCvTextResponse>(body, _json);
                var text = parsed?.TexteExtrait?.Trim();
                if (string.IsNullOrWhiteSpace(text))
                    return null;

                _logger.LogInformation(
                    "[AiCvText] OK {File} — {Len} chars, OCR={Ocr}, pages={Pages}",
                    fileName, text.Length, parsed?.UsedOcr ?? false, parsed?.PageCount ?? 0);

                return text;
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "[AiCvText] Failed for {File}", fileName);
                return null;
            }
        }

        private static string GuessMime(string fileName)
        {
            var ext = Path.GetExtension(fileName).ToLowerInvariant();
            return ext switch
            {
                ".pdf"  => "application/pdf",
                ".png"  => "image/png",
                ".jpg" or ".jpeg" => "image/jpeg",
                ".webp" => "image/webp",
                ".tif" or ".tiff" => "image/tiff",
                ".docx" => "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                _       => "application/octet-stream",
            };
        }

        private sealed class ExtractCvTextResponse
        {
            [JsonPropertyName("texteExtrait")]
            public string? TexteExtrait { get; set; }

            [JsonPropertyName("usedOcr")]
            public bool UsedOcr { get; set; }

            [JsonPropertyName("pageCount")]
            public int PageCount { get; set; }
        }
    }
}
