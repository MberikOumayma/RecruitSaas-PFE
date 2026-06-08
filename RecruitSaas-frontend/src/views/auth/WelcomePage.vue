<template>
  <div class="welcome-page" :class="{ 'dark-mode': isDark }">

    <!-- NAVBAR -->
    <nav class="navbar" :class="{ scrolled: isScrolled }">
      <div class="nav-logo" @click="scrollTo('hero')">
        <img class="appli-brand-logo appli-brand-logo--nav" src="/appli-logo.png" alt="TalentFlow" />
      </div>

     

      <div class="nav-actions">
        <button class="btn-icon" @click="toggleDark" :title="isDark ? 'Light mode' : 'Dark mode'">
          {{ isDark ? '☀️' : '🌙' }}
        </button>
        <a class="btn-login" @click="goToLogin">Login</a>
        <button class="btn-primary" @click="goToRoleSelection">Get Started</button>
        <button class="burger" @click="menuOpen = !menuOpen">
          <span></span><span></span><span></span>
        </button>
      </div>
    </nav>

    <!-- HERO SECTION -->
    <section class="hero" id="hero">
      <div class="hero-left">
          
        <h1 class="hero-title">
          Revolutionize Your Recruitment with
          <span class="hero-accent">AI-Powered Intelligence.</span>
        </h1>
        <p class="hero-subtitle">
          The all-in-one multi-tenant platform to find, track, and hire the
          world's best talent faster. Designed for scale, built for speed.
        </p>
        <div class="hero-ctas">
          <button class="btn-primary btn-large" @click="goToRoleSelection">Get Started</button>
        </div>
        
      </div>

      <div class="hero-right">
        <div class="hero-mockup">
          <div class="mockup-window">
            <div class="window-bar">
              <span class="dot red"></span>
              <span class="dot yellow"></span>
              <span class="dot green"></span>
            </div>
            <div class="mockup-content">
              <div class="mockup-header">
                <div class="mockup-avatar"></div>
                <div class="mockup-search"></div>
              </div>
              <div class="mockup-section">
                <div class="section-label"></div>
                <div class="mockup-row">
                  <div class="cell wide"></div>
                  <div class="cell medium"></div>
                  <div class="cell short"></div>
                </div>
                <div class="mockup-row">
                  <div class="cell medium"></div>
                  <div class="cell wide"></div>
                </div>
                <div class="mockup-row mt">
                  <div class="cell short"></div>
                  <div class="cell short"></div>
                  <div class="cell short"></div>
                  <div class="cell short"></div>
                  <div class="cell short active"></div>
                </div>
                <div class="mockup-row">
                  <div class="cell short"></div>
                  <div class="cell short"></div>
                  <div class="cell short"></div>
                  <div class="cell short active-yellow"></div>
                </div>
              </div>
              <div class="mockup-footer-row">
                <div v-for="i in 9" :key="i" class="avatar-circle"></div>
              </div>
              <div class="mockup-tabs">
                <div v-for="label in ['Employees','Finance','History','Assets','Inventory','Queue','Employment','Values','Distribution']" :key="label" class="tab-item">{{ label }}</div>
              </div>
            </div>
          </div>
        </div>
        
      </div>
    </section>

    

    <!-- FEATURES SECTION -->
    <section class="features" id="features">
      <h2 class="section-title">Powerful Features for Modern Hiring</h2>
      <p class="section-subtitle">
        Our platform is engineered to automate the heavy lifting, allowing your team to focus on
        what matters: the human side of recruitment.
      </p>
      <div class="features-grid">
        <div class="feature-card" v-for="feature in features" :key="feature.title">
          <div class="feature-icon">
            <span v-html="feature.icon"></span>
          </div>
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-desc">{{ feature.desc }}</p>
          <a class="feature-link" @click="goToRoleSelection">Learn more →</a>
        </div>
      </div>
    </section>

    <!-- CHOOSE YOUR PATH SECTION -->
    <section class="choose-path" id="path">
      <div class="path-header">
        <h2 class="path-title">Choose Your Path</h2>
        <p class="path-subtitle">Whether you are hiring or looking, we have the tools you need.</p>
      </div>
      <div class="path-cards">

        <!-- EMPLOYERS CARD -->
        <div class="path-card employers" @click="goToRoleSelection">
          <div class="path-illustration">
            <div class="card-icon-wrap employers-icon">
              <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                <rect x="10" y="24" width="44" height="34" rx="3" fill="rgba(255,255,255,0.15)" stroke="rgba(255,255,255,0.3)" stroke-width="1.5"/>
                <rect x="22" y="12" width="20" height="14" rx="2" fill="rgba(255,255,255,0.2)" stroke="rgba(255,255,255,0.35)" stroke-width="1.5"/>
                <rect x="26" y="38" width="12" height="20" rx="2" fill="rgba(255,255,255,0.25)"/>
                <rect x="14" y="30" width="10" height="8" rx="1.5" fill="rgba(255,255,255,0.3)"/>
                <rect x="40" y="30" width="10" height="8" rx="1.5" fill="rgba(255,255,255,0.3)"/>
                <rect x="14" y="42" width="10" height="8" rx="1.5" fill="rgba(255,255,255,0.2)"/>
                <rect x="40" y="42" width="10" height="8" rx="1.5" fill="rgba(255,255,255,0.2)"/>
              </svg>
            </div>
          </div>
          <div class="path-content">
            <div class="path-tag">For Employers</div>
            <h3>Hire Smarter , Build Faster</h3>
            <p>Scale your team with top-tier talent and AI-powered screening that reduces time-to-hire by 60%.</p>
            <ul class="path-perks">
              <li><span class="perk-check">✓</span> Post unlimited job listings</li>
              <li><span class="perk-check">✓</span> AI-ranked candidate shortlists</li>
              <li><span class="perk-check">✓</span> Integrated interview scheduling</li>
            </ul>
            <button class="path-btn dark-btn" @click.stop="goToRoleSelection">Post a Job →</button>
          </div>
        </div>

        <!-- CANDIDATES CARD -->
        <div class="path-card candidates" @click="goToRoleSelection">
          <div class="path-illustration">
            <div class="card-icon-wrap candidates-icon">
              <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                <circle cx="32" cy="20" r="12" fill="rgba(255,255,255,0.2)" stroke="rgba(255,255,255,0.35)" stroke-width="1.5"/>
                <path d="M10 54c0-12.15 9.85-22 22-22s22 9.85 22 22" fill="rgba(255,255,255,0.15)" stroke="rgba(255,255,255,0.3)" stroke-width="1.5" stroke-linecap="round"/>
                <rect x="38" y="34" width="18" height="22" rx="3" fill="rgba(255,255,255,0.18)" stroke="rgba(255,255,255,0.3)" stroke-width="1"/>
                <rect x="41" y="38" width="10" height="2" rx="1" fill="rgba(255,255,255,0.5)"/>
                <rect x="41" y="42" width="8" height="2" rx="1" fill="rgba(255,255,255,0.35)"/>
                <rect x="41" y="46" width="10" height="2" rx="1" fill="rgba(255,255,255,0.35)"/>
                <circle cx="51" cy="33" r="6" fill="rgba(99,200,140,0.85)" stroke="rgba(255,255,255,0.4)" stroke-width="1.5"/>
                <path d="M48 33 l2 2 l4-4" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
          <div class="path-content">
            <div class="path-tag"> For Candidates</div>
            <h3>Land Your Dream Job</h3>
            <p>Get matched with leading companies that value your unique skill set and accelerate your career.</p>
            <ul class="path-perks">
              <li><span class="perk-check">✓</span> Roles that fit, easy to find and apply</li>
              <li><span class="perk-check">✓</span> One-click CV upload &amp; parsing</li>
              <li><span class="perk-check">✓</span> Real-time application tracking</li>
            </ul>
            <button class="path-btn light-btn" @click.stop="goToRoleSelection">Upload CV →</button>
          </div>
        </div>

      </div>
    </section>

    <!-- FOOTER -->
    <footer class="footer" id="footer">

      <!-- CTA BAND -->
      <div class="footer-cta-band">
        <div class="footer-cta-text">
          <h3>Ready to transform your hiring?</h3>
        </div>
        <div class="footer-cta-actions">
          <button class="btn-white" @click="goToRoleSelection">Get Started Free</button>
          <button class="btn-ghost" @click="scrollTo('features')">See how it works →</button>
        </div>
      </div>

      <!-- MAIN FOOTER -->
      <div class="footer-main">

        <!-- BRAND COL -->
        <div class="footer-brand">
          <div class="footer-logo">
            <img class="appli-brand-logo appli-brand-logo--footer" src="/appli-logo.png" alt="TalentFlow" />
          </div>
          <p class="footer-tagline">
