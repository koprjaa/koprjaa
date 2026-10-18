#
# Project: koprjaa
# File:    test_readme.py
#
# Description:
# Tests for profile README existence, section presence, and link validity.
#
# Author:
# Jan Alexandr Kopřiva
# jan.alexandr.kopriva@gmail.com
#
# License: MIT
#

"""Validační testy pro profilové README: existence, sekce, platnost odkazů."""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
README = REPO_ROOT / "README.md"

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
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


def test_readme_has_expected_blocks():
    # profil je neofetch karta (světlé a tmavé SVG) a sbalený stack
    text = README.read_text(encoding="utf-8")
    for svg in ("neofetch-light.svg", "neofetch-dark.svg"):
        assert svg in text, f"README neodkazuje na {svg}"
        assert (README.parent / svg).is_file(), f"chybí {svg}"
    alt = re.search(r'alt="([^"]+)"', text).group(1)
    for needle in ("AI engineer", "Prague University of Economics and Business", "linkedin.com/in/"):
        assert needle in alt, f"chybí {needle!r} v alt textu karty"
    assert "<summary>STACK</summary>" in text


def test_readme_relative_links_all_exist():
    text = README.read_text(encoding="utf-8")
    assert find_broken_relative_links(text, README.parent) == []


def test_readme_has_external_links_sanity_check():
    # ověří, že extraktor skutečně něco najde (vyloučí vacuous pass výš)
    text = README.read_text(encoding="utf-8")
    targets = LINK_RE.findall(text)
    external = [t for t in targets if SCHEME_RE.match(t)]
    assert len(external) >= 1


def test_link_checker_catches_missing_relative_file(tmp_path):
    md = "see [doc](missing/file.md) and ![pic](missing.png)"
    broken = find_broken_relative_links(md, tmp_path)
    assert broken == ["missing/file.md", "missing.png"]


def test_link_checker_accepts_existing_relative_file(tmp_path):
    (tmp_path / "exists.md").write_text("x")
    md = "see [doc](exists.md) and [ext](https://example.com) and [anchor](#top)"
    broken = find_broken_relative_links(md, tmp_path)
    assert broken == []
