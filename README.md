
# Verple

**Verple** is a ridiculously serious, conservative universal version format, comparator, serializer, and protocol.

## Design Goals

- 🔒 **Ultra-conservative equality**: versions are considered different if any field differs (`release`, `prerelease`, `postrelease`, `devrelease`, `local`).
- ⚖ **Strict conservative ordering**: ordering is only permitted when local metadata matches exactly; otherwise ordering raises `ValueError` to avoid ambiguity.
- 🔎 **Multi-standard input support**: parses version strings from PEP 440, SemVer, Canonical, and Calendar Versioning (CalVer).
- 🔁 **Canonical serialization**: provides fully reversible serialization via `to_canonical_string()` and parsing via `from_canonical_string()`.
- 🧮 **Hashable and set-safe**: fully hashable and safe for use in sets and dictionaries, with hashes consistent with strict equality.
- 📦 **JSON-LD serialization**: supports semantic serialization with provenance (`sourceFormat` and `sourceInput` fields).
- 🔐 **Versioned deserialization protocol**: fully versioned serialization model allowing future-safe protocol evolution.
- 📚 **Use Case Domains**: reproducible builds, registries, deployment pipelines, archival systems, provenance tracking, scientific reproducibility.

## Supported Python Versions

- Python >= 3.10

## Installation

```bash
pip install verple
```

## Example Usage

```python
from verple import Verple

# Parse version string
v1 = Verple.parse("1.2.3a1.post2.dev3+build99")
print(v1.to_canonical_string())  # 1.2.3-a1.post2.dev3+build99

# Strict equality
v2 = Verple.parse("1.2.3a1.post2.dev3+build99")
assert v1 == v2

# Hashable and set-safe
versions = {v1, v2}
assert len(versions) == 1

# Conservative ordering (only if local metadata matches)
v3 = Verple.parse("1.2.4+build99")
assert v1 < v3

# JSON-LD serialization
jsonld = v1.to_jsonld()
v1_roundtrip = Verple.from_jsonld(jsonld)
assert v1 == v1_roundtrip
```

## Canonical Serialization Format

Verple canonical strings follow this grammar:

```
<release>[-<prerelease>][.post<N>][.dev<N>][+<local>]
```

Example:

- `1.2.3-a1.post2.dev3+build99`

## JSON-LD Serialization Format

Verple also supports semantic serialization:

```json
{
  "@context": "https://gitlab.com/willynilly/verple/-/raw/main/src/verple/context/v1.0.0.jsonld",
  "@type": "Verple",
  "verple": "1.0.0",
  "sourceFormat": "pep440",
  "sourceInput": "1.2.3a1.post2.dev3+build99",
  "release": [1, 2, 3],
  "prerelease": ["a", 1],
  "postrelease": 2,
  "devrelease": 3,
  "local": "build99"
}
```

This allows full provenance and schema evolution.

## Tests

This project uses `pytest`:

```bash
pytest tests/
```

## License

Apache 2.0

## Author

- Will Riley
- Co-developed with ChatGPT-4o during protocol design.

## Protocol Semantics

### Normalization

Verple normalizes versions into a fully structured model with the following fields:

- `release`: tuple of integers (major, minor, patch, or calendar parts)
- `prerelease`: tuple of `(label: str, num: int)` or `None`
- `postrelease`: integer or `None`
- `devrelease`: integer or `None`
- `local`: string or `None`
- `sourceInput`: original version string
- `sourceFormat`: the parsed format (`pep440`, `semver`, `canonical`, `calver`)

All formats (PEP 440, SemVer, Canonical, CalVer) are converted into this internal structure.

### Equality Algorithm

Two versions are equal if and only if all of the following fields are equal:

- `release`
- `prerelease`
- `postrelease`
- `devrelease`
- `local`

Fields are compared strictly; any difference implies inequality.

### Ordering Algorithm

Ordering is permitted only if both versions have identical `local` metadata. If `local` differs, ordering is refused.

If allowed, versions are compared using the tuple:

```
(
  release,
  prerelease_key(prerelease),
  postrelease or -1,
  devrelease or infinity
)
```

Where:

- `prerelease_key(None)` → `(infinity,)` (normal releases sort after prereleases)
- `prerelease_key((label, num))` → `(label, num)` (string then numeric comparison)

The algorithm aligns with PEP 440 precedence where applicable.

### Canonical Form Algorithm

Serialization via `to_canonical_string()` reconstructs the version string as:

```
<release>[-<prerelease>][.post<N>][.dev<N>][+<local>]
```

Fields that are `None` are omitted.

### JSON-LD Serialization

The full semantic model is serialized as JSON-LD, including provenance fields `sourceFormat` and `sourceInput` for full reproducibility.

## Field Definitions

The following fields are used throughout Verple's internal model, canonical serialization, and JSON-LD serialization:

| Field        | Type             | Meaning |
|--------------|------------------|-------------------------------------------------------------|
| `release`    | tuple of int     | Core version numbers: major.minor.patch or calendar parts |
| `prerelease` | tuple (str, int) or None | Pre-release stage (alpha, beta, rc, etc.) and stage number |
| `postrelease` | int or None     | Post-release revision applied after final release |
| `devrelease` | int or None      | Development release version for pre-release internal builds |
| `local`      | str or None      | Local build metadata identifier (build info, git hash, etc.) |
| `sourceInput` | str            | The original version string provided as input |
| `sourceFormat` | str          | The detected format: `pep440`, `semver`, `canonical`, or `calver` |
| `verple`     | str              | Serialization format version (e.g. `"1.0.0"`) |
| `@context`   | URL              | JSON-LD context URL defining linked data vocabulary |
| `@type`      | str              | Always `"Verple"` |

### Conceptual Definitions

- **release**: The main numeric version (e.g. `1.2.3`), structured as Major.Minor.Patch (SemVer, PEP 440) or Year.Month.[Day] (CalVer).

- **prerelease**: A pre-final release marker such as `alpha`, `beta`, or `rc`, optionally followed by a stage number (e.g. `rc1`).

- **postrelease**: Identifies patches or hotfixes applied after a final release (`.postN`).

- **devrelease**: Development snapshots issued before formal releases (`.devN`), typically for internal or unstable builds.

- **local**: Build metadata or local identifiers following `+build` semantics, capturing build environment or other internal state.

- **sourceInput**: The raw version string provided by the caller.

- **sourceFormat**: Indicates which parser was used to interpret the input (`pep440`, `semver`, `canonical`, `calver`).

- **verple**: The version of the Verple serialization protocol used to encode the JSON-LD document.

- **@context / @type**: JSON-LD linked data metadata used to enable semantic parsing of Verple objects.
