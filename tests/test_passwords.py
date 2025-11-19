from pass_manager.passwords import AMBIGUOUS, GeneratorOptions, generate_password


def test_generate_password_default_length():
    options = GeneratorOptions(length=30)
    password = generate_password(options)
    assert len(password) == 30
    assert any(ch.islower() for ch in password)
    assert any(ch.isupper() for ch in password)
    assert any(ch.isdigit() for ch in password)


def test_generate_password_avoids_ambiguous_chars():
    options = GeneratorOptions(length=40, allow_ambiguous=False)
    password = generate_password(options)
    assert not any(ch in AMBIGUOUS for ch in password)

