#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join, relative, resolve } from 'node:path';
import { execFileSync } from 'node:child_process';

export const EXPECTED_PAGES = [
  'index',
  'quickstart',
  'workflows',
  'concepts/how-stet-works',
  'concepts/trial-result',
  'prompts',
  'troubleshooting',
];

export const PROTECTED_FALLBACKS = [
  'ONBOARDING.md',
];

// These public collateral files may evolve, but each must retain the small
// set of phrases that makes it an honest entry point. ONBOARDING.md remains a
// legacy byte-protected file and is intentionally excluded from this map.
export const PUBLIC_COLLATERAL_REQUIREMENTS = {
  'README.md': [
    '# Improve the instructions, skills, and model settings your coding agents actually use',
    '## Example Trial Result',
    'Historical April 2026 model comparison across 28 paired Zod tasks',
    '## Install and get a first result',
    'stet --version',
  ],
  'BETA_QUICKSTART.md': [
    '## What you will accomplish',
    'narrowest credible bounded',
    'pass it explicitly with `--test`',
    'stop before the dataset build',
  ],
  'PROMPT_COOKBOOK.md': [
    '# Prompt cookbook',
    'narrowest credible verifier',
    'pass it explicitly with `--test`',
    'stop before model smoke, probe, or rules evals',
  ],
  'TROUBLESHOOTING.md': [
    '# Troubleshooting',
    '## Fast setup checks',
    'refresh it with the official installer',
    'The installer refreshes the CLI only',
  ],
};

const EXPECTED_DOCS_REVIEW = {
  content_base_commit: 'ce0aef110469d8d7dab37566cef99d8a7dee67e1',
  reviewed_at: '2026-07-14',
};

const EXPECTED_RECEIPT = {
  schema_version: 'stet.receipt/v1',
  source_commit: 'e1980547',
  report_sha256: '88ca838e3098ae99043bb7d71454e608490938e05f17116352a929a4c2f8bf74',
  historical: true,
  historical_period: 'April 2026',
  corpus: { name: 'Zod', task_count: 28, paired: true, invalid_task_count: 0 },
  baseline: { model: 'Opus 4.6', reasoning: 'high' },
  candidate: { model: 'Opus 4.7', reasoning: 'high' },
  decision: { recommendation: 'PROMOTE', candidate: 'Opus 4.7', confidence: 'high' },
  metrics: [
    { name: 'Test pass rate', baseline: '42.9%', candidate: '42.9%' },
    { name: 'Equivalence rate', baseline: '32.1%', candidate: '46.4%' },
    { name: 'Observed cost per task', baseline: '$19.96', candidate: '$8.11' },
    { name: 'Mean agent duration', baseline: '7m 58s', candidate: '3m 12s' },
  ],
  caveats: [
    'Historical April 2026 result, scoped to this 28-task Zod corpus and recorded harness.',
    "The legacy report predates Stet's current calibration and claim-readiness fields.",
    'The displayed metric values are observations, not generalized or uncertainty-calibrated improvement claims.',
    'The receipt also used declared grader evidence not reproduced here.',
  ],
  publication_approved_at: '2026-07-14',
  publication_approved_by: 'benredmond',
};

const EXPECTED_ASSETS = {
  'stet-mark.svg': '7eafbc923028aac5ee21c9599d10684b8841a592f74fd1e1951c483d3ddb3960',
  'stet-loop.svg': 'd4150cdb7920eeceff3443373bab51f65b2265ed791e5c4d8fa0674cde6e2e55',
};

const EXPECTED_COLORS = {
  primary: '#df3328',
  light: '#e8352a',
  dark: '#df3328',
};

const EXPECTED_NODE_ENGINE = '>=18 <25';
const EXPECTED_MINT_VERSION = '4.2.687';

const OFFICIAL_INSTALLER_URLS = {
  unix: 'https://raw.githubusercontent.com/Stet-AI/stet-cli/main/install.sh',
  windows: 'https://raw.githubusercontent.com/Stet-AI/stet-cli/main/install.ps1',
};

