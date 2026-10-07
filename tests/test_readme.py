"""Validační testy pro profilové README: existence, sekce, platnost odkazů."""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
README = REPO_ROOT / "README.md"

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADER_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def find_broken_relative_links(markdown_text: str, base_dir: Path) -> list[str]:
    """Vrátí relativní odkazy/obrázky z markdownu, které na disku neexistují.

    Externí URL (mají schéma jako http:, https:, mailto:) a čisté
    in-page anchory (#sekce) se přeskakují beze síťové kontroly.
    """
    broken = []
    for target in LINK_RE.findall(markdown_text):
        if target.startswith("#") or SCHEME_RE.match(target):
            continue
        clean_target = target.split("#", 1)[0]
        if not clean_target:
            continue
        if not (base_dir / clean_target).exists():
            broken.append(target)
    return broken


def test_readme_exists_and_nonempty():
    assert README.is_file()
    text = README.read_text(encoding="utf-8").strip()
    assert len(text) > 200


def test_readme_has_expected_headers():
    text = README.read_text(encoding="utf-8")
    headers = [(len(level), title) for level, title in HEADER_RE.findall(text)]
    expected = [
        (1, "Jan Alexandr Kopřiva"),
        (2, "Projects"),
        (2, "Contact"),
    ]
    for item in expected:
        assert item in headers, f"chybí sekce {item} v README"


def test_readme_relative_links_all_exist():
    text = README.read_text(encoding="utf-8")
    assert find_broken_relative_links(text, README.parent) == []


def test_readme_has_external_links_sanity_check():
    # ověří, že extraktor skutečně něco najde (vyloučí vacuous pass výš)
    text = README.read_text(encoding="utf-8")
    targets = LINK_RE.findall(text)
    external = [t for t in targets if SCHEME_RE.match(t)]
    assert len(external) >= 5


def test_link_checker_catches_missing_relative_file(tmp_path):
    md = "see [doc](missing/file.md) and ![pic](missing.png)"
    broken = find_broken_relative_links(md, tmp_path)
    assert broken == ["missing/file.md", "missing.png"]


def test_link_checker_accepts_existing_relative_file(tmp_path):
    (tmp_path / "exists.md").write_text("x")
    md = "see [doc](exists.md) and [ext](https://example.com) and [anchor](#top)"
    broken = find_broken_relative_links(md, tmp_path)
    assert broken == []