AI-powered recruitment tools built for fast-moving teams.
Automate candidate screening, streamline hiring workflows, and make smarter decisions with data-driven insights.
Hire top talent faster while improving efficiency, collaboration, and overall candidate experience.          </p>
          
          <div class="footer-socials">
            <a class="social-btn" href="https://linkedin.com" target="_blank" rel="noopener" title="LinkedIn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6zM2 9h4v12H2z"/><circle cx="4" cy="4" r="2"/></svg>
            </a>
            <a class="social-btn" href="https://twitter.com" target="_blank" rel="noopener" title="Twitter / X">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
            </a>
            <a class="social-btn" href="https://github.com" target="_blank" rel="noopener" title="GitHub">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/></svg>
            </a>
            <a class="social-btn" href="mailto:hello@talentflow.io" title="Email us">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
            </a>
          </div>
        </div>

        <!-- LINKS GRID -->
        <div class="footer-nav">

          <div class="footer-col">
            <h4>Product</h4>
            <ul>
              <li><a @click="scrollTo('features')">Platform Overview</a></li>
              <li><a @click="scrollTo('features')">AI Matching <span class="link-badge new">New</span></a></li>
              <li><a @click="scrollTo('features')">Pipeline Tracking</a></li>
              <li><a @click="scrollTo('features')">Enterprise Tools</a></li>
              <li><a @click="scrollTo('features')">Integrations</a></li>
              <li><a @click="scrollTo('features')">Security & Compliance</a></li>
              <li><a @click="scrollTo('features')" class="link-muted">Changelog</a></li>
            </ul>
          </div>

          <div class="footer-col">
            <h4>Company</h4>
            <ul>
              <li><a @click="scrollTo('hero')">About Us</a></li>
              <li>
                <a @click="goToRoleSelection">
                  Careers
                </a>
              </li>
              <li><a @click="scrollTo('features')">Blog & Insights</a></li>
              <li><a @click="scrollTo('features')">Press & Media</a></li>
              <li><a @click="scrollTo('features')">Partners</a></li>
              <li><a @click="scrollTo('footer')">Contact Us</a></li>
            </ul>
          </div>

          <div class="footer-col">
            <h4>Resources</h4>
            <ul>
              <li><a @click="scrollTo('features')">Documentation</a></li>
              <li><a @click="scrollTo('features')">API Reference</a></li>
              <li><a @click="scrollTo('features')">Help Center</a></li>
              <li><a @click="scrollTo('features')">Community Forum</a></li>
              <li>
                <a @click="scrollTo('features')" class="status-link">
                  <span class="status-dot"></span>
                  System Status
                </a>
              </li>
              <li><a @click="scrollTo('features')">Release Notes</a></li>
            </ul>
          </div>

          <div class="footer-col footer-newsletter">
            <h4>Stay in the Loop</h4>
            <p>Weekly hiring insights, product updates and industry trends — straight to your inbox.</p>
            <div class="newsletter-form">
              <input
                type="email"
                placeholder="you@company.com"
                v-model="newsletterEmail"
                @keyup.enter="subscribeNewsletter"
              />
              <button class="btn-subscribe" @click="subscribeNewsletter" :disabled="subscribed">
                <span v-if="!subscribed">Subscribe</span>
                <span v-else>✓ Done</span>
              </button>
            </div>
            <p v-if="subscribed" class="subscribe-success">🎉 Welcome aboard! Check your inbox.</p>
            <p class="newsletter-note">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
              No spam ever. Unsubscribe anytime.
            </p>
          </div>

        </div>
      </div>

      <!-- FOOTER BOTTOM -->
      <div class="footer-bottom">
        <div class="footer-bottom-left">
          <span>© 2026 TalentFlow Technologies Inc.</span>
          <span class="footer-sep">·</span>
          <span class="footer-location">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
            Available worldwide
          </span>
        </div>
        <div class="footer-legal">
          <a href="#">Privacy Policy</a>
          <a href="#">Terms of Service</a>
          <a href="#">Cookie Preferences</a>
          <a href="#">Accessibility</a>
        </div>
      </div>

    </footer>

    <!-- SCROLL TO TOP -->
    <button class="scroll-top" v-show="isScrolled" @click="scrollToTop" title="Back to top">↑</button>

  </div>
