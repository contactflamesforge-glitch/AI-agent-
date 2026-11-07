from coldmail.quality import local_quality_check

def test_flags_empty_subject():
    result = local_quality_check("", "Hello there, I wanted to reach out about a service.")
    assert any("subject" in issue.lower() for issue in result["issues"])

def test_flags_deceptive_subject():
    result = local_quality_check("Re: our call", "Hello, this is a first message to introduce a service.")
    assert any("deceptive" in issue.lower() for issue in result["issues"])

def test_word_count():
    result = local_quality_check("Quick question", " ".join(["hello"] * 60))
    assert result["word_count"] == 60
