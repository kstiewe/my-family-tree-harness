"""The data model: allowed fields and values of the YAML files.

This module is the single source of truth for validation and for `build.py --schema`;
docs/data-format.md describes the same model in prose.
"""

from __future__ import annotations

from .i18n import tr

FILES = {"project": "project.yaml", "persons": "persons.yaml", "families": "families.yaml",
         "places": "places.yaml", "sources": "sources.yaml"}
ID_PREFIX = {"persons": "I", "families": "F", "places": "P", "sources": "S"}

PROJECT_KEYS = {"name", "author", "proband", "surnames", "regions", "language"}
PERSON_KEYS = {"id", "given", "surname", "married_surnames", "variants", "sex", "living", "religion",
               "birth", "baptism", "death", "burial", "events", "occupation", "confidence", "notes", "todo", "quote"}
LIFE_EVENTS = ("birth", "baptism", "death", "burial")
EVENT_KEYS = {"date", "place", "sources", "note", "age", "cause", "confidence", "godparents"}
EXTRA_EVENT_KEYS = EVENT_KEYS | {"type", "value"}
EVENT_TYPES = ("residence", "occupation", "emigration", "military", "census", "confirmation", "education", "signature",
               "other")
FAMILY_KEYS = {"id", "husband", "wife", "marriage", "divorce", "children", "confidence", "notes", "todo"}
MARRIAGE_KEYS = EVENT_KEYS | {"husband_age", "wife_age", "witnesses"}
QUOTE_KEYS = {"text", "source", "note"}
# `value` of a `signature` event: the person signed the record, or made a mark (a cross) as unable to write.
SIGNATURES = {"signed", "mark"}
PLACE_KEYS = {"id", "name", "type", "aliases", "parish", "denomination", "partition", "admin", "today",
              "country", "coords", "geneteka_region", "records", "notes"}
SOURCE_KEYS = {"id", "type", "title", "parish", "year", "act", "repository", "signature", "url", "quality",
               "accessed", "informant", "language", "transcription", "notes"}
SEXES = {"M", "F", "U"}
CONFIDENCE = {"confirmed", "probable", "hypothesis"}

# Partitions of Poland 1795–1918. Polish values are accepted as aliases of the English ones.
PARTITIONS = {"russian": "russian", "prussian": "prussian", "austrian": "austrian",
              "rosyjski": "russian", "pruski": "prussian", "austriacki": "austrian"}

# Place types the code reasons about. Any other type (village, town, manor …) is free text.
PLACE_TYPE_ALIASES = {"parish": "parish", "parafia": "parish", "region": "region",
                      "commune": "commune", "gmina": "commune", "county": "county", "powiat": "county",
                      "country": "country", "kraj": "country"}
NO_PARISH_NEEDED = {"parish", "region", "commune", "county", "country"}

SOURCE_TYPES = {"birth_record", "baptism_record", "marriage_record", "death_record", "burial_record",
                "civil_record", "index", "census", "population_register", "family_document", "photo",
                "gravestone", "oral", "online_tree", "publication", "other"}
SOURCE_QUALITY = {"original", "image", "transcription", "index", "derivative", "oral"}

# Language of the original document (ISO 639-1; `la` = Latin). A list when a record mixes languages.
LANGUAGES = {"pl": "Polish", "la": "Latin", "de": "German", "ru": "Russian", "uk": "Ukrainian", "be": "Belarusian",
             "lt": "Lithuanian", "lv": "Latvian", "cs": "Czech", "sk": "Slovak", "hu": "Hungarian", "yi": "Yiddish",
             "he": "Hebrew", "en": "English", "fr": "French", "it": "Italian", "nl": "Dutch", "sv": "Swedish"}


def place_kind(place: dict) -> str | None:
    """Canonical type of a place (`parafia` → `parish`), or None for free-text types."""
    return PLACE_TYPE_ALIASES.get(str(place.get("type") or "").strip().lower())


def event_label(key: str) -> str:
    return {"birth": tr("Birth"), "baptism": tr("Baptism"), "death": tr("Death"), "burial": tr("Burial")}[key]


def event_type_label(kind: str | None) -> str:
    labels = {"residence": tr("Residence"), "occupation": tr("Occupation"), "emigration": tr("Emigration"),
              "military": tr("Military service"), "census": tr("Census"), "confirmation": tr("Confirmation"),
              "education": tr("Education"), "signature": tr("Signature"), "other": tr("Other")}
    return labels.get(kind or "", "?")


def language_names(value) -> list[str]:
    codes = value if isinstance(value, list) else [value] if value else []
    return [tr(LANGUAGES[c]) if c in LANGUAGES else str(c) for c in codes]


def schema_json() -> dict:
    """Machine-readable description of the data model (for agents)."""
    return {
        "files": FILES,
        "id_pattern": {k: f"{p}0001 (prefix {p} + at least 4 digits)" for k, p in ID_PREFIX.items()},
        "date_patterns": ["1850-03-12", "1850-03", "1850", "~1850 (about)", "<1870 (before)", ">1845 (after)",
                          "1848..1852 (between)"],
        "project": sorted(PROJECT_KEYS),
        "person": sorted(PERSON_KEYS),
        "person_life_events": list(LIFE_EVENTS),
        "event": sorted(EVENT_KEYS),
        "extra_event": sorted(EXTRA_EVENT_KEYS),
        "extra_event_types": list(EVENT_TYPES),
        "family": sorted(FAMILY_KEYS),
        "marriage": sorted(MARRIAGE_KEYS),
        "person_quote": sorted(QUOTE_KEYS),
        "place": sorted(PLACE_KEYS),
        "source": sorted(SOURCE_KEYS),
        "enums": {
            "sex": sorted(SEXES), "confidence": sorted(CONFIDENCE),
            "partition": sorted(PARTITIONS), "place_type_with_meaning": sorted(PLACE_TYPE_ALIASES),
            "source_type": sorted(SOURCE_TYPES), "source_quality": sorted(SOURCE_QUALITY),
            "source_language": LANGUAGES, "signature_value": sorted(SIGNATURES),
        },
        "field_notes": {
            "place.coords": "[latitude, longitude] in decimal degrees (WGS84), optional. A place without it is shown at "
                            "its parish's coords on the map; write where the coordinates come from in notes.",
            "event.confidence": "optional: probable / hypothesis marks one fact (the card says \"probably\").",
            "event.godparents": "birth/baptism: the godparents as written in the record (text or list).",
            "event.type=occupation": "value = the occupation or status as written in the record (one per record, "
                                     "with its date and source); the card shows them in order.",
            "event.type=residence": "value = the house number or address, if the record gives one.",
            "event.type=signature": "value = signed (the person signed the record) or mark (made a cross).",
            "person.quote": "optional {text, source, note}: one short sentence the card shows as a quote.",
        },
        "references": {
            "event.place": "places", "event.sources[]": "sources", "family.husband": "persons",
            "family.wife": "persons", "family.children[]": "persons", "place.parish": "places",
            "source.parish": "places", "project.proband": "persons", "person.quote.source": "sources",
        },
    }
