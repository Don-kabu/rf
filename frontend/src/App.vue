<script setup>
import { computed, onMounted, ref } from 'vue'
import { diagonalTotal, formatInteger, formatPercent } from './metrics.js'

const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
const areaName = ref('Zone de démonstration')
const nSegments = ref(500)
const nDates = ref(12)
const compactness = ref(10)
const result = ref(null)
const loading = ref(false)
const errorMessage = ref('')
const apiStatus = ref('Connexion…')
const classById = computed(() => Object.fromEntries((result.value?.classes ?? []).map((item) => [item.id, item])))
const isRealResult = computed(() => Boolean(result.value && !result.value.is_simulation))
const totalCorrect = computed(() => result.value ? diagonalTotal(result.value.confusion_matrix) : 0)
const maxFeatureImportance = computed(() => Math.max(0, ...(result.value?.feature_importances ?? []).map((item) => item.importance)))

function colorForClass(classId) {
  return classById.value[classId]?.color ?? '#d8ddd4'
}
function nameForClass(classId) {
  return classById.value[classId]?.name ?? 'Inconnu'
}
function importanceWidth(importance) {
  return maxFeatureImportance.value > 0 ? `${importance * 100 / maxFeatureImportance.value}%` : '0%'
}

async function requestResult(path, options = {}) {
  loading.value = true
  errorMessage.value = ''
  let serverReached = false
  try {
    const response = await fetch(`${apiBase}${path}`, options)
    serverReached = true
    apiStatus.value = 'API connectée'
    if (!response.ok) {
      const details = await response.json().catch(() => null)
      const detail = details?.detail
      const message = Array.isArray(detail) ? detail[0]?.msg : detail
      throw new Error(message || `Le serveur a répondu ${response.status}.`)
    }
    result.value = await response.json()
    apiStatus.value = 'API connectée'
  } catch (error) {
    errorMessage.value = `${error.message}${serverReached ? '' : ' Vérifie que le serveur FastAPI est démarré.'}`
    apiStatus.value = serverReached ? 'API connectée' : 'API indisponible'
  } finally {
    loading.value = false
  }
}

function loadDemo() {
  return requestResult('/api/v1/demo')
}

function loadLatestResult() {
  return requestResult('/api/v1/results/latest')
}

function runSimulation() {
  return requestResult('/api/v1/simulations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      area_name: areaName.value,
      n_segments: Number(nSegments.value),
      n_dates: Number(nDates.value),
      compactness: Number(compactness.value),
    }),
  })
}

