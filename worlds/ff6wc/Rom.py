import hashlib
import logging
import os
from typing import Dict, Tuple

import Utils
from worlds.Files import APDeltaPatch

NA10HASH = 'e986575b98300f721ce27c180264d890'
ROM_PLAYER_LIMIT = 65535
ROM_NAME = 0x00FFC0
treasure_chest_base_address = 0xF51E40
event_flag_base_address = 0xF51E80
bit_positions = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]
esper_bit_base_address = 0xF51A69
espers_obtained_address = 0xF51FC8
character_intialized_bit_base_address = 0xF51EDC
character_recruited_bit_base_address = 0xF51EDE
characters_obtained_address = 0xF51FC6
item_types_base_address = 0xF51869
item_quantities_base_address = 0xF51969
items_received_address = 0xF51DC9
traps_received_address = 0xE07E02
victory_address = 0xF51ED8
map_index_address = 0xF50082
swdtech_byte = 0xF51CF7
blitz_byte = 0xF51D28
menu_address = 0xF50059
formation_id = 0xF511E0
animation_byte = 0xF5009A

espers = [  # This is the internal order of the Espers in the game. Editing this will break things.
    "Ramuh", "Ifrit", "Shiva",
    "Siren", "Terrato", "Shoat",
    "Maduin", "Bismark", "Stray",
    "Palidor", "Tritoch", "Odin",
    "Raiden", "Bahamut", "Alexandr",
    "Crusader", "Ragnarok Esper", "Kirin",
    "ZoneSeek", "Carbunkl", "Phantom",
    "Sraphim", "Golem", "Unicorn",
    "Fenrir", "Starlet", "Phoenix"
]

characters = [  # Same here.
    "Terra", "Locke", "Cyan", "Shadow", "Edgar", "Sabin", "Celes", "Strago",
    "Relm", "Setzer", "Mog", "Gau", "Gogo", "Umaro"
]

