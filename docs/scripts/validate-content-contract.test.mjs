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

for (const [field, value] of [['title', 'Wrong title'], ['sidebarTitle', 'Wrong sidebar']]) {
  test(`index frontmatter ${field} mutation fails`, async () => {
    const result = await runCopy(async (root) => {
      const path = join(root, 'index.mdx');
      const text = await readFile(path, 'utf8');
      await writeFile(path, text.replace(new RegExp(`^${field}:.*$`, 'm'), `${field}: ${value}`));
    });
    assert.equal(result.ok, false);
    assert.match(result.errors.join('\n'), /frontmatter title\/sidebarTitle/);
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

test('approved publication passes the contract', () => {
  const result = validateContentContract({ rootDir: DOCS_DIR, mode: 'publication' });
  assert.deepEqual(result, { ok: true, errors: [] });
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
    const collapsed = text.replace(/```text[^\n]*\n([\s\S]*?)\n```/, (_, body) => `\`\`\`text wrap\n${body.replaceAll('\n', ' ')}\n\`\`\``);
    await writeFile(path, collapsed);
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /prompt fence must contain at least two nonempty lines/);
});

test('overlong prompt line fails', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, 'quickstart.mdx');
    const text = await readFile(path, 'utf8');
    const overlong = text.replace('Use the Stet skill. Onboard this repo for Stet evals. Ask what work I want', `Use the Stet skill. ${'x'.repeat(101)}`);
    await writeFile(path, overlong);
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /prompt fence contains a line longer than 100 characters/);
});

test('unclosed prompt fence fails', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, 'quickstart.mdx');
    const text = await readFile(path, 'utf8');
    await writeFile(path, text.replace('the onboarding receipt with the selected slice, scope, skips, and confidence.\n```', 'the onboarding receipt with the selected slice, scope, skips, and confidence.'));
  });
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /unclosed text prompt fence/);
});

test('prompt fence without mobile wrapping fails', async () => {
  const result = await runCopy(async (root) => {
    const path = join(root, 'quickstart.mdx');
    const text = await readFile(path, 'utf8');
    await writeFile(path, text.replace(/^```text.*$/m, '```text nowrap'));
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
    await writeFile(path, text.replace('# Improve the instructions, skills, and model settings your coding agents use', '# Improve coding workflows'));
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
