import { readFileSync, writeFileSync } from 'fs'

const path = 'src/lib/mtg-slang.ts'
let content = readFileSync(path, 'utf8')
content = content.replace(
  "import { REANIMATOR_ORACLE } from './reanimator-patterns'",
  "import { REANIMATOR_ORACLE, THEFT_ORACLE } from './archetype-patterns'",
)
writeFileSync(path, content)
console.log('Updated', path)