item_id_name_weight = {  # second element is the chest item tier weight
    0: ("Dirk", 143),
    1: ("MithrilKnife", 143),
    2: ("Guardian", 291),
    3: ("Air Lancet", 143),
    4: ("ThiefKnife", 291),
    5: ("Assassin", 667),
    6: ("Man Eater", 667),
    7: ("SwordBreaker", 667),
    8: ("Graedus", 667),
    9: ("ValiantKnife", 40),
    10: ("MithrilBlade", 143),
    11: ("RegalCutlass", 143),
    12: ("Rune Edge", 291),
    13: ("Flame Sabre", 291),
    14: ("Blizzard", 291),
    15: ("ThunderBlade", 291),
    16: ("Epee", 143),
    17: ("Break Blade", 291),
    18: ("Drainer", 291),
    19: ("Enhancer", 340),
    20: ("Crystal", 291),
    21: ("Falchion", 291),
    22: ("Soul Sabre", 291),
    23: ("Ogre Nix", 291),
    24: ("Excalibur", 667),
    25: ("Scimitar", 667),
    26: ("Illumina", 25),
    27: ("Ragnarok Sword", 35),
    28: ("Atma Weapon", 291),
    29: ("Mithril Pike", 143),
    30: ("Trident", 143),
    31: ("Stout Spear", 143),
    32: ("Partisan", 291),
    33: ("Pearl Lance", 340),
    34: ("Gold Lance", 291),
    35: ("Aura Lance", 340),
    36: ("Imp Halberd", 667),
    37: ("Imperial", 143),
    38: ("Kodachi", 143),
    39: ("Blossom", 143),
    40: ("Hardened", 143),
    41: ("Striker", 667),
    42: ("Stunner", 667),
    43: ("Ashura", 143),
    44: ("Kotetsu", 143),
    45: ("Forged", 143),
    46: ("Tempest", 667),
    47: ("Murasame", 143),
    48: ("Aura", 291),
    49: ("Strato", 291),
    50: ("Sky Render", 667),
    51: ("Heal Rod", 291),
    52: ("Mithril Rod", 143),
    53: ("Fire Rod", 667),
    54: ("Ice Rod", 667),
    55: ("Thunder Rod", 667),
    56: ("Poison Rod", 291),
    57: ("Pearl Rod", 340),
    58: ("Gravity Rod", 291),
    59: ("Punisher", 291),
    60: ("Magus Rod", 340),
    61: ("Chocobo Brsh", 143),
    62: ("DaVinci Brsh", 143),
    63: ("Magical Brsh", 291),
    64: ("Rainbow Brsh", 291),
    65: ("Shuriken", 143),
    66: ("Ninja Star", 291),
    67: ("Tack Star", 667),
    68: ("Flail", 291),
    69: ("Full Moon", 291),
    70: ("Morning Star", 291),
    71: ("Boomerang", 291),
    72: ("Rising Sun", 291),
    73: ("Hawk Eye", 667),
    74: ("Bone Club", 291),
    75: ("Sniper", 340),
    76: ("Wing Edge", 667),
    77: ("Cards", 143),
    78: ("Darts", 143),
    79: ("Doom Darts", 667),
    80: ("Trump", 291),
    81: ("Dice", 291),
    82: ("Fixed Dice", 40),
    83: ("MetalKnuckle", 143),
    84: ("Mithril Claw", 143),
    85: ("Kaiser", 143),
    86: ("Poison Claw", 143),
    87: ("Fire Knuckle", 291),
    88: ("Dragon Claw", 291),
    89: ("Tiger Fangs", 667),
    90: ("Buckler", 143),
    91: ("Heavy Shld", 143),
    92: ("Mithril Shld", 143),
    93: ("Gold Shld", 143),
    94: ("Aegis Shld", 340),
    95: ("Diamond Shld", 291),
    96: ("Flame Shld", 340),
    97: ("Ice Shld", 340),
    98: ("Thunder Shld", 340),
    99: ("Crystal Shld", 291),
    100: ("Genji Shld", 340),
    101: ("TortoiseShld", 667),
    102: ("Cursed Shld", 0),
    103: ("Paladin Shld", 10),
    104: ("Force Shld", 667),
    105: ("Leather Hat", 143),
    106: ("Hair Band", 143),
    107: ("Plumed Hat", 143),
    108: ("Beret", 291),
    109: ("Magus Hat", 291),
    110: ("Bandana", 143),
    111: ("Iron Helmet", 143),
    112: ("Coronet", 291),
    113: ("Bard's Hat", 291),
    114: ("Green Beret", 291),
    115: ("Head Band", 143),
    116: ("Mithril Helm", 143),
    117: ("Tiara", 291),
    118: ("Gold Helmet", 143),
    119: ("Tiger Mask", 143),
    120: ("Red Cap", 667),
    121: ("Mystery Veil", 667),
    122: ("Circlet", 667),
    123: ("Regal Crown", 291),
    124: ("Diamond Helm", 291),
    125: ("Dark Hood", 291),
    126: ("Crystal Helm", 291),
    127: ("Oath Veil", 667),
    128: ("Cat Hood", 60),
    129: ("Genji Helmet", 340),
    130: ("Thornlet", 291),
    131: ("Titanium", 291),
    132: ("LeatherArmor", 143),
    133: ("Cotton Robe", 143),
    134: ("Kung Fu Suit", 143),
    135: ("Iron Armor", 143),
    136: ("Silk Robe", 143),
    137: ("Mithril Vest", 143),
    138: ("Ninja Gear", 143),
    139: ("White Dress", 291),
    140: ("Mithril Mail", 143),
    141: ("Gaia Gear", 291),
    142: ("Mirage Vest", 667),
    143: ("Gold Armor", 143),
    144: ("Power Sash", 143),
    145: ("Light Robe", 291),
    146: ("Diamond Vest", 291),
    147: ("Red Jacket", 667),
    148: ("Force Armor", 340),
    149: ("DiamondArmor", 291),
    150: ("Dark Gear", 291),
    151: ("Tao Robe", 667),
    152: ("Crystal Mail", 291),
    153: ("Czarina Gown", 667),
    154: ("Genji Armor", 340),
    155: ("Imp's Armor", 667),
    156: ("Minerva", 35),
    157: ("Tabby Suit", 291),
    158: ("Chocobo Suit", 291),
    159: ("Moogle Suit", 667),
    160: ("Nutkin Suit", 340),
    161: ("BehemothSuit", 340),
    162: ("Snow Muffler", 60),
    163: ("NoiseBlaster", 291),
    164: ("Bio Blaster", 291),
    165: ("Flash", 291),
    166: ("Chain Saw", 667),
    167: ("Debilitator", 291),
    168: ("Drill", 667),
    169: ("Air Anchor", 667),
    170: ("AutoCrossbow", 291),
    171: ("Fire Skean", 291),
    172: ("Water Edge", 291),
    173: ("Bolt Edge", 291),
    174: ("Inviz Edge", 291),
    175: ("Shadow Edge", 291),
    176: ("Goggles", 143),
    177: ("Star Pendant", 143),
    178: ("Peace Ring", 291),
    179: ("Amulet", 291),
    180: ("White Cape", 291),
    181: ("Jewel Ring", 143),
    182: ("Fairy Ring", 143),
    183: ("Barrier Ring", 143),
    184: ("MithrilGlove", 143),
    185: ("Guard Ring", 291),
    186: ("RunningShoes", 291),
    187: ("Wall Ring", 667),
    188: ("Cherub Down", 291),
    189: ("Cure Ring", 143),
    190: ("True Knight", 291),
    191: ("DragoonBoots", 667),
    192: ("Zephyr Cape", 291),
    193: ("Czarina Ring", 143),
    194: ("Cursed Ring", 291),
    195: ("Earrings", 667),
    196: ("Atlas Armlet", 667),
    197: ("Blizzard Orb", 667),
    198: ("Rage Ring", 667),
    199: ("Sneak Ring", 143),
    200: ("Pod Bracelet", 667),
    201: ("Hero Ring", 340),
    202: ("Ribbon", 340),
    203: ("Muscle Belt", 340),
    204: ("Crystal Orb", 291),
    205: ("Gold Hairpin", 667),
    206: ("Economizer", 340),
    207: ("Thief Glove", 291),
    208: ("Gauntlet", 291),
    209: ("Genji Glove", 340),
    210: ("Hyper Wrist", 291),
    211: ("Offering", 40),
    212: ("Beads", 291),
    213: ("Black Belt", 291),
    214: ("Coin Toss", 291),
    215: ("FakeMustache", 291),
    216: ("Gem Box", 50),
    217: ("Dragon Horn", 340),
    218: ("Merit Award", 340),
    219: ("Memento Ring", 667),
    220: ("Safety Bit", 667),
    221: ("Relic Ring", 143),
    222: ("Moogle Charm", 340),
    223: ("Charm Bangle", 667),
    224: ("Marvel Shoes", 75),
    225: ("Back Guard", 291),
    226: ("Gale Hairpin", 291),
    227: ("Sniper Sight", 143),
    228: ("Exp. Egg", 30),
    229: ("Tintinabar", 143),
    230: ("Sprint Shoes", 143),
    231: ("ArchplgoItem", 0),
    232: ("Tonic", 1000),
    233: ("Potion", 1000),
    234: ("X-Potion", 1500),
    235: ("Tincture", 1000),
    236: ("Ether", 1714),
    237: ("X-Ether", 1500),
    238: ("Elixir", 750),
    239: ("Megalixir", 500),
    240: ("Fenix Down", 1714),
    241: ("Revivify", 1000),
    242: ("Antidote", 1000),
    243: ("Eyedrop", 1000),
    244: ("Soft", 1000),
    245: ("Remedy", 1714),
    246: ("Sleeping Bag", 1714),
    247: ("Tent", 1714),
    248: ("Green Cherry", 1000),
    249: ("Magicite", 1000),
    250: ("Super Ball", 340),
    251: ("Echo Screen", 1000),
    252: ("Smoke Bomb", 1714),
    253: ("Warp Stone", 1714),
    254: ("Dried Meat", 750),
    255: ("Empty", 0),
}

