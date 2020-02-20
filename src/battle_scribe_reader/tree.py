from __future__ import annotations

from typing import Type, TypeVar, List, Dict, Optional
from xml.etree.ElementTree import Element
from textwrap import indent

from .linkable import Linkable
from .typed import Typed

T = TypeVar('T')
BS = '{http://www.battlescribe.net/schema/catalogueSchema}'
_SPACE = '  '
_BOOL: Dict[str, bool] = {
    'true': True,
    'false': False
}
'''
_VISIBLE = {
    True: chr(0x1D9FF) + chr(0x1DA14),
    False: chr(0x1D9FF) + chr(0x1DA16)
}
'''
_VISIBLE = '-H'
_HIDDEN = 'H-'
_COLLECTIVE = '-C'
_SHARE = '-S'
_PERCENT = '0%'
_FORCES = '-F'
_SELECTION = '-S'
_ROUND = 'v^'


def get(values, value):
    try:
        return values[int(value)]
    except TypeError:
        return ' '


def bools(hidden=None, collective=None, share=None, percent=None, forces=None, selection=None, round=None):
    return (
        f'{get(_HIDDEN, hidden)}'
        f'{get(_COLLECTIVE, collective)}'
        f'{get(_SHARE, share)}'
        f'{get(_PERCENT, percent)}'
        f':'
        f'{get(_FORCES, forces)}'
        f'{get(_SELECTION, selection)}'
    )


def _obj(name=None, value=None, id=None, target=None, p_name=None, p_id=None):
    # (name = value [id -> target] | p_name [p_id])
    # Profile
    p = ''
    if p_name is not None or p_id is not None:
        p = f' | {p_name or ""}' + (f' [{p_id}]' if p_id else '')
    # IDs
    ids = ''
    if id is not None or target is not None:
        target = '' if target is None else f' -> {target}'
        ids = f' [{id or ""}{target}]'
    # Wrapping
    value = '' if value is None else f' = {value}'
    return f'({name or ""}{value}{ids}{p})'


def _dict(**kwargs):
    flags = kwargs.pop('flags', None)
    if flags is not None:
        flags = repr(flags)
    _dict = {
        'flags': flags,
        'type': kwargs.pop('type', None),
        **kwargs
    }
    _dict = {k: v for k, v in _dict.items() if v is not None}
    return ', '.join(f'{k}: {v}' for k, v in _dict.items())


def _disp(disp, name=None, value=None, id=None, target=None, p_name=None, p_id=None, **kwargs):
    o = _obj(name, value, id, target, p_name, p_id)
    d = _dict(**kwargs)
    d = f' {{{d}}}' if d else ''
    return f'{disp}{o}{d}'


class XMLLinkable(Linkable):
    PATH: str
    xml: Element

    def __init__(self, xml: Element):
        self.xml = xml

    @staticmethod
    def _build_link(parent: Linkable, item: str, raw: Type, type: Typed, link: Type[T]) -> T:
        if type.type is list:
            return [link(i) for i in parent.xml.findall(link.PATH)]
        else:
            return link(parent.xml.find(link.PATH))

    def __str__(self):
        lists = [
            (name, [str(i) for i in lst])
            for name, lst in self.get_lists().items()
            if lst
        ]
        return ''.join(
            f'\n' + indent('\n'.join(lst), _SPACE)
            for name, lst in lists
        )


