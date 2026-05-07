#!/usr/bin/env node

/**
 * powerhouse Apply Workflow
 *
 * Applies development conventions to an existing project.
 * Only copies workflow files - never touches source code.
 *
 * Usage:
 *   npx powerhouse apply    # In project directory
 *   powerhouse apply         # Via cli.js routing
 */

import { existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync, copyFileSync } from 'fs';
import { join, dirname, resolve } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const TEMPLATES_DIR = join(__dirname, '..', 'templates');
const WORKFLOW_DIR = join(TEMPLATES_DIR, 'workflow');

const WORKFLOW_FILES = [
  'AGENTS.md',
  'QUICKSTART.md',
  'CLAUDE.md',
  'opencode.json',
];

const WORKFLOW_DIRS = [
  '.claude',
  '.github',
  '.husky',
  'docs',
  'session-tracking',
];

function copyDirContents(src, dest) {
  const entries = readdirSync(src, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name === '.git') continue;
    const srcPath = join(src, entry.name);
    const destPath = join(dest, entry.name);

    if (entry.isDirectory()) {
      if (!existsSync(destPath)) {
        mkdirSync(destPath, { recursive: true });
      }
      copyDirContents(srcPath, destPath);
    } else {
      if (entry.name.endsWith('.template')) {
        continue;
      }
      copyFileSync(srcPath, destPath);
    }
  }
}

async function apply() {
  const projectDir = process.cwd();

  console.log('=== Apply Workflow ===\n');

  if (!existsSync(projectDir)) {
    console.error(`Project directory not found: ${projectDir}`);
    process.exit(1);
  }

  if (!existsSync(WORKFLOW_DIR)) {
    console.error('Workflow template not found. Reinstall claude-powerhouse.');
    process.exit(1);
  }

  console.log(`Project: ${projectDir}\n`);

  let copied = 0;

  for (const file of WORKFLOW_FILES) {
    const src = join(WORKFLOW_DIR, file);
    const dest = join(projectDir, file);

    if (!existsSync(src)) continue;

    if (!existsSync(dest)) {
      try {
        copyFileSync(src, dest);
        console.log(`  ✓ ${file}`);
        copied++;
      } catch (err) {
        console.error(`  ✗ ${file}: ${err.message}`);
      }
    } else {
      console.log(`  - ${file} (exists)`);
    }
  }

  for (const dir of WORKFLOW_DIRS) {
    const src = join(WORKFLOW_DIR, dir);
    const dest = join(projectDir, dir);

    if (!existsSync(src)) continue;

    try {
      if (!existsSync(dest)) {
        mkdirSync(dest, { recursive: true });
      }
      copyDirContents(src, dest);
      console.log(`  ✓ ${dir}/`);
      copied++;
    } catch (err) {
      console.error(`  ✗ ${dir}/: ${err.message}`);
    }
  }

  console.log(`\n[DONE] ${copied} item(s) added.\n`);
  console.log('Next: Run "npx powerhouse" to verify setup.\n');
}

export { apply };

// Run directly when called as main script (not imported by cli.js)
if (resolve(process.argv[1] || '') === resolve(__filename)) {
  await apply();
}