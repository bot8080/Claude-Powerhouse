#!/usr/bin/env node

/**
 * powerhouse Command Handler
 *
 * Single entry point for both new and existing project workflows.
 * Auto-detects context: existing project if package.json exists, new project otherwise.
 *
 * Usage:
 *   npx powerhouse              # Auto-detect
 *   npx powerhouse my-project   # New project named "my-project"
 *   npx powerhouse .            # New project in current dir
 *   powerhouse apply            # Apply workflow to existing project
 */

import { existsSync, readFileSync } from 'fs';
import { cwd } from 'process';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function detectStack() {
  const pkgJson = join(cwd(), 'package.json');
  if (!existsSync(pkgJson)) return null;

  try {
    const pkg = JSON.parse(readFileSync(pkgJson, 'utf8'));
    const deps = { ...pkg.dependencies, ...pkg.devDependencies };

    if (deps.expo || deps['expo-modules-core']) return 'expo';
    if (deps.react) return 'react';
    if (deps.next) return 'next';
    if (deps.vue) return 'vue';
    if (deps.svelte) return 'svelte';
    if (deps.angular) return 'angular';
    if (deps.express) return 'express';

    return 'generic';
  } catch {
    return 'generic';
  }
}

async function detectContext() {
  const pkgJson = join(cwd(), 'package.json');
  return existsSync(pkgJson);
}

async function main() {
  const args = process.argv.slice(2);
  const targetArg = args[0];

  console.log('\n=== powerhouse ===\n');

  // Route: "apply" command explicitly requested
  if (targetArg === 'apply') {
    const { apply } = await import('./apply.js');
    return apply();
  }

  // Route: "--help" flag
  if (targetArg === '--help' || targetArg === '-h') {
    console.log('Usage: npx powerhouse [command]');
    console.log('');
    console.log('Commands:');
    console.log('  init [name]    Scaffold a new project');
    console.log('  apply          Add workflow conventions to existing project');
    console.log('  --help, -h     Show this help');
    console.log('');
    console.log('Examples:');
    console.log('  npx powerhouse init my-app');
    console.log('  npx powerhouse init .');
    console.log('  npx powerhouse apply');
    return;
  }

  // Route: Explicit project name provided
  if (targetArg && targetArg !== '.') {
    const { init } = await import('./init.js');
    return init(targetArg);
  }

  // Route: "." means new project in current directory
  if (targetArg === '.') {
    const { init } = await import('./init.js');
    return init('.');
  }

  // Auto-detect: existing project?
  const hasPkg = await detectContext();
  const stack = await detectStack();

  if (hasPkg) {
    console.log(`Detected existing project (${stack || 'unknown stack'})`);
    console.log('Applying workflow...\n');
    const { apply } = await import('./apply.js');
    return apply();
  }

  // New project (interactive)
  const { init } = await import('./init.js');
  return init();
}

main().catch(console.error);