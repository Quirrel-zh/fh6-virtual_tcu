/**
 * Propagate root package.json "version" to all workspace packages and Python metadata.
 * Single source of truth: package.json at repo root.
 */
import { readFileSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const rootPkgPath = resolve(root, 'package.json')
const rootPkg = JSON.parse(readFileSync(rootPkgPath, 'utf-8'))
const { version } = rootPkg

if (!version || typeof version !== 'string') {
  throw new Error(`${rootPkgPath} is missing a string "version" field`)
}

const jsonTargets = [
  'apps/electron/package.json',
  'apps/dashboard/package.json',
  'packages/shared/package.json',
  'packages/ui/package.json',
]

for (const rel of jsonTargets) {
  const path = resolve(root, rel)
  const pkg = JSON.parse(readFileSync(path, 'utf-8'))
  if (pkg.version === version) continue
  pkg.version = version
  writeFileSync(path, `${JSON.stringify(pkg, null, 2)}\n`)
  console.info(`sync-version: ${rel} → ${version}`)
}

const pyprojectPath = resolve(root, 'pyproject.toml')
const pyproject = readFileSync(pyprojectPath, 'utf-8')
const pyprojectNext = pyproject.replace(/^version = "[^"]*"/m, `version = "${version}"`)
if (pyprojectNext !== pyproject) {
  writeFileSync(pyprojectPath, pyprojectNext)
  console.info(`sync-version: pyproject.toml → ${version}`)
}

const initPath = resolve(root, 'virtual_tcu/__init__.py')
const init = readFileSync(initPath, 'utf-8')
const initNext = init.replace(/^__version__ = "[^"]*"/m, `__version__ = "${version}"`)
if (initNext !== init) {
  writeFileSync(initPath, initNext)
  console.info(`sync-version: virtual_tcu/__init__.py → ${version}`)
}
