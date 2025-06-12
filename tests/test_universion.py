import pytest

from universion.universion import UniVersion

# ---- Equality Tests ----

@pytest.mark.parametrize("v1,v2,expected_equal", [
    ("1.2.3", "1.2.3", True),
    ("1.2.3", "1.2.3+local", False),
    ("1.2.3a1", "1.2.3a1", True),
    ("1.2.3a1", "1.2.3a2", False),
    ("1.2.3a1.post2.dev3+abc", "1.2.3a1.post2.dev3+abc", True),
    ("1.2.3a1.post2.dev3+abc", "1.2.3a1.post2.dev3+xyz", False),
])
def test_equality(v1, v2, expected_equal):
    sv1 = UniVersion.parse(v1)
    sv2 = UniVersion.parse(v2)
    assert (sv1 == sv2) == expected_equal

# ---- Hashability Tests ----

@pytest.mark.parametrize("versions,expected_set_size", [
    (["1.0.0", "1.0.0"], 1),
    (["1.0.0", "1.0.0+build1"], 2),
    (["1.0.0a1", "1.0.0a1.post1", "1.0.0a1.post1.dev1"], 3),
])
def test_hashability(versions, expected_set_size):
    version_set = {UniVersion.parse(v) for v in versions}
    assert len(version_set) == expected_set_size

# ---- Canonical Serialization Roundtrip ----

@pytest.mark.parametrize("version_string", [
    "1.0.0",
    "1.2.3a1",
    "1.2.3a1.post2",
    "1.2.3a1.post2.dev3",
    "1.2.3a1.post2.dev3+local",
])
def test_canonical_serialization_roundtrip(version_string):
    sv = UniVersion.parse(version_string)
    canonical = sv.to_canonical_string()
    sv2 = UniVersion.from_canonical_string(canonical)
    assert sv == sv2

# ---- JSON-LD Serialization Roundtrip ----

@pytest.mark.parametrize("version_string", [
    "1.0.0",
    "1.2.3a1",
    "1.2.3a1.post2.dev3+localdata"
])
def test_jsonld_serialization_roundtrip(version_string):
    sv = UniVersion.parse(version_string)
    data = sv.to_jsonld()
    sv2 = UniVersion.from_jsonld(data)
    assert sv == sv2

# ---- Ordering Tests ----

@pytest.mark.parametrize("v1,v2,expected_result", [
    ("1.2.3", "1.2.4", True),
    ("1.2.3a1", "1.2.3a2", True),
    ("1.2.3a1.post1", "1.2.3a1.post2", True),
    ("1.2.3a1.dev1", "1.2.3a1.dev2", True),
])
def test_ordering_comparable(v1, v2, expected_result):
    sv1 = UniVersion.parse(v1)
    sv2 = UniVersion.parse(v2)
    assert (sv1 < sv2) == expected_result

@pytest.mark.parametrize("v1,v2", [
    ("1.2.3+build1", "1.2.3+build2"),
    ("1.2.3a1+abc", "1.2.3a1+xyz"),
])
def test_ordering_incomparable(v1, v2):
    sv1 = UniVersion.parse(v1)
    sv2 = UniVersion.parse(v2)
    with pytest.raises(ValueError):
        _ = sv1 < sv2
