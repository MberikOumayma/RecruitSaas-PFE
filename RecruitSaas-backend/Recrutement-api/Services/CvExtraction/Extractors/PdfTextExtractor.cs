using System.Text;
using System.Threading.Tasks;
using iText.Kernel.Pdf;
using iText.Kernel.Pdf.Canvas.Parser;
using iText.Kernel.Pdf.Canvas.Parser.Listener;
using Tesseract;
using Docnet.Core;
using Docnet.Core.Models;
using System.Drawing;
using System.Drawing.Imaging;

namespace Recrutement_api.Services.CvExtraction.Extractors
{
    public class PdfTextExtractor : ITextExtractor
    {
        // Chemin vers les données Tesseract (tessdata/)
        private const string TessDataPath = "./tessdata";

        public async Task<string> ExtractTextFromFileAsync(string filePath)
        {
            // 1️⃣ Tentative normale avec iText7
            string text = await ExtractWithIText(filePath);

            // 2️⃣ Si vide → fallback OCR
            if (string.IsNullOrWhiteSpace(text))
            {
                Console.WriteLine("[INFO] Texte vide détecté → fallback OCR Tesseract");
                text = await ExtractWithOcr(filePath);
            }

            return text;
        }

        private async Task<string> ExtractWithIText(string filePath)
        {
            return await Task.Run(() =>
            {
                var sb = new StringBuilder();
                try
                {
                    using var reader   = new PdfReader(filePath);
                    using var document = new iText.Kernel.Pdf.PdfDocument(reader);
                    for (int i = 1; i <= document.GetNumberOfPages(); i++)
                    {
                        try
                        {
                            var strategy = new LocationTextExtractionStrategy();
                            var page     = document.GetPage(i);
                            var pageText = iText.Kernel.Pdf.Canvas.Parser.PdfTextExtractor
                                               .GetTextFromPage(page, strategy);
                            if (!string.IsNullOrWhiteSpace(pageText))
                                sb.AppendLine(pageText);
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine($"[WARN] Page {i} skippée : {ex.Message}");
                        }
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[WARN] PDF illisible : {ex.Message}");
                }
                return sb.ToString().Trim();
            });
        }

        private async Task<string> ExtractWithOcr(string filePath)
        {
            return await Task.Run(() =>
            {
                var sb = new StringBuilder();
                try
                {
                    // Convertir chaque page PDF en image via Docnet
                    using var lib = DocLib.Instance;
                    using var docReader = lib.GetDocReader(filePath, new PageDimensions(1080, 1920));
                    int pageCount = docReader.GetPageCount();

                    using var engine = new TesseractEngine(TessDataPath, "fra+eng", EngineMode.Default);

                    for (int i = 0; i < pageCount; i++)
                    {
                        using var pageReader = docReader.GetPageReader(i);
                        var rawBytes = pageReader.GetImage(); // BGRA bytes
                        int width    = pageReader.GetPageWidth();
                        int height   = pageReader.GetPageHeight();

                        // Convertir BGRA → Bitmap
                        using var bmp = new Bitmap(width, height, PixelFormat.Format32bppArgb);
                        var bmpData  = bmp.LockBits(
                            new Rectangle(0, 0, width, height),
                            ImageLockMode.WriteOnly,
                            PixelFormat.Format32bppArgb);
                        System.Runtime.InteropServices.Marshal.Copy(
                            rawBytes, 0, bmpData.Scan0, rawBytes.Length);
                        bmp.UnlockBits(bmpData);

                        // OCR sur le bitmap
                        using var ms  = new MemoryStream();
                        bmp.Save(ms, System.Drawing.Imaging.ImageFormat.Png);
                        ms.Position = 0;
                        using var img  = Pix.LoadFromMemory(ms.ToArray());
                        using var page = engine.Process(img);
                        sb.AppendLine(page.GetText());
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[ERROR] OCR échoué : {ex.Message}");
                }
                return sb.ToString().Trim();
            });
        }
    }
}