class Root(XMLLinkable):
    profiles: List[Profile]
    rules: List[Rule]
    info_links: List[InfoLink]
    cost_types: List[CostType]
    profile_types: List[ProfileType]
    category_entries: List[CategoryEntry]
    force_entries: List[ForceEntry]
    selection_entries: List[SelectionEntry]
    entry_links: List[EntryLink]
    shared_selection_entries: List[SharedSelectionEntry]
    shared_selection_entries_groups: List[SharedSelectionEntryGroups]
    shared_rules: List[SharedRules]
    shared_profiles: List[SharedProfile]

    @property
    def id(self):
        return self.xml.attrib['id']

    @property
    def name(self):
        return self.xml.attrib['name']

    @property
    def book(self):
        return self.xml.attrib['book']

    @property
    def revision(self):
        return self.xml.attrib['revision']

    @property
    def battle_scribe_version(self):
        return self.xml.attrib['battleScribeVersion']

    @property
    def author_name(self):
        return self.xml.attrib['authorName']

    @property
    def author_url(self):
        return self.xml.attrib['authorUrl']

    @property
    def game_system_id(self):
        return self.xml.attrib['gameSystemId']

    @property
    def game_system_revision(self):
        return self.xml.attrib['gameSystemRevision']

    @property
    def xmlns(self):
        return self.xml.attrib['xmlns']

    def __str__(self):
        return (
            f'{self.name} - {self.id}'
            + super().__str__()
        )


class Profile(XMLLinkable):
    PATH = f'{BS}profiles/{BS}profile'

    profiles: List[Profile]
    rules: List[Rule]
    info_links: List[InfoLink]
    modifiers: List[Modifier]
    characteristics: List[Characteristic]

    @property
    def id(self) -> str:
        return self.xml.attrib['id']

    @property
    def name(self) -> str:
        return self.xml.attrib['name']

    @property
    def hidden(self) -> bool:
        return _BOOL[self.xml.attrib['hidden']]

    @property
    def profile_type_id(self) -> str:
        return self.xml.attrib['profileTypeId']

    @property
    def profile_type_name(self) -> str:
        return self.xml.attrib.get('profileTypeName')

    def __str__(self):
        return (
            _disp(
                'Profile',
                name=self.name,
                id=self.id,
                p_name=self.profile_type_name,
                p_id=self.profile_type_id,
                flags=bools(hidden=self.hidden)
            )
            + super().__str__()
        )


class Rule(XMLLinkable):
    PATH = f'{BS}rules/{BS}rule'

    profiles: List[Profile]
    rules: List[Rule]
    info_links: List[InfoLink]
    modifiers: List[Modifier]
    constraints: List[Constraint]

    @property
    def id(self) -> str:
        return self.xml.attrib['id']

    @property
    def name(self) -> str:
        return self.xml.attrib['name']

    @property
    def hidden(self) -> bool:
        return _BOOL[self.xml.attrib['hidden']]

    @property
    def description(self) -> str:
        return self.xml.find(f'{BS}description').text

    def __str__(self):
        return (
            _disp(
                'Rule',
                name=self.name,
                id=self.id,
                flags=bools(hidden=self.hidden)
            )
            + f'\n {indent(self.description, _SPACE)}'
            + super().__str__()
        )


class InfoLink(XMLLinkable):
    PATH = f'{BS}infoLinks/{BS}infoLink'

    profiles: List[Profile]
    rules: List[Rule]
    info_links: List[InfoLink]
    modifiers: List[Modifier]

    @property
    def id(self) -> str:
        return self.xml.attrib['id']

    @property
    def name(self) -> str:
        return self.xml.attrib.get('name')

    @property
    def hidden(self) -> bool:
        return _BOOL[self.xml.attrib['hidden']]

    @property
    def target_id(self) -> str:
        return self.xml.attrib['targetId']

    @property
    def type(self) -> str:
        return self.xml.attrib['type']

    def __str__(self):
        bs = bools(self.hidden)
        return (
            f'InfoLink[{bs}](type={self.type})\n'
            f' {self.name} [{self.id} -> {self.target_id}]'
            + super().__str__()
        )


# TODO: Add
class CostType(XMLLinkable):
    PATH = f'{BS}costTypes/{BS}costType'


class ProfileType(XMLLinkable):
    PATH = f'{BS}profileTypes/{BS}profileType'

    characteristic_types: List[CharacteristicType]

    @property
    def id(self) -> str:
        return self.xml.attrib['id']

    @property
    def name(self) -> str:
        return self.xml.attrib['name']

    def __str__(self):
        bs = bools()
        return (
            f'ProfileType[{bs}]()\n'
            f' {self.name} [{self.id}]'
            + super().__str__()
        )


