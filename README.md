## Frontdesk BE - Backend

#### Prerequisite

- Python 3.10+
- Node.js
- pnpm `(npm i -g pnpm)`

### SETUP:

0. Change directory to `frontdesk-be`

```bash
cd frontdesk-be
```

1. Create virtual env & activate it

```bash
python3 -m venv venv
source venv/bin/activate # MacOS
```

2. Install dependency

```bash
pip install -r requirements.txt
```

3. Download files

```bash
python3 agent.py download-files
```

Set up the environment by copying `.env.example` to `.env.local` and filling in the required values:

- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `GOOGLE_API_KEY`
- `CARTESIA_API_KEY`
- `DEEPGRAM_API_KEY`

4. Run both agent & api server

```bash
fastapi dev app/main.py # FastAPI server
python agent.py dev # LiveKit Agent
```

## Frontdesk FE - Frontend

0. Change directory to `frontdesk-fe`

```bash
cd frontdesk-fe
```

1. Install dependency

```bash
pnpm install
```

2. Run the server

```bash
pnpm dev
```