item_name_id = {v[0]: k for k, v in item_id_name_weight.items()}

event_flag_location_names = {
    "Whelk": 0x135,
    "Lete River": 0x257,
    "Sealed Gate": 0x471,
    "Zozo": 0x52,
    "Mobliz": 0x0bf,
    "South Figaro Cave": 0x0b1,
    "Narshe Weapon Shop 1": 0x0b7,
    "Narshe Weapon Shop 2": 0x0b6,
    "Phoenix Cave": 0x0d7,
    "Red Dragon": 0x120,
    "Doma Castle Siege": 0x040,
    "Dream Stooges": 0x0d8,
    "Wrexsoul": 0x0da,
    "Doma Castle Throne": 0x0db,
    "Mt. Zozo": 0x0d2,
    "Storm Dragon": 0x11b,
    "Gau Father House": 0x162,
    "Imperial Air Force": 0x02a,
    "AtmaWeapon": 0x0a1,
    "Nerapa": 0x0a5,
    "Veldt Cave": 0x199,
    "Figaro Castle Throne": 0x004,
    "Figaro Castle Basement": 0x0c6,
    "Ancient Castle": 0x2dd,
    "Blue Dragon": 0x11f,
    "Mt. Kolts": 0x010,
    "Collapsing House": 0x28a,
    "Baren Falls": 0x03f,
    "Imperial Camp": 0x037,
    "Phantom Train": 0x192,
    "South Figaro": 0x01d,
    "Ifrit and Shiva": 0x061,
    "Number 024": 0x05f,
    "Cranes": 0x06b,
    "Opera House": 0x5b,
    "Burning House": 0x090,
    "Ebot's Rock": 0x19c,
    "MagiMaster": 0x0ba,
    "Gem Box": 0x2da,  # Stepped in front of the chest, triggering boss fight.
    "Esper Mountain": 0x095,
    "Owzer Mansion": 0x253,
    "Kohlingen": 0x18e,
    "Daryl's Tomb": 0x2b2,
    "Lone Wolf 1": 0x29f,
    "Lone Wolf 2": 0x241,
    "Narshe Moogle Defense": 0x12e,
    "Veldt": 0x1bc,
    "Serpent Trench": 0x050,
    "Gogo's Cave": 0x0d4,
    "Umaro's Cave": 0x07e,
    "Kefka at Narshe": 0x046,
    "Tzen Thief": 0x27c,
    "Doom Gaze": 0x2a1,
    "Tritoch": 0x29e,
    "Auction House 10kGP": 0x16c,
    "Auction House 20kGP": 0x16d,
    "Dirt Dragon": 0x11c,
    "White Dragon": 0x121,
    "Ice Dragon": 0x11a,
    "Atma": 0x0a2,
    "Skull Dragon": 0x11e,
    "Gold Dragon": 0x11d
}

