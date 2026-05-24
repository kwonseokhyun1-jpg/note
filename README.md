# Commander Helper

A Magic: The Gathering Commander toolkit:

1. **Find Commander**  Theme/keyword matching with optional popularity sorting
2. **Find Cards**  Natural language card search with semantic ability matching
3. **Helper**  Deck validation, upgrades, and playtest
4. **Finance**  Staples by color (non-lands), prices, deck value chart
5. **Judge**  Rules chatbot with Comprehensive Rules sources

## Run locally

```bash
npm install
cp .env.example .env   # optional OpenAI key for Judge AI
npm run build:data     # downloads commander + card DBs into public/data/
npm run dev
```

## Judge AI (optional)

Set `VITE_OPENAI_API_KEY` for deeper answers on complex scenarios. Without it, the Judge uses curated rules knowledge locally.

## Data

Card data and prices come from the [Scryfall API](https://scryfall.com/docs/api). Popularity ranks are included in Scryfall bulk data.