onMounted(loadDemo)
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <a class="brand" href="#top" aria-label="AgriSLIC, accueil">
        <span class="brand-mark" aria-hidden="true"><i></i><i></i><i></i><i></i></span>
        <span>agri<span class="brand-light">slic</span></span>
      </a>
      <div class="topbar-meta">
        <span class="project-tag">TP · Reconnaissance des formes</span>
        <span class="connection"><span class="connection-dot" :class="{ offline: apiStatus !== 'API connectée' }"></span>{{ apiStatus }}</span>
      </div>
    </header>

    <main id="top" class="main-content">
      <section class="page-heading">
        <div>
          <p class="eyebrow"><span class="eyebrow-line"></span> TÉLÉDÉTECTION AGRICOLE</p>
          <h1>Classification de parcelles</h1>
          <p class="subtitle">Explore le pipeline SLIC + caractéristiques spectrales + Random Forest.</p>
        </div>
        <div class="heading-badge"><span class="badge-orbit">✳</span><span>Variante B<br><strong>SLIC + RF</strong></span></div>
      </section>

      <section v-if="result?.is_simulation" class="demo-notice" role="status">
        <span class="notice-icon">i</span>
        <div><strong>Mode démonstration — résultats synthétiques</strong><p>{{ result.notice }}</p></div>
        <span class="demo-pill">SIMULATION</span>
      </section>
      <section v-else-if="isRealResult" class="real-result-notice" role="status">
        <span class="notice-icon">✓</span>
        <div><strong>Résultat réel chargé</strong><p>{{ result.notice }}</p></div>
        <span class="real-pill">ÉVALUATION TEST</span>
      </section>

      <section class="method-explainer" aria-labelledby="method-title">
        <div class="method-heading">
          <div>
            <p class="eyebrow"><span class="eyebrow-line"></span> POUR LA SOUTENANCE</p>
            <h2 id="method-title">Du pixel à la classe, en trois étapes</h2>
          </div>
          <span class="method-status">{{ isRealResult ? 'Résultat réel chargé depuis l’API' : 'Méthode expliquée · calculs non exécutés ici' }}</span>
        </div>
        <div class="method-steps">
          <article class="method-step">
            <div class="method-step-top"><span class="step-index">01</span><span class="method-symbol slic-icon">▦</span><span class="method-arrow">→</span></div>
            <h3>SLIC regroupe les pixels</h3>
            <p>Il forme des régions voisines à partir de la proximité dans l’image et de la similarité des couleurs ou bandes spectrales.</p>
            <div class="method-output"><strong>Entrée</strong> pixels multispectraux <span>→</span> <strong>Sortie</strong> identifiant de superpixel</div>
            <small>Un superpixel est une unité d’analyse, pas nécessairement une parcelle entière.</small>
          </article>
          <article class="method-step">
            <div class="method-step-top"><span class="step-index">02</span><span class="method-symbol feature-icon">ƒ</span><span class="method-arrow">→</span></div>
            <h3>On décrit chaque région</h3>
            <p>Les pixels d’un superpixel sont résumés en une ligne de variables ; les dates permettent aussi de décrire l’évolution du couvert.</p>
            <div class="feature-vector"><code>[B2, B3, B4, B8, B11, B12, NDVI, NDMI]</code></div>
            <div class="index-formulas"><span>NDVI = (B8 − B4) / (B8 + B4)</span><span>NDMI = (B8 − B11) / (B8 + B11)</span></div>
          </article>
          <article class="method-step">
            <div class="method-step-top"><span class="step-index">03</span><span class="method-symbol rf-icon">⌘</span></div>
            <h3>Random Forest décide</h3>
            <p>Plusieurs arbres apprennent sur les variables et les classes de référence. Pour un nouveau superpixel, leurs votes déterminent la classe prédite.</p>
            <div class="forest-vote"><span>Arbre 1</span><i></i><span>Arbre 2</span><i></i><span>Arbre 3</span><b>→ vote majoritaire</b></div>
            <small>{{ isRealResult ? 'Les mesures ci-dessous proviennent du résultat réel chargé.' : 'Les métriques affichées plus bas sont simulées ; elles ne proviennent pas de ces étapes.' }}</small>
          </article>
        </div>
      </section>

      <div v-if="errorMessage" class="error-banner" role="alert">
        <span>{{ apiStatus === 'API connectée' ? 'Résultat indisponible' : 'Connexion impossible' }}</span><p>{{ errorMessage }}</p>
        <button class="small-button" @click="loadDemo">Recharger la démo</button>
      </div>

      <section class="workspace-grid">
        <aside class="control-panel card">
          <div class="section-title"><span class="step-index">01</span><div><h2>Paramètres</h2><p>Scénario de démonstration</p></div></div>
          <form class="controls" @submit.prevent="runSimulation">
            <label class="field-label" for="area">Zone d’étude</label>
            <input id="area" v-model="areaName" maxlength="120" required />
            <div class="field-row">
              <div><label class="field-label" for="segments">Superpixels cibles</label><input id="segments" v-model.number="nSegments" type="number" min="10" max="100000" required /></div>
              <div><label class="field-label" for="dates">Dates observées</label><input id="dates" v-model.number="nDates" type="number" min="1" max="60" required /></div>
            </div>
            <label class="field-label" for="compactness">Compacité SLIC <span class="field-value">{{ compactness }}</span></label>
            <input id="compactness" v-model.number="compactness" type="range" min="1" max="30" step="0.5" />
            <div class="range-labels"><span>Contours adaptés</span><span>Formes régulières</span></div>
            <div class="pipeline-mini">
              <p class="field-label">Chaîne illustrée</p>
              <div class="pipeline-step"><span class="pipeline-icon">◈</span><span>Images multispectrales</span><span class="pipeline-check">✓</span></div>
              <div class="pipeline-step"><span class="pipeline-icon slic-icon">▦</span><span>Segmentation SLIC</span><span class="pipeline-check">✓</span></div>
              <div class="pipeline-step"><span class="pipeline-icon rf-icon">⌘</span><span>Random Forest</span><span class="pipeline-check">✓</span></div>
            </div>
            <button class="run-button" type="submit" :disabled="loading">
              <span v-if="loading" class="spinner"></span><span v-else>▶</span>
              {{ loading ? 'Chargement…' : 'Lancer la simulation' }}
            </button>
            <button class="secondary-button" type="button" @click="loadLatestResult" :disabled="loading">
              Charger le dernier résultat réel
            </button>
            <button class="text-button" type="button" @click="loadDemo" :disabled="loading">
              Revenir à la démonstration
            </button>
            <p class="control-footnote">Les champs modifient uniquement la simulation. Le bouton ci-dessus charge le résultat réel fourni par le pipeline.</p>
          </form>
        </aside>

        <section class="results-column" aria-live="polite">
          <div v-if="result" class="metric-grid">
            <article class="metric-card card metric-primary">
              <div class="metric-label">Exactitude globale <span class="metric-mark">↗</span></div>
              <div class="metric-number">{{ formatPercent(result.metrics.accuracy) }}</div>
              <div class="metric-caption">{{ formatInteger(result.metrics.correct) }} bonnes prédictions sur {{ formatInteger(result.metrics.samples) }}</div>
              <div class="metric-track"><span :style="{ width: `${result.metrics.accuracy * 100}%` }"></span></div>
            </article>
            <article class="metric-card card">
              <div class="metric-label">F1 macro <span class="metric-mark green">◎</span></div>
              <div class="metric-number">{{ formatPercent(result.metrics.macro_f1) }}</div>
              <div class="metric-caption">Moyenne équilibrée entre les classes</div>
              <div class="metric-track green-track"><span :style="{ width: `${result.metrics.macro_f1 * 100}%` }"></span></div>
            </article>
            <article class="metric-card card metric-samples">
              <div class="metric-label">Échantillons testés <span class="metric-mark amber">◷</span></div>
              <div class="metric-number">{{ formatInteger(result.metrics.samples) }}</div>
              <div class="metric-caption">{{ result.classes.length }} classes présentées</div>
              <div class="sample-dots"><i v-for="item in result.classes" :key="item.id" :style="{ background: item.color }"></i></div>
            </article>
          </div>

          <div v-if="result" class="visual-grid">
            <article class="card map-card">
              <div class="card-heading">
                <div class="section-title compact"><span class="step-index">02</span><div><h2>Carte de classification</h2><p>{{ isRealResult ? 'Aperçu catégoriel sans géoréférencement' : 'Grille synthétique, sans coordonnées géographiques' }}</p></div></div>
                <span class="map-caption">{{ result.configuration.area_name }}</span>
              </div>
              <div class="map-frame" role="img" :aria-label="isRealResult ? 'Aperçu de la classification réelle sans coordonnées géographiques' : 'Carte de démonstration composée de superpixels synthétiques'">
                <div class="map-grid" :style="{ '--grid-columns': result.map_grid[0]?.length ?? 1 }">
                  <template v-for="(row, rowIndex) in result.map_grid" :key="rowIndex">
                    <span v-for="(cell, cellIndex) in row" :key="`${rowIndex}-${cellIndex}`" class="map-cell" :style="{ backgroundColor: colorForClass(cell) }" :title="nameForClass(cell)"></span>
                  </template>
                </div>
                <div class="map-north" aria-hidden="true">N<br>↑</div>
                <div class="map-scale" aria-hidden="true"><span></span>{{ isRealResult ? 'aperçu' : 'illustration' }}</div>
              </div>
              <div class="legend"><span v-for="item in result.classes" :key="item.id"><i :style="{ background: item.color }"></i>{{ item.name }}</span></div>
            </article>

            <article class="card confusion-card">
              <div class="section-title compact"><span class="step-index">03</span><div><h2>Matrice de confusion</h2><p>Lignes : réel · colonnes : prédit</p></div></div>
              <div class="matrix-wrap">
                <table class="confusion-table">
                  <thead><tr><th aria-label="Classe réelle / prédite">Réel ↓<br>Prédit →</th><th v-for="item in result.classes" :key="item.id" :title="item.name"><span class="matrix-header" :style="{ background: item.color }"></span>{{ item.name }}</th></tr></thead>
                  <tbody><tr v-for="(row, rowIndex) in result.confusion_matrix" :key="rowIndex"><th><span class="matrix-header" :style="{ background: result.classes[rowIndex]?.color }"></span>{{ result.classes[rowIndex]?.name }}</th><td v-for="(value, colIndex) in row" :key="colIndex" :class="{ diagonal: rowIndex === colIndex }">{{ value }}</td></tr></tbody>
                </table>
              </div>
              <div class="matrix-summary"><span><i class="diagonal-key"></i> Prédictions correctes</span><strong>{{ totalCorrect }} / {{ result.metrics.samples }}</strong></div>
            </article>
          </div>

          <div v-if="result" class="detail-grid">
            <article class="card class-card">
              <div class="section-title compact"><span class="step-index">04</span><div><h2>Résultats par classe</h2><p>Précision · rappel · F1-score</p></div></div>
              <div class="class-list">
                <div v-for="item in result.class_metrics" :key="item.class_id" class="class-row">
                  <div class="class-name"><i :style="{ background: classById[item.class_id]?.color }"></i><span>{{ item.class_name }}</span></div>
                  <div class="class-score"><span>{{ formatPercent(item.precision) }}<small>Précision</small></span><span>{{ formatPercent(item.recall) }}<small>Rappel</small></span><span class="f1-value">{{ formatPercent(item.f1) }}<small>F1</small></span></div>
                  <div class="class-track"><span :style="{ width: `${item.f1 * 100}%`, background: classById[item.class_id]?.color }"></span></div>
                </div>
              </div>
            </article>

            <article class="card importance-card">
              <div class="section-title compact"><span class="step-index">05</span><div><h2>Importance des variables</h2><p>{{ isRealResult ? 'Valeurs du modèle chargé' : 'Importances fictives, non apprises' }}</p></div></div>
              <div class="importance-list">
                <div v-for="item in result.feature_importances" :key="item.feature" class="importance-row">
                  <span>{{ item.feature }}</span><div class="importance-track"><i :style="{ width: importanceWidth(item.importance) }"></i></div><strong>{{ formatPercent(item.importance) }}</strong>
                </div>
              </div>
              <p class="importance-note">{{ isRealResult ? 'Importance issue du modèle entraîné ; elle indique une contribution au modèle, pas une causalité.' : 'Dans le vrai pipeline, ces importances seront calculées sur le modèle entraîné et interprétées avec prudence.' }}</p>
            </article>
          </div>

          <div v-else-if="loading" class="loading-card card"><span class="spinner"></span> Récupération de la démonstration…</div>
        </section>
      </section>

      <section class="method-note">
        <div class="method-icon">✳</div><p><strong>À retenir pour la soutenance</strong><br>Un superpixel est une région homogène de l’image, pas nécessairement une parcelle complète. Une évaluation crédible devra séparer les données par parcelle ou bloc spatial.</p>
        <a href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer">Voir l’API <span>↗</span></a>
      </section>
      <footer class="footer"><span>AgriSLIC <b>·</b> prototype pédagogique</span><span>Vue.js + FastAPI <b>·</b> {{ isRealResult ? 'résultat réel chargé' : 'résultats simulés' }}</span></footer>
    </main>
  </div>
</template>