class CategoryEntry(XMLLinkable):
    PATH = f'{BS}categoryEntries/{BS}categoryEntry'

    profiles: List[Profile]
    rules: List[Rule]
    info_links: List[InfoLink]
    modifiers: List[Modifier]
    constraints: List[Constraint]

    @property
    def id(self) -> str:
        return self.xml.attrib['id']

    @property
    def name(self) -> str:
        return self.xml.attrib['name']

    def __str__(self):
        bs = bools()
        return (
            f'CategoryEntry[{bs}]()\n'
            f' {self.name} [{self.id}]'
            + super().__str__()
        )


class ForceEntry(XMLLinkable):
    PATH = f'{BS}forceEntries/{BS}forceEntry'

    profiles: List[Profile]
    rules: List[Rule]
    info_links: List[InfoLink]
    modifiers: List[Modifier]
    constraints: List[Constraint]
    force_entries: List[ForceEntry]
    category_link: List[CategoryLink]

    @property
    def id(self) -> str:
        return self.xml.attrib['id']

    @property
    def name(self) -> str:
        return self.xml.attrib['name']

    @property
    def hidden(self) -> bool:
        return _BOOL[self.xml.attrib['hidden']]

    def __str__(self):
        bs = bools(self.hidden)
        return (
                f'ForceEntry[{bs}]()\n'
                f' {self.name} [{self.id}]'
                + super().__str__()
        )


class SelectionEntry(XMLLinkable):
    PATH = f'{BS}selectionEntries/{BS}selectionEntry'

    profiles: List[Profile]
    rules: List[Rule]
    info_links: List[InfoLink]
    modifiers: List[Modifier]
    constraints: List[Constraint]
    category_links: List[CategoryLink]
    selection_entries: List[SelectionEntry]
    selection_entry_groups: List[SelectionEntryGroup]
    entry_links: List[EntryLink]
    # cost: Link[Cost]

    @property
    def id(self) -> str:
        return self.xml.attrib['id']

    @property
    def name(self) -> str:
        return self.xml.attrib['name']

    @property
    def page(self) -> Optional[int]:
        page = self.xml.attrib.get('page')
        if not page:
            return None
        return int(page)

    @property
    def hidden(self) -> bool:
        return _BOOL[self.xml.attrib['hidden']]

    @property
    def collective(self) -> bool:
        return _BOOL[self.xml.attrib['collective']]

    @property
    def type(self) -> str:
        return self.xml.attrib['type']

    def __str__(self):
        bs = bools(self.hidden, collective=self.collective)
        return (
            f'SelectionEntry[{bs}](type={self.type}, page={self.page})\n'
            f' {self.name} [{self.id}]'
            + super().__str__()
        )


class EntryLink(XMLLinkable):
    PATH = f'{BS}entryLinks/{BS}entryLink'

    profiles: List[Profile]
    rules: List[Rule]
    info_links: List[InfoLink]
    modifiers: List[Modifier]
    constraints: List[Constraint]
    category_link: List[CategoryLink]

    @property
    def id(self) -> str:
        return self.xml.attrib['id']

    @property
    def name(self) -> str:
        return self.xml.attrib['name']

    @property
    def hidden(self) -> bool:
        return _BOOL[self.xml.attrib['hidden']]

    @property
    def target_id(self) -> str:
        return self.xml.attrib['targetId']

    @property
    def type(self) -> str:
        return self.xml.attrib['type']

    def __str__(self):
        bs = bools(self.hidden)
        return (
            f'EntryLink[{bs}](type={self.type})\n'
            f' {self.name} [{self.id} -> {self.target_id}]'
            + super().__str__()
        )