const PUBLIC_CLI_SEMVER = /(?:^|[^\w])v?\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?=$|[^\w])/g;
const PROMPT_OPENING_FENCE = /^```text(?:[ \t]+([^\r\n]*))?[ \t]*$/gm;
const PROMPT_FENCE = /^```text(?:[ \t]+[^\r\n]*)?[ \t]*\r?\n([\s\S]*?)\r?\n^```[ \t]*$/gm;
const PROMPT_PAGES = new Set(['quickstart', 'workflows', 'prompts', 'troubleshooting']);

const QUESTIONS = [
  ['Is my AGENTS.md change helping?', 'agents-md-ab'],
  ['Improve my AGENTS.md', 'iterative-instruction-improvement'],
  ['Is this skill helping?', 'skill-evaluation'],
  ['Which model or reasoning effort should I use?', 'model-reasoning-comparison'],
];

const PAGE_REQUIREMENTS = {
  'index': ['task corpus', 'Trial Result', 'baseline', 'candidate'],
  'quickstart': ['Install the CLI', 'onboard one repository', 'onboarding receipt'],
  'workflows': ['recommended prompt', 'Evidence expectation'],
  'concepts/how-stet-works': ['task corpus', 'replay', 'baseline', 'candidate', 'tests', 'graders', 'evaluator'],
  'concepts/trial-result': ['recommendation', 'confidence', 'evidence quality', 'validity', 'task', 'grader', 'uncertainty', 'next action', 'promote', 'hold', 'inspect'],
  'prompts': ['copy-paste', 'workflow', 'evidence'],
  'troubleshooting': ['Setup', 'authentication', 'Docker', 'stalled', 'replay', 'grader', 'inspect'],
};

const EXPECTED_PAGE_METADATA = {
  index: { title: 'Change control for AI coding agents', sidebarTitle: 'Overview' },
  quickstart: { title: 'Quickstart', sidebarTitle: 'Quickstart' },
  workflows: { title: 'Choose a workflow', sidebarTitle: 'Choose a workflow' },
  'concepts/how-stet-works': { title: 'How Stet works', sidebarTitle: 'How Stet works' },
  'concepts/trial-result': { title: 'Read a Trial Result', sidebarTitle: 'Read a Trial Result' },
  prompts: { title: 'Prompt cookbook', sidebarTitle: 'Prompt cookbook' },
  troubleshooting: { title: 'Troubleshooting', sidebarTitle: 'Troubleshooting' },
};

const FORBIDDEN_PATHS = [
  /\/Users\//,
  /\/home\//,
  /(?:^|[^\w])apex\//,
  /distribution\/stet-dist\//,
  /\.stet\/(?:archive|report)(?:\/|\b)/,
];

const SECRET_PATTERNS = [
  /\bsk-ant-[A-Za-z0-9_-]+/,
  /\bsk-proj-[A-Za-z0-9_-]+/,
  /\bghp_[A-Za-z0-9]+/,
  /\bgithub_pat_[A-Za-z0-9_]+/,
  /\bxox[bp]-[A-Za-z0-9-]+/,
  /\bAKIA[0-9A-Z]{12,}/,
  /\b(?:[A-Z][A-Z0-9_]*(?:TOKEN|SECRET|API_KEY|PRIVATE_KEY)|(?:api[_-]?key|token|secret))\s*[:=]\s*["']?[^\s"']+/i,
];

const UNSUPPORTED_CLAIMS = [
  /post-training layer/i,
  /enterprise learning system/i,
  /continuous production capture/i,
  /recursive self-improvement/i,
  /automatic production transfer/i,
  /cross-domain support/i,
  /universal model ranking/i,
  /generalized improvement/i,
  /percentage savings/i,
  /--target-ready(?:\b|=)/i,
  /\bautomatic(?:ally)?(?:[-\s]+(?:run|runs|launch|launches|start|starts|execute|executes))?[-\s]+(?:(?:a|the|one)[-\s]+)?canary\b/i,
  /\bcanary(?:[-\s]+(?:is[-\s]+)?(?:run|runs|launched|started|executed))?[-\s]+automatic(?:ally)?\b/i,
  /\bcanary[-\s]+controller\b/i,
  /\bcanary[-\s]+before[-\s]+fan[-\s]?out\b/i,
];

const APPROVED_NEGATIONS = [
  'not a current or universal model ranking',
  'not a universal model ranking',
  'not generalized or uncertainty-calibrated improvement claims',
];

// Dependency and generated trees are not public source pages. Hidden files and
// directories outside this explicit set remain visible so accidental pages fail.
const IGNORED_SOURCE_DIRECTORIES = new Set([
  '.git',
  '.cache',
  '.mintlify',
  '.next',
  'build',
  'cache',
  'dist',
  'node_modules',
  'out',
]);

function readJson(path) {
  return JSON.parse(readFileSync(path, 'utf8'));
}

function deepEqual(a, b) {
  if (Object.is(a, b)) return true;
  if (Array.isArray(a) || Array.isArray(b)) {
    return Array.isArray(a) && Array.isArray(b) && a.length === b.length && a.every((value, index) => deepEqual(value, b[index]));
  }
  if (a && b && typeof a === 'object' && typeof b === 'object') {
    const aKeys = Object.keys(a).sort();
    const bKeys = Object.keys(b).sort();
    return deepEqual(aKeys, bKeys) && aKeys.every((key) => deepEqual(a[key], b[key]));
  }
  return false;
}

function walkFiles(dir) {
  const files = [];
  if (!existsSync(dir)) return files;
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory() && !IGNORED_SOURCE_DIRECTORIES.has(entry.name)) files.push(...walkFiles(path));
    else files.push(path);
  }
  return files;
}

function walkAllFiles(dir) {
  const files = [];
  if (!existsSync(dir)) return files;
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) files.push(...walkAllFiles(path));
    else files.push(path);
  }
  return files;
}

function findPagePath(rootDir, page) {
  for (const extension of ['.mdx', '.md']) {
    const path = join(rootDir, `${page}${extension}`);
    if (existsSync(path)) return path;
  }
  return null;
}

function parseFrontmatter(text) {
  if (!text.startsWith('---\n')) return null;
  const end = text.indexOf('\n---', 4);
  if (end < 0) return null;
  const metadata = {};
  for (const line of text.slice(4, end).split('\n')) {
    const match = /^(title|sidebarTitle):\s*(.*)$/.exec(line);
    if (match) metadata[match[1]] = match[2].trim();
  }
  return metadata;
}

function git(rootDir, args) {
  return execFileSync('git', ['-C', rootDir, ...args], { encoding: 'utf8' }).trim();
}

function defaultExistsCommit(rootDir, sha) {
  try {
    git(rootDir, ['cat-file', '-e', `${sha}^{commit}`]);
    return true;
  } catch {
    return false;
  }
}

function defaultIsAncestor(rootDir, base, head) {
  try {
    git(rootDir, ['merge-base', '--is-ancestor', base, head]);
    return true;
  } catch {
    return false;
  }
}

function defaultChangedFiles(rootDir, base, head) {
  return git(rootDir, ['diff', '--name-only', '--no-renames', base, head]).split('\n').filter(Boolean);
}

function addError(errors, message) {
  errors.push(message);
}

function isValidApprovalDate(value) {
  if (typeof value !== 'string') return false;
  const dateOnly = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  if (dateOnly) {
    const date = new Date(Date.UTC(Number(dateOnly[1]), Number(dateOnly[2]) - 1, Number(dateOnly[3])));
    return date.getUTCFullYear() === Number(dateOnly[1]) && date.getUTCMonth() === Number(dateOnly[2]) - 1 && date.getUTCDate() === Number(dateOnly[3]);
  }
  return /^\d{4}-\d{2}-\d{2}T\S+$/.test(value) && !Number.isNaN(Date.parse(value));
}

function validateConfig(rootDir, errors) {
  const path = join(rootDir, 'docs.json');
  if (!existsSync(path)) return addError(errors, 'missing docs/docs.json');
  const config = readJson(path);
  const allowed = ['$schema', 'name', 'description', 'theme', 'colors', 'appearance', 'logo', 'favicon', 'navigation'];
  for (const key of Object.keys(config)) if (!allowed.includes(key)) addError(errors, `docs.json has forbidden key: ${key}`);
  if (config.$schema !== 'https://mintlify.com/docs.json') addError(errors, 'docs.json $schema is incorrect');
  if (config.name !== 'Stet') addError(errors, 'docs.json name must be Stet');
  if (config.description !== 'Change control for AI coding agents.') addError(errors, 'docs.json description is incorrect');
  if (config.theme !== 'willow') addError(errors, 'docs.json theme must be willow');
  if (!deepEqual(config.colors, EXPECTED_COLORS)) addError(errors, 'docs.json colors must be exactly primary #df3328, light #e8352a, dark #df3328');
  if (!deepEqual(config.appearance, { default: 'dark', strict: false })) addError(errors, 'docs.json appearance must be exactly default dark and strict false');
  if (!config.logo || !deepEqual(Object.keys(config.logo).sort(), ['dark', 'light']) || config.logo.light !== '/assets/stet-mark.svg' || config.logo.dark !== '/assets/stet-mark.svg') addError(errors, 'docs.json logo must use the approved local mark');
  if (config.favicon !== '/assets/stet-mark.svg') addError(errors, 'docs.json favicon must use the approved local mark');
  if (!config.navigation || !deepEqual(Object.keys(config.navigation).sort(), ['groups']) || !Array.isArray(config.navigation.groups) || config.navigation.groups.length !== 1) addError(errors, 'docs.json navigation must contain exactly one group');
  const pages = config.navigation?.groups?.[0]?.pages;
  if (config.navigation?.groups?.[0]?.group !== 'Stet') addError(errors, 'docs.json navigation group must be Stet');
  if (config.navigation?.groups?.[0] && Object.keys(config.navigation.groups[0]).some((k) => !['group', 'pages'].includes(k))) addError(errors, 'docs.json group has forbidden keys');
  if (!deepEqual(pages, EXPECTED_PAGES)) addError(errors, 'docs.json navigation pages must match the seven-page contract in order');
}

function validatePackageAndInstall(rootDir, errors) {
  const packagePath = join(rootDir, 'package.json');
  const lockPath = join(rootDir, 'package-lock.json');
  if (!existsSync(packagePath) || !existsSync(lockPath)) {
    addError(errors, 'docs package.json and package-lock.json are required');
    return;
  }
  let packageJson;
  let lockJson;
  try {
    packageJson = readJson(packagePath);
    lockJson = readJson(lockPath);
  } catch {
    addError(errors, 'docs package metadata must be valid JSON');
    return;
  }
  if (packageJson.engines?.node !== EXPECTED_NODE_ENGINE) addError(errors, `package.json engines.node must be ${EXPECTED_NODE_ENGINE}`);
  if (packageJson.devDependencies?.mint !== EXPECTED_MINT_VERSION) addError(errors, `package.json devDependency mint must be ${EXPECTED_MINT_VERSION}`);
  const lockRoot = lockJson.packages?.[''];
  if (!lockRoot || lockRoot.engines?.node !== EXPECTED_NODE_ENGINE || lockRoot.devDependencies?.mint !== EXPECTED_MINT_VERSION) addError(errors, 'package-lock.json root metadata must match the pinned package contract');

  const quickstartPath = findPagePath(rootDir, 'quickstart');
  const quickstart = quickstartPath ? readFileSync(quickstartPath, 'utf8') : '';
  if (!quickstart.includes(OFFICIAL_INSTALLER_URLS.unix)) addError(errors, 'quickstart must use the official Unix installer URL');
  if (!quickstart.includes(OFFICIAL_INSTALLER_URLS.windows)) addError(errors, 'quickstart must use the official Windows installer URL');
  const installerPages = EXPECTED_PAGES.map((name) => findPagePath(rootDir, name)).filter(Boolean);
  for (const page of installerPages) {
    const text = readFileSync(page, 'utf8');
    for (const line of text.split('\n')) {
      if (/install\.(?:sh|ps1)/i.test(line) && /(?:--version|-Version)\b/i.test(line)) {
        addError(errors, `${relative(rootDir, page)} must not pass a version argument to the installer`);
      }
    }
  }
  for (const page of EXPECTED_PAGES.map((name) => findPagePath(rootDir, name)).filter(Boolean)) {
    if (/\bstet\s+update\b/i.test(readFileSync(page, 'utf8'))) addError(errors, `${relative(rootDir, page)} must not advertise generic stet update`);
  }
}

function validatePages(rootDir, errors) {
  const allowed = new Set(EXPECTED_PAGES);
  const docsFiles = walkFiles(rootDir).filter((p) => /\.(?:md|mdx)$/i.test(p));
  const seen = new Map();
  for (const path of docsFiles) {
    const rel = relative(rootDir, path).replaceAll('\\', '/');
    const page = rel.replace(/\.(?:md|mdx)$/i, '');
    if (!allowed.has(page)) addError(errors, `unexpected docs page: ${rel}`);
    else seen.set(page, (seen.get(page) || 0) + 1);
  }
  for (const page of allowed) {
    if (!findPagePath(rootDir, page)) addError(errors, `missing docs page: ${page}.mdx`);
    else if (seen.get(page) > 1) addError(errors, `duplicate docs page variants: ${page}`);
  }
  const contents = new Map();
  for (const page of allowed) {
    const path = findPagePath(rootDir, page);
    if (path) contents.set(page, readFileSync(path, 'utf8'));
  }
  for (const [page, terms] of Object.entries(PAGE_REQUIREMENTS)) {
    const text = contents.get(page) || '';
    const metadata = parseFrontmatter(text);
    if (!metadata || metadata.title !== EXPECTED_PAGE_METADATA[page].title || metadata.sidebarTitle !== EXPECTED_PAGE_METADATA[page].sidebarTitle) addError(errors, `${page} frontmatter title/sidebarTitle must match the page contract`);
    if (/^#\s+/m.test(text.slice(text.indexOf('\n---', 4) + 4))) addError(errors, `${page} must not contain a Markdown H1; use frontmatter title`);
    for (const term of terms) if (!text.toLowerCase().includes(term.toLowerCase())) addError(errors, `${page} is missing required term: ${term}`);
  }
  const overview = contents.get('index') || '';
  for (const [question, anchor] of QUESTIONS) {
    if (!overview.includes(question)) addError(errors, `index.mdx is missing workflow question: ${question}`);
    if (!overview.includes(`#${anchor}`)) addError(errors, `index.mdx is missing workflow link anchor: ${anchor}`);
    const workflows = contents.get('workflows') || '';
    if (!workflows.includes(question)) addError(errors, `workflows.mdx is missing workflow question: ${question}`);
    if (!workflows.includes(`id="${anchor}"`)) addError(errors, `workflows.mdx is missing anchor: ${anchor}`);
  }
}

