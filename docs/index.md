---
title: Home
hide:
  - navigation
  - toc
---

<style>
.md-content {
  max-width: 100%;
  margin: 0;
  padding: 0;
}

.hero {
  background: linear-gradient(135deg, #0d9488 0%, #0891b2 100%);
  padding: 4rem 2rem;
  text-align: center;
  color: white;
  margin-bottom: 3rem;
}

.hero h1 {
  font-size: 3.5rem;
  font-weight: 800;
  margin: 0;
  color: white;
}

.hero p {
  font-size: 1.3rem;
  opacity: 0.95;
  margin-top: 1rem;
  color: white;
}

.bento-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.bento-card {
  background: var(--md-default-bg-color);
  border: 1px solid var(--md-default-fg-color--lightest);
  border-radius: 12px;
  padding: 2rem;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.bento-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  border-color: var(--md-primary-fg-color);
}

.bento-card h3 {
  margin-top: 0;
  color: var(--md-primary-fg-color);
  font-size: 1.5rem;
}

.bento-card.featured {
  grid-column: span 2;
  background: linear-gradient(135deg, rgba(13, 148, 136, 0.1) 0%, rgba(8, 145, 178, 0.1) 100%);
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  margin-right: 0.5rem;
  background: var(--md-primary-fg-color);
  color: white;
}

.code-example {
  background: var(--md-code-bg-color);
  border-radius: 8px;
  padding: 1rem;
  font-family: monospace;
  font-size: 0.9rem;
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .bento-card.featured {
    grid-column: span 1;
  }
  .hero h1 {
    font-size: 2.5rem;
  }
}
</style>

<div class="hero">
  <h1>Chora</h1>
  <p>The Operating System for Human-Centric Social Physics</p>
  <p><em>Model place as experience, not location</em></p>
</div>

<div class="bento-grid">

  <div class="bento-card featured">
    <h3>🎯 What is Chora?</h3>
    <p>Chora is the first Python library to model <strong>the human experience of place</strong>. Unlike standard GIS which asks <em>"What is at coordinates X,Y?"</em>, Chora asks <em>"Why does this park feel like Home to Alice, but Danger to Bob?"</em></p>
    <p>Chora treats <strong>place</strong> as an emergent phenomenon—arising from memory, habit, emotion, and social interaction—rather than a static polygon on a map.</p>
  </div>

  <div class="bento-card">
    <h3>📚 Core Concepts</h3>
    <p><span class="badge">Encounters</span> Atomic events in space-time</p>
    <p><span class="badge">Familiarity</span> Memory that decays without reinforcement</p>
    <p><span class="badge">Practices</span> Routines & rituals detected from patterns</p>
    <p><span class="badge">Affect</span> Emotional valence of experiences</p>
    <a href="core_concepts/">→ Learn the fundamentals</a>
  </div>

  <div class="bento-card">
    <h3>⚡ Quick Start</h3>
    <div class="code-example">
pip install chora<br>
<br>
# Model Alice visiting a park<br>
from chora.core import *<br>
graph = PlatialGraph("City")<br>
alice = Agent.individual("Alice")<br>
park = SpatialExtent.from_bounds(...)<br>
<br>
# Derive familiarity over time<br>
place = extract_place(graph, park.id)
    </div>
    <a href="getting_started/">→ Get started</a>
  </div>

  <div class="bento-card">
    <h3>🌐 Real-Time API</h3>
    <p>Phase 2 delivers a <strong>FastAPI server</strong> with WebSocket streaming, vector embeddings for semantic search, and Redis caching.</p>
    <div class="code-example">
POST /agents/<br>
POST /encounters/<br>
GET /places/{agent}/{extent}<br>
WS /ws/stream
    </div>
    <a href="api_reference/#server-module-choraserver">→ API Reference</a>
  </div>

  <div class="bento-card">
    <h3>🔬 Theory</h3>
    <p>Chora embodies formal theory from GIScience, cognitive geography, and social physics:</p>
    <ul>
      <li>Relational primacy</li>
      <li>Encounter-centric modeling</li>
      <li>Temporal decay functions</li>
      <li>Epistemic separation</li>
    </ul>
    <a href="theory/">→ Read the theory</a>
  </div>

  <div class="bento-card">
    <h3>🧪 Examples</h3>
    <p>Production-ready examples demonstrating real-world applications:</p>
    <ul>
      <li>Urban mobility analysis</li>
      <li>Affective mapping</li>
      <li>GPS trace processing</li>
      <li>Semantic vector search</li>
    </ul>
    <a href="https://github.com/jameswilliams/chora/tree/master/examples">→ Browse examples</a>
  </div>

  <div class="bento-card featured">
    <h3>🗺️ Roadmap</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">
      <div>
        <strong>v0.5 (Q1 '26)</strong> ✅<br>
        <small>Core, Tests, Docs, CI/CD</small>
      </div>
      <div>
        <strong>v0.9 (Q2 '26)</strong> ✅<br>
        <small>API, WebSockets, Embeddings</small>
      </div>
      <div>
        <strong>v1.0 (Q3 '26)</strong><br>
        <small>Social Physics, Frontend</small>
      </div>
      <div>
        <strong>v2.0 (2027+)</strong><br>
        <small>LLMs, Simulation, Digital Twins</small>
      </div>
    </div>
  </div>

</div>

---

<p style="text-align: center; margin-top: 3rem; opacity: 0.7;">
  <strong>Built for the Platial Turn.</strong><br>
  Open Source • MIT License • <a href="https://github.com/jameswilliams/chora">GitHub</a>
</p>
