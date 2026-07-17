import test from 'node:test';
import assert from 'node:assert/strict';
import { cp, mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { validateContentContract } from './validate-content-contract.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const DOCS_DIR = resolve(HERE, '..');

async function withCopy(mutator) {
  const temp = await mkdtemp(join(tmpdir(), 'stet-content-contract-'));
  const docsDir = join(temp, 'docs');
  try {
    await cp(DOCS_DIR, docsDir, {
      recursive: true,
      filter: (source) => !source.split('/').includes('node_modules'),
    });
    for (const file of ['README.md', 'BETA_QUICKSTART.md', 'ONBOARDING.md', 'PROMPT_COOKBOOK.md', 'TROUBLESHOOTING.md']) {
      await cp(resolve(DOCS_DIR, '..', file), join(temp, file));
    }
    if (mutator) await mutator(docsDir);
    return { temp, docsDir };
  } catch (error) {
    await rm(temp, { recursive: true, force: true });
    throw error;
  }
}

async function runCopy(mutator, options = {}) {
  const { temp, docsDir } = await withCopy(mutator);
  try {
    return validateContentContract({
      rootDir: docsDir,
      resolveRef: () => '778a4fe0ca8eb96cbcc0d1f35b9c0955a7e884e5',
      existsCommit: () => true,
      isAncestor: () => true,
      ...options,
    });
  } finally {
    await rm(temp, { recursive: true, force: true });
  }
}

test('current docs pass the contract', async () => {
  const result = validateContentContract({ rootDir: DOCS_DIR, mode: 'contract' });
  assert.deepEqual(result, { ok: true, errors: [] });
});

for (const field of ['title', 'sidebarTitle']) {
  test(`index frontmatter requires ${field}`, async () => {
    const result = await runCopy(async (root) => {
      const path = join(root, 'index.mdx');
      const text = await readFile(path, 'utf8');
      await writeFile(path, text.replace(new RegExp(`^${field}:.*\\n`, 'm'), ''));
    });
    assert.equal(result.ok, false);
    assert.match(result.errors.join('\n'), /frontmatter title\/sidebarTitle are required/);
  });
}

test('Markdown H1 in a page body fails', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, 'quickstart.mdx');
    await writeFile(path, `${await readFile(path, 'utf8')}\n# Duplicate heading\n`);
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /must not contain a Markdown H1/);
});

for (const [name, value] of [['primary', '#000000'], ['light', '#000000'], ['dark', '#000000']]) {
  test(`docs.json ${name} color mutation fails`, async () => {
    const result = await runCopy(async (root) => {
      const path = join(root, 'docs.json');
      const config = JSON.parse(await readFile(path, 'utf8'));
      config.colors[name] = value;
      await writeFile(path, `${JSON.stringify(config, null, 2)}\n`);
    });
    assert.equal(result.ok, false);
    assert.match(result.errors.join('\n'), /docs\.json colors must be exactly/);
  });
}

test('the exact header contextual menu is accepted', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, 'docs.json');
    const config = JSON.parse(await readFile(path, 'utf8'));
    config.contextual = {
      options: ['copy', 'view', 'chatgpt', 'claude', 'mcp', 'cursor', 'vscode'],
      display: 'header',
    };
    await writeFile(path, `${JSON.stringify(config, null, 2)}\n`);
  });
  assert.deepEqual(result, { ok: true, errors: [] });
});

for (const [field, value] of [['engines.node', '>=18'], ['devDependencies.mint', '4.2.688']]) {
  test(`package.json ${field} mutation fails`, async () => {
    const result = await runCopy(async (root) => {
      const path = join(root, 'package.json');
      const packageJson = JSON.parse(await readFile(path, 'utf8'));
      const [section, key] = field.split('.');
      packageJson[section][key] = value;
      await writeFile(path, `${JSON.stringify(packageJson, null, 2)}\n`);
    });
    assert.equal(result.ok, false);
    assert.match(result.errors.join('\n'), /package\.json (engines\.node|devDependency mint)/);
  });
}