function extractReceipt(text) {
  const start = text.indexOf('<!-- stet-receipt:start -->');
  const end = text.indexOf('<!-- stet-receipt:end -->');
  if (start < 0 || end < 0 || end <= start) throw new Error('index.mdx must contain one stet receipt source block');
  if (text.indexOf('<!-- stet-receipt:start -->', start + 1) >= 0 || text.indexOf('<!-- stet-receipt:end -->', end + 1) >= 0) throw new Error('index.mdx must contain exactly one stet receipt source block');
  const block = text.slice(start, end);
  const fenced = block.match(/```json\s*([\s\S]*?)\s*```/);
  if (!fenced) throw new Error('stet receipt block must contain a fenced JSON object');
  return JSON.parse(fenced[1]);
}

function validateReceipt(rootDir, errors) {
  const fixturePath = join(rootDir, 'receipt-review.json');
  const indexPath = findPagePath(rootDir, 'index');
  if (!existsSync(fixturePath) || !existsSync(indexPath)) return addError(errors, 'receipt fixture or index page is missing');
  let fixture;
  try { fixture = readJson(fixturePath); } catch { return addError(errors, 'receipt-review.json is not valid JSON'); }
  if (!deepEqual(fixture, EXPECTED_RECEIPT)) addError(errors, 'receipt-review.json must match the approved receipt values');
  if (fixture.publication_approved_at != null && !isValidApprovalDate(fixture.publication_approved_at)) addError(errors, 'receipt publication_approved_at must be a YYYY-MM-DD date or ISO timestamp');
  if (fixture.publication_approved_by != null && (typeof fixture.publication_approved_by !== 'string' || !fixture.publication_approved_by.trim())) addError(errors, 'receipt publication_approved_by must be nonempty when present');
  let rendered;
  try { rendered = extractReceipt(readFileSync(indexPath, 'utf8')); } catch (error) { return addError(errors, error.message); }
  if (!deepEqual(rendered, fixture)) addError(errors, 'rendered receipt JSON must exactly equal receipt-review.json');
  const prose = readFileSync(indexPath, 'utf8').replace(/<!-- stet-receipt:start -->[\s\S]*?<!-- stet-receipt:end -->/, '');
  for (const caveat of fixture.caveats || []) if (!prose.includes(caveat)) addError(errors, `index.mdx is missing readable caveat: ${caveat}`);
}

