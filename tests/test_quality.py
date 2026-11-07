from coldmail.quality import local_quality_check


def test_flags_empty_subject():
    result = local_quality_check("", "Hello there, I wanted to reach out about a service.")
    assert any("subject" in issue.lower() for issue in result["issues"])


def test_flags_deceptive_subject():
    result = local_quality_check("Re: our call", "Hello, this is a first message to introduce a service.")
    assert any("deceptive" in issue.lower() for issue in result["issues"])


def test_word_count():
    result = local_quality_check("A useful subject", " ".join(["hello"] * 60))
    assert result["word_count"] == 60


def test_flags_stock_marketing_language():
    result = local_quality_check(
        "A useful subject",
        "I wanted to reach out and unlock your business potential with a game-changer. " + " ".join(["hello"] * 30)
    )
    assert any("cliché" in issue.lower() or "cliche" in issue.lower() for issue in result["issues"])


def test_flags_unverified_observation():
    result = local_quality_check(
        "A useful subject",
        "I noticed your website has a problem. " + " ".join(["hello"] * 30)
    )
    assert any("unsupported" in issue.lower() for issue in result["issues"])


def test_does_not_flag_observation_when_facts_supplied():
    result = local_quality_check(
        "A useful subject",
        "I noticed your website has a problem. " + " ".join(["hello"] * 30),
        verified_facts={"source": "official website", "fact": "contact page is broken"}
    )
    assert not any("unsupported" in issue.lower() for issue in result["issues"])


def test_flags_unresolved_merge_fields():
    result = local_quality_check(
        "A useful subject",
        "Hi [First Name], this is a note about your business and a useful service. " + " ".join(["hello"] * 25)
    )
    assert any("merge fields" in issue.lower() for issue in result["issues"])