test('the unapproved transparency fixture blocks publication', () => {
  const result = validateContentContract({ rootDir: DOCS_DIR, mode: 'publication' });
  assert.equal(result.ok, false);
  assert.ok(result.errors.every((error) => /concepts-trial-result-example receipt fixture requires publication approval/.test(error)));
});

test('clearing publication approval fails closed', async () => {
  const result = await runCopy(async (root) => {
    for (const name of ['receipt-review.json', 'index.mdx']) {
      const path = join(root, name);
      const text = await readFile(path, 'utf8');
      await writeFile(path, text
        .replace('"publication_approved_at": "2026-07-14"', '"publication_approved_at": null')
        .replace('"publication_approved_by": "benredmond"', '"publication_approved_by": null'));
    }
  }, { mode: 'publication' });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /receipt-review\.json must match the approved receipt values/);
  assert.match(result.errors.join('\n'), /publication_approved_at must be non-null in publication mode/);
  assert.match(result.errors.join('\n'), /publication_approved_by must be non-null and nonempty in publication mode/);
});

test('missing official Unix installer URL fails', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, 'quickstart.mdx');
    const text = await readFile(path, 'utf8');
    await writeFile(path, text.replace('https://raw.githubusercontent.com/Stet-AI/stet-cli/main/install.sh', 'https://example.com/install.sh'));
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /official Unix installer URL/);
});

test('missing official Windows installer URL fails', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, 'quickstart.mdx');
    const text = await readFile(path, 'utf8');
    await writeFile(path, text.replace('https://raw.githubusercontent.com/Stet-AI/stet-cli/main/install.ps1', 'https://example.com/install.ps1'));
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /official Windows installer URL/);
});

test('installer version argument fails', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, 'quickstart.mdx');
    const text = await readFile(path, 'utf8');
    await writeFile(path, text.replace('install.sh | sh', 'install.sh | sh --version 9.9.9'));
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /must not pass a version argument to the installer/);
});

test('static Stet CLI semver token fails', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, 'quickstart.mdx');
    const text = await readFile(path, 'utf8');
    await writeFile(path, `${text}\nThe CLI release is v9.9.9.\n`);
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /hard-coded Stet CLI semver token/);
});

test('collapsed one-line prompt fails', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, 'quickstart.mdx');
    const text = await readFile(path, 'utf8');
    await writeFile(path, `${text}\n\`\`\`text wrap\none line\n\`\`\`\n`);
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /prompt fence must contain at least two nonempty lines/);
});

test('overlong prompt line fails', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, 'quickstart.mdx');
    const text = await readFile(path, 'utf8');
    await writeFile(path, `${text}\n\`\`\`text wrap\n${'x'.repeat(101)}\nsecond line\n\`\`\`\n`);
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /prompt fence contains a line longer than 100 characters/);
});

test('unclosed prompt fence fails', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, 'quickstart.mdx');
    const text = await readFile(path, 'utf8');
    await writeFile(path, `${text}\n\`\`\`text wrap\nfirst\nsecond\n`);
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /unclosed text prompt fence/);
});

test('prompt fence without mobile wrapping fails', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, 'quickstart.mdx');
    const text = await readFile(path, 'utf8');
    await writeFile(path, `${text}\n\`\`\`text nowrap\nfirst\nsecond\n\`\`\`\n`);
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /prompt fence must enable wrapping/);
});

test('generic stet update command fails', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, 'quickstart.mdx');
    await writeFile(path, `${await readFile(path, 'utf8')}\nRun stet update when needed.\n`);
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /must not advertise generic stet update/);
});