function validateDocsReview(rootDir, errors, options) {
  const path = join(rootDir, 'docs-review.json');
  if (!existsSync(path)) return addError(errors, 'missing docs-review.json');
  let review;
  try { review = readJson(path); } catch { return addError(errors, 'docs-review.json is not valid JSON'); }
  if (!deepEqual(review, EXPECTED_DOCS_REVIEW)) addError(errors, 'docs-review.json must exactly match the reviewed content values');
  const existsCommit = options.existsCommit || ((sha) => defaultExistsCommit(rootDir, sha));
  if (!existsCommit(EXPECTED_DOCS_REVIEW.content_base_commit)) addError(errors, `required commit does not exist: ${EXPECTED_DOCS_REVIEW.content_base_commit}`);
  if (options.expectedBaseSha && review.content_base_commit !== options.expectedBaseSha) addError(errors, `content_base_commit ${review.content_base_commit} does not equal expected base ${options.expectedBaseSha}`);
  if (options.headSha) {
    const isAncestor = options.isAncestor || ((base, head) => defaultIsAncestor(rootDir, base, head));
    if (!isAncestor(review.content_base_commit, options.headSha)) addError(errors, `content_base_commit ${review.content_base_commit} is not an ancestor of ${options.headSha}`);
  }
}

function validateAssets(rootDir, errors) {
  const assetsDir = join(rootDir, 'assets');
  const assets = existsSync(assetsDir) ? walkAllFiles(assetsDir).map((p) => relative(assetsDir, p).replaceAll('\\', '/')) : [];
  if (!deepEqual([...assets].sort(), Object.keys(EXPECTED_ASSETS).sort())) addError(errors, `docs/assets must contain exactly ${Object.keys(EXPECTED_ASSETS).join(' and ')}`);
  for (const [name, expected] of Object.entries(EXPECTED_ASSETS)) {
    const path = join(assetsDir, name);
    if (!existsSync(path)) continue;
    const digest = createHash('sha256').update(readFileSync(path)).digest('hex');
    if (digest !== expected) addError(errors, `${name} has SHA256 ${digest}, expected ${expected}`);
  }
}