</template>

<script>
export default {
  name: 'WelcomePage',
  data() {
    return {
      isDark: false,
      isScrolled: false,
      menuOpen: false,
      newsletterEmail: '',
      subscribed: false,
      trustedCompanies: ['Google', 'Stripe', 'Airbnb', 'Notion', 'Figma', 'Linear'],
      features: [
        {
          title: 'AI Candidate Matching',
          icon: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3b6ef0" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M12 14c-6 0-8 3-8 4h16c0-1-2-4-8-4z"/><path d="M20 8c0-2-1-3-2-3"/></svg>`,
          desc: 'Leverage advanced algorithms to visualize candidate fit with automated intelligence scores based on skills and culture.'
        },
        {
          title: 'Multi-tenant Management',
          icon: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3b6ef0" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>`,
          desc: 'Perfect for agencies and large enterprises to manage multiple organizations and separate pipelines in one unified place.'
        },
        {
          title: 'Seamless Pipeline Tracking',
          icon: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3b6ef0" stroke-width="2"><rect x="3" y="3" width="5" height="5" rx="1"/><rect x="10" y="3" width="5" height="5" rx="1"/><rect x="17" y="3" width="4" height="4" rx="1"/><rect x="3" y="10" width="5" height="5" rx="1"/><rect x="10" y="10" width="5" height="5" rx="1"/></svg>`,
          desc: 'Track every applicant through a high-speed, intuitive interface designed for maximum efficiency and clarity.'
        }
      ]
    }
  },
  mounted() {
    window.addEventListener('scroll', this.handleScroll)
  },
  beforeUnmount() {
    window.removeEventListener('scroll', this.handleScroll)
  },
  methods: {
    goToRoleSelection() {
      this.menuOpen = false
      this.$router.push('/role-selection')
    },
    goToLogin() {
      this.menuOpen = false
      this.$router.push('/login')
    },
    toggleDark() {
      this.isDark = !this.isDark
    },
    handleScroll() {
      this.isScrolled = window.scrollY > 40
    },
    scrollTo(id) {
      this.menuOpen = false
      const el = document.getElementById(id)
      if (el) el.scrollIntoView({ behavior: 'smooth' })
    },
    scrollToTop() {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    },
    subscribeNewsletter() {
      if (this.newsletterEmail && this.newsletterEmail.includes('@')) {
        this.subscribed = true
        this.newsletterEmail = ''
      }
    }
  }
}
</script>

