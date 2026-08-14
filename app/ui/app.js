const prose = document.querySelector('#prose');
const analyseButton = document.querySelector('#analyse');
const clearButton = document.querySelector('#clear');
const wordCount = document.querySelector('#word-count');
const inputHint = document.querySelector('#input-hint');
const error = document.querySelector('#error');
const emptyState = document.querySelector('#empty-state');
const resultState = document.querySelector('#result-state');
const score = document.querySelector('#score');
const band = document.querySelector('#band');
const metrics = document.querySelector('#metrics');
const summary = document.querySelector('#summary');
const findingCount = document.querySelector('#finding-count');
const findings = document.querySelector('#findings');
const insights = document.querySelector('#insights');
const capacityCount = document.querySelector('#capacity-count');
const capacityRemaining = document.querySelector('#capacity-remaining');
const capacityProgress = document.querySelector('#capacity-progress');

const MIN_CHARS = 20;
const MAX_WORDS = 8000;

function getWordCount(value) {
  const trimmed = value.trim();
  return trimmed ? trimmed.split(/\s+/).length : 0;
}

function setError(message) {
  error.textContent = message || '';
  error.hidden = !message;
}

function updateEditorState() {
  const value = prose.value;
  const characterCount = value.trim().length;
  const words = getWordCount(value);
  const remaining = Math.max(0, MAX_WORDS - words);
  wordCount.textContent = `${words} ${words === 1 ? 'word' : 'words'}`;
  capacityCount.textContent = `${words.toLocaleString()} / ${MAX_WORDS.toLocaleString()} words`;
  capacityRemaining.textContent = words > MAX_WORDS
    ? `${(words - MAX_WORDS).toLocaleString()} words over limit`
    : `${remaining.toLocaleString()} words remaining`;
  capacityProgress.style.width = `${Math.min(100, (words / MAX_WORDS) * 100)}%`;
  capacityProgress.classList.toggle('over-limit', words > MAX_WORDS);
  analyseButton.disabled = characterCount < MIN_CHARS || words > MAX_WORDS;
  inputHint.textContent = characterCount < MIN_CHARS
    ? `At least ${MIN_CHARS} characters`
    : words > MAX_WORDS
      ? `Please shorten to ${MAX_WORDS.toLocaleString()} words or fewer`
      : 'Ready for local analysis';
}

function showResult(result) {
  emptyState.hidden = true;
  resultState.hidden = false;
  score.textContent = result.score;
  band.textContent = result.band;
  metrics.textContent = `${result.metrics.word_count || getWordCount(prose.value)} words analysed`;
  summary.textContent = result.summary;
  findingCount.textContent = `${result.findings.length} ${result.findings.length === 1 ? 'finding' : 'findings'}`;
  findings.replaceChildren();
  insights.replaceChildren();

  (result.insights || []).forEach((item) => {
    const article = document.createElement('article');
    article.className = `insight insight-${item.tone || 'neutral'}`;
    const label = document.createElement('p');
    label.className = 'insight-label';
    label.textContent = item.label;
    const value = document.createElement('strong');
    value.className = 'insight-value';
    value.textContent = item.value;
    const message = document.createElement('p');
    message.className = 'insight-message';
    message.textContent = item.message;
    article.append(label, value, message);
    insights.append(article);
  });

  if (!result.findings.length) {
    const empty = document.createElement('p');
    empty.className = 'finding-message';
    empty.textContent = 'No scored writing-pattern signals were returned.';
    findings.append(empty);
    return;
  }

  result.findings.forEach((item) => {
    const article = document.createElement('article');
    article.className = 'finding';

    const top = document.createElement('div');
    top.className = 'finding-top';

    const title = document.createElement('p');
    title.className = 'finding-title';
    title.textContent = item.label;

    const severity = document.createElement('span');
    severity.className = `severity severity-${item.severity}`;
    severity.textContent = item.severity;

    const message = document.createElement('p');
    message.className = 'finding-message';
    message.textContent = item.message;

    top.append(title, severity);
    article.append(top, message);
    findings.append(article);
  });
}

async function requestAnalysis(text) {
  if (!(window.__TAURI__ && window.__TAURI__.core)) {
    throw new Error('The desktop analysis bridge is not connected yet.');
  }

  const analysis = window.__TAURI__.core.invoke('analyse_text', { text });
  const timeout = new Promise((_, reject) => {
    window.setTimeout(() => {
      reject(new Error('Local analysis timed out. Please try again.'));
    }, 25000);
  });
  return Promise.race([analysis, timeout]);
}

prose.addEventListener('input', () => {
  setError('');
  updateEditorState();
});

analyseButton.addEventListener('click', async () => {
  setError('');
  analyseButton.disabled = true;
  analyseButton.textContent = 'Reviewing locally...';

  try {
    const result = await requestAnalysis(prose.value);
    showResult(result);
  } catch (cause) {
    setError(cause instanceof Error ? cause.message : 'Local analysis failed.');
  } finally {
    analyseButton.textContent = 'Analyse writing';
    updateEditorState();
  }
});

clearButton.addEventListener('click', () => {
  prose.value = '';
  emptyState.hidden = false;
  resultState.hidden = true;
  findings.replaceChildren();
  insights.replaceChildren();
  setError('');
  updateEditorState();
});

document.querySelectorAll('[data-info]').forEach((button) => {
  button.addEventListener('click', () => {
    const messages = {
      privacy: 'StopSlop performs core analysis locally and does not intentionally send your prose to a server.',
      credits: 'StopSlop builds on Sloptrim by Seyed Ehsan Hadi under Apache License 2.0. The upstream author does not endorse StopSlop.',
      limitations: 'StopSlop reports writing patterns. It does not identify an author, prove AI use, or support high-stakes decisions.',
    };
    setError(messages[button.dataset.info]);
  });
});

updateEditorState();