function validateUnsupportedClaims(text, rel, errors) {
  let safeText = text;
  for (const phrase of APPROVED_NEGATIONS) safeText = safeText.replaceAll(phrase, '');
  for (const pattern of UNSUPPORTED_CLAIMS) {
    if (pattern.test(safeText)) addError(errors, `${rel} contains unsupported claim: ${pattern}`);
  }
}

function validatePublicText(rootDir, errors) {
  const pages = EXPECTED_PAGES.map((page) => findPagePath(rootDir, page)).filter(Boolean);
  for (const path of pages) {
    const rel = relative(rootDir, path).replaceAll('\\', '/');
    const text = readFileSync(path, 'utf8');
    for (const pattern of FORBIDDEN_PATHS) if (pattern.test(text)) addError(errors, `${rel} contains forbidden private path pattern: ${pattern}`);
    for (const pattern of SECRET_PATTERNS) if (pattern.test(text)) addError(errors, `${rel} contains a secret assignment or token prefix`);
    validateUnsupportedClaims(text, rel, errors);
    PUBLIC_CLI_SEMVER.lastIndex = 0;
    if (PUBLIC_CLI_SEMVER.test(text)) addError(errors, `${rel} contains a hard-coded Stet CLI semver token`);
    if (PROMPT_PAGES.has(rel.replace(/\.(?:md|mdx)$/i, ''))) validatePromptFences(text, rel, errors);
  }
  for (const rel of ['docs.json', 'docs-review.json']) {
    const path = join(rootDir, rel);
    if (!existsSync(path)) continue;
    const text = readFileSync(path, 'utf8');
    PUBLIC_CLI_SEMVER.lastIndex = 0;
    if (PUBLIC_CLI_SEMVER.test(text)) addError(errors, `${rel} contains a hard-coded Stet CLI semver token`);
  }
}

