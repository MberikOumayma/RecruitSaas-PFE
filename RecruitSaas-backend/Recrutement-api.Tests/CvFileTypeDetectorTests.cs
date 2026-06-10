using Recrutement_api.Services.CvExtraction;
using Xunit;

namespace Recrutement_api.Tests;

public class CvFileTypeDetectorTests
{
    [Fact]
    public void DetectExtension_PdfMagicBytes_ReturnsPdf()
    {
        var pdfHeader = new byte[] { 0x25, 0x50, 0x44, 0x46, 0x2D, 0x31, 0x2E, 0x34 };
        Assert.Equal(".pdf", CvFileTypeDetector.DetectExtension(pdfHeader, null));
    }

    [Fact]
    public void DetectExtension_PngMagicBytes_ReturnsPng()
    {
        var pngHeader = new byte[]
        {
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
            0x00, 0x00, 0x00, 0x0D
        };
        Assert.Equal(".png", CvFileTypeDetector.DetectExtension(pngHeader, null));
    }

    [Fact]
    public void DetectExtension_CloudinaryRawUrl_ReturnsPdf()
    {
        Assert.Equal(
            ".pdf",
            CvFileTypeDetector.DetectExtension(Array.Empty<byte>(),
                "https://res.cloudinary.com/demo/raw/upload/v123/cv"));
    }

    [Fact]
    public void IsImageExtension_RecognizesCommonImageTypes()
    {
        Assert.True(CvFileTypeDetector.IsImageExtension(".jpg"));
        Assert.True(CvFileTypeDetector.IsImageExtension(".png"));
        Assert.False(CvFileTypeDetector.IsImageExtension(".pdf"));
    }
}