class SharedSelectionEntry(XMLLinkable):
    PATH = f'{BS}sharedSelectionEntries/{BS}selectionEntry'

    profiles: List[Profile]
    rules: List[Rule]
    info_links: List[InfoLink]
    modifiers: List[Modifier]
    constraints: List[Constraint]
    category_link: List[CategoryLink]
    selection_entries: List[SelectionEntry]
    selection_entry_groups: List[SelectionEntryGroup]
    entry_links: List[EntryLink]
    costs: List[Cost]

    @property
    def id(self) -> str:
        return self.xml.attrib['id']

    @property
    def name(self) -> str:
        return self.xml.attrib['name']

    @property
    def page(self) -> Optional[int]:
        page = self.xml.attrib.get('page')
        if not page:
            return None
        return int(page)

    @property
    def hidden(self) -> bool:
        return _BOOL[self.xml.attrib['hidden']]

    @property
    def collective(self) -> bool:
        return _BOOL[self.xml.attrib['collective']]

    @property
    def type(self) -> str:
        return self.xml.attrib['type']

    def __str__(self):
        bs = bools(self.hidden)
        return (
            f'SharedSelectionEntry[{bs}](type={self.type}, page={self.page})\n'
            f' {self.name} [{self.id}]'
            + super().__str__()
        )


class SharedSelectionEntryGroups(XMLLinkable):
    PATH = f'{BS}sharedSelectionEntryGroups/{BS}selectionEntryGroup'

    profiles: List[Profile]
    rules: List[Rule]
    info_links: List[InfoLink]
    modifiers: List[Modifier]
    constraints: List[Constraint]
    category_link: List[CategoryLink]
    selection_entries: List[SelectionEntry]
    selection_entry_groups: List[SelectionEntryGroup]
    entry_links: List[EntryLink]

    @property
    def id(self) -> str:
        return self.xml.attrib['id']

    @property
    def name(self) -> str:
        return self.xml.attrib['name']

    @property
    def hidden(self) -> bool:
        return _BOOL[self.xml.attrib['hidden']]

    @property
    def collective(self) -> bool:
        return _BOOL[self.xml.attrib['collective']]

    @property
    def default_selection_entry_id(self) -> Optional[str]:
        return self.xml.attrib.get('defaultSelectionEntryId')

    def __str__(self):
        bs = bools(self.hidden, collective=self.collective)
        return (
            f'SharedSelectionEntryGroups[{bs}](default={self.default_selection_entry_id})\n'
            f' {self.name} [{self.id}]'
            + super().__str__()
        )


# TODO: Fix
class SharedRules(XMLLinkable):
    PATH = f'{BS}sharedRules/{BS}sharedRule'


class SharedProfile(XMLLinkable):
    PATH = f'{BS}sharedProfiles/{BS}profile'

    profiles: List[Profile]
    rules: List[Rule]
    info_links: List[InfoLink]
    modifiers: List[Modifier]
    characteristics: List[Characteristic]

    @property
    def id(self) -> str:
        return self.xml.attrib['id']

    @property
    def name(self) -> str:
        return self.xml.attrib['name']

    @property
    def hidden(self) -> bool:
        return _BOOL[self.xml.attrib['hidden']]

    @property
    def profile_type_id(self) -> str:
        return self.xml.attrib['profileTypeId']

    @property
    def profile_type_name(self) -> str:
        return self.xml.attrib.get('profileTypeName')

    def __str__(self):
        bs = bools(self.hidden)
        return (
            f'SharedProfile[{bs}]() {self.profile_type_name} [{self.profile_type_id}]\n'
            f' {self.name} [{self.id}]'
            + super().__str__()
        )


# Base