function validatePromptFences(text, rel, errors) {
  const openings = [...text.matchAll(PROMPT_OPENING_FENCE)];
  PROMPT_OPENING_FENCE.lastIndex = 0;
  for (const opening of openings) {
    const metadata = opening[1]?.trim() || '';
    const tokens = metadata.split(/[ \t]+/).filter(Boolean);
    if (!tokens.includes('wrap')) addError(errors, `${rel} prompt fence must enable wrapping with the exact wrap token`);
  }
  let matchedFenceCount = 0;
  let match;
  while ((match = PROMPT_FENCE.exec(text))) {
    matchedFenceCount += 1;
    const lines = match[1].split(/\r?\n/);
    const nonempty = lines.filter((line) => line.trim().length > 0);
    if (nonempty.length < 2) addError(errors, `${rel} prompt fence must contain at least two nonempty lines`);
    if (lines.some((line) => line.length > 100)) addError(errors, `${rel} prompt fence contains a line longer than 100 characters`);
  }
  PROMPT_FENCE.lastIndex = 0;
  if (matchedFenceCount !== openings.length) addError(errors, `${rel} contains an unclosed text prompt fence`);
}

function validateChangedFallbacks(rootDir, errors, options) {
  if (!options.baseSha && !options.headSha) return;
  if (!options.baseSha || !options.headSha || /^0+$/.test(options.baseSha) || /^0+$/.test(options.headSha)) return addError(errors, 'changed-file comparison requires non-zero --base-sha and --head-sha');
  const existsCommit = options.existsCommit || ((sha) => defaultExistsCommit(rootDir, sha));
  if (!existsCommit(options.baseSha)) addError(errors, `comparison base commit does not exist: ${options.baseSha}`);
  if (!existsCommit(options.headSha)) addError(errors, `comparison head commit does not exist: ${options.headSha}`);
  if (!existsCommit(options.baseSha) || !existsCommit(options.headSha)) return;
  const changedFiles = options.changedFiles || defaultChangedFiles(rootDir, options.baseSha, options.headSha);
  const changedLegacy = changedFiles.filter((file) => file === 'ONBOARDING.md');
  if (changedLegacy.length) addError(errors, `protected fallback files changed: ${changedLegacy.join(', ')}`);
  const changedCollateral = changedFiles.filter((file) => Object.hasOwn(PUBLIC_COLLATERAL_REQUIREMENTS, file));
  for (const file of changedCollateral) {
    // The validator normally receives docs/ as root while these collateral
    // files live one level above it; support both layouts for isolated tests.
    const path = existsSync(join(rootDir, file)) ? join(rootDir, file) : join(resolve(rootDir, '..'), file);
    if (!existsSync(path)) {
      addError(errors, `${file} is missing after the public collateral change`);
      continue;
    }
    const text = readFileSync(path, 'utf8');
    for (const phrase of PUBLIC_COLLATERAL_REQUIREMENTS[file]) {
      if (!text.includes(phrase)) addError(errors, `${file} is missing required public content: ${phrase}`);
    }
    validateUnsupportedClaims(text, file, errors);
    PUBLIC_CLI_SEMVER.lastIndex = 0;
    if (PUBLIC_CLI_SEMVER.test(text)) addError(errors, `${file} contains a hard-coded Stet CLI semver token`);
  }
}

