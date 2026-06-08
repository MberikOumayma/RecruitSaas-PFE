/** English labels for recruiter UI (backend may still send French enum values). */

export const APPLICATION_STATUS_LABELS = {
  Nouvelle: 'New',
  'En cours': 'In progress',
  Acceptée: 'Accepted',
  Acceptee: 'Accepted',
  Refusée: 'Rejected',
  Refusee: 'Rejected',
  Présélectionné: 'Shortlisted',
  Preselectionne: 'Shortlisted',
  Entretien: 'Interview',
}

export const INTERVIEW_STATUS_LABELS = {
  LienEnvoye: 'Invitation sent',
  Planifie: 'Scheduled',
  EnCours: 'In progress',
  Termine: 'Completed',
  Annule: 'Cancelled',
  EnAttente: 'Pending',
}

export const TENANT_ACCOUNT_STATUS_LABELS = {
  Approved: 'Approved',
  Approuvé: 'Approved',
  Pending: 'Pending',
  'En attente': 'Pending',
  Rejected: 'Rejected',
  Refusé: 'Rejected',
}

export function applicationStatusLabel(status) {
  return APPLICATION_STATUS_LABELS[status] || status || '—'
}

export function isRejectedApplicationStatus(status) {
  return status === 'Refusée' || status === 'Refusee' || status === 'Rejected'
}

export function interviewStatusLabel(status) {
  return INTERVIEW_STATUS_LABELS[status] || status || '—'
}

export function tenantAccountStatusLabel(status) {
  return TENANT_ACCOUNT_STATUS_LABELS[status] || status || '—'
}

export function formatRecruiterDate(dateStr, options = {}) {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  if (Number.isNaN(d.getTime())) return '—'
  return d.toLocaleDateString('en-US', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    ...options,
  })
}

export function formatRecruiterDateTime(dateStr) {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  if (Number.isNaN(d.getTime())) return '—'
  return d.toLocaleString('en-US', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatRecruiterTime(dateStr) {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  if (Number.isNaN(d.getTime())) return '—'
  return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
}

export const INTERVIEW_MENTION_LABELS = {
  Excellent: 'Excellent',
  Bien: 'Good',
  Satisfaisant: 'Satisfactory',
  Insuffisant: 'Insufficient',
}

export const FRAUD_LEVEL_LABELS = {
  ELEVE: 'High',
  MOYEN: 'Medium',
  FAIBLE: 'Low',
  AUCUN: 'None',
}

export function interviewMentionLabel(mention) {
  return INTERVIEW_MENTION_LABELS[mention] || mention || '—'
}

export function fraudLevelLabel(level) {
  return FRAUD_LEVEL_LABELS[level] || level || '—'
}
