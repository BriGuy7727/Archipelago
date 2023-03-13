from typing import Dict, Any, List, Optional

from BaseClasses import Tutorial, ItemClassification
from worlds.AutoWorld import World, WebWorld
from .Constants import NOTES, PROG_ITEMS, PHOBEKINS, USEFUL_ITEMS, ALWAYS_LOCATIONS, SEALS, ALL_ITEMS
from .Options import MessengerOptions, NotesNeeded, Goal, PowerSeals
from .Regions import REGIONS, REGION_CONNECTIONS
from .Rules import MessengerRules
from .SubClasses import MessengerRegion, MessengerItem


class MessengerWeb(WebWorld):
    theme = "ocean"

    bug_report_page = "https://github.com/minous27/TheMessengerRandomizerMod/issues"

    tut_en = Tutorial(
        "Multiworld Setup Tutorial",
        "A guide to setting up The Messenger randomizer on your computer.",
        "English",
        "setup_en.md",
        "setup/en",
        ["alwaysintreble"]
    )

    tutorials = [tut_en]


class MessengerWorld(World):
    """
    As a demon army besieges his village, a young ninja ventures through a cursed world, to deliver a scroll paramount
    to his clan’s survival. What begins as a classic action platformer soon unravels into an expansive time-traveling
    adventure full of thrills, surprises, and humor.
    """
    game = "The Messenger"

    item_name_groups = {
        "Notes": set(NOTES),
        "Keys": set(NOTES),
        "Crest": {"Sun Crest", "Moon Crest"},
        "Phobe": set(PHOBEKINS),
        "Phobekin": set(PHOBEKINS),
        "Shuriken": {"Windmill Shuriken"},
    }

    options_dataclass = MessengerOptions
    o: MessengerOptions

    base_offset = 0xADD_000
    item_name_to_id = {item: item_id
                       for item_id, item in enumerate(ALL_ITEMS, base_offset)}
    location_name_to_id = {location: location_id
                           for location_id, location in enumerate([*ALWAYS_LOCATIONS, *SEALS], base_offset)}

    data_version = 1

    web = MessengerWeb()

    total_seals: Optional[int] = None
    required_seals: Optional[int] = None

    def generate_early(self) -> None:
        if self.o.goal == Goal.option_power_seal_hunt:
            self.o.shuffle_seals.value = PowerSeals.option_true
            self.total_seals = self.o.total_seals.value
            self.required_seals = int(self.o.percent_seals_required.value / 100 * self.total_seals)

    def create_regions(self) -> None:
        for region in [MessengerRegion(reg_name, self) for reg_name in REGIONS]:
            if region.name in REGION_CONNECTIONS:
                region.add_exits(REGION_CONNECTIONS[region.name])

    def create_items(self) -> None:
        itempool: List[MessengerItem] = []
        if self.o.goal == Goal.option_power_seal_hunt:
            seals = [self.create_item("Power Seal") for _ in range(self.total_seals)]
            for i in range(self.required_seals):
                seals[i].classification = ItemClassification.progression_skip_balancing
            itempool += seals
        else:
            notes = self.multiworld.random.sample(NOTES, k=len(NOTES))
            precollected_notes_amount = NotesNeeded.range_end - self.o.notes_needed
            if precollected_notes_amount:
                for note in notes[:precollected_notes_amount]:
                    self.multiworld.push_precollected(self.create_item(note))
            itempool += [self.create_item(note) for note in notes[precollected_notes_amount:]]

        itempool += [self.create_item(item)
                     for item in self.item_name_to_id
                     if item not in
                     {
                         "Power Seal", "Time Shard", *NOTES,
                         *{collected_item.name for collected_item in self.multiworld.precollected_items[self.player]}
                         # this is a set and currently won't create items for anything that appears in here at all
                         # if we get in a position where this can have duplicates of items that aren't Power Seals
                         # or Time shards, this will need to be redone.
                     }]
        itempool += [self.create_filler()
                     for _ in range(len(self.multiworld.get_unfilled_locations(self.player)) - len(itempool))]

        self.multiworld.itempool += itempool

    def set_rules(self) -> None:
        MessengerRules(self).set_messenger_rules()

    def fill_slot_data(self) -> Dict[str, Any]:
        locations: Dict[int, List[str]] = {}
        for loc in self.multiworld.get_filled_locations(self.player):
            if loc.item.code:
                locations[loc.address] = [loc.item.name, self.multiworld.player_name[loc.item.player]]

        return {
            "deathlink": self.o.death_link.value,
            "goal": self.o.goal.current_key,
            "music_box": self.o.music_box.value,
            "required_seals": self.required_seals,
            "locations": locations,
            "settings": {"Difficulty": "Basic" if not self.o.shuffle_seals else "Advanced"}
        }

    def get_filler_item_name(self) -> str:
        return "Time Shard"

    def create_item(self, name: str) -> MessengerItem:
        item_id: Optional[int] = self.item_name_to_id.get(name, None)
        return MessengerItem(name, self.player, item_id)