export function validateContentContract({ rootDir = resolve(new URL('.', import.meta.url).pathname, '..'), mode = 'contract', ...options } = {}) {
  const errors = [];
  validateConfig(rootDir, errors);
  validatePackageAndInstall(rootDir, errors);
  validatePages(rootDir, errors);
  validateReceipt(rootDir, errors);
  validateDocsReview(rootDir, errors, options);
  validateAssets(rootDir, errors);
  validatePublicText(rootDir, errors);
  validateChangedFallbacks(rootDir, errors, options);
  if (mode === 'publication') {
    let receipt = {};
    try { if (existsSync(join(rootDir, 'receipt-review.json'))) receipt = readJson(join(rootDir, 'receipt-review.json')); } catch { /* validateReceipt reports malformed JSON */ }
    if (receipt.publication_approved_at == null) addError(errors, 'publication_approved_at must be non-null in publication mode');
    if (typeof receipt.publication_approved_by !== 'string' || !receipt.publication_approved_by.trim()) addError(errors, 'publication_approved_by must be non-null and nonempty in publication mode');
    if (receipt.publication_approved_at != null && !isValidApprovalDate(receipt.publication_approved_at)) addError(errors, 'publication_approved_at must be a YYYY-MM-DD date or ISO timestamp');
  }
  return { ok: errors.length === 0, errors };
}