test('manual dispatch workflow binds checkout and expected base to explicit SHAs', async () => {
  const workflow = await readFile(resolve(DOCS_DIR, '..', '.github/workflows/docs-validation.yml'), 'utf8');
  assert.match(workflow, /ref:\s+\$\{\{ github\.event_name == 'workflow_dispatch' && inputs\.head_sha \|\| github\.sha \}\}/);
  assert.match(workflow, /--base-sha \"\$INPUT_BASE_SHA\" --head-sha \"\$INPUT_HEAD_SHA\" --expected-base-sha \"\$INPUT_BASE_SHA\"/);
});

test('legacy onboarding fallback remains byte-protected', async () => {
    const result = await runCopy(undefined, {
      baseSha: 'base',
      headSha: 'head',
      existsCommit: () => true,
      changedFiles: ['ONBOARDING.md'],
    });
    assert.equal(result.ok, false);
    assert.match(result.errors.at(-1), /protected fallback files changed/);
  });

for (const fallback of ['README.md', 'BETA_QUICKSTART.md', 'PROMPT_COOKBOOK.md', 'TROUBLESHOOTING.md']) {
  test(`authorized public collateral change passes when required content remains (${fallback})`, async () => {
    const result = await runCopy(async (root) => {
      await writeFile(join(root, '..', fallback), await readFile(resolve(DOCS_DIR, '..', fallback), 'utf8'));
    }, {
      baseSha: 'base',
      headSha: 'head',
      existsCommit: () => true,
      changedFiles: [fallback],
    });
    assert.deepEqual(result, { ok: true, errors: [] });
  });
}

test('authorized public collateral change fails when required content is removed', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, '..', 'README.md');
    const text = await readFile(resolve(DOCS_DIR, '..', 'README.md'), 'utf8');
    await writeFile(path, text.replace('# Improve the instructions, skills, and model settings your coding agents actually use', '# Improve coding workflows'));
  }, {
    baseSha: 'base',
    headSha: 'head',
    existsCommit: () => true,
    changedFiles: ['README.md'],
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /README\.md is missing required public content/);
});

test('authorized public collateral change rejects static Stet CLI versions', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, '..', 'PROMPT_COOKBOOK.md');
    await writeFile(path, `${await readFile(resolve(DOCS_DIR, '..', 'PROMPT_COOKBOOK.md'), 'utf8')}\nThe CLI release is v9.9.9.\n`);
  }, {
    baseSha: 'base',
    headSha: 'head',
    existsCommit: () => true,
    changedFiles: ['PROMPT_COOKBOOK.md'],
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /PROMPT_COOKBOOK\.md contains a hard-coded Stet CLI semver token/);
});

test('stable-incompatible --target-ready claim fails on a Mintlify page', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, 'quickstart.mdx');
    await writeFile(path, `${await readFile(path, 'utf8')}\nRun stet suite build --target-ready 20.\n`);
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /quickstart\.mdx contains unsupported claim/);
});

test('stable-incompatible automatic canary claims fail in public collateral', async () => {
  for (const claim of [
    'Stet automatically runs one canary.',
    'Use the canary controller to manage the build.',
    'Run one canary before fan-out.',
  ]) {
    const result = await runCopy(async (root) => {
      const path = join(root, '..', 'PROMPT_COOKBOOK.md');
      const text = await readFile(resolve(DOCS_DIR, '..', 'PROMPT_COOKBOOK.md'), 'utf8');
      await writeFile(path, `${text}\n${claim}\n`);
    }, {
      baseSha: 'base',
      headSha: 'head',
      existsCommit: () => true,
      changedFiles: ['PROMPT_COOKBOOK.md'],
    });
    assert.equal(result.ok, false, claim);
    assert.match(result.errors.join('\n'), /PROMPT_COOKBOOK\.md contains unsupported claim/, claim);
  }
});

test('postfixed automatic canary claim fails in public collateral', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, '..', 'PROMPT_COOKBOOK.md');
    const text = await readFile(resolve(DOCS_DIR, '..', 'PROMPT_COOKBOOK.md'), 'utf8');
    await writeFile(path, `${text}\nStet runs one canary automatically.\n`);
  }, {
    baseSha: 'base',
    headSha: 'head',
    existsCommit: () => true,
    changedFiles: ['PROMPT_COOKBOOK.md'],
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /PROMPT_COOKBOOK\.md contains unsupported claim/);
});

test('fully hyphenated canary-before-fan-out claim fails in public collateral', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, '..', 'PROMPT_COOKBOOK.md');
    const text = await readFile(resolve(DOCS_DIR, '..', 'PROMPT_COOKBOOK.md'), 'utf8');
    await writeFile(path, `${text}\nStet runs one canary-before-fan-out.\n`);
  }, {
    baseSha: 'base',
    headSha: 'head',
    existsCommit: () => true,
    changedFiles: ['PROMPT_COOKBOOK.md'],
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /PROMPT_COOKBOOK\.md contains unsupported claim/);
});

