---
title: PTA Standards - Plain Text Accounting Specifications
---

<div class="landing-hero">
  <p class="hero-subtitle">Plain Text Accounting</p>
  <h1 class="hero-title"><span class="text-accent">PTA</span> Standards</h1>
  <p class="hero-tagline">Formal specifications for Beancount, Ledger, and hledger formats.</p>

  <div class="hero-actions">
    <a href="https://github.com/rustledger/pta-standards" target="_blank" rel="noopener noreferrer" class="github-btn">
      <svg class="github-icon" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
      <span>View on GitHub</span>
    </a>
  </div>

  <div class="install-buttons">
    <a href="/pta-standards/formats/beancount/v3/" class="install-btn primary">Beancount Spec</a>
    <a href="/pta-standards/core/" class="install-btn secondary">Core Model</a>
  </div>
</div>

<section class="status-section">
  <h2 class="section-title">Format Status</h2>
  <p class="section-subtitle">Current specification progress</p>

  <div class="status-grid">
    <a href="/pta-standards/formats/beancount/v3/" class="status-card">
      <h3>Beancount v3</h3>
      <span class="status-badge draft">Draft</span>
      <p>Complete grammar, AST schema, and semantic rules.</p>
    </a>
    <div class="status-card">
      <h3>Ledger</h3>
      <span class="status-badge planned">Planned</span>
      <p>Specification work planned for future release.</p>
    </div>
    <div class="status-card">
      <h3>hledger</h3>
      <span class="status-badge planned">Planned</span>
      <p>Specification work planned for future release.</p>
    </div>
  </div>
</section>

<section class="features-section">
  <h2 class="section-title">Goals</h2>
  <p class="section-subtitle">What we're building towards</p>

  <div class="features-grid">
    <div class="feature-card">
      <div class="feature-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg></div>
      <h3>Precision</h3>
      <p>Unambiguous specifications that enable correct implementations.</p>
    </div>
    <div class="feature-card">
      <div class="feature-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg></div>
      <h3>Testability</h3>
      <p>Comprehensive conformance test suites for validation.</p>
    </div>
    <div class="feature-card">
      <div class="feature-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 17h6M17 14v6"/></svg></div>
      <h3>Interoperability</h3>
      <p>Enable format conversion and tool compatibility.</p>
    </div>
    <div class="feature-card">
      <div class="feature-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg></div>
      <h3>Community</h3>
      <p>Open evolution through RFCs and community input.</p>
    </div>
  </div>
</section>

<section class="included-section">
  <h2 class="section-title">What's Included</h2>
  <p class="section-subtitle">Comprehensive tooling for implementers</p>

  <div class="included-list">
    <div class="included-item">
      <div class="included-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg></div>
      <div>
        <strong>EBNF & ABNF Grammars</strong>
        <p>Formal grammar definitions for parsing</p>
      </div>
    </div>
    <div class="included-item">
      <div class="included-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg></div>
      <div>
        <strong>AST Definitions</strong>
        <p>JSON Schema and Protocol Buffer schemas</p>
      </div>
    </div>
    <div class="included-item">
      <div class="included-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="4,17 10,11 4,5"/><line x1="12" y1="19" x2="20" y2="19"/></svg></div>
      <div>
        <strong>Tree-sitter Grammars</strong>
        <p>Editor integration for syntax highlighting</p>
      </div>
    </div>
    <div class="included-item">
      <div class="included-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg></div>
      <div>
        <strong>Test Vectors</strong>
        <p>Conformance test suites for validation</p>
      </div>
    </div>
  </div>
</section>

<style>
.landing-hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 4rem 1.5rem 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.hero-subtitle {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  margin-bottom: 1.5rem;
}

.hero-title {
  font-size: clamp(2.5rem, 8vw, 4rem);
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.02em;
  margin: 0 0 1.5rem 0;
  color: white;
}

.text-accent { color: #f97316; }

.hero-tagline {
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 2rem 0;
  max-width: 500px;
}

.hero-actions { margin-bottom: 2rem; }

.github-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  color: white;
  text-decoration: none;
  transition: all 0.2s;
}

.github-btn:hover { background: rgba(255, 255, 255, 0.15); }

.github-icon { width: 1.25rem; height: 1.25rem; }

.install-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

.install-btn {
  display: inline-block;
  padding: 0.75rem 2rem;
  border-radius: 0.5rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s;
}

.install-btn.primary { background: #f97316; color: white; }
.install-btn.primary:hover { background: #ea580c; }

.install-btn.secondary {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
}

.install-btn.secondary:hover { background: rgba(255, 255, 255, 0.15); }

.status-section, .features-section, .included-section {
  padding: 4rem 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.section-title {
  text-align: center;
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.75rem 0;
  color: white;
}

.section-subtitle {
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
  margin: 0 0 3rem 0;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  max-width: 900px;
  margin: 0 auto;
}

.status-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.75rem;
  padding: 1.5rem;
  text-decoration: none;
  transition: border-color 0.2s;
}

.status-card:hover { border-color: rgba(249, 115, 22, 0.3); }

.status-card h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: white;
  margin: 0 0 0.75rem 0;
}

.status-card p {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.5);
  margin: 0.75rem 0 0 0;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.draft {
  background: rgba(249, 115, 22, 0.2);
  color: #f97316;
}

.status-badge.planned {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.6);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
  max-width: 900px;
  margin: 0 auto;
}

.feature-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.75rem;
  padding: 1.5rem;
  transition: border-color 0.2s;
}

.feature-card:hover { border-color: rgba(249, 115, 22, 0.3); }

.feature-icon {
  width: 24px;
  height: 24px;
  margin-bottom: 1rem;
  color: #f97316;
}

.feature-icon svg { width: 100%; height: 100%; }

.feature-card h3 {
  font-size: 1rem;
  font-weight: 600;
  color: white;
  margin: 0 0 0.5rem 0;
}

.feature-card p {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
  line-height: 1.6;
}

.included-list {
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.included-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.5rem;
}

.included-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  color: #f97316;
}

.included-icon svg { width: 100%; height: 100%; }

.included-item strong {
  color: white;
  display: block;
  margin-bottom: 0.25rem;
}

.included-item p {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.9rem;
  margin: 0;
}

.VPDoc.has-aside .content-container,
.VPDoc .content-container { max-width: 100% !important; }

.VPDoc.has-aside .content,
.VPDoc .content { padding: 0 !important; max-width: 100% !important; }

.VPDoc .aside { display: none !important; }
</style>