additional_event_flags = {
    "Lone Wolf Encountered": 0x68d,
    "Lone Wolf First Reward Picked": 0x29f,
    "Lone Wolf Both Rewards Picked": 0x241,
    "Narshe Weapon Shop Encountered": 0x605,
    "Narshe Weapon Shop First Reward Picked": 0x0b5,
    "Narshe Weapon Shop Both Rewards Picked": 0x0b7
}

treasure_chest_data: Dict[str, Tuple[int, int, int]] = {
    "Narshe Arvis's Clock": (0x1E40, 2, 1),
    "Narshe Elder's Clock": (0x1E41, 2, 9),
    "Narshe Adventuring School Advanced Battle Tactics Chest": (0x1E51, 4, 74),
    "Narshe Adventuring School Battle Tactics Chest": (0x1E51, 3, 75),
    "Narshe Adventuring School Environmental Science Chest": (0x1E51, 2, 76),
    "Narshe Adventuring School Environmental Science Pot": (0x1E51, 5, 77),
    "Narshe Treasure House South Chest": (0x1E41, 1, 8),
    "Narshe Treasure House Middle Right": (0x1E41, 0, 7),
    "Narshe Treasure House Middle Left": (0x1E40, 7, 6),
    "Narshe Treasure House Top Right": (0x1E40, 6, 5),
    "Narshe Treasure House Top Middle": (0x1E40, 5, 4),
    "Narshe Treasure House Top Left": (0x1E40, 4, 3),
    "Narshe West Mines Right WoB": (0x1E60, 3, 14),
    "Narshe West Mines Left WoB": (0x1E60, 4, 15),
    "Narshe Moogle Lair WoB": (0x1E60, 5, 16),
    "Narshe West Mines Right WoR": (0x1E41, 3, 10),
    "Narshe West Mines Left WoR": (0x1E41, 4, 11),
    "Narshe Moogle Lair WoR": (0x1E41, 5, 12),
    "Albrook Armor Shop Left": (0x1E4C, 5, 205),
    "Albrook Armor Shop Right": (0x1E4C, 6, 206),
    "Albrook Cafe Clock": (0x1E4C, 7, 207),
    "Albrook Inn Barrel": (0x1E4C, 2, 202),
    "Albrook Weapon Shop Pot": (0x1E4C, 4, 204),
    "Albrook Docks Crate": (0x1E4C, 3, 208),
    "Ancient Cave North Cavern Left": (0x1E58, 5, 272),
    "Ancient Cave North Cavern Right": (0x1E58, 4, 271),
    "Ancient Cave South Cavern Bottom": (0x1E58, 7, 274),
    "Ancient Cave South Cavern Top": (0x1E58, 6, 273),
    "Ancient Cave West Cavern Bottom": (0x1E59, 0, 275),
    "Ancient Cave West Cavern Left": (0x1E59, 1, 276),
    "Ancient Castle Treasure Room Left": (0x1E59, 2, 277),
    "Ancient Castle Treasure Room Right": (0x1E59, 3, 278),
    "Ancient Castle East Room": (0x1E59, 6, 280),
    "Ancient Castle Library": (0x1E59, 4, 281),
    "Ancient Castle Jail": (0x1E59, 5, 279),
    "Sealed Gate Basement 1": (0x1E4F, 3, 254),
    "Sealed Gate Basement 2 Bottom": (0x1E50, 5, 264),
    "Sealed Gate Basement 2 Top": (0x1E50, 6, 265),
    "Sealed Gate Basement 3 Bottom Left": (0x1E4F, 4, 255),
    "Sealed Gate Basement 3 Island": (0x1E4F, 5, 256),
    "Sealed Gate Basement 3 Plaza": (0x1E50, 0, 259),
    "Sealed Gate Basement 3 Hidden Passage": (0x1E4F, 6, 257),
    "Sealed Gate Basement 3 Bridge": (0x1E4F, 7, 258),
    "Sealed Gate Entrance": (0x1E4F, 2, 253),
    "Sealed Gate Save Point": (0x1E48, 4, 266),
    "Sealed Gate Treasure Room Left": (0x1E50, 1, 260),
    "Sealed Gate Treasure Room Upper Left": (0x1E50, 2, 261),
    "Sealed Gate Treasure Room Upper Floor Left": (0x1E50, 3, 262),
    "Sealed Gate Treasure Room Upper Floor Right": (0x1E50, 4, 263),
    "Darill's Tomb Basement 2 Southeast": (0x1E53, 4, 176),
    "Darill's Tomb Basement 2 Southwest": (0x1E53, 5, 177),
    "Darill's Tomb Basement 3 Center": (0x1E53, 6, 178),
    "Darill's Tomb Basement 3 Right": (0x1E53, 7, 179),
    "Darill's Tomb Pre-Boss Room Left": (0x1E54, 1, 181),
    "Darill's Tomb Pre-Boss Room Right": (0x1E54, 0, 180),
    "Doma Castle Cyan's Bedroom": (0x1E4C, 0, 95),
    "Doma Castle Lower Hall Pot": (0x1E46, 4, 92),
    "Doma Castle Southeast Tower Left": (0x1E46, 5, 93),
    "Doma Castle Southeast Tower Right": (0x1E46, 6, 94),
    "Doma Castle West Sleeping Quarters Chest": (0x1E56, 3, 96),
    "Doma Castle West Sleeping Quarters Clock": (0x1E46, 3, 91),
    "Dragon's Neck Cabin Pot": (0x1E5C, 5, 126),
    "Duncan's Cabin Bucket": (0x1E44, 4, 67),
    "Cyan's Dream Phantom Train Fourth Car Upper Right": (0x1E57, 4, 104),
    "Cyan's Dream Phantom Train Fourth Car Middle": (0x1E57, 5, 105),
    "Cyan's Dream Phantom Train Third Car Bottom Right": (0x1E57, 2, 200),
    "Cyan's Dream Phantom Train Third Car Middle": (0x1E57, 3, 201),
    "Esper Mountain Entrance Cavern": (0x1E4D, 5, 239),
    "Esper Mountain Outside Bridge": (0x1E4D, 2, 236),
    "Esper Mountain Side Slope": (0x1E4D, 3, 237),
    "Esper Mountain Treasure Slope": (0x1E4D, 4, 238),
    "Fanatics' Tower Seventeenth Floor": (0x1E56, 5, 232),
    "Fanatics' Tower Twenty-sixth Floor": (0x1E56, 6, 233),
    "Fanatics' Tower Thirty-fifth Floor": (0x1E56, 7, 234),
    "Fanatics' Tower Seventh Floor": (0x1E57, 1, 235),
    "Fanatics' Tower Eighth Floor": (0x1E56, 4, 230),
    "Figaro Castle East Shop Left": (0x1E41, 6, 17),
    "Figaro Castle East Shop Right": (0x1E41, 7, 18),
    "Figaro Castle Upper Hall": (0x1E42, 1, 20),
    "Figaro Castle West Shop": (0x1E42, 0, 19),
    "Figaro Castle Basement 2 Treasure Room": (0x1E53, 2, 26),
    "Figaro Castle Basement 3 Treasure Room Far Left": (0x1E52, 6, 21),
    "Figaro Castle Basement 3 Treasure Room Left": (0x1E52, 7, 22),
    "Figaro Castle Basement 3 Treasure Room Right": (0x1E53, 0, 23),
    "Figaro Castle Basement 3 Treasure Room Far Right": (0x1E53, 1, 24),
    "Figaro Castle Basement 3 Treasure Room Statue": (0x1E53, 3, 25),
    "Floating Continent North Path": (0x1E50, 7, 268),
    "Floating Continent Lower Path": (0x1E4B, 7, 270),
    "Floating Continent Northeast of Save": (0x1E51, 0, 269),
    "Floating Continent Escape": (0x1E51, 1, 267),
    "Imperial Base First Row Right": (0x1E4D, 7, 241),
    "Imperial Base First Row Left": (0x1E4D, 6, 240),
    "Imperial Base Stove": (0x1E4F, 1, 251),
    "Imperial Base Second Row Far Right": (0x1E4E, 3, 245),
    "Imperial Base Second Row Right": (0x1E4E, 2, 244),
    "Imperial Base Second Row Left": (0x1E4E, 1, 243),
    "Imperial Base Second Row Far Left": (0x1E4E, 0, 242),
    "Imperial Base Third Row": (0x1E4E, 4, 246),
    "Imperial Base Fourth Row Left": (0x1E4E, 5, 247),
    "Imperial Base Fourth Row Right": (0x1E4E, 6, 248),
    "Imperial Base Fifth Row Left": (0x1E4E, 7, 249),
    "Imperial Base Fifth Row Right": (0x1E4F, 0, 250),
    "Imperial Base Bottom Right Hidden Chest": (0x1E60, 1, 252),
    "Imperial Camp Kick Chest": (0x1E46, 2, 87),
    "Imperial Camp Central Tent Left": (0x1E5A, 4, 90),
    "Imperial Camp Central Tent Right": (0x1E5A, 3, 89),
    "Imperial Camp Central Tent Back": (0x1E5A, 2, 88),
    "Owzer's House Pot": (0x1E48, 2, 131),
    "Owzer's Basement Left Door": (0x1E5A, 5, 129),
    "Owzer's Basement Door Trio": (0x1E60, 2, 130),
    "Kefka's Tower Group 3 Balcony Left": (0x1E5C, 1, 174),
    "Kefka's Tower Group 3 Balcony Right": (0x1E5D, 3, 175),
    "Kefka's Tower Group 3 Entrance Stairs": (0x1E5C, 2, 282),
    "Kefka's Tower Group 3 Hidden Room": (0x1E5E, 1, 283),
    "Kefka's Tower Group 1 Metal Switchback": (0x1E5A, 7, 182),
    "Kefka's Tower Group 1 Landing Area": (0x1E5A, 6, 209),
    "Kefka's Tower Group 2 Left Area Top": (0x1E5B, 1, 210),
    "Kefka's Tower Group 2 Left Area Bottom": (0x1E5B, 2, 211),
    "Kefka's Tower Group 3 Right Path": (0x1E5B, 5, 214),
    "Kefka's Tower Group 3 After Magitek Left": (0x1E5B, 3, 212),
    "Kefka's Tower Group 3 After Magitek Right": (0x1E5B, 6, 215),
    "Kefka's Tower Group 1 Winding Path": (0x1E5B, 4, 213),
    "Kefka's Tower Poltergeist Hidden Chest": (0x1E5E, 2, 216),
    "Kefka's Tower Group 2 Outside Switchback": (0x1E5B, 7, 217),
    "Kefka's Tower Group 2 Pipe Output": (0x1E5C, 0, 218),
    "Kefka's Tower Group 2 Switch Room": (0x1E5B, 0, 173),
    "Kohlingen Old Man's House": (0x1E48, 1, 127),
    "Kohlingen Rachel's House Clock": (0x1E48, 5, 128),
    "Magitek Factory North Upper Left": (0x1E4A, 2, 146),
    "Magitek Factory North Right Side Pipe": (0x1E4A, 3, 147),
    "Magitek Factory North Lower Landing": (0x1E4A, 4, 148),
    "Magitek Factory North Across Conveyor Belt": (0x1E4A, 7, 151),
    "Magitek Factory North Near Crate": (0x1E4A, 5, 149),
    "Magitek Factory North Lower Balcony": (0x1E4A, 6, 150),
    "Magitek Factory South Secret Room Left": (0x1E4B, 2, 154),
    "Magitek Factory South Secret Room Right": (0x1E4B, 3, 155),
    "Magitek Factory South Lower Balcony": (0x1E4B, 4, 156),
    "Magitek Factory South Hidden Chest": (0x1E4B, 5, 157),
    "Magitek Factory South Lower Left": (0x1E4B, 0, 152),
    "Magitek Factory South Bottom Left": (0x1E4B, 1, 153),
    "Magitek Factory Specimen Room": (0x1E4B, 6, 158),
    "Maranda Crate Left": (0x1E5E, 5, 172),
    "Maranda Crate Bottom Right": (0x1E5E, 4, 171),
    "Mobliz Shelter Pot": (0x1E54, 7, 108),
    "Mobliz Post Office Clock": (0x1E47, 5, 116),
    "Mobliz House Barrel": (0x1E5F, 3, 115),
    "Mt. Kolts Exit": (0x1E45, 0, 73),
    "Mt. Kolts Hidden Cavern": (0x1E44, 7, 72),
    "Mt. Kolts West Face South": (0x1E44, 6, 69),
    "Mt. Kolts West Face North": (0x1E44, 5, 68),
    "Mt. Zozo East Cavern Middle": (0x1E54, 3, 122),
    "Mt. Zozo East Cavern Right": (0x1E54, 2, 121),
    "Mt. Zozo East Cavern Lower Left": (0x1E54, 5, 124),
    "Mt. Zozo East Cavern Upper": (0x1E54, 4, 123),
    "Mt. Zozo Treasure Slope": (0x1E54, 6, 120),
    "Mt. Zozo Cyan's Room": (0x1E5D, 6, 125),
    "Umaro's Cave Basement 1 Lower Left": (0x1E55, 2, 170),
    "Umaro's Cave Basement 1 Left Central": (0x1E55, 0, 169),
    "Umaro's Cave Basement 2 Lower Left": (0x1E55, 1, 168),
    "Nikeah Inn Clock": (0x1E47, 6, 117),
    "Phantom Train Dining Car": (0x1E46, 7, 107),
    "Phantom Train Third Car Far Left Chest": (0x1E5E, 3, 114),
    "Phantom Train Third Car Left Chest": (0x1E47, 4, 113),
    "Phantom Train Third Car Right Chest": (0x1E47, 3, 112),
    "Phantom Train Third Car Far Right Chest": (0x1E47, 2, 111),
    "Phoenix Cave Lower Cavern East Pool Island": (0x1E56, 0, 192),
    "Phoenix Cave Lower Cavern East Pool Bridge": (0x1E55, 6, 193),
    "Phoenix Cave Lower Cavern Spikes": (0x1E55, 7, 194),
    "Phoenix Cave Lower Cavern Rock Jumping": (0x1E57, 6, 195),
    "Phoenix Cave Lower Cavern Cool Lava": (0x1E55, 3, 191),
    "Phoenix Cave Upper Cavern Spikes": (0x1E55, 5, 197),
    "Phoenix Cave Upper Cavern Hidden Room": (0x1E58, 3, 199),
    "Phoenix Cave Upper Cavern Across Bridge": (0x1E55, 4, 196),
    "Phoenix Cave Upper Cavern Near Red Dragon": (0x1E56, 1, 198),
    "Returners' Hideout Banon's Room": (0x1E46, 0, 85),
    "Returners' Hideout Bedroom": (0x1E45, 2, 79),
    "Returners' Hideout Main Room Pot": (0x1E45, 1, 78),
    "Returners' Hideout North Room Bottom Left": (0x1E45, 6, 83),
    "Returners' Hideout North Room Bottom Right": (0x1E45, 7, 84),
    "Returners' Hideout North Room Upper Left": (0x1E45, 5, 82),
    "Returners' Hideout North Room Bucket": (0x1E45, 3, 80),
    "Returners' Hideout North Room Pot": (0x1E45, 4, 81),
    "Returners' Hideout North Room Secret Room": (0x1E46, 1, 86),
    "Serpent Trench First Branch": (0X1E47, 7, 118),
    "Serpent Trench Second Branch": (0x1E48, 0, 119),
    "South Figaro Basement Hidden Path Entrance": (0x1E44, 0, 57),
    "South Figaro Basement Hidden Path North Left": (0x1E44, 2, 59),
    "South Figaro Basement Hidden Path North Right": (0x1E44, 3, 60),
    "South Figaro Basement Hidden Path South": (0x1E44, 1, 58),
    "South Figaro Basement 2 South": (0x1E5F, 7, 64),
    "South Figaro Basement 2 Northeast": (0x1E5F, 5, 62),
    "South Figaro Basement 2 Hidden Chest": (0x1E5F, 6, 63),
    "South Figaro Old Man's Bucket": (0x1E43, 6, 55),
    "South Figaro Secret Path Clock": (0x1E43, 7, 56),
    "South Figaro Chocobo Stable Box WoB": (0x1E61, 6, 48),
    "South Figaro Chocobo Stable Barrel WoB": (0x1E61, 5, 47),
    "South Figaro Shoreline Box WoB": (0x1E61, 7, 49),
    "South Figaro Barrel Near Cafe WoB": (0x1E61, 3, 45),
    "South Figaro Box Near Cafe WoB": (0x1E61, 4, 46),
    "South Figaro Arsenal Barrel WoB": (0x1E61, 2, 44),
    "South Figaro Wall Barrel WoB": (0x1E62, 0, 50),
    "South Figaro Mansion Exit Barrel WoB": (0x1E61, 1, 43),
    "South Figaro Chocobo Stable Box WoR": (0x1E43, 1, 40),
    "South Figaro Chocobo Stable Barrel WoR": (0x1E43, 0, 39),
    "South Figaro Shoreline Box WoR": (0x1E5C, 6, 41),
    "South Figaro Barrel Near Cafe WoR": (0x1E42, 6, 37),
    "South Figaro Box Near Cafe WoR": (0x1E42, 7, 38),
    "South Figaro Arsenal Barrel WoR": (0x1E42, 5, 36),
    "South Figaro Wall Barrel WoR": (0x1E5C, 7, 42),
    "South Figaro Mansion Exit Barrel WoR": (0x1E42, 4, 35),
    "South Figaro Mansion Basement West Cell": (0x1E5F, 4, 61),
    "South Figaro Mansion Basement East Cell": (0x1E60, 0, 65),
    "South Figaro Mansion Basement East Room Left": (0x1E43, 2, 51),
    "South Figaro Mansion Basement East Room Below Clock": (0x1E43, 4, 53),
    "South Figaro Mansion Basement East Room Right": (0x1E43, 3, 52),
    "South Figaro Mansion Basement East Room Far Right": (0x1E43, 5, 54),
    "South Figaro Cave Eastern Passage WoB": (0x1E60, 7, 30),
    "South Figaro Cave Southwest Passage WoB": (0x1E60, 6, 29),
    "South Figaro Cave Eastern Bridge WoB": (0x1E61, 0, 31),
    "South Figaro Cave Eastern Passage WoR": (0x1E4C, 1, 28),
    "South Figaro Cave Southwest Passage WoR": (0x1E42, 2, 27),
    "South Figaro Cave Eastern Bridge WoR": (0x1E42, 3, 66),
    "Thamasa Strago's House Near Table (Second Floor)": (0x1E5C, 3, 224),
    "Thamasa Item Shop Barrel": (0x1E5F, 1, 222),
    "Thamasa Relic Shop Barrel": (0x1E5F, 0, 221),
    "Thamasa Inn Barrel": (0x1E5F, 2, 223),
    "Thamasa Strago's House Barrel": (0x1E5E, 7, 220),
    "Thamasa Elder's House Barrel": (0x1E5E, 6, 219),
    "Burning House First Chest": (0x1E4D, 0, 225),
    "Burning House Second Chest": (0x1E4D, 1, 226),
    "Collapsing House First Floor Top Right": (0x1E51, 6, 183),
    "Collapsing House First Floor Middle": (0x1E52, 1, 186),
    "Collapsing House First Floor Top Left": (0x1E51, 7, 184),
    "Collapsing House First Floor Left": (0x1E52, 0, 185),
    "Collapsing House First Floor Bottom Left": (0x1E52, 2, 187),
    "Collapsing House Basement Bottom": (0x1E52, 5, 190),
    "Collapsing House Basement Left": (0x1E52, 4, 189),
    "Collapsing House Basement Right": (0x1E52, 3, 188),
    "Veldt Cave North Upper Left": (0x1E57, 7, 227),
    "Veldt Cave North Hidden Room": (0x1E58, 0, 228),
    "Veldt Cave South Lower Left": (0x1E58, 1, 229),
    "Zone Eater Crusher Room Right": (0x1E5D, 0, 165),
    "Zone Eater Crusher Room Middle": (0x1E5D, 1, 166),
    "Zone Eater Crusher Room Left": (0x1E5D, 2, 167),
    "Zone Eater Jumping Room": (0x1E5C, 4, 164),
    "Zone Eater Lower Cavern Left": (0x1E58, 2, 161),
    "Zone Eater Lower Cavern Right": (0x1E5A, 1, 160),
    "Zone Eater Triple Bridge Right": (0x1E5D, 5, 163),
    "Zone Eater Triple Bridge Middle": (0x1E5D, 4, 162),
    "Zone Eater Triple Bridge Left": (0x1E5A, 0, 159),
    "Zozo Armor Shop": (0x1E49, 0, 134),
    "Zozo Cafe": (0x1E49, 2, 133),
    "Zozo Clock Puzzle": (0x1E49, 1, 132),
    "Zozo Relic Shop Seventh Floor": (0x1E49, 3, 135),
    "Zozo West Tower North Left Pot": (0x1E5D, 7, 137),
    "Zozo West Tower North Right Pot": (0x1E5E, 0, 138),
    "Zozo Relic Shop Thirteenth Floor": (0x1E49, 4, 136),
    "Zozo Esper Room Left": (0x1E48, 6, 139),
    "Zozo Esper Room Right": (0x1E48, 7, 140)
}