function parseArgs(argv) {
  const [mode = 'contract', ...rest] = argv;
  if (!['contract', 'publication'].includes(mode)) throw new Error(`mode must be contract or publication, got ${mode}`);
  const options = { mode };
  for (let i = 0; i < rest.length; i += 1) {
    const arg = rest[i];
    if (['--base-sha', '--head-sha', '--expected-base-sha', '--root-dir'].includes(arg) && i + 1 >= rest.length) throw new Error(`${arg} requires a value`);
    if (arg === '--base-sha') options.baseSha = rest[++i];
    else if (arg === '--head-sha') options.headSha = rest[++i];
    else if (arg === '--expected-base-sha') options.expectedBaseSha = rest[++i];
    else if (arg === '--root-dir') options.rootDir = resolve(rest[++i]);
    else throw new Error(`unknown argument: ${arg}`);
  }
  return options;
}

if (process.argv[1] && resolve(process.argv[1]) === resolve(new URL(import.meta.url).pathname)) {
  try {
    const result = validateContentContract(parseArgs(process.argv.slice(2)));
    if (result.ok) console.log(`content ${parseArgs(process.argv.slice(2)).mode} contract: PASS`);
    else {
      for (const error of result.errors) console.error(`ERROR: ${error}`);
      process.exitCode = 1;
    }
  } catch (error) {
    console.error(`ERROR: ${error.message}`);
    process.exitCode = 1;
  }
}