test('generic human-controlled canary wording remains allowed in public collateral', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, '..', 'PROMPT_COOKBOOK.md');
    const text = await readFile(resolve(DOCS_DIR, '..', 'PROMPT_COOKBOOK.md'), 'utf8');
    await writeFile(path, `${text}\nA human can run a bounded canary after reviewing the onboarding receipt.\n`);
  }, {
    baseSha: 'base',
    headSha: 'head',
    existsCommit: () => true,
    changedFiles: ['PROMPT_COOKBOOK.md'],
  });
  assert.deepEqual(result, { ok: true, errors: [] });
});

test('extra hidden MDX page fails', async () => {
  const result = await runCopy((root) => writeFile(join(root, '.hidden.mdx'), '# Hidden'));
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /unexpected docs page: \.hidden\.mdx/);
});

test('dependency README files under node_modules are ignored', async () => {
  const result = await runCopy(async (root) => {
    const packageDir = join(root, 'node_modules', 'pkg');
    await mkdir(packageDir, { recursive: true });
    await writeFile(join(packageDir, 'README.md'), '# Dependency metadata');
  });
  assert.deepEqual(result, { ok: true, errors: [] });
});

test('content-base mismatch fails through the PR base assertion', async () => {
  const result = await runCopy(undefined, {
    expectedBaseSha: 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    existsCommit: () => true,
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /content_base_commit .* does not equal expected base/);
});

test('missing docs-review fixture fails', async () => {
  const result = await runCopy((root) => rm(join(root, 'docs-review.json')));
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /missing docs-review\.json/);
});

test('missing reviewed content-base commit fails', async () => {
  const result = await runCopy(undefined, { existsCommit: () => false });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /required commit does not exist/);
});

test('non-ancestor content base fails', async () => {
  const result = await runCopy(undefined, {
    headSha: 'head',
    existsCommit: () => true,
    isAncestor: () => false,
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /content_base_commit .* is not an ancestor/);
});

test('changed-file comparison rejects an all-zero or missing base', async () => {
  const result = await runCopy(undefined, {
    baseSha: '0000000000000000000000000000000000000000',
    headSha: 'head',
    existsCommit: () => true,
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /requires non-zero --base-sha and --head-sha/);
});

test('receipt metric mutation fails exact deep equality', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, 'index.mdx');
    const text = await readFile(path, 'utf8');
    await writeFile(path, text.replace('"candidate": "46.4%"', '"candidate": "46.5%"'));
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /rendered receipt JSON must exactly equal/);
});

test('receipt model mutation fails exact deep equality', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, 'index.mdx');
    const text = await readFile(path, 'utf8');
    await writeFile(path, text.replace('"Opus 4.7"', '"Opus 4.8"'));
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /rendered receipt JSON must exactly equal/);
});

test('index receipt fixture formatting must retain approved bytes', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, 'receipt-review.json');
    await writeFile(path, `${await readFile(path, 'utf8')}\n`);
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /receipt-review\.json must exactly retain the approved bytes/);
});

test('extra asset and PNG fail the exact asset allowlist', async () => {
  const result = await runCopy((root) => writeFile(join(root, 'assets', 'extra.png'), 'not an image'));
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /docs\/assets must contain exactly/);
});

for (const injected of [
  '/Users/ben/private.txt',
  'TOKEN=sk-ant-test-value',
  'This is a post-training layer for agents.',
]) {
  test(`forbidden public text fails (${injected.slice(0, 20)})`, async () => {
    const result = await runCopy(async (root) => {
      const path = join(root, 'quickstart.mdx');
      await writeFile(path, `${await readFile(path, 'utf8')}\n${injected}\n`);
    });
    assert.equal(result.ok, false);
    assert.ok(result.errors.some((error) => /forbidden private path|secret assignment|unsupported claim/.test(error)));
  });
}

