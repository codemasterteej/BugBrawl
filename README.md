# BugBrawl
Application where a user uploads pictures of bugs that they find. The bugs then battle in a simulated environment to see whos the best!

## start up
1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

2. Install dependencies
pip install -r requirements.txt

3. Create .env file
echo "SECRET_KEY=your-secret-key-here" > .env

4. Run the app
python run.py

5. Visit http://localhost:6000

Proposed Project Strucuture:

```
BugBrawl/
├── app/
│   ── __init__.py
│   ── models.py
│   ── routes/
│   │   ── __init__.py <- dunder wrapper
│   │   ── main.py <- ties everything together
│   │   ── auth.py <-- for frontend user account auth
│   │   ── bugs.py <- creates a bug db
│   │   ── battle_engine.py <-battle engine for sim
│    ── templates/
│   │   ── base.html
│   │   ── index.html
│   │   ── dashboard.html
│   │   ── tournament creation/viewer
|   |   -- (others)
│   └── static/
│       ├── css/
│       └── java?
├── config.py
├── run.py <- python run.py to spin app up
└── requirements.txt
```


##To-do:

- refine battle engine
- create tournament format
- generate pokedex
- connect LLM narrator - anthropic, openai, ollama
- connect taxonomy api (inaturalist, wiki, etc)