<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: 100%; min-height: 100vh; overflow-x: hidden; }
#app { width: 100% !important; max-width: 100% !important; margin: 0 !important; padding: 0 !important; }
</style>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800;900&display=swap');

.welcome-page {
  font-family: 'Manrope', sans-serif;
  background: #f0f4f8;
  color: #0d1b2a;
  width: 100vw;
  min-height: 100vh;
  overflow-x: hidden;
  position: relative;
  left: 50%;
  margin-left: -50vw;
  transition: background 0.3s, color 0.3s;
}

/* ===== DARK MODE ===== */
.dark-mode { background: #0d1117; color: #e5e7eb; }
.dark-mode .navbar { background: rgba(13,17,23,0.95); border-bottom-color: rgba(255,255,255,0.06); }
.dark-mode .nav-links a { color: #9ca3af; }
.dark-mode .btn-login { color: #9ca3af; }
.dark-mode .hero-title { color: #f3f4f6; }
.dark-mode .hero-subtitle { color: #9ca3af; }
.dark-mode .stat-value { color: #f3f4f6; }
.dark-mode .stat-label { color: #6b7280; }
.dark-mode .stat-divider { background: #21262d; }
.dark-mode .hero-mockup { background: #2a5a4a; }
.dark-mode .mockup-window { background: #161b22; }
.dark-mode .window-bar { background: #0d1117; }
.dark-mode .mockup-avatar,
.dark-mode .mockup-search,
.dark-mode .section-label,
.dark-mode .cell { background: #21262d; }
.dark-mode .cell.active { background: #10b981; }
.dark-mode .cell.active-yellow { background: #f59e0b; }
.dark-mode .match-badge { background: #161b22; box-shadow: 0 8px 30px rgba(0,0,0,0.4); }
.dark-mode .match-value { color: #f3f4f6; }
.dark-mode .trusted-bar { background: #0d1117; border-color: #21262d; }
.dark-mode .trusted-label { color: #6b7280; }
.dark-mode .features { background: #0d1117; }
.dark-mode .section-title { color: #f3f4f6; }
.dark-mode .feature-card { background: #161b22; border-color: #21262d; }
.dark-mode .feature-title { color: #f3f4f6; }
.dark-mode .choose-path { background: #0a0e14; }
.dark-mode .path-title { color: #f3f4f6; }
.dark-mode .btn-outline { background: #161b22; color: #e5e7eb; border-color: #30363d; }

/* ===== NAVBAR ===== */
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
  min-height: 104px;
  height: 104px;
  background: rgba(240, 244, 248, 0.92);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(0,0,0,0.06);
  transition: box-shadow 0.3s, background 0.3s;
}

.navbar.scrolled { box-shadow: 0 2px 20px rgba(0,0,0,0.08); }

.nav-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.appli-brand-logo {
  object-fit: contain;
  display: block;
  flex-shrink: 0;
}

/* Navbar wordmark — large horizontal logo */
.appli-brand-logo--nav {
  width: auto;
  height: auto;
  max-height: clamp(56px, 11vw, 100px);
  max-width: min(720px, 95vw);
}

.nav-links { display: flex; list-style: none; gap: 32px; }

.nav-links a {
  text-decoration: none;
  color: #374151;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s;
}

.nav-links a:hover { color: #2563eb; }

.nav-actions { display: flex; align-items: center; gap: 12px; }

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 18px;
  padding: 6px;
  border-radius: 8px;
  transition: background 0.2s;
}

.btn-icon:hover { background: rgba(0,0,0,0.06); }

.btn-login {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  padding: 8px 14px;
  border-radius: 8px;
  transition: background 0.2s, color 0.3s;
}

.btn-login:hover { background: rgba(0,0,0,0.05); }

.btn-primary {
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 10px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Manrope', sans-serif;
  transition: background 0.2s, transform 0.15s, box-shadow 0.2s;
}

.btn-primary:hover {
  background: #1d4ed8;
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(37,99,235,0.35);
}

.btn-primary:disabled { background: #10b981; cursor: default; transform: none; box-shadow: none; }

.btn-outline {
  background: white;
  color: #0d1b2a;
  border: 1.5px solid #d1d5db;
  border-radius: 10px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Manrope', sans-serif;
  transition: border-color 0.2s, color 0.2s, transform 0.15s, box-shadow 0.2s;
}

.btn-outline:hover {
  border-color: #2563eb;
  color: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(37,99,235,0.1);
}

.burger {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
}

.burger span {
  display: block;
  width: 22px;
  height: 2px;
  background: #374151;
  border-radius: 2px;
}

/* ===== HERO ===== */
.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 80px 80px 120px;
  gap: 60px;
  min-height: calc(100vh - 104px);
}

.hero-left { flex: 1; max-width: 560px; }

.badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 700;
  color: #2563eb;
  letter-spacing: 0.08em;
  margin-bottom: 24px;
  background: rgba(37,99,235,0.08);
  padding: 6px 14px;
  border-radius: 50px;
  border: 1px solid rgba(37,99,235,0.2);
}

.badge-dot {
  width: 7px;
  height: 7px;
  background: #2563eb;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.75); }
}

.hero-title {
  font-size: 58px;
  font-weight: 900;
  line-height: 1.1;
  color: #0d1b2a;
  margin-bottom: 24px;
  transition: color 0.3s;
}

.hero-accent { color: #2563eb; }

.hero-subtitle {
  font-size: 16px;
  color: #4b5563;
  line-height: 1.7;
  margin-bottom: 40px;
  max-width: 480px;
  transition: color 0.3s;
}

.hero-ctas { display: flex; gap: 16px; align-items: center; margin-bottom: 48px; }

.btn-large { padding: 14px 28px; font-size: 15px; border-radius: 12px; }

.hero-stats { display: flex; align-items: center; gap: 24px; }
.stat { display: flex; flex-direction: column; gap: 2px; }
.stat-value { font-size: 22px; font-weight: 800; color: #0d1b2a; transition: color 0.3s; }
.stat-label { font-size: 12px; color: #6b7280; font-weight: 500; }
.stat-divider { width: 1px; height: 36px; background: #e5e7eb; transition: background 0.3s; }

.hero-right { flex: 1; max-width: 580px; position: relative; }

.hero-mockup {
  background: #4a8c7a;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 30px 80px rgba(0,0,0,0.18);
  transition: background 0.3s;
}

.mockup-window { background: white; border-radius: 12px; overflow: hidden; transition: background 0.3s; }

.window-bar {
  background: #f3f4f6;
  padding: 10px 14px;
  display: flex;
  gap: 6px;
  align-items: center;
  transition: background 0.3s;
}

.dot { width: 12px; height: 12px; border-radius: 50%; }
.dot.red { background: #ef4444; }
.dot.yellow { background: #f59e0b; }
.dot.green { background: #10b981; }

.mockup-content { padding: 16px; }

.mockup-header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.mockup-avatar { width: 32px; height: 32px; background: #e5e7eb; border-radius: 50%; transition: background 0.3s; }
.mockup-search { flex: 1; height: 24px; background: #f3f4f6; border-radius: 6px; transition: background 0.3s; }
.section-label { height: 14px; width: 140px; background: #e5e7eb; border-radius: 4px; margin-bottom: 12px; transition: background 0.3s; }

.mockup-row { display: flex; gap: 8px; margin-bottom: 8px; align-items: center; }
.mockup-row.mt { margin-top: 12px; }

.cell { height: 20px; background: #f3f4f6; border-radius: 4px; transition: background 0.3s; }
.cell.wide { width: 120px; }
.cell.medium { width: 80px; }
.cell.short { width: 55px; }
.cell.active { background: #10b981 !important; }
.cell.active-yellow { background: #f59e0b !important; }

.mockup-footer-row { display: flex; gap: 6px; padding: 12px 0 8px; flex-wrap: wrap; }
.avatar-circle { width: 32px; height: 32px; background: #4a8c7a; border-radius: 50%; }

.mockup-tabs { display: flex; border-top: 1px solid #f3f4f6; padding-top: 8px; overflow-x: auto; }
.tab-item { font-size: 9px; color: #9ca3af; white-space: nowrap; padding: 4px 8px; flex-shrink: 0; }

.match-badge {
  position: absolute;
  bottom: -24px;
  left: -20px;
  background: white;
  border-radius: 16px;
  padding: 14px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.12);
  transition: background 0.3s;
}

.match-icon {
  width: 40px;
  height: 40px;
  background: #d1fae5;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.match-label { font-size: 12px; color: #6b7280; font-weight: 500; }
.match-value { font-size: 22px; font-weight: 800; color: #0d1b2a; transition: color 0.3s; }

/* ===== TRUSTED BAR ===== */
.trusted-bar {
  background: white;
  border-top: 1px solid #e5e7eb;
  border-bottom: 1px solid #e5e7eb;
  padding: 20px 80px;
  display: flex;
  align-items: center;
  gap: 32px;
  transition: background 0.3s, border-color 0.3s;
}

.trusted-label {
  font-size: 13px;
  color: #9ca3af;
  font-weight: 500;
  white-space: nowrap;
  transition: color 0.3s;
}

.trusted-logos { display: flex; gap: 40px; align-items: center; overflow-x: auto; }

.trusted-item {
  font-size: 15px;
  font-weight: 800;
  color: #d1d5db;
  letter-spacing: -0.02em;
  white-space: nowrap;
  transition: color 0.2s;
}

.trusted-item:hover { color: #9ca3af; cursor: default; }

/* ===== FEATURES ===== */
.features {
  background: white;
  padding: 100px 80px;
  text-align: center;
  transition: background 0.3s;
}

.section-title { font-size: 36px; font-weight: 800; color: #0d1b2a; margin-bottom: 16px; transition: color 0.3s; }
.section-subtitle { font-size: 16px; color: #6b7280; max-width: 600px; margin: 0 auto 60px; line-height: 1.7; }

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  max-width: 1100px;
  margin: 0 auto;
}

.feature-card {
  background: #f8fafc;
  border-radius: 16px;
  padding: 36px 32px;
  text-align: left;
  border: 1px solid #e5e7eb;
  transition: box-shadow 0.25s, transform 0.25s, background 0.3s, border-color 0.3s;
}

.feature-card:hover {
  box-shadow: 0 16px 48px rgba(37,99,235,0.12);
  transform: translateY(-6px);
  border-color: #bfdbfe;
}

.feature-icon {
  width: 52px;
  height: 52px;
  background: #eff6ff;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  transition: transform 0.2s;
}

.feature-card:hover .feature-icon { transform: scale(1.1); }

.feature-title { font-size: 18px; font-weight: 700; color: #0d1b2a; margin-bottom: 12px; transition: color 0.3s; }
.feature-desc { font-size: 14px; color: #6b7280; line-height: 1.7; margin-bottom: 24px; }

.feature-link {
  font-size: 14px;
  font-weight: 600;
  color: #2563eb;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: gap 0.2s;
}

.feature-card:hover .feature-link { gap: 8px; }

/* ===== CHOOSE YOUR PATH ===== */
.choose-path { padding: 100px 80px; background: #f0f4f8; transition: background 0.3s; }

.path-header { margin-bottom: 48px; }
.path-title { font-size: 36px; font-weight: 800; color: #0d1b2a; margin-bottom: 12px; transition: color 0.3s; }
.path-subtitle { font-size: 16px; color: #6b7280; margin-bottom: 0; }

.path-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }

.path-card {
  border-radius: 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: transform 0.25s, box-shadow 0.25s;
}

.path-card:hover { transform: translateY(-6px); box-shadow: 0 24px 60px rgba(0,0,0,0.2); }

.employers { background: linear-gradient(160deg, #6b8fa8 0%, #2d4a5c 100%); }
.candidates { background: linear-gradient(160deg, #6080d4 0%, #3251b8 100%); }

.path-illustration {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 36px 32px 8px;
}
.card-icon-wrap {
  width: 120px; height: 120px; border-radius: 30px;
  display: flex; align-items: center; justify-content: center;
  background: rgba(255,255,255,0.1);
  border: 1.5px solid rgba(255,255,255,0.2);
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
}



.path-content {
  padding: 20px 32px 32px;
}

.path-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 700;
  color: rgba(255,255,255,0.65);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  background: rgba(255,255,255,0.1);
  padding: 5px 12px;
  border-radius: 50px;
  margin-bottom: 14px;
  border: 1px solid rgba(255,255,255,0.15);
}
.path-content h3 { font-size: 26px; font-weight: 800; color: white; line-height: 1.2; margin-bottom: 10px; }
.path-content p { font-size: 14px; color: rgba(255,255,255,0.8); line-height: 1.6; margin-bottom: 16px; }
.path-perks {
  list-style: none;
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.path-perks li {
  font-size: 13.5px;
  color: rgba(255,255,255,0.82);
  font-weight: 500;
  display: flex; align-items: center; gap: 8px;
}
.perk-check {
  display: inline-flex; align-items: center; justify-content: center;
  width: 18px; height: 18px;
  background: rgba(255,255,255,0.15);
  border-radius: 50%;
  font-size: 10px; flex-shrink: 0; color: white;
}

.path-btn {
  padding: 12px 24px;
  border-radius: 50px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  font-family: 'Manrope', sans-serif;
  border: none;
  transition: transform 0.2s, box-shadow 0.2s;
}

.path-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.2); }
.dark-btn { background: white; color: #0d1b2a; }
.light-btn { background: white; color: #3251b8; }

/* ===== FOOTER ===== */
.footer { background: #0b0f1a; color: white; }

/* CTA Band */
.footer-cta-band {
  background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 60%, #3b82f6 100%);
  padding: 60px 80px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 40px;
  position: relative;
  overflow: hidden;
}
.footer-cta-band::before {
  content: '';
  position: absolute;
  top: -60px; right: -60px;
  width: 300px; height: 300px;
  background: rgba(255,255,255,0.04);
  border-radius: 50%;
}
.footer-cta-band::after {
  content: '';
  position: absolute;
  bottom: -80px; left: 20%;
  width: 200px; height: 200px;
  background: rgba(255,255,255,0.03);
  border-radius: 50%;
}
.footer-cta-text h3 { font-size: 26px; font-weight: 800; color: white; margin-bottom: 8px; }
.footer-cta-text p { font-size: 15px; color: rgba(255,255,255,0.7); }
.footer-cta-actions { display: flex; align-items: center; gap: 14px; flex-shrink: 0; position: relative; z-index: 1; }
.btn-white {
  background: white; color: #1d4ed8;
  border: none; border-radius: 10px;
  padding: 13px 26px; font-size: 14px; font-weight: 700;
  cursor: pointer; font-family: 'Manrope', sans-serif;
  transition: transform 0.15s, box-shadow 0.2s;
  white-space: nowrap;
}
.btn-white:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.2); }
.btn-ghost {
  background: rgba(255,255,255,0.1);
  color: white;
  border: 1px solid rgba(255,255,255,0.25);
  border-radius: 10px;
  padding: 13px 22px; font-size: 14px; font-weight: 600;
  cursor: pointer; font-family: 'Manrope', sans-serif;
  transition: background 0.2s;
  white-space: nowrap;
}
.btn-ghost:hover { background: rgba(255,255,255,0.18); }

/* Main footer layout */
.footer-main {
  display: flex;
  gap: 64px;
  padding: 60px 80px 52px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
}

/* Brand col */
.footer-brand { flex-shrink: 0; width: 240px; }
.footer-logo { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
.footer-logo .appli-brand-logo--footer {
  height: clamp(20px, 2.6vw, 32px);
  width: auto;
  max-width: min(200px, 88vw);
  object-fit: contain;
}
.footer-tagline { font-size: 13.5px; color: #6b7280; line-height: 1.75; margin-bottom: 20px; }

.footer-rating { display: flex; align-items: center; gap: 10px; margin-bottom: 22px; padding: 10px 14px; background: rgba(255,255,255,0.04); border-radius: 10px; border: 1px solid rgba(255,255,255,0.07); }
.stars { color: #f59e0b; font-size: 13px; letter-spacing: 1px; }
.rating-text { display: flex; flex-direction: column; }
.rating-score { font-size: 13px; font-weight: 700; color: #e5e7eb; }
.rating-count { font-size: 11px; color: #6b7280; }

.footer-socials { display: flex; gap: 8px; }
.social-btn {
  width: 36px; height: 36px; border-radius: 9px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  color: #9ca3af;
  cursor: pointer; font-size: 13px;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.2s, color 0.2s, transform 0.2s;
  text-decoration: none;
}
.social-btn:hover { background: rgba(255,255,255,0.12); color: white; transform: translateY(-2px); }

/* Nav grid */
.footer-nav { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0 40px; flex: 1; }
.footer-col h4 { font-size: 12px; font-weight: 700; color: #e5e7eb; margin-bottom: 18px; letter-spacing: 0.08em; text-transform: uppercase; }
.footer-col ul { list-style: none; }
.footer-col ul li { margin-bottom: 11px; }
.footer-col ul li a {
  color: #6b7280; font-size: 13.5px; cursor: pointer;
  transition: color 0.2s;
  display: inline-flex; align-items: center; gap: 6px;
}
.footer-col ul li a:hover { color: #e5e7eb; }
.link-muted { opacity: 0.6; }

/* Badges */
.link-badge {
  display: inline-block;
  font-size: 10px; font-weight: 700;
  padding: 2px 7px; border-radius: 50px;
  vertical-align: middle; line-height: 1.6;
}
.link-badge.new { background: rgba(37,99,235,0.2); color: #60a5fa; border: 1px solid rgba(37,99,235,0.3); }
.link-badge.hiring { background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.25); }
.footer-badge { display: inline-block; background: #10b981; color: white; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 50px; margin-left: 6px; }

/* Status link */
.status-link { display: inline-flex; align-items: center; gap: 6px; }
.status-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 6px rgba(16,185,129,0.6);
  flex-shrink: 0;
}

/* Newsletter */

.footer-newsletter p { font-size: 13px; color: #6b7280; line-height: 1.65; margin-bottom: 16px; }
.newsletter-form { display: flex; flex-direction: column; gap: 8px; margin-bottom: 10px; }
.newsletter-form input {
  width: 100%;
  padding: 10px 14px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 9px;
  color: white;
  font-size: 13px;
  font-family: 'Manrope', sans-serif;
  outline: none;
  transition: border-color 0.2s, background 0.2s;
}
.newsletter-form input::placeholder { color: #4b5563; }
.newsletter-form input:focus { border-color: #3b82f6; background: rgba(255,255,255,0.09); }
.btn-subscribe {
  width: 100%;
  padding: 10px 16px;
  background: #2563eb; color: white;
  border: none; border-radius: 9px;
  font-size: 13px; font-weight: 700;
  cursor: pointer; font-family: 'Manrope', sans-serif;
  transition: background 0.2s, transform 0.15s;
}
.btn-subscribe:hover { background: #1d4ed8; transform: translateY(-1px); }
.btn-subscribe:disabled { background: #10b981; cursor: default; transform: none; }
.subscribe-success { font-size: 12px; color: #34d399; font-weight: 600; margin-bottom: 6px; }
.newsletter-note {
  font-size: 11.5px; color: #374151;
  display: flex; align-items: center; gap: 5px;
}
.newsletter-note svg { flex-shrink: 0; }

/* Bottom bar */
.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 80px;
}
.footer-bottom-left { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.footer-bottom span { font-size: 12.5px; color: #4b5563; }
.footer-sep { color: #1f2937; }
.footer-location {
  font-size: 12.5px; color: #374151;
  display: inline-flex; align-items: center; gap: 5px;
}
.footer-location svg { color: #10b981; }
.footer-legal { display: flex; gap: 20px; }
.footer-legal a { font-size: 12.5px; color: #4b5563; text-decoration: none; transition: color 0.2s; }
.footer-legal a:hover { color: #9ca3af; }

/* ===== SCROLL TO TOP ===== */
.scroll-top {
  position: fixed;
  bottom: 32px;
  right: 32px;
  width: 44px;
  height: 44px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 18px;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(37,99,235,0.4);
  z-index: 200;
  transition: transform 0.2s, box-shadow 0.2s;
}

.scroll-top:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(37,99,235,0.5); }

/* ===== RESPONSIVE ===== */
@media (max-width: 900px) {
  .navbar { padding: 0 20px; position: relative; min-height: 88px; height: auto; }
  .nav-logo { min-width: 0; max-width: 82%; }
  .appli-brand-logo--nav {
    max-height: clamp(48px, 16vw, 84px);
    max-width: min(560px, 90vw);
  }

  .nav-links { display: none; }
  .nav-links.open {
    display: flex;
    flex-direction: column;
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    padding: 20px 24px;
    border-bottom: 1px solid #e5e7eb;
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    z-index: 99;
    gap: 16px;
  }
  .burger { display: flex; }
  .hero { flex-direction: column; padding: 48px 24px 80px; min-height: auto; }
  .hero-title { font-size: 36px; }
  .hero-right { width: 100%; max-width: 100%; }
  .trusted-bar { padding: 16px 24px; flex-direction: column; align-items: flex-start; gap: 12px; }
  .features { padding: 60px 24px; }
  .features-grid { grid-template-columns: 1fr; }
  .path-cards { grid-template-columns: 1fr; }
  .choose-path { padding: 60px 24px; }
  .footer-cta-band { padding: 36px 24px; flex-direction: column; text-align: center; gap: 20px; }
  .footer-main { flex-direction: column; padding: 40px 24px; gap: 40px; }
  .footer-brand { width: 100%; }
  .footer-nav { grid-template-columns: 1fr 1fr; gap: 32px; }
  .footer-bottom { padding: 20px 24px; flex-direction: column; gap: 16px; text-align: center; }
  .footer-bottom-left { flex-direction: column; gap: 6px; justify-content: center; }
  .footer-cta-actions { flex-direction: column; width: 100%; }
  .btn-white, .btn-ghost { width: 100%; text-align: center; }
  .footer-top { flex-direction: column; gap: 40px; }
  .footer-links { flex-wrap: wrap; gap: 32px; }
  .hero-stats { flex-wrap: wrap; gap: 16px; }
  .scroll-top { bottom: 20px; right: 20px; }
}
</style>