name: 🔄 Update README dynamic sections

on:
  schedule:
    # Runs every day at 18:00 IST (12:30 UTC)
    - cron: "30 12 * * *"
  workflow_dispatch: {}

jobs:
  update-readme:
    runs-on: ubuntu-latest

    permissions:
      contents: write

    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Update dynamic sections
        run: |
          python - << 'PY'
          import re, random, datetime, pathlib

          path = pathlib.Path("README.md")
          text = path.read_text(encoding="utf-8")

          # IST time (UTC+5:30)
          ist = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
          last_updated = ist.strftime("%Y-%m-%d %H:%M IST")

          quotes = [
              "Discipline compounds. Tiny steps, big outcomes.",
              "Code. Ship. Learn. Repeat.",
              "Consistency beats motivation.",
              "Build things that outlive the tutorial.",
              "Your GitHub is your portfolio. Treat it like one.",
              "Small progress every day becomes unfair advantage.",
          ]
          quote = random.choice(quotes)

          def replace(tag, new_value, src):
              pattern = rf"<!--{tag}-->(.*?)<!--/{tag}-->"
              repl = f"<!--{tag}-->{new_value}<!--/{tag}-->"
              return re.sub(pattern, repl, src, flags=re.DOTALL)

          new_text = text
          new_text = replace("LAST_UPDATED", last_updated, new_text)
          new_text = replace("RANDOM_QUOTE", quote, new_text)

          if new_text != text:
              path.write_text(new_text, encoding="utf-8")
              print("README updated.")
          else:
              print("No changes to README.")
          PY

      - name: Commit & push if changed
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          if [ -n "$(git status --porcelain)" ]; then
            git config user.name "github-actions[bot]"
            git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
            git add README.md
            git commit -m "chore: 🔄 update dynamic README sections" || exit 0
            git push
          else
            echo "No changes to commit."
