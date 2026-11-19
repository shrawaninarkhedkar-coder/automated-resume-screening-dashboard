"""
src/cleaner.py
Module responsible for NLP text cleaning, normalization, and stopword removal.
Preserves technical terms like C++, C#, .NET, Node.js.
"""

import re

# Comprehensive list of standard English stopwords to filter out non-informative words
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't",
    "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself",
    "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into",
    "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our",
    "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's",
    "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs",
    "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't",
    "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's",
    "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't",
    "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself",
    "yourselves", "responsibilities", "responsible", "duty", "duties", "including", "worked", "working"
}


def clean_text(raw_text: str, remove_stopwords: bool = True) -> str:
    """
    Cleans raw resume or job description text.
    - Lowers case
    - Removes URLs and email addresses
    - Removes excessive whitespaces and line breaks
    - Protects special tokens (c++, c#, .net)
    - Optionally removes standard stopwords
    """
    if not raw_text or not isinstance(raw_text, str):
        return ""

    text = raw_text.lower()

    # 1. Protect special programming language tokens
    text = re.sub(r'\bc\+\+\b', ' cplusplus ', text)
    text = re.sub(r'\bc\#\b', ' csharp ', text)
    text = re.sub(r'\b\.net\b', ' dotnet ', text)
    text = re.sub(r'\bnode\.js\b', ' nodejs ', text)
    text = re.sub(r'\bnext\.js\b', ' nextjs ', text)
    text = re.sub(r'\bvue\.js\b', ' vuejs ', text)

    # 2. Remove URLs, emails, phone numbers
    text = re.sub(r'http\S+|www\.\S+', ' ', text)
    text = re.sub(r'\S+@\S+', ' ', text)
    text = re.sub(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', ' ', text)

    # 3. Remove non-alphanumeric characters except basic word separators
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)

    # 4. Tokenize by whitespace
    words = text.split()

    # 5. Restore aliases back to canonical forms if desired or keep clean tokens
    alias_map = {
        "cplusplus": "c++",
        "csharp": "c#",
        "dotnet": ".net",
        "nodejs": "node.js",
        "nextjs": "next.js",
        "vuejs": "vue.js"
    }

    cleaned_words = []
    for word in words:
        mapped_word = alias_map.get(word, word)
        if remove_stopwords:
            if word not in STOPWORDS and len(word) > 1:
                cleaned_words.append(mapped_word)
        else:
            if len(word) > 1:
                cleaned_words.append(mapped_word)

    return " ".join(cleaned_words)
