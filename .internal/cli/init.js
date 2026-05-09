#!/usr/bin/env node

/**
 * powerhouse Multi-Stack Project Scaffolder
 *
 * Usage: node cli/init.js [project-name]
 *
 * Prompts for stack, addons, then assembles the project from:
 *   templates/workflow/ (Generic conventions, always copied)
 *   templates/stacks/ (Stack-specific code)
 *   templates/addons/ (Optional addons)
 */

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import readline from 'readline';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const TEMPLATES_DIR = path.resolve(__dirname, '..', 'templates');
const WORKFLOW_DIR = path.join(TEMPLATES_DIR, 'workflow');
const STACKS_DIR = path.join(TEMPLATES_DIR, 'stacks');
const ADDONS_DIR = path.join(TEMPLATES_DIR, 'addons');

function ask(question) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((resolve) => rl.question(question, (ans) => { rl.close(); resolve(ans); }));
}

function askChoice(question, options) {
  const opts = options.map((o, i) => `  ${i + 1}. ${o}`).join('\n');
  return ask(`${question}\n${opts}\n> `);
}

function listStacks() {
  if (!fs.existsSync(STACKS_DIR)) return [];
  return fs.readdirSync(STACKS_DIR).filter((d) => {
    const stackFile = path.join(STACKS_DIR, d, 'stack.json');
    return fs.existsSync(stackFile);
  });
}

function readStack(stackName) {
  const stackFile = path.join(STACKS_DIR, stackName, 'stack.json');
  if (!fs.existsSync(stackFile)) return null;
  return JSON.parse(fs.readFileSync(stackFile, 'utf8'));
}

function copyDir(src, dest, replacements = {}, stripTemplateExt = false) {
  if (!fs.existsSync(src)) return;
  if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true });

  const entries = fs.readdirSync(src, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name === '.git') continue;
    const srcPath = path.join(src, entry.name);
    let destName = entry.name;

    // Strip .template extension from filenames
    if (stripTemplateExt && destName.endsWith('.template')) {
      destName = destName.replace(/\.template$/, '');
    }

    const destPath = path.join(dest, destName);

    if (entry.isDirectory()) {
      copyDir(srcPath, destPath, replacements, stripTemplateExt);
    } else {
      let content = fs.readFileSync(srcPath, 'utf8');
      for (const [key, val] of Object.entries(replacements)) {
        content = content.split(key).join(val);
      }
      // Skip binary-ish files
      if (content.includes('\u0000')) {
        fs.copyFileSync(srcPath, destPath);
      } else {
        fs.writeFileSync(destPath, content, 'utf8');
      }
    }
  }
}

