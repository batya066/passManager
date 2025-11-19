from __future__ import annotations

from dataclasses import dataclass
import secrets
import string
from typing import List


AMBIGUOUS = set("O0I1l|S5B8G6Z2")
SYMBOL_SETS = {
    "none": "",
    "soft": "!@#$%^&*?",
    "hard": "!@#$%^&*?-_=+[]{}()<>:;,./|~",
}


@dataclass
class GeneratorOptions:
    length: int = 24
    symbols: str = "soft"  # none | soft | hard
    allow_ambiguous: bool = False
    require_each_category: bool = True

    def validate(self) -> None:
        if self.length < 8:
            raise ValueError("Parola uzunluğu en az 8 olmalıdır.")
        if self.symbols not in SYMBOL_SETS:
            raise ValueError(f"Geçersiz sembol seti: {self.symbols}")


def _sanitize_characters(characters: str, allow_ambiguous: bool) -> str:
    if allow_ambiguous:
        return characters
    return "".join(ch for ch in characters if ch not in AMBIGUOUS)


def generate_password(options: GeneratorOptions) -> str:
    options.validate()
    rng = secrets.SystemRandom()
    lowercase = _sanitize_characters(string.ascii_lowercase, options.allow_ambiguous)
    uppercase = _sanitize_characters(string.ascii_uppercase, options.allow_ambiguous)
    digits = _sanitize_characters(string.digits, options.allow_ambiguous)
    symbols = _sanitize_characters(SYMBOL_SETS[options.symbols], options.allow_ambiguous)

    pools: List[str] = [lowercase, uppercase, digits]
    if symbols:
        pools.append(symbols)

    merged = "".join(pools)
    if len(set(merged)) < 10:
        raise ValueError("Karakter havuzu çok küçük. Parametreleri yeniden deneyin.")

    password_chars: List[str] = []
    if options.require_each_category:
        for pool in pools:
            password_chars.append(rng.choice(pool))

    while len(password_chars) < options.length:
        password_chars.append(rng.choice(merged))

    rng.shuffle(password_chars)
    return "".join(password_chars[: options.length])

