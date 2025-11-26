# BugBrawl
Application where a user uploads pictures of bugs that they find. The bugs then battle in a simulated environment to see whos the best!


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