async function main(projectNameArg = null) {
  console.log('\n=== powerhouse - Project Scaffolder ===\n');

  // Template directory check
  if (!fs.existsSync(TEMPLATES_DIR)) {
    console.error(`Templates directory not found: ${TEMPLATES_DIR}`);
    console.error('Run this script from the repo root: node cli/init.js [name]');
    process.exit(1);
  }

  // Step 1: Project name
  const projectName = projectNameArg || process.argv[2] || (await ask('Project name: ')).trim();
  if (!projectName) {
    console.error('Project name is required.');
    process.exit(1);
  }

  const targetDir = path.resolve(process.cwd(), projectName);
  if (fs.existsSync(targetDir)) {
    console.error(`Directory already exists: ${targetDir}`);
    process.exit(1);
  }

  // Step 2: Stack selection
  const stacks = listStacks();
  if (stacks.length === 0) {
    console.error('No stacks found in templates/stacks/');
    process.exit(1);
  }

  const stackChoice = await askChoice('Which stack do you want?', stacks);
  const stackIndex = parseInt(stackChoice, 10) - 1;
  const stackName = stackIndex >= 0 && stackIndex < stacks.length
    ? stacks[stackIndex]
    : stackChoice.trim();

  const stackMeta = readStack(stackName);
  if (!stackMeta) {
    console.error(`Stack "${stackName}" not found or missing stack.json.`);
    process.exit(1);
  }

  console.log(`  Selected stack: ${stackMeta.name}\n`);

  // Common replacements (project name + stack variables)
  const projectVars = {
    'AppName': projectName.charAt(0).toUpperCase() + projectName.slice(1),
    'app-name': projectName.toLowerCase().replace(/\s+/g, '-'),
    'PROJECT_NAME': projectName,
  };

  const vars = { ...projectVars, ...stackMeta.variables };

  // Step 3: Addon selections
  const backend = (await askChoice('Which backend do you need?', ['None', 'Firebase', 'Supabase'])).trim();
  const payments = (await askChoice('Do you need payments?', ['No', 'Stripe'])).trim();
  const ai = (await askChoice('AI-assisted development workflow?', ['None', 'OpenCode'])).trim();

  const withFirebase = backend === '2' || backend.toLowerCase() === 'firebase';
  const withStripe = payments === '2' || payments.toLowerCase() === 'stripe';
  const withOpenCode = ai === '2' || ai.toLowerCase() === 'opencode';

  // Extra for Expo
  let bundleId = 'com.example.app';
  if (stackName === 'expo') {
    bundleId = (await ask(`Bundle identifier (e.g., com.example.app): `)).trim() || bundleId;
  }
  vars['com.example.app'] = bundleId;
  vars['your-eas-project-id'] = 'your-eas-project-id';

  // Step 4: Copy workflow template
  console.log('\nCreating project structure...');
  copyDir(WORKFLOW_DIR, targetDir, vars, true);
  console.log('  ✓ Workflow conventions');

  // Step 5: Copy stack files
  const stackDir = path.join(STACKS_DIR, stackName);
  if (fs.existsSync(stackDir)) {
    // Copy stack files (without interpolation -- these are real source files)
    copyDir(stackDir, targetDir, {}, false);
    console.log(`  ✓ Stack: ${stackMeta.name}`);
  }

  // Step 6: Copy addons
  if (withFirebase) {
    const firebaseDir = path.join(ADDONS_DIR, 'firebase');
    if (fs.existsSync(firebaseDir)) {
      copyDir(firebaseDir, targetDir);
      console.log('  ✓ Firebase addon');
    }
  }

  if (withStripe) {
    const stripeDir = path.join(ADDONS_DIR, 'stripe');
    if (fs.existsSync(stripeDir)) {
      copyDir(stripeDir, targetDir);
      console.log('  ✓ Stripe addon');
    }
  }

  if (withOpenCode) {
    const opencodeDir = path.join(ADDONS_DIR, 'opencode-ai');
    if (fs.existsSync(opencodeDir)) {
      copyDir(opencodeDir, targetDir);
      console.log('  ✓ OpenCode AI addon');
    }
  }

  // Step 7: Create .env from example
  const envExample = path.join(targetDir, '.env.example');
  const envFile = path.join(targetDir, '.env');
  if (fs.existsSync(envExample) && !fs.existsSync(envFile)) {
    fs.copyFileSync(envExample, envFile);
    console.log('  ✓ .env created from .env.example');
  }

  // Step 8: Install dependencies
  const install = await ask('\nInstall dependencies? (Y/n): ');
  if (install.toLowerCase() !== 'n') {
    console.log('\nInstalling dependencies...');
    try {
      const installCmd = stackMeta.variables.INSTALL_CMD || 'npm install';
      execSync(installCmd, { cwd: targetDir, stdio: 'inherit' });
      console.log('  ✓ Dependencies installed');
    } catch {
      const cmd = stackMeta.variables.INSTALL_CMD || 'npm install';
      console.log(`  - Dependency install failed. Run \`${cmd}\` manually.`);
    }
  }

  // Done
  const startCmd = stackMeta.variables.START_CMD || 'npm start';
  console.log(`\n[DONE] Project created at: ${targetDir}\n`);
  console.log('Next steps:');
  console.log(`  cd ${projectName}`);
  console.log(`  ${startCmd}`);
  console.log('');
}

main().catch(console.error);

export async function init(projectName) {
  return main(projectName);
}
