<template>
  <div class="page-wrapper">

    <header class="header">
      <div class="logo">
        <img class="appli-brand-logo" src="/appli-logo.png" alt="TalentFlow" />
      </div>
      <div class="header-right">
        <span class="step-text">Step 1 of 3</span>
        <button class="btn-signup" @click="$router.push('/register-candidate')">Sign up</button>
      </div>
    </header>

    <main class="main-content">
      <h1 class="title">You are...</h1>
      <p class="subtitle">Select the role that best describes your current goals</p>

      <div class="cards-container">
        <div class="role-card" :class="{ selected: selectedRole === 'candidate' }" @click="selectRole('candidate')">
          <div class="card-icon">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#4A6CF7" stroke-width="1.5">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
          <h2 class="card-title">Candidate</h2>
          <p class="card-desc">I am looking for my next dream job or project.</p>
          <button class="btn-card" @click.stop="goToRegisterCandidate">Get Started</button>
        </div>

        <div class="role-card" :class="{ selected: selectedRole === 'company' }" @click="selectRole('company')">
          <div class="card-icon">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#4A6CF7" stroke-width="1.5">
              <rect x="2" y="3" width="20" height="18" rx="2"/>
              <path d="M8 3v18M16 3v18M2 9h20M2 15h20"/>
            </svg>
          </div>
          <h2 class="card-title">Company</h2>
          <p class="card-desc">I am looking to hire top talent for my organization.</p>
          <button class="btn-card btn-card-primary" @click.stop="goToRegisterCompany">Hire Talent</button>
        </div>
      </div>

      <p class="login-link">
        Already have an account?
        <router-link to="/login" class="link">Log in here</router-link>
      </p>
    </main>

    <footer class="footer">
      <span>© 2026 TalentFlow Inc. All rights reserved.</span>
      <div class="footer-links">
        <a href="#">Terms of Service</a>
        <a href="#">Privacy Policy</a>
        <a href="#">Help Center</a>
        <span class="info-icon">ℹ</span>
      </div>
    </footer>

  </div>
</template>

<script>
export default {
  name: 'RoleSelection',
  data() { return { selectedRole: null } },
  methods: {
    selectRole(role) { this.selectedRole = role },
    goToRegisterCandidate() { this.$router.push('/register-candidate') },
    goToRegisterCompany() { this.$router.push('/register-company') }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

/* ═══════════════════════════════════════════════
   CLEF : position fixed + inset:0 = plein écran
   indépendamment de #app et body de Vite
   ═══════════════════════════════════════════════ */
.page-wrapper {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  /* Reset total des héritages Vite */
  background-color: #f0f2f8;
  color: #1a1d2e;
  font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 16px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

.page-wrapper *,
.page-wrapper *::before,
.page-wrapper *::after {
  box-sizing: border-box;
}

/* ── Header ── */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 48px;
  background: #ffffff;
  border-bottom: 1px solid #e5e7f0;
  flex-shrink: 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  font-size: 16px;
  color: #1a1d2e;
  text-decoration: none;
}

.appli-brand-logo {
  height: clamp(24px, 3.4vw, 40px);
  width: auto;
  max-width: min(240px, 62vw);
  object-fit: contain;
  display: block;
  flex-shrink: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.step-text {
  font-size: 14px;
  color: #9095b0;
}

.btn-signup {
  all: unset;
  background: #4A6CF7;
  color: #ffffff;
  padding: 8px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.2s;
}
.btn-signup:hover { background: #3b5de0; }

/* ── Main ── */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  background-color: #f0f2f8;
}

.title {
  font-size: 36px;
  font-weight: 700;
  color: #1a1d2e;
  text-align: center;
  margin: 0 0 12px 0;
}

.subtitle {
  font-size: 15px;
  color: #4a4f6a;
  text-align: center;
  margin: 0 0 48px 0;
}

/* ── Cards ── */
.cards-container {
  display: flex;
  gap: 24px;
  margin-bottom: 32px;
  flex-wrap: wrap;
  justify-content: center;
}

.role-card {
  background: #ffffff;
  border: 2px solid #e5e7f0;
  border-radius: 12px;
  padding: 36px 32px;
  width: 260px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.role-card:hover {
  border-color: #4A6CF7;
  box-shadow: 0 6px 24px rgba(74,108,247,0.15);
}

.role-card.selected {
  border-color: #4A6CF7;
  background: #eef0fe;
}

.card-icon {
  background: #eef0fe;
  border-radius: 50%;
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  color: #1a1d2e;
  margin: 0 0 8px 0;
}

.card-desc {
  font-size: 13px;
  color: #4a4f6a;
  margin: 0 0 24px 0;
  line-height: 1.5;
}

.btn-card {
  all: unset;
  display: block;
  width: 100%;
  padding: 11px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  text-align: center;
  background: #eef0fe;
  color: #4A6CF7;
  transition: background 0.2s, color 0.2s;
}
.btn-card:hover { background: #4A6CF7; color: #ffffff; }
.btn-card-primary { background: #4A6CF7; color: #ffffff; }
.btn-card-primary:hover { background: #3b5de0; }

/* ── Login link ── */
.login-link {
  font-size: 14px;
  color: #4a4f6a;
  margin: 0;
}

.link { color: #4A6CF7; font-weight: 600; text-decoration: none; }
.link:hover { text-decoration: underline; }

/* ── Footer ── */
.footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 48px;
  font-size: 12px;
  color: #9095b0;
  border-top: 1px solid #e5e7f0;
  background: #ffffff;
  flex-wrap: wrap;
  gap: 8px;
  flex-shrink: 0;
}

.footer-links { display: flex; gap: 16px; align-items: center; }
.footer-links a { color: #9095b0; font-size: 12px; text-decoration: none; }
.footer-links a:hover { color: #4A6CF7; }

.info-icon {
  width: 18px; height: 18px;
  border: 1px solid #9095b0;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 10px; cursor: pointer; color: #9095b0;
}

/* ── Responsive ── */
@media (max-width: 600px) {
  .header, .footer { padding: 12px 16px; }
  .cards-container { flex-direction: column; }
  .role-card { width: 100%; }
  .footer { flex-direction: column; text-align: center; }
  .logo { min-width: 0; max-width: calc(100% - 120px); }
  .appli-brand-logo { max-width: min(200px, 70vw); height: clamp(22px, 7vw, 34px); }
}
</style>