GREETINGS = {"en": "Hello, {name}!", "sv": "Hej, {name}!"}


def greeting(name: str, lang: str = "en") -> str:
    """Return a greeting for ``name`` in ``lang``.

    Raises ValueError for an empty name or an unsupported language.
    """
    name = name.strip()
    if not name:
        raise ValueError("name must not be empty")
    if lang not in GREETINGS:
        raise ValueError(f"unsupported language: {lang}")
    return GREETINGS[lang].format(name=name)
