#!/usr/bin/env node
const branch = process.argv[2] || '';

const allowed = /^(feature|chore|docs|release|hotfix)\//;
if (!allowed.test(branch)) {
  console.error(
    `Invalid branch name: "${branch}".\n` +
    `Branch must start with: feature/, chore/, docs/, release/, or hotfix/.`,
  );
  process.exit(1);
}

console.log(`Branch name "${branch}" is valid.`);