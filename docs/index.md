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
  background: linear-gradient(135deg, #0d9488 0%, #0891b2 50%, #6366f1 100%);
  padding: 5rem 2rem;
  text-align: center;
  color: white;
  margin-bottom: 3rem;
}

.hero h1 {
  font-size: 4rem;
  font-weight: 800;
  margin: 0;
  color: white;
  letter-spacing: -0.02em;
}

.hero .tagline {
  font-size: 1.5rem;
  opacity: 0.95;
  margin-top: 1rem;
  color: white;
  font-weight: 300;
}

.hero .subtitle {
  font-size: 1.1rem;
  opacity: 0.8;
  margin-top: 0.5rem;
}

.hero-buttons {
  margin-top: 2rem;
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.hero-btn {
  padding: 0.75rem 2rem;
  border-radius: 8px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s ease;
}

.hero-btn.primary {
  background: white;
  color: #0d9488;
}

.hero-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.hero-btn.secondary {
  background: rgba(255,255,255,0.15);
  color: white;
  border: 1px solid rgba(255,255,255,0.3);
}

.hero-btn.secondary:hover {
  background: rgba(255,255,255,0.25);
}

.bento-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
  padding: 0 2rem 3rem;
  max-width: 1400px;
  margin: 0 auto;
}

.bento-card {
  background: var(--md-default-bg-color);
  border: 1px solid var(--md-default-fg-color--lightest);
  border-radius: 16px;
  padding: 2rem;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.bento-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0,0,0,0.12);
  border-color: var(--md-primary-fg-color);
}

.bento-card h3 {
  margin-top: 0;
  color: var(--md-primary-fg-color);
  font-size: 1.4rem;
}

.bento-card.featured {
  grid-column: span 2;
  background: linear-gradient(135deg, rgba(13, 148, 136, 0.08) 0%, rgba(99, 102, 241, 0.08) 100%);
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  margin-right: 0.5rem;
  margin-bottom: 0.5rem;
  background: var(--md-primary-fg-color);
  color: white;
}

.code-example {
  background: var(--md-code-bg-color);
  border-radius: 8px;
  padding: 1rem;
  font-family: var(--md-code-font-family);
  font-size: 0.85rem;
  margin-top: 1rem;
  overflow-x: auto;
}

.install-box {
  background: #1a1a2e;
  color: #e2e8f0;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  font-family: var(--md-code-font-family);
  font-size: 1rem;
  display: inline-block;
  margin-top: 1.5rem;
}

.install-box code {
  color: #22d3ee;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 1rem 0;
}

.feature-list li {
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--md-default-fg-color--lightest);
}

.feature-list li:last-child {
  border-bottom: none;
}

@media (max-width: 768px) {
  .bento-card.featured {
    grid-column: span 1;
  }
  .hero h1 {
    font-size: 2.5rem;
  }
  .hero .tagline {
    font-size: 1.2rem;
  }
}
</style>

<div class="hero">
  <h1>Chora</h1>
  <p class="tagline">The Python Library for Place-Based Computing</p>
  <p class="subtitle">Model place as experience, not just location</p>
  
  <div class="hero-buttons">
    <a href="getting_started/" class="hero-btn primary">Get Started →</a>
    <a href="guides/" class="hero-btn secondary">View Guides</a>
    <a href="https://github.com/jameswilliamsresearch/chora" class="hero-btn secondary">GitHub</a>
  </div>
  
  <div class="install-box">
    <code>pip install chora</code>
  </div>
</div>

<div class="bento-grid">

  <div class="bento-card featured">
    <h3>🎯 What is Chora?</h3>
    <p>Chora is the first Python library to model <strong>the human experience of place</strong>. Unlike standard GIS which asks <em>"What is at coordinates X,Y?"</em>, Chora asks <em>"Why does this park feel like Home to Alice, but Danger to Bob?"</em></p>
    <p>Place isn't a polygon—it's an emergent phenomenon arising from <strong>memory, habit, emotion, and social interaction</strong>.</p>
    <div style="margin-top: 1.5rem;">
      <span class="badge">Encounters</span>
      <span class="badge">Familiarity</span>
      <span class="badge">Practices</span>
      <span class="badge">Affect</span>
      <span class="badge">H3 Indexing</span>
      <span class="badge">LLM Integration</span>
    </div>
  </div>

  <div class="bento-card">
    <h3>⚡ Quick Example</h3>
    <div class="code-example">
