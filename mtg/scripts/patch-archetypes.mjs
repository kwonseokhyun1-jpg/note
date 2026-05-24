import { readFileSync, writeFileSync } from 'fs'

const files = [
  {
    path: 'src/lib/archetypes.ts',
    patches: [
      {
        from: `    id: 'group-hug',
    label: 'Group hug',
    aliases: ['group', 'hug', 'politics', 'everyone', 'table'],
    signals: [/each player (draws?|may|gains)/i, /all players/i],`,
        to: `    id: 'group-hug',
    label: 'Group hug',
    aliases: ['group-hug', 'grouphug', 'hug'],
    signals: [
      /each player may draw a card/i,
      /each player draws? (?:a |one |two |three |\\d+ )?cards?/i,
      /each player gains? \\d+ life/i,
      /each player adds? \\{[wubrgc]/i,
      /each player may put (?:a |up to .* )?land .* onto the battlefield/i,
      /each player creates? .* [Tt]reasure tokens?/i,
    ],
    excludeSignals: [
      /whenever an opponent draws?.*(?:deals? \\d+ damage|loses \\d+ life)/i,
      /each player discards?/i,
      /each player sacrifices?/i,
      /each player may attack only/i,
      /you may cast any number of spells from among/i,
      /exile the top .* of (?:their|target opponent)/i,
    ],`,
      },
      {
        from: `    id: 'theft',
    label: 'Theft / steal',
    aliases: ['theft', 'steal', 'thief', 'thieves', 'rob', 'robbery', 'greed', 'impulse'],
    signals: [
      /cast .* from (?:an )?opponent'?s? (?:hand|graveyard|library|exile)/i,
      /you may cast .* (?:an )?opponent'?s? (?:hand|library|exile)/i,
      /look at the top .* opponent'?s? library.*you may cast/i,
      /exile .* face down.*you may cast/i,
      /exchange control of (?:target )?permanents?/i,
      /you may cast .* spells? (?:your )?opponents control/i,
    ],`,
        to: `    id: 'theft',
    label: 'Theft / steal',
    aliases: ['theft', 'steal', 'thief', 'thieves', 'rob', 'robbery', 'impulse'],
    signals: [
      /cast .* from (?:an )?opponent/i,
      /you may cast .* opponent/i,
      /look at the top .* opponent'?s? library.*you may cast/i,
      /exile the top .*cards? of (?:their|target opponent'?s?) library.*you may cast/i,
      /each player exiles? cards? from the top of their library.*you may cast/i,
      /exile .* face down.*you may cast/i,
      /exchange control of (?:target )?permanents?/i,
      /gain control of (?:target )?permanents?/i,
    ],`,
      },
      {
        from: `    id: 'graveyard',
    label: 'Graveyard / reanimator',
    aliases: ['reanimator', 'reanimate', 'recursion', 'graveyard', 'yard'],
    signals: [
      /from (?:your |a )?graveyard to the battlefield/i,
      /return .* from (?:your |a )?graveyard/i,
      /cast .* from (?:your )?graveyard/i,
      /play .* from (?:your )?graveyard/i,
      /(?:in|from) (?:your |a )?graveyard.{0,160}return .* to the battlefield/is,
      /return target (?:creature )?card from (?:your )?graveyard/i,
    ],`,
        to: `    id: 'graveyard',
    label: 'Reanimator',
    aliases: ['reanimator', 'reanimate', 'recursion'],
    signals: [
      /from your graveyard to the battlefield/i,
      /return target .* from your graveyard to the battlefield/i,
      /return .* from your graveyard/i,
      /cast .* from your graveyard/i,
      /play .* from your graveyard/i,
      /(?:in|from) your graveyard.{0,160}return .* to the battlefield/is,
      /return target (?:artifact|creature|permanent) card from your graveyard/i,
      /creature card in your graveyard.{0,120}return it to the battlefield/is,
      /may cast a creature spell from your graveyard/i,
    ],
    excludeSignals: [
      /you may cast any number of spells from among/i,
      /exile the top .* of (?:their|target opponent)/i,
      /cast .* from (?:an )?opponent/i,
    ],`,
      },
    ],
  },
]

for (const file of files) {
  let content = readFileSync(file.path, 'utf8')
  for (const patch of file.patches) {
    if (!content.includes(patch.from)) {
      console.error('Missing patch block in', file.path)
      process.exit(1)
    }
    content = content.replace(patch.from, patch.to)
  }
  writeFileSync(file.path, content)
  console.log('Updated', file.path)
}
