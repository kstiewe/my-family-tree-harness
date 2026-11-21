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
               "birth", "baptism", "death", "burial", "events", "occupation", "confidence", "notes", "todo", "quote",
               "conflicts", "confidence_override", "identity"}
LIFE_EVENTS = ("birth", "baptism", "death", "burial")
EVENT_KEYS = {"date", "place", "sources", "note", "age", "cause", "confidence", "godparents"}
EXTRA_EVENT_KEYS = EVENT_KEYS | {"type", "value"}
EVENT_TYPES = ("residence", "occupation", "emigration", "military", "census", "confirmation", "education", "signature",
               "other")
FAMILY_KEYS = {"id", "husband", "wife", "marriage", "divorce", "children", "confidence", "notes", "todo", "conflicts",
               "confidence_override"}
MARRIAGE_KEYS = EVENT_KEYS | {"husband_age", "wife_age", "witnesses"}
QUOTE_KEYS = {"text", "source", "note"}
# `value` of a `signature` event: the person signed the record, or made a mark (a cross) as unable to write.
SIGNATURES = {"signed", "mark"}
PLACE_KEYS = {"id", "name", "type", "aliases", "parish", "denomination", "partition", "admin", "today",
              "country", "coords", "geneteka_region", "records", "notes"}
SOURCE_KEYS = {"id", "type", "title", "parish", "year", "act", "repository", "signature", "url", "quality",
               "accessed", "informant", "language", "file", "transcription", "notes", "classification", "information",
               "evidence", "same_record_as", "derived_from"}
# Where the workspace keeps local copies of sources (scans, saved pages); `source.file` points into it.
SCANS_DIR = "research/skany"
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

# Evidence analysis (familytree/confidence.py, docs/confidence.md). Optional overrides of a source's defaults:
SOURCE_CLASSES = {"original", "derivative", "authored"}      # `classification`: what kind of source it is
INFORMATION = {"primary", "secondary"}                       # `information`: first-hand at the time, or not
EVIDENCE = {"direct", "indirect"}                            # `evidence`: answers the question alone (names the parents)
# `conflicts` of a person or a family: what disagrees, whether it is resolved, and which score it touches.
CONFLICT_KEYS = {"about", "note", "resolved", "sources"}
PERSON_CONFLICT_ABOUT = {"link", "identity", "birth", "death"}
FAMILY_CONFLICT_ABOUT = {"marriage", "link"}
# `confidence_override`: a score set by hand, with the reason; `about` picks the score (person: link by default).
OVERRIDE_KEYS = {"score", "reason", "about"}
PERSON_OVERRIDE_ABOUT = {"link", "birth", "death"}
FAMILY_OVERRIDE_ABOUT = {"marriage"}
# `identity` of a person: whether other persons of the same name (namesakes) were checked.
IDENTITY_KEYS = {"namesakes", "note"}
NAMESAKES = {"excluded", "possible"}

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
        "conflict": sorted(CONFLICT_KEYS),
        "confidence_override": sorted(OVERRIDE_KEYS),
        "person_identity": sorted(IDENTITY_KEYS),
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
            "source_classification": sorted(SOURCE_CLASSES), "source_information": sorted(INFORMATION),
            "source_evidence": sorted(EVIDENCE), "person_conflict_about": sorted(PERSON_CONFLICT_ABOUT),
            "family_conflict_about": sorted(FAMILY_CONFLICT_ABOUT), "person_override_about": sorted(PERSON_OVERRIDE_ABOUT),
            "family_override_about": sorted(FAMILY_OVERRIDE_ABOUT), "identity_namesakes": sorted(NAMESAKES),
        },
        "confidence_scores": {
            "computed_by": "build.py (familytree/confidence.py, docs/confidence.md); never typed in by hand",
            "range": "0-100",
            "bands": {"confirmed": ">= 85", "probable": "60-84", "hypothesis": "30-59", "unsupported": "< 30"},
            "manual_confidence": "person/family/event `confidence` is an upper cap: probable <= 84, hypothesis <= 59",
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
            "source.classification": "optional override: original (a record made at the time, or its image), derivative "
                                     "(index, transcription, abstract) or authored (family account, someone's tree, "
                                     "publication). Default: from type and quality.",
            "source.information": "optional override: primary (from someone who knew it first-hand, at the time) or "
                                  "secondary. Default: from the type and the event that cites the source.",
            "source.evidence": "optional override: direct (answers the question alone, e.g. names the parents) or "
                               "indirect. Default: from the type, the event that cites it and whether the transcription "
                               "names the parents.",
            "source.same_record_as": "optional list of source IDs that are the same record (e.g. the index entry and the "
                                     "image of one act): they count once for the confidence.",
            "source.derived_from": "optional source ID (or list): this source was made from that one (an index of an "
                                   "act); they count once.",
            "person.conflicts": "optional list of {about: link|identity|birth|death, note, resolved: true|false, sources}: "
                                "evidence that disagrees. Unresolved conflicts lower the score and block confirmed; "
                                "without about the conflict touches every score of the person.",
            "family.conflicts": "optional list of {about: marriage|link, note, resolved, sources}; link = the links of "
                                "the children.",
            "person.confidence_override": "optional {score: 0-100, reason, about: link|birth|death} (or a list of them): "
                                          "replaces the computed score; the reason is shown with it.",
            "family.confidence_override": "optional {score: 0-100, reason}: replaces the computed score of the marriage.",
            "person.identity": "optional {namesakes: excluded|possible, note}: excluded = other persons of the same name "
                               "were checked and ruled out; possible = a namesake could be the person.",
            "source.file": "optional: path (or list of paths) relative to the workspace of the local copy of the source, "
                           f"e.g. {SCANS_DIR}/<archive>/<fonds>/<file>.jpg. The build checks that the file exists and "
                           "reports sources whose scan is not saved locally.",
        },
        "references": {
            "event.place": "places", "event.sources[]": "sources", "family.husband": "persons",
            "family.wife": "persons", "family.children[]": "persons", "place.parish": "places",
            "source.parish": "places", "project.proband": "persons", "person.quote.source": "sources",
            "source.same_record_as[]": "sources", "source.derived_from": "sources", "person.conflicts[].sources[]": "sources",
            "family.conflicts[].sources[]": "sources",
        },
    }
