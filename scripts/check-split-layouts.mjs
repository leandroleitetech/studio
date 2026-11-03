import fs from 'node:fs';
import path from 'node:path';

const sourceRoot = path.resolve('src');
const allowed = new Set(['_shared/synchronized-split.tsx']);

const collect = (directory) =>
  fs.readdirSync(directory, {withFileTypes: true}).flatMap((entry) => {
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) return collect(absolute);
    return entry.isFile() && /\.(ts|tsx)$/.test(entry.name) ? [absolute] : [];
  });

const violations = [];
for (const absolute of collect(sourceRoot)) {
  const relative = path.relative(sourceRoot, absolute).replaceAll('\\', '/');
  if (allowed.has(relative)) continue;
  const source = fs.readFileSync(absolute, 'utf8');
  const buildsCameraGeometryManually =
    /cameraLeft\s*=\s*interpolate/.test(source) &&
    /cameraWidth\s*=\s*interpolate/.test(source) &&
    /(splitOut|windowProgress)/.test(source);
  if (
    buildsCameraGeometryManually &&
    !source.includes('getSynchronizedSplitState')
  ) {
    violations.push(relative);
  }
}

if (violations.length > 0) {
  console.error('Novos splits manuais não são permitidos. Use src/_shared/synchronized-split.tsx:');
  for (const file of violations) console.error(`- ${file}`);
  process.exit(1);
}

console.log('Verificação de splits: ok.');

