import re
from typing import TYPE_CHECKING

from text_to_num import alpha2digit

if TYPE_CHECKING:
    from besser.bot.nlp.nlp_engine import NLPEngine


def ner_number(sentence: str, nlp_engine: 'NLPEngine') -> tuple[str, str, dict]:
    # First, we parse any number in the sentence expressed in natural language (e.g. "five") to actual numbers
    language = nlp_engine.get_property('language')
    sentence = alpha2digit(sentence, lang=language)

    # Negative/positive numbers with optional point/comma followed by more digits
    regex = re.compile(r'(\b|[-+])\d+\.?\d*([.,]\d+)?\b')
    search = regex.search(sentence)
    if search is None:
        return None, None, None
    matched_frag = search.group(0)
    formatted_frag = matched_frag.replace(',', '.').replace('+', '')
    sentence = sentence[:search.span(0)[0]] + formatted_frag + sentence[search.span(0)[1]:]
    return sentence, formatted_frag, {}