class Constraint(XMLLinkable):
    PATH = f'{BS}constraints/{BS}constraint'

    @property
    def field(self) -> str:
        return self.xml.attrib['field']

    @property
    def scope(self) -> str:
        return self.xml.attrib['scope']

    @property
    def value(self) -> str:
        return self.xml.attrib['value']

    @property
    def percent_value(self) -> bool:
        return _BOOL[self.xml.attrib['percentValue']]

    @property
    def shared(self) -> bool:
        return _BOOL[self.xml.attrib['shared']]

    @property
    def include_child_selections(self) -> bool:
        return _BOOL[self.xml.attrib['includeChildSelections']]

    @property
    def include_child_forces(self) -> bool:
        return _BOOL[self.xml.attrib['includeChildForces']]

    @property
    def id(self) -> str:
        return self.xml.attrib['id']

    @property
    def type(self) -> str:
        return self.xml.attrib['type']

    def __str__(self) -> str:
        bs = bools(
            share=self.shared,
            forces=self.include_child_forces,
            selection=self.include_child_selections,
            percent=self.percent_value
        )
        return (
            f'Constraint[{bs}](scope={self.scope}, type={self.type})\n'
            f' {self.field} = {self.value} [{self.id}]'
            + super().__str__()
        )


class Modifier(XMLLinkable):
    PATH = f'{BS}modifiers/{BS}modifier'

    repeats: List[Repeat]
    conditions: List[Condition]
    condition_groups: List[ConditionGroup]

    @property
    def field(self) -> str:
        return self.xml.attrib['field']

    @property
    def value(self) -> str:
        return self.xml.attrib['value']

    @property
    def type(self) -> str:
        return self.xml.attrib['type']

    def __str__(self):
        bs = bools()
        return (
            f'Modifier[{bs}](type={self.type})\n'
            f' {self.value} = {self.field}'
            + super().__str__()
        )


class Repeat(XMLLinkable):
    PATH = f'{BS}repeats/{BS}repeat'

    @property
    def field(self) -> str:
        return self.xml.attrib['field']

    @property
    def scope(self) -> str:
        return self.xml.attrib['scope']

    @property
    def value(self) -> str:
        return self.xml.attrib['value']

    @property
    def percent_value(self) -> bool:
        return _BOOL[self.xml.attrib['percentValue']]

    @property
    def shared(self) -> bool:
        return _BOOL[self.xml.attrib['shared']]

    @property
    def include_child_selections(self) -> bool:
        return _BOOL[self.xml.attrib['includeChildSelections']]

    @property
    def include_child_forces(self) -> bool:
        return _BOOL[self.xml.attrib['includeChildForces']]

    @property
    def child_id(self) -> str:
        return self.xml.attrib['childId']

    @property
    def repeats(self):
        return self.xml.attrib['repeats']

    @property
    def round_up(self):
        return self.xml.attrib['roundUp']

    # TODO: Add missing values
    def __str__(self):
        bs = bools(
            share=self.shared,
            forces=self.include_child_forces,
            selection=self.include_child_selections,
            percent=self.percent_value,
            round=self.round_up
        )
        return (
            f'Repeat[{bs}](scope={self.scope}, repeats={self.repeats})\n'
            f' {self.field} = {self.value} [{self.child_id}]'
            + super().__str__()
        )


class Condition(XMLLinkable):
    PATH = f'{BS}conditions/{BS}condition'

    @property
    def field(self) -> str:
        return self.xml.attrib['field']

    @property
    def scope(self) -> str:
        return self.xml.attrib['scope']

    @property
    def value(self) -> str:
        return self.xml.attrib['value']

    @property
    def percent_value(self) -> bool:
        return _BOOL[self.xml.attrib['percentValue']]

    @property
    def shared(self) -> bool:
        return _BOOL[self.xml.attrib['shared']]

    @property
    def include_child_selections(self) -> bool:
        return _BOOL[self.xml.attrib['includeChildSelections']]

    @property
    def include_child_forces(self) -> bool:
        return _BOOL[self.xml.attrib['includeChildForces']]

    @property
    def child_id(self) -> str:
        return self.xml.attrib['childId']

    @property
    def type(self) -> str:
        return self.xml.attrib['type']

    def __str__(self):
        bs = bools(
            share=self.shared,
            forces=self.include_child_forces,
            selection=self.include_child_selections,
            percent=self.percent_value
        )
        return (
            f'Condition[{bs}](scope={self.scope}, type={self.type})\n'
            f' {self.field} = {self.value} [{self.child_id}]'
            + super().__str__()
        )


