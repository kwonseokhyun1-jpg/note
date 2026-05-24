import { readFileSync, writeFileSync } from 'fs'

const slangPath = 'src/lib/mtg-slang.ts'
let slang = readFileSync(slangPath, 'utf8')
slang = slang.replace(
  "import { REANIMATOR_ORACLE } from './reanimator-patterns'",
  "import { REANIMATOR_ORACLE, THEFT_ORACLE } from './archetype-patterns'",
)
writeFileSync(slangPath, slang)

const matchPath = 'src/lib/commander-match.ts'
let match = readFileSync(matchPath, 'utf8')
match = match.replace('    const strongSignals = arch?.signals ?? []\n', '')
writeFileSync(matchPath, match)

console.log('Fixed build errors')
