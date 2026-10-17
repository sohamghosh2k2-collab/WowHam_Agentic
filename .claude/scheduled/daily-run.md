# Scheduled daily run (fires 09:40 Europe/Berlin so the email lands by 10:00)

You are running unattended. Nobody can approve actions during this run.

1. Read `CLAUDE.md` and `memory/learned_rules.md`.
2. Run the `daily-news-brief` skill end to end for today (Europe/Berlin date):
   collect feedback replies from Gmail, then queries, collection,
   summary, benchmark, email.
3. Mondays only: also run the `startup-sourcing` skill for the last 7 days
   (focus from `config/startup_focus.yaml`). Add a "New deep-tech startups
   worth a look" section (top 5, one line each, with sources) to the brief
   before sending.
4. 1st of the month only: run `python3 tools/startup_db.py calibrate` and put
   the summary in the brief's scorecard.
5. **Never** run `tools/meta_ads.py create --live` or change any ad object.
   Read-only `insights` is allowed only if `data/ads/*/created.json` exists.
   In that case add a 3-line ads performance note.
6. Commit and push `memory/` and `data/` with message `brief: <date>`.
7. End with a 3-line status: sent yes/no (with the Gmail message id), quality
   score, and any errors. Never report the email as sent unless the Gmail
   tool confirmed it.