class ConditionGroup(XMLLinkable):
    PATH = f'{BS}conditionGroups/{BS}conditionGroup'

    conditions: List[Condition]
    condition_groups: List[ConditionGroup]

    @property
    def type(self) -> str:
        return self.xml.attrib['type']

    def __str__(self):
        bs = bools()
        return (
            f'ConditionGroup[{bs}](type={self.type})'
            + super().__str__()
        )


# Other


class CharacteristicType(XMLLinkable):
    PATH = f'{BS}characteristicTypes/{BS}characteristicType'

    @property
    def id(self) -> str:
        return self.xml.attrib['id']

    @property
    def name(self) -> str:
        return self.xml.attrib['name']

    def __str__(self):
        bs = bools()
        return (
            f'CharacteristicType[{bs}]()\n'
            f' {self.name} [{self.id}]'
            + super().__str__()
        )


class CategoryLink(XMLLinkable):
    PATH = f'{BS}categoryLinks/{BS}categoryLink'

    profiles: List[Profile]
    rules: List[Rule]
    info_links: List[InfoLink]
    modifiers: List[Modifier]
    constraints: List[Constraint]

    @property
    def id(self) -> str:
        return self.xml.attrib['id']

    @property
    def name(self) -> str:
        return self.xml.attrib.get('name')

    @property
    def hidden(self) -> bool:
        return _BOOL[self.xml.attrib['hidden']]

    @property
    def target_id(self) -> str:
        return self.xml.attrib['targetId']

    @property
    def primary(self) -> str:
        return self.xml.attrib['primary']

    def __str__(self):
        bs = bools(
            hidden=self.hidden
        )
        return (
            f'CategoryLink[{bs}](primary={self.primary})\n'
            f' {self.name} [{self.id} -> {self.target_id}]'
            + super().__str__()
        )


class Characteristic(XMLLinkable):
    PATH = f'{BS}characteristics/{BS}characteristic'

    @property
    def name(self) -> str:
        return self.xml.attrib['name']

    @property
    def characteristic_type_id(self) -> str:
        return self.xml.attrib['characteristicTypeId']

    @property
    def value(self) -> str:
        return self.xml.attrib.get('value')

    def __str__(self):
        bs = bools()
        return (
            f'Characteristic[{bs}](characteristic={self.characteristic_type_id})\n'
            f' {self.name} = {self.value}'
            + super().__str__()
        )


class SelectionEntryGroup(XMLLinkable):
    PATH = f'{BS}selectionEntryGroups/{BS}selectionEntryGroup'

    profiles: List[Profile]
    rules: List[Rule]
    info_links: List[InfoLink]
    modifiers: List[Modifier]
    constraints: List[Constraint]
    category_link: List[CategoryLink]
    selection_entries: List[SelectionEntry]
    selection_entry_groups: List[SelectionEntryGroup]
    entry_links: List[EntryLink]

    @property
    def id(self) -> str:
        return self.xml.attrib['id']

    @property
    def name(self) -> str:
        return self.xml.attrib.get('name')

    @property
    def hidden(self) -> bool:
        return _BOOL[self.xml.attrib['hidden']]

    @property
    def collective(self):
        return self.xml.attrib['collective']

    @property
    def default_selection_entry_id(self):
        return self.xml.attrib.get('defaultSelectionEntryId')

    def __str__(self):
        bs = bools()
        return (
            f'SelectionEntryGroup[{bs}](default={self.default_selection_entry_id})\n'
            f' {self.name} [{self.id}]'
            + super().__str__()
        )


class Cost(XMLLinkable):
    PATH = f'{BS}costs/{BS}cost'

    @property
    def name(self) -> str:
        return self.xml.attrib.get('name')

    @property
    def value(self) -> str:
        return self.xml.attrib['value']

    @property
    def cost_type_id(self) -> str:
        return self.xml.attrib['costTypeId']

    def __str__(self):
        bs = bools()
        return (
            f'Cost[{bs}](cost={self.cost_type_id})\n'
            f' {self.name} = {self.value}'
            + super().__str__()
        )
