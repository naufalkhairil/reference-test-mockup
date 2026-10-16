from __future__ import annotations

import re
from pathlib import Path

import streamlit as st


APP_DIR = Path(__file__).resolve().parent
MOCKUP_DIR = APP_DIR / "mockup-test"
OPTION_RE = re.compile(r"^([A-D])\.\s+(.*)$")


def parse_mockup(path: Path) -> dict:
    """Read a quiz mockup from the Markdown source files."""
    text = path.read_text(encoding="utf-8")
    title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else path.stem
    chunks = re.split(r"^## Question\s+(\d+)\s*$", text, flags=re.MULTILINE)
    questions = []

    for index in range(1, len(chunks), 2):
        number = int(chunks[index])
        body = chunks[index + 1]
        details = re.search(r"<details>\s*<summary>Show answer and explanation</summary>(.*?)</details>", body, re.S)
        question_part = body[: details.start()] if details else body
        lines = [line.strip() for line in question_part.strip().splitlines() if line.strip()]
        prompt_lines, options = [], []
        for line in lines:
            match = OPTION_RE.match(line)
            if match:
                options.append((match.group(1), match.group(2).strip()))
            else:
                prompt_lines.append(line)

        answer_match = re.search(r"\*\*Answer:\s*([A-D])\*\*", details.group(1) if details else "")
        if prompt_lines and options and answer_match:
            explanation = details.group(1)
            explanation = re.sub(r"^\s*\*\*Answer:\s*[A-D]\*\*\s*", "", explanation, flags=re.S)
            explanation = re.sub(r"^\s*", "", explanation)
            questions.append({
                "number": number,
                "prompt": "\n\n".join(prompt_lines),
                "options": options,
                "answer": answer_match.group(1),
                "explanation": explanation.strip(),
            })

    return {"title": title, "questions": questions, "source": text}


