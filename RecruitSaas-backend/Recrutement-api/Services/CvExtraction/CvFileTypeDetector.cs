namespace Recrutement_api.Services.CvExtraction
{
    /// <summary>
    /// Detect CV file type from content bytes and optional URL (Cloudinary paths often lack extensions).
    /// </summary>
    public static class CvFileTypeDetector
    {
        public static string DetectExtension(byte[] data, string? url)
        {
            if (data != null && data.Length >= 4)
            {
                // %PDF
                if (data[0] == 0x25 && data[1] == 0x50 && data[2] == 0x44 && data[3] == 0x46)
                    return ".pdf";
                // JPEG
                if (data.Length >= 3 && data[0] == 0xFF && data[1] == 0xD8 && data[2] == 0xFF)
                    return ".jpg";
                // PNG
                if (data.Length >= 8
                    && data[0] == 0x89 && data[1] == 0x50 && data[2] == 0x4E && data[3] == 0x47
                    && data[4] == 0x0D && data[5] == 0x0A && data[6] == 0x1A && data[7] == 0x0A)
                    return ".png";
                // WEBP (RIFF....WEBP)
                if (data.Length >= 12
                    && data[0] == 0x52 && data[1] == 0x49 && data[2] == 0x46 && data[3] == 0x46
                    && data[8] == 0x57 && data[9] == 0x45 && data[10] == 0x42 && data[11] == 0x50)
                    return ".webp";
                // TIFF
                if ((data[0] == 0x49 && data[1] == 0x49) || (data[0] == 0x4D && data[1] == 0x4D))
                    return ".tiff";
            }

            var urlLower = (url ?? "").ToLowerInvariant();

            // Cloudinary: image vs raw upload
            if (urlLower.Contains("/image/upload/"))
                return ".jpg";
            if (urlLower.Contains("/raw/upload/"))
                return ".pdf";

            if (urlLower.Contains(".docx") || urlLower.Contains(".doc"))
                return ".docx";
            if (urlLower.Contains(".png"))
                return ".png";
            if (urlLower.Contains(".webp"))
                return ".webp";
            if (urlLower.Contains(".jpeg") || urlLower.Contains(".jpg"))
                return ".jpg";
            if (urlLower.Contains(".tif"))
                return ".tiff";
            if (urlLower.Contains(".pdf"))
                return ".pdf";

            return ".pdf";
        }

        public static bool IsImageExtension(string ext)
            => ext is ".png" or ".jpg" or ".jpeg" or ".webp" or ".tif" or ".tiff" or ".bmp" or ".gif";
    }
}
