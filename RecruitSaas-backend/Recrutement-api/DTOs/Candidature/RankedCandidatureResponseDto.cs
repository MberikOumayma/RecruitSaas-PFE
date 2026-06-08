namespace Recrutement_api.DTOs.Candidature
{
    public class RankedCandidatureResponseDto : CandidatureResponseDto
    {
        public int Rank { get; set; }
        public float FaissScore { get; set; }
        public float? VectorSimilarity { get; set; }
        public float? DomainFit { get; set; }
        public float? Technical { get; set; }
        public float? Experience { get; set; }
    }
}
