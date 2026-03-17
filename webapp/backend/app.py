import json
import re
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from analysis.compound_analyzer import translate_compound
from generator.rule_based_translator import (
    apply_grammar_rules,
    apply_rules_to_word,
    load_grammar,
    load_model,
    preserve_case,
    translate_sentence,
)


class TranslateRequest(BaseModel):
    text: str
    mode: str = "auto"  # auto | word | sentence | text


class TranslateResponse(BaseModel):
    input_text: str
    translated_text: str
    mode_used: str


app = FastAPI(title="Bischemerisch Translator", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL = load_model()
GRAMMAR = load_grammar()


def _translate_word_extended(word: str) -> str:
    clean = word.lower()
    dictionary = MODEL["direct_dictionary"]

    if clean in dictionary:
        return preserve_case(word, dictionary[clean])

    compound = translate_compound(clean, MODEL)
    if compound:
        return preserve_case(word, compound)

    transformed = apply_rules_to_word(clean, MODEL["rules"])

    for rule in GRAMMAR.get("auto_phonetic_rules", []):
        src = rule.get("src", "")
        dst = rule.get("dst", "")
        if src and src in transformed:
            transformed = transformed.replace(src, dst)

    return preserve_case(word, transformed)


def _translate_text_block(text: str) -> str:
    lines = text.splitlines()
    translated_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            translated_lines.append("")
            continue

        sentences = re.split(r"(?<=[.!?])\s+", stripped)
        translated_sentences = [translate_sentence(sentence, MODEL) for sentence in sentences if sentence]
        translated_lines.append(" ".join(translated_sentences))

    return "\n".join(translated_lines)


def translate_text(text: str, mode: str = "auto") -> tuple[str, str]:
    source = text.strip()
    if not source:
        return "", "auto"

    chosen_mode = mode
    if mode == "auto":
        if re.fullmatch(r"[\wäöüßÄÖÜ-]+", source, flags=re.UNICODE):
            chosen_mode = "word"
        elif len(source.split()) <= 12 and "\n" not in source:
            chosen_mode = "sentence"
        else:
            chosen_mode = "text"

    if chosen_mode == "word":
        translated = _translate_word_extended(source)
    elif chosen_mode == "sentence":
        translated = translate_sentence(source, MODEL)
    else:
        translated = _translate_text_block(source)

    translated = apply_grammar_rules(translated)
    return translated, chosen_mode


@app.post("/api/translate", response_model=TranslateResponse)
def api_translate(payload: TranslateRequest):
    translated, mode_used = translate_text(payload.text, payload.mode)
    return TranslateResponse(
        input_text=payload.text,
        translated_text=translated,
        mode_used=mode_used,
    )


FRONTEND_DIR = BASE_DIR / "webapp" / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