test('approved negated caveat does not false-positive', () => {
  const result = validateContentContract({ rootDir: DOCS_DIR, mode: 'contract' });
  assert.equal(result.ok, true);
  assert.equal(result.errors.some((error) => /unsupported claim/.test(error)), false);
});

test('a newly discovered page is accepted when navigation includes it', async () => {
  const result = await runCopy(async (root) => {
    await writeFile(join(root, 'new-page.mdx'), '---\ntitle: New page\nsidebarTitle: New page\n---\n\nNew page body.\n');
    const configPath = join(root, 'docs.json');
    const config = JSON.parse(await readFile(configPath, 'utf8'));
    config.navigation.groups[0].pages.push('new-page');
    await writeFile(configPath, `${JSON.stringify(config, null, 2)}\n`);
  });
  assert.deepEqual(result, { ok: true, errors: [] });
});

test('new page omitted from navigation fails', async () => {
  const result = await runCopy((root) => writeFile(join(root, 'new-page.mdx'), '---\ntitle: New page\nsidebarTitle: New page\n---\n\nNew page body.\n'));
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /new-page is missing from docs\.json navigation/);
});

test('designated root skill asset is allowed outside navigation and remains safety-scanned', async () => {
  const result = await runCopy((root) => writeFile(join(root, 'skill.md'), '---\nname: Stet docs router\ndescription: Context only.\n---\n\nUse the canonical skill.\n'));
  assert.deepEqual(result, { ok: true, errors: [] });
});

for (const [name, injected, expected] of [
  ['forbidden path', '/Users/ben/private.txt', /forbidden private path/],
  ['secret', 'TOKEN=sk-ant-test-value', /secret assignment/],
  ['unsupported claim', 'This is a post-training layer for agents.', /unsupported claim/],
  ['installer version argument', 'curl https://raw.githubusercontent.com/Stet-AI/stet-cli/main/install.sh | sh --version 9.9.9', /must not pass a version argument/],
  ['stet update', 'Run stet update when needed.', /must not advertise generic stet update/],
]) {
  test(`designated root skill asset ${name} fails`, async () => {
    const result = await runCopy((root) => writeFile(join(root, 'skill.md'), `---\nname: Stet docs router\ndescription: Context only.\n---\n\n${injected}\n`));
    assert.equal(result.ok, false);
    assert.match(result.errors.join('\n'), expected);
  });
}

test('four navigation groups with wrong names fail even when they cover each page once', async () => {
  const result = await runCopy(async (root) => {
    const configPath = join(root, 'docs.json');
    const config = JSON.parse(await readFile(configPath, 'utf8'));
    const pages = config.navigation.groups.flatMap((group) => group.pages);
    config.navigation.groups = [
      { group: 'Start', pages: pages.slice(0, 2) },
      { group: 'Learn', pages: pages.slice(2, 4) },
      { group: 'Reference', pages: pages.slice(4, 6) },
      { group: 'Help', pages: pages.slice(6) },
    ];
    await writeFile(configPath, `${JSON.stringify(config, null, 2)}\n`);
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /navigation group names must be exactly/);
});

test('legacy single Stet navigation group fails', async () => {
  const result = await runCopy(async (root) => {
    const configPath = join(root, 'docs.json');
    const config = JSON.parse(await readFile(configPath, 'utf8'));
    const pages = config.navigation.groups.flatMap((group) => group.pages);
    config.navigation.groups = [{ group: 'Stet', pages }];
    await writeFile(configPath, `${JSON.stringify(config, null, 2)}\n`);
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /navigation must contain exactly four named groups/);
});

for (const [name, injected, expected] of [
  ['forbidden path', '/Users/ben/private.txt', /forbidden private path/],
  ['leaderboard path', '.stet/leaderboard/zod', /forbidden private path/],
  ['secret', 'TOKEN=sk-ant-test-value', /secret assignment/],
  ['unsupported claim', 'This is a post-training layer for agents.', /unsupported claim/],
  ['installer version argument', 'curl https://raw.githubusercontent.com/Stet-AI/stet-cli/main/install.sh | sh --version 9.9.9', /must not pass a version argument/],
  ['stet update', 'Run stet update when needed.', /must not advertise generic stet update/],
  ['body H1', '# Not allowed', /must not contain a Markdown H1/],
]) {
  test(`new page ${name} fails`, async () => {
    const result = await runCopy(async (root) => {
      await writeFile(join(root, 'new-page.mdx'), `---\ntitle: New page\nsidebarTitle: New page\n---\n\n${injected}\n`);
      const configPath = join(root, 'docs.json');
      const config = JSON.parse(await readFile(configPath, 'utf8'));
      config.navigation.groups[0].pages.push('new-page');
      await writeFile(configPath, `${JSON.stringify(config, null, 2)}\n`);
    });
    assert.equal(result.ok, false);
    assert.match(result.errors.join('\n'), expected);
  });
}

test('Prompt bodies require closure, multiple lines, and short lines', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, 'quickstart.mdx');
    await writeFile(path, `${await readFile(path, 'utf8')}\n<Prompt>\n${'x'.repeat(101)}\n</Prompt>\n<Prompt>one line</Prompt>\n<Prompt>\nfirst\nsecond\n`);
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /Prompt contains a line longer than 100 characters/);
  assert.match(result.errors.join('\n'), /Prompt must contain at least two nonempty lines/);
  assert.match(result.errors.join('\n'), /unclosed Prompt/);
});

