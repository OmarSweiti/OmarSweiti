"""Remove the language donut and star/fork counters from the 3D contribution SVGs.

github-profile-3d-contrib always draws both beside the calendar. The donut is
weighted by commits per repository, so it surfaces repositories this profile
deliberately leaves out, and the counters add nothing. The calendar, radar
chart and contribution total are kept.

Exits non-zero when the markup no longer matches, so an upstream change fails
the workflow instead of publishing an untrimmed graph.
"""

import sys
import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
G = f"{{{SVG_NS}}}g"
TEXT = f"{{{SVG_NS}}}text"
TITLE = f"{{{SVG_NS}}}title"

ET.register_namespace("", SVG_NS)


def has_class(element, name):
    return name in element.get("class", "").split()


def trim(path):
    tree = ET.parse(path)
    root = tree.getroot()
    groups = root.findall(G)

    # The donut is the only part of the image drawn with the stroke-bg class.
    donuts = [g for g in groups if any(has_class(el, "stroke-bg") for el in g.iter())]
    # The summary row is the group that holds the contribution total.
    summaries = [g for g in groups if any(has_class(el, "fill-strong") for el in g)]
    if len(donuts) != 1 or len(summaries) != 1:
        sys.exit(f"{path}: expected 1 donut and 1 summary row, "
                 f"found {len(donuts)} and {len(summaries)}")
    root.remove(donuts[0])

    # Each counter is an icon group plus a count label carrying a <title> tooltip.
    summary = summaries[0]
    counters = [el for el in summary
                if el.tag == G or (el.tag == TEXT and el.find(TITLE) is not None)]
    if len(counters) != 4:
        sys.exit(f"{path}: expected 4 star/fork elements, found {len(counters)}")
    for el in counters:
        summary.remove(el)

    tree.write(path, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: trim.py SVG [SVG ...]")
    for svg in sys.argv[1:]:
        trim(svg)
        print(f"Trimmed {svg}")