class FF6WCDeltaPatch(APDeltaPatch):
    hash = NA10HASH
    game = "Final Fantasy 6 Worlds Collide"
    patch_file_ending = ".apff6wc"

    @classmethod
    def get_source_data(cls) -> bytes:
        return get_base_rom_bytes()


def get_base_rom_bytes(file_name: str = "") -> bytes:
    base_rom_bytes = getattr(get_base_rom_bytes, "base_rom_bytes", None)
    if not base_rom_bytes:
        file_name = get_base_rom_path(file_name)
        base_rom_bytes = bytes(open(file_name, "rb").read())

        basemd5 = hashlib.md5()
        basemd5.update(base_rom_bytes)
        if NA10HASH != basemd5.hexdigest():
            raise Exception('Supplied Base Rom does not match known MD5 for NA (1.0) release. '
                            'Get the correct game and version, then dump it')
        setattr(get_base_rom_bytes, "base_rom_bytes", base_rom_bytes)
    return base_rom_bytes


def get_base_rom_path(file_name: str = "") -> str:
    options = Utils.get_options()
    if not file_name:
        file_name = options["ff6wc_options"]["rom_file"]
    if not os.path.exists(file_name):
        file_name = Utils.local_path(file_name)
    return file_name


def get_event_flag_value(event_id: int) -> Tuple[int, int]:
    event_byte = event_flag_base_address + (event_id // 8)
    event_bit = event_id % 8
    hbyte = hex(event_byte)
    bbyte = bin(event_byte)
    hbit = hex(bit_positions[event_bit])
    bbit = bin(bit_positions[event_bit])
    logging.debug(f"{hbyte=} {bbyte=} {hbit=} {bbit=}")
    return event_byte, bit_positions[event_bit]


def get_obtained_esper_bit(esper_name: int) -> Tuple[int, int]:
    esper_index = esper_name
    esper_byte = esper_bit_base_address + (esper_index // 8)
    esper_bit = esper_index % 8
    return esper_byte, bit_positions[esper_bit]


def add_esper(initial: int, esper_name: int) -> int:
    _byte, bit = get_obtained_esper_bit(esper_name)
    return initial | bit


def get_character_bit(character: int, address: int) -> Tuple[int, int]:
    character_index = character
    character_byte = address + character_index // 8
    character_bit = character_index % 8
    return character_byte, bit_positions[character_bit]


def get_character_initialized_bit(character_name: int) -> Tuple[int, int]:
    return get_character_bit(character_name, character_intialized_bit_base_address)


def get_character_recruited_bit(character_name: int) -> Tuple[int, int]:
    return get_character_bit(character_name, character_recruited_bit_base_address)


def get_treasure_chest_bit(treasure_chest: str) -> Tuple[int, int]:
    treasure_byte = treasure_chest_data[treasure_chest][0] - 0x1E40
    treasure_bit = bit_positions[treasure_chest_data[treasure_chest][1]]
    return treasure_byte, treasure_bit


def get_map_index(map_byte: int) -> int:
    return map_byte & 0x01FF