test('unsupported claims inside Prompt bodies fail', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, 'quickstart.mdx');
    await writeFile(path, `${await readFile(path, 'utf8')}\n<Prompt>\nThis is a post-training layer for agents.\nContinue safely.\n</Prompt>\n`);
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /unsupported claim/);
});

test('per-page receipt fixture validates a uniquely named marker and caveats', async () => {
  const result = await runCopy(async (root) => {
    const fixtureDir = join(root, 'receipt-fixtures');
    await mkdir(fixtureDir, { recursive: true });
    const fixture = { caveats: ['Synthetic receipt caveat.'], publication_approved_at: null, publication_approved_by: null };
    await writeFile(join(fixtureDir, 'quickstart-demo.json'), `${JSON.stringify(fixture, null, 2)}\n`);
    const path = join(root, 'quickstart.mdx');
    await writeFile(path, `${await readFile(path, 'utf8')}\nSynthetic receipt caveat.\n{/* <!-- stet-receipt:quickstart-demo:start --> */}\n\`\`\`json\n${JSON.stringify(fixture, null, 2)}\n\`\`\`\n{/* <!-- stet-receipt:quickstart-demo:end --> */}\n`);
  });
  assert.deepEqual(result, { ok: true, errors: [] });
});

test('nested-page receipt fixture binds through its hyphenated logical page name', async () => {
  const result = await runCopy(async (root) => {
    const fixtureDir = join(root, 'receipt-fixtures');
    await mkdir(fixtureDir, { recursive: true });
    const fixture = { caveats: ['Nested synthetic receipt caveat.'], publication_approved_at: null, publication_approved_by: null };
    await writeFile(join(fixtureDir, 'concepts-trial-result-demo.json'), `${JSON.stringify(fixture, null, 2)}\n`);
    const path = join(root, 'concepts', 'trial-result.mdx');
    await writeFile(path, `${await readFile(path, 'utf8')}\nNested synthetic receipt caveat.\n{/* <!-- stet-receipt:concepts-trial-result-demo:start --> */}\n\`\`\`json\n${JSON.stringify(fixture, null, 2)}\n\`\`\`\n{/* <!-- stet-receipt:concepts-trial-result-demo:end --> */}\n`);
  });
  assert.deepEqual(result, { ok: true, errors: [] });
});

