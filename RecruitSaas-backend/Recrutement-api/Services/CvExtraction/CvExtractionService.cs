using System;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Recrutement_api.Data;
using Recrutement_api.Models;
using Recrutement_api.Services.CvExtraction.Processors;
using Recrutement_api.Services.CvExtraction.Extractors;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace Recrutement_api.Services.CvExtraction
{
    public interface ICvExtractionService
    {
        Task<AnalyseCV> ProcessCvAsync(Guid candidatureId);
    }

    public class CvExtractionService : ICvExtractionService
    {
        private readonly ApplicationDbContext _dbContext;
        private readonly ILogger<CvExtractionService> _logger;
        private readonly PdfTextExtractor _pdfExtractor;
        private readonly DocxTextExtractor _docxExtractor;
        private readonly AiCvTextExtractor _aiCvExtractor;
        private readonly HttpClient _httpClient;
        private readonly string _publicOrigin;

        public CvExtractionService(
            ApplicationDbContext dbContext,
            ILogger<CvExtractionService> logger,
            PdfTextExtractor pdfExtractor,
            DocxTextExtractor docxExtractor,
            AiCvTextExtractor aiCvExtractor,
            HttpClient httpClient,
            IConfiguration configuration)
        {
            _dbContext           = dbContext;
            _logger              = logger;
            _pdfExtractor        = pdfExtractor;
            _docxExtractor       = docxExtractor;
            _aiCvExtractor       = aiCvExtractor;
            _httpClient          = httpClient;
            _publicOrigin        = configuration["AppSettings:PublicOrigin"]?.TrimEnd('/')
                ?? "http://localhost:5202";
        }

        public async Task<AnalyseCV> ProcessCvAsync(Guid candidatureId)
        {
            _logger.LogInformation($"Début d'extraction du CV pour la candidature {candidatureId}");

            var candidature = await _dbContext.Candidatures
                .FirstOrDefaultAsync(c => c.Id == candidatureId);

            if (candidature == null || string.IsNullOrEmpty(candidature.CvUrl))
            {
                _logger.LogWarning($"Candidature introuvable ou CvUrl manquant : {candidatureId}");
                throw new Exception("CV introuvable pour cette candidature.");
            }

            var analyse = await _dbContext.AnalysesCV
                .FirstOrDefaultAsync(a => a.CandidatureId == candidatureId);

            if (analyse == null)
            {
                analyse = new AnalyseCV
                {
                    Id            = Guid.NewGuid(),
                    CandidatureId = candidatureId,
                    CreeLe        = DateTime.UtcNow
                };
                _dbContext.AnalysesCV.Add(analyse);
            }

            string cleanedText = "";
            try
            {
                string rawText = await ExtractTextAsync(ResolveCvUrl(candidature.CvUrl));
                cleanedText    = TextCleaner.Clean(rawText);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Extraction échouée pour {candidatureId}");
                cleanedText = "";
            }

            // Sentinelle : espace = "déjà tenté, texte vide"
            // Évite la boucle infinie dans EnsureTextExtractedAsync
            analyse.TexteExtrait = string.IsNullOrWhiteSpace(cleanedText) ? "EMPTY_PDF" : cleanedText;

            // Upsert manuel pour éviter DbUpdateConcurrencyException
            // quand plusieurs requêtes parallèles tentent de sauvegarder le même AnalyseCV
            try
            {
                var existing = await _dbContext.AnalysesCV
                    .AsNoTracking()
                    .FirstOrDefaultAsync(a => a.CandidatureId == candidatureId);

                if (existing == null)
                    _dbContext.AnalysesCV.Add(analyse);
                else
                    _dbContext.AnalysesCV.Update(analyse);

                await _dbContext.SaveChangesAsync();
            }
            catch (Microsoft.EntityFrameworkCore.DbUpdateConcurrencyException)
            {
                // Une autre requête parallèle a déjà sauvegardé — on recharge depuis la DB
                _logger.LogWarning($"Concurrency conflict pour {candidatureId} — rechargement depuis la DB");
                _dbContext.ChangeTracker.Clear();
                var fresh = await _dbContext.AnalysesCV
                    .FirstOrDefaultAsync(a => a.CandidatureId == candidatureId);
                if (fresh != null)
                {
                    fresh.TexteExtrait = analyse.TexteExtrait;
                    await _dbContext.SaveChangesAsync();
                }
            }

            _logger.LogInformation(
                $"Extraction terminée pour {candidatureId}. " +
                $"Texte : {cleanedText.Length} caractères.");

            return analyse;
        }

        private string ResolveCvUrl(string cvUrl)
        {
            if (string.IsNullOrWhiteSpace(cvUrl))
                return cvUrl;
            if (cvUrl.StartsWith("http://", StringComparison.OrdinalIgnoreCase)
                || cvUrl.StartsWith("https://", StringComparison.OrdinalIgnoreCase))
                return cvUrl;
            return $"{_publicOrigin}/{cvUrl.TrimStart('/')}";
        }

        internal async Task<string> ExtractTextAsync(string fileUrl)
        {
            string tempFilePath = Path.GetTempFileName();

            try
            {
                byte[] fileBytes = await _httpClient.GetByteArrayAsync(fileUrl);

                string ext = CvFileTypeDetector.DetectExtension(fileBytes, fileUrl);
                var fileName = $"cv{ext}";
                _logger.LogInformation("[CV] Downloaded {Url} — {Bytes} bytes, detected type {Ext}", fileUrl, fileBytes.Length, ext);

                tempFilePath = Path.ChangeExtension(tempFilePath, ext);
                await File.WriteAllBytesAsync(tempFilePath, fileBytes);

                // 1) recruit-ai-service (PyMuPDF + OCR Tesseract) for PDF/images
                if (ext == ".pdf" || CvFileTypeDetector.IsImageExtension(ext))
                {
                    var aiText = await _aiCvExtractor.ExtractFromBytesAsync(fileBytes, fileName);
                    if (!string.IsNullOrWhiteSpace(aiText))
                        return aiText;
                    _logger.LogWarning("[CV] AI extraction empty for {Url}, fallback local", fileUrl);
                }

                if (ext == ".docx")
                    return await _docxExtractor.ExtractTextFromFileAsync(tempFilePath);

                if (CvFileTypeDetector.IsImageExtension(ext))
                {
                    _logger.LogWarning("[CV] Image OCR failed for {Url}", fileUrl);
                    return "";
                }

                return await _pdfExtractor.ExtractTextFromFileAsync(tempFilePath);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Erreur extraction : {fileUrl}");
                throw;
            }
            finally
            {
                if (File.Exists(tempFilePath))
                    try { File.Delete(tempFilePath); } catch { }
            }
        }

    }
}