st.set_page_config(
    page_title="Alibaba LLM Pro · Mockup Lab",
    page_icon="✳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --ink:#17251f; --muted:#718078; --green:#16855c; --lime:#dcf36a; --line:#e5eae6; --paper:#f7f9f6; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--ink); }
.stApp { background:var(--paper); }
[data-testid="stSidebar"] { background:#eef3ee; border-right:1px solid var(--line); }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1 { font-family:Manrope,sans-serif; letter-spacing:-.04em; }
.hero { background:#173d31; color:white; padding:34px 40px; border-radius:20px; position:relative; overflow:hidden; margin:8px 0 26px; }
.hero:after { content:'✳'; position:absolute; right:34px; top:-55px; font-size:220px; line-height:1; color:#255b47; font-weight:800; }
.eyebrow { text-transform:uppercase; letter-spacing:.16em; font-size:11px; font-weight:700; color:#bde8a4; }
.hero h1 { font:800 34px/1.15 Manrope,sans-serif; letter-spacing:-.045em; margin:12px 0 10px; color:white; position:relative; z-index:1; }
.hero p { max-width:610px; color:#d1e0d7; margin:0; font-size:15px; position:relative; z-index:1; }
.meta { display:flex; gap:10px; margin-top:22px; position:relative; z-index:1; }
.pill { display:inline-block; border:1px solid #547367; color:#e1eee6; border-radius:999px; padding:6px 11px; font-size:12px; }
.section-label { color:var(--green); font-size:11px; font-weight:700; letter-spacing:.13em; text-transform:uppercase; }
.quiz-card { background:white; border:1px solid var(--line); border-radius:16px; padding:21px 24px 16px; margin:12px 0; box-shadow:0 3px 12px #173d3108; }
.question-number { color:var(--green); font-size:11px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; }
.question-text { color:var(--ink); font:600 17px/1.5 Manrope,sans-serif; margin:8px 0 4px; }
.stButton button[kind="primary"] { background:#16855c; border-color:#16855c; border-radius:10px; font-weight:700; }
.stButton button[kind="primary"]:hover { background:#106b49; border-color:#106b49; }
div[data-testid="stRadio"] label { background:white; border:1px solid #e8ede9; padding:10px 13px; border-radius:10px; margin:5px 0; }
div[data-testid="stRadio"] label:hover { border-color:#92c6a7; }
.score-box { background:#eaf4ed; border:1px solid #d5e8d9; border-radius:14px; padding:20px 24px; margin:12px 0 20px; }
div[data-testid="stProgress"] > div > div { background:#16855c; }
</style>
""", unsafe_allow_html=True)


files = sorted(MOCKUP_DIR.glob("*.md"))
if not files:
    st.error(f"No Markdown mockups found in {MOCKUP_DIR}")
    st.stop()

quizzes = [parse_mockup(path) for path in files]
labels = [quiz["title"].replace("Mockup Test: ", "") for quiz in quizzes]

with st.sidebar:
    st.markdown("# ✳ Mockup Lab")
    st.caption("ALIBABA LLM PRO · COURSE TESTS")
    st.markdown("---")
    selected_label = st.selectbox("Choose a mockup", labels, label_visibility="visible")
    selected_index = labels.index(selected_label)
    current = quizzes[selected_index]
    st.markdown("---")
    st.markdown(f"**{len(quizzes)}** mockups · **{sum(len(q['questions']) for q in quizzes)}** questions")
    st.caption("Select a chapter to begin. Your answers stay in this browser session.")

quiz_key = f"quiz_{selected_index}"
if st.session_state.get("active_quiz") != quiz_key:
    st.session_state.active_quiz = quiz_key
    st.session_state.pop(f"submitted_{quiz_key}", None)

st.markdown(f"""
<div class="hero">
  <div class="eyebrow">Alibaba LLM Pro · Knowledge Check</div>
  <h1>{current['title'].replace('Mockup Test: ', '')}</h1>
  <p>Choose the best answer for each question. Submit when you’re ready to review your score and explanations.</p>
  <div class="meta"><span class="pill">{len(current['questions'])} questions</span><span class="pill">Multiple choice</span><span class="pill">Self paced</span></div>
</div>
""", unsafe_allow_html=True)

if not current["questions"]:
    st.warning("This mockup could not be parsed. Open the source preview below to inspect its Markdown structure.")
    st.stop()

st.markdown('<div class="section-label">Your assessment</div>', unsafe_allow_html=True)
submitted_key = f"submitted_{quiz_key}"
submitted = st.session_state.get(submitted_key, False)
answers = {}

for question in current["questions"]:
    number = question["number"]
    st.markdown(f"""<div class="quiz-card"><div class="question-number">Question {number:02d}</div><div class="question-text">{question['prompt']}</div></div>""", unsafe_allow_html=True)
    choices = [f"{letter}  ·  {text}" for letter, text in question["options"]]
    option_to_letter = {choice: letter for choice, (letter, _) in zip(choices, question["options"])}
    prior = st.session_state.get(f"answer_{quiz_key}_{number}")
    start_index = next((i for i, choice in enumerate(choices) if option_to_letter[choice] == prior), None)
    chosen = st.radio("Select one answer", choices, index=start_index, key=f"answer_{quiz_key}_{number}", label_visibility="collapsed", disabled=submitted)
    answers[number] = option_to_letter.get(chosen)
    checked_key = f"checked_{quiz_key}_{number}"
    check_clicked = st.button("Check answer", key=f"check_{quiz_key}_{number}", disabled=submitted)
    if check_clicked:
        if not answers[number]:
            st.warning("Choose an answer first.")
        else:
            st.session_state[checked_key] = True

    if submitted or st.session_state.get(checked_key, False):
        is_correct = answers[number] == question["answer"]
        if is_correct:
            st.success("Correct")
        else:
            st.error(f"Not quite · Correct answer: {question['answer']}")
        st.markdown(question["explanation"])

if not submitted:
    if st.button("Submit answers", type="primary", use_container_width=False):
        missing = [q["number"] for q in current["questions"] if not answers.get(q["number"])]
        if missing:
            st.warning(f"Answer every question before submitting. Still to go: {', '.join(map(str, missing))}.")
        else:
            st.session_state[submitted_key] = True
            st.rerun()
else:
    correct = sum(answers.get(q["number"]) == q["answer"] for q in current["questions"])
    total = len(current["questions"])
    st.markdown(f'<div class="score-box"><div class="section-label">Assessment complete</div><h2 style="margin:6px 0 4px">{correct} / {total} correct</h2><div style="color:#53675c">{round(correct / total * 100)}% · Review the explanations above, then try again if you like.</div></div>', unsafe_allow_html=True)
    st.progress(correct / total)
    if st.button("Try again"):
        for q in current["questions"]:
            st.session_state.pop(f"answer_{quiz_key}_{q['number']}", None)
            st.session_state.pop(f"checked_{quiz_key}_{q['number']}", None)
        st.session_state.pop(submitted_key, None)
        st.rerun()

with st.expander("View original mockup source"):
    st.markdown(current["source"])

st.markdown("<div style='text-align:center;color:#839087;font-size:12px;padding:28px 0 12px'>ALIBABA LLM PRO · MOCKUP TEST ENVIRONMENT</div>", unsafe_allow_html=True)
