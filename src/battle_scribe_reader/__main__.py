from __future__ import annotations

import xml.etree.ElementTree

from .tree import Root

e = xml.etree.ElementTree.parse("Chaos - Chaos Space Marines.cat").getroot()
r = Root(e)
SPACE = "  "


if __name__ == "__main__":
    attrs = (
        "profiles rules info_links cost_types profile_types category_entries force_entries selection_entries "
        "entry_links shared_selection_entries shared_selection_entries_groups shared_rules shared_profiles"
    ).split()
    for a in attrs:
        obj = getattr(r, a)
        print(a, len(obj))
        if obj:
            for i in obj[0].xml:
                print("", i)

    print(r)
