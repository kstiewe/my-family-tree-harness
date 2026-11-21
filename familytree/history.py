"""Great events of Polish and European history, for the "At a glance" part of a person's card: what the person
lived through. General history only — nothing here is about any family.

Each event: the first and the last year, the partitions of Poland (1772–1918) it concerns — empty when it touched
everyone —, its weight (3 = epochal, 2 = major, 1 = lesser; the short line of the card shows the weightiest) and its
name (a message id; the translations are in familytree/locales/)."""

from __future__ import annotations

from typing import NamedTuple

from .i18n import tr


class Event(NamedTuple):
    first: int
    last: int
    partitions: tuple[str, ...]
    weight: int
    name: str


EVENTS = tuple(Event(*e) for e in (
    (1700, 1721, (), 2, "the Great Northern War"),
    (1733, 1735, (), 1, "the War of the Polish Succession"),
    (1756, 1763, (), 2, "the Seven Years' War"),
    (1768, 1772, (), 2, "the Bar Confederation"),
    (1772, 1772, (), 3, "the First Partition of Poland"),
    (1788, 1792, (), 2, "the Great Sejm and the Constitution of 3 May"),
    (1793, 1793, (), 3, "the Second Partition of Poland"),
    (1794, 1794, (), 3, "the Kościuszko Uprising"),
    (1795, 1795, (), 3, "the Third Partition of Poland"),
    (1806, 1815, (), 2, "the Napoleonic Wars and the Duchy of Warsaw"),
    (1815, 1815, ("russian",), 2, "the Congress Kingdom of Poland is created"),
    (1830, 1831, ("russian",), 3, "the November Uprising"),
    (1846, 1846, ("austrian",), 2, "the Kraków Uprising and the Galician peasant revolt"),
    (1848, 1848, (), 2, "the Spring of Nations"),
    (1848, 1848, ("austrian",), 2, "serfdom is abolished in Galicia"),
    (1863, 1864, ("russian",), 3, "the January Uprising"),
    (1864, 1864, ("russian",), 2, "the peasants of the Congress Kingdom are granted their land"),
    (1866, 1866, ("prussian", "austrian"), 1, "the Austro-Prussian War"),
    (1870, 1871, ("prussian",), 2, "the Franco-Prussian War and the founding of the German Empire"),
    (1871, 1878, ("prussian",), 2, "the Kulturkampf"),
    (1874, 1874, ("prussian",), 1, "civil registry offices (Standesamt) are introduced in Prussia"),
    (1885, 1890, ("prussian",), 1, "the Prussian deportations of Poles"),
    (1904, 1905, ("russian",), 1, "the Russo-Japanese War"),
    (1905, 1907, ("russian",), 2, "the Revolution of 1905"),
    (1906, 1907, ("prussian",), 1, "the school strikes against Germanisation"),
    (1914, 1918, (), 3, "the First World War"),
    (1918, 1918, (), 3, "Poland regains independence"),
    (1918, 1920, (), 2, "the Spanish flu pandemic"),
    (1919, 1920, ("prussian",), 2, "the lands of the Prussian partition join Poland"),
    (1919, 1921, (), 3, "the Polish–Soviet War"),
    (1929, 1933, (), 2, "the Great Depression"),
    (1939, 1945, (), 3, "the Second World War"),
    (1945, 1945, (), 2, "the new borders of Poland and the resettlements"),
    (1956, 1956, (), 2, "the Poznań protests and the thaw of October 1956"),
    (1970, 1970, (), 1, "the protests of December 1970"),
    (1978, 1978, (), 2, "Karol Wojtyła becomes Pope John Paul II"),
    (1980, 1981, (), 3, "the Solidarity movement"),
    (1981, 1983, (), 3, "martial law in Poland"),
    (1989, 1989, (), 3, "the end of communist rule in Poland"),
    (2004, 2004, (), 2, "Poland joins the European Union"),
))


def lived_through(born: int, last: int, partitions: set[str] | None = None, min_age: int = 5) -> list[Event]:
    """The events of a life from `born` to `last`: those that had not ended before the person was `min_age`, and —
    for an event of some partitions only — that concern one of `partitions` (left out when those are unknown).
    The names come translated."""
    return [e._replace(name=tr(e.name)) for e in EVENTS
            if e.last >= born + min_age and e.first <= last
            and (not e.partitions or set(e.partitions) & (partitions or set()))]