test('nested-page receipt fixture rejects a misbound marker ID', async () => {
  const result = await runCopy(async (root) => {
    const fixtureDir = join(root, 'receipt-fixtures');
    await mkdir(fixtureDir, { recursive: true });
    const fixture = { caveats: ['Nested synthetic receipt caveat.'], publication_approved_at: null, publication_approved_by: null };
    await writeFile(join(fixtureDir, 'wrong-page-demo.json'), `${JSON.stringify(fixture, null, 2)}\n`);
    const path = join(root, 'concepts', 'trial-result.mdx');
    await writeFile(path, `${await readFile(path, 'utf8')}\nNested synthetic receipt caveat.\n{/* <!-- stet-receipt:wrong-page-demo:start --> */}\n\`\`\`json\n${JSON.stringify(fixture, null, 2)}\n\`\`\`\n{/* <!-- stet-receipt:wrong-page-demo:end --> */}\n`);
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /must be named for page concepts\/trial-result/);
});

for (const [name, mutate, expected] of [
  ['unfixtured marker', async (root) => {
    const path = join(root, 'quickstart.mdx');
    await writeFile(path, `${await readFile(path, 'utf8')}\n{/* <!-- stet-receipt:quickstart-missing:start --> */}\n\`\`\`json\n{}\n\`\`\`\n{/* <!-- stet-receipt:quickstart-missing:end --> */}\n`);
  }, /has no receipt fixture/],
  ['orphan fixture', async (root) => {
    await mkdir(join(root, 'receipt-fixtures'), { recursive: true });
    await writeFile(join(root, 'receipt-fixtures', 'orphan.json'), '{"caveats": []}\n');
  }, /orphan receipt fixture/],
  ['duplicate marker', async (root) => {
    const text = await readFile(join(root, 'index.mdx'), 'utf8');
    await writeFile(join(root, 'index.mdx'), `${text}\n${text.match(/<!--[\s\S]*?stet-receipt:start[\s\S]*?stet-receipt:end[\s\S]*?-->/)?.[0] || ''}`);
  }, /exactly one stet receipt source block/],
  ['malformed fixture', async (root) => {
    await mkdir(join(root, 'receipt-fixtures'), { recursive: true });
    await writeFile(join(root, 'receipt-fixtures', 'bad.json'), '{ nope }\n');
    const path = join(root, 'quickstart.mdx');
    await writeFile(path, `${await readFile(path, 'utf8')}\n{/* <!-- stet-receipt:bad:start --> */}\n\`\`\`json\n{}\n\`\`\`\n{/* <!-- stet-receipt:bad:end --> */}\n`);
  }, /not valid JSON/],
  ['mismatch fixture', async (root) => {
    await mkdir(join(root, 'receipt-fixtures'), { recursive: true });
    await writeFile(join(root, 'receipt-fixtures', 'bad.json'), '{"caveats": []}\n');
    const path = join(root, 'quickstart.mdx');
    await writeFile(path, `${await readFile(path, 'utf8')}\n{/* <!-- stet-receipt:bad:start --> */}\n\`\`\`json\n{"caveats":["different"]}\n\`\`\`\n{/* <!-- stet-receipt:bad:end --> */}\n`);
  }, /must exactly equal receipt fixture/],
]) {
  test(`${name} fails`, async () => {
    const result = await runCopy(mutate);
    assert.equal(result.ok, false);
    assert.match(result.errors.join('\n'), expected);
  });
}

test('an unapproved second receipt fixture fails publication but not contract', async () => {
  const mutate = async (root) => {
    const fixtureDir = join(root, 'receipt-fixtures');
    await mkdir(fixtureDir, { recursive: true });
    const fixture = { caveats: ['Synthetic receipt caveat.'], publication_approved_at: null, publication_approved_by: null };
    await writeFile(join(fixtureDir, 'quickstart-demo.json'), `${JSON.stringify(fixture, null, 2)}\n`);
    const path = join(root, 'quickstart.mdx');
    await writeFile(path, `${await readFile(path, 'utf8')}\nSynthetic receipt caveat.\n{/* <!-- stet-receipt:quickstart-demo:start --> */}\n\`\`\`json\n${JSON.stringify(fixture, null, 2)}\n\`\`\`\n{/* <!-- stet-receipt:quickstart-demo:end --> */}\n`);
  };
  assert.deepEqual(await runCopy(mutate), { ok: true, errors: [] });
  const publication = await runCopy(mutate, { mode: 'publication' });
  assert.equal(publication.ok, false);
  assert.match(publication.errors.join('\n'), /quickstart-demo receipt fixture requires publication approval/);
});
