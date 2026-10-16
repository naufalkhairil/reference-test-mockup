# Streamlit Mockup Test Viewer

Browse and take the quiz mockups stored in `mockup-test/`. The app reads each Markdown file at startup and adds it to the chapter selector. Use **Check answer** under a question for immediate feedback, or submit the full quiz to see your score and review all explanations and source references.

## Requirements

- Python 3.9 or newer
- pip

## Start the app

From this directory, install the dependency and launch Streamlit:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit prints a local URL in the terminal. Open it in a browser to use the viewer.

## Add or update mockups

Put Markdown quiz files in `mockup-test/`. Each file should have a top-level title, numbered `## Question` sections, A–D answer options, and an answer plus explanation inside a `<details>` block. The app discovers the files automatically the next time it starts.

## Project files

- `app.py` — Streamlit interface and Markdown quiz reader
- `requirements.txt` — Python app dependency
- `mockup-test/` — quiz content displayed by the app
