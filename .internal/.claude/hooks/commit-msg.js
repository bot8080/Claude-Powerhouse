#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const msg = fs.readFileSync(process.argv[2], 'utf8').trim();
const pattern = /^(feat|fix|chore|docs|refactor|test|perf|build|ci|style|revert)(\(.+\))?: .+/;

if (!pattern.test(msg)) {
  console.error(
    `Invalid commit message: "${msg}"\n` +
    `Must follow conventional commits: <type>(<scope>): <subject>\n` +
    `Types: feat | fix | chore | docs | refactor | test | perf | build | ci | style | revert`,
  );
  process.exit(1);
}