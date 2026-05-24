# MTG Minigames

Commander card minigames extracted from Commander Helper for standalone expansion.

## Games

- **Art Guess** — name the card from a zoomed-in art crop
- **Unscramble** — unscramble the card name

Both share easy/hard modes (EDHREC staples vs full database), five guesses, streak tracking, and progressive hints: CMC → type → colors → USD price.

## Layout

```
mtgminigames/
  src/
    games/          Art Guess, Unscramble
    shared/         shared UI and game logic
    index.ts        public exports
```

## Current dependency

Games currently import the card database and utilities from `../mtg/src`. When expanding this package, move or duplicate those libs here and add a standalone Vite app entry point.

## Usage in Commander Helper

```tsx
import { ArtGuessGame, UnscrambleGame } from '@mtgminigames'
```
