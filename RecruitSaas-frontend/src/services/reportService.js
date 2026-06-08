import api from "./api"

/**
 * Generic helper: call an endpoint that returns a Blob and trigger a browser download.
 */
async function downloadFile(url, filename) {
  const response = await api.get(url, { responseType: "blob" })
  const blob = new Blob([response.data], { type: response.headers["content-type"] })
  const link = document.createElement("a")
  link.href = URL.createObjectURL(blob)
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(link.href)
}

/* ── Candidate-level exports ─────────────────────────────────── */

/**
 * Download a PDF report for a single candidate.
 * GET /api/reports/candidate/{id}/pdf
 */
export const downloadCandidatePdf = (candidatureId, candidateName = "candidate") =>
  downloadFile(
    `/reports/candidate/${candidatureId}/pdf`,
    `${candidateName.replace(/\s+/g, "_")}_report.pdf`
  )

/**
 * Download a Word report for a single candidate.
 * GET /api/reports/candidate/{id}/word
 */
export const downloadCandidateWord = (candidatureId, candidateName = "candidate") =>
  downloadFile(
    `/reports/candidate/${candidatureId}/word`,
    `${candidateName.replace(/\s+/g, "_")}_report.docx`
  )

/* ── Offer-level exports ─────────────────────────────────────── */

/**
 * Download an Excel report with all candidates for a given job offer.
 * GET /api/reports/job/{jobId}/candidates/excel
 */
export const downloadOfferCandidatesExcel = (offreId, offerTitle = "offer") =>
  downloadFile(
    `/reports/job/${offreId}/candidates/excel`,
    `${offerTitle.replace(/\s+/g, "_")}_candidates.xlsx`
  )

/* ── Global KPI data (for Reports dashboard) ─────────────────── */

/**
 * GET /api/reports/global/kpis
 * Returns aggregated KPI data for the tenant.
 */
export const getGlobalKpis = () => api.get("/reports/global/kpis")