from chora.core import *<br><br>
# Create a platial graph<br>
graph = PlatialGraph("City")<br>
alice = Agent.individual("Alice")<br>
park = SpatialExtent.from_point(-0.1, 51.5, "Park")<br><br>
# Record an encounter<br>
enc = Encounter(agent_id=alice.id, extent_id=park.id)<br>
graph.add_node(enc)<br><br>
# Derive familiarity over time<br>
update_familiarity(graph, enc)
    </div>
    <a href="getting_started/" style="margin-top: 1rem; display: inline-block;">→ Full tutorial</a>
  </div>

  <div class="bento-card">
    <h3>📚 Guides</h3>
    <ul class="feature-list">
      <li><a href="guides/gps-to-places/">GPS to Places</a> — Process traces into meaningful places</li>
      <li><a href="guides/affective-mapping/">Affective Mapping</a> — Map emotions to locations</li>
      <li><a href="guides/practice-detection/">Detecting Routines</a> — Find habits & patterns</li>
      <li><a href="guides/visualization/">Visualization</a> — D3.js graphs & reports</li>
      <li><a href="guides/h3-indexing/">H3 Indexing</a> — Hexagonal spatial analysis</li>
    </ul>
  </div>

  <div class="bento-card">
    <h3>🔬 Theoretical Foundation</h3>
    <p>Built on rigorous theory from GIScience, cognitive geography, and social physics:</p>
    <ul class="feature-list">
      <li><strong>Relational primacy</strong> — Places defined by relations, not coordinates</li>
      <li><strong>Encounter-centric</strong> — Atomic events as foundation</li>
      <li><strong>Temporal decay</strong> — Memory fades without reinforcement</li>
      <li><strong>Epistemic separation</strong> — Different agents, different places</li>
    </ul>
    <a href="theory/">→ Read the theory</a>
  </div>

  <div class="bento-card">
    <h3>🛠️ CLI Tool</h3>
    <div class="code-example">
# Load GPS data<br>
chora load gpx trace.gpx --agent alice<br><br>
# Derive familiarity<br>
chora derive familiarity --agent alice<br><br>
# Find routines<br>
chora derive practices --agent alice<br><br>
# Visualize<br>
chora viz export --format d3 -o graph.html
    </div>
    <a href="api_reference/">→ CLI reference</a>
  </div>

  <div class="bento-card">
    <h3>🔍 Vibe Search</h3>
    <p>Find places by semantic description using vector embeddings:</p>
    <div class="code-example">
from chora.search import vibe_search<br><br>
results = vibe_search(<br>
    graph,<br>
    "quiet peaceful park for reading"<br>
)<br><br>
# Returns: [(park, 0.87), (garden, 0.72), ...]
    </div>
    <a href="guides/affective-mapping/#step-3-vibe-search-with-embeddings">→ Learn vibe search</a>
  </div>

  <div class="bento-card featured">
    <h3>🗺️ Roadmap</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1.5rem; margin-top: 1rem;">
      <div>
        <strong>v0.5</strong> ✅<br>
        <small>Core, Tests, CI/CD, Docs</small>
      </div>
      <div>
        <strong>v0.9</strong> ✅<br>
        <small>CLI, Notebooks, Visualization</small>
      </div>
      <div>
        <strong>v1.0</strong> ✅<br>
        <small>H3, Embeddings, LLM, Streaming</small>
      </div>
      <div>
        <strong>v2.0</strong> 🚧<br>
        <small>Social Physics, Digital Twins</small>
      </div>
    </div>
  </div>

</div>

---

<p style="text-align: center; margin: 3rem 0; opacity: 0.7;">
  <strong>Built for the Platial Turn</strong><br>
  Open Source • MIT License • <a href="https://github.com/jameswilliamsresearch/chora">GitHub</a>
</p>
