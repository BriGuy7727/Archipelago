import struct
import typing
from BaseClasses import CollectionState, Region
from struct import unpack

if typing.TYPE_CHECKING:
    from .Rom import RomData

animal_map = {
    "Rick Spawn": 0,
    "Kine Spawn": 1,
    "Coo Spawn": 2,
    "Nago Spawn": 3,
    "ChuChu Spawn": 4,
    "Pitch Spawn": 5
}


class Room(Region):
    pointer: int = 0
    level: int = 0
    stage: int = 0
    room: int = 0
    music: int = 0
    default_exits: typing.List[typing.Dict[str, typing.Union[int, typing.List[str]]]]
    animal_pointers: typing.List[int]

    def __init__(self, name, player, multiworld, hint, level, stage, room, pointer, music, default_exits, animal_pointers):
        super().__init__(name, player, multiworld, hint)
        self.level = level
        self.stage = stage
        self.room = room
        self.pointer = pointer
        self.music = music
        self.default_exits = default_exits
        self.animal_pointers = animal_pointers

    def patch(self, rom: "RomData"):
        rom.write_byte(self.pointer + 2, self.music)
        animals = [x.item for x in self.locations if "Animal" in x.name]
        if len(animals) > 0:
            for current_animal, address in zip(animals, self.animal_pointers):
                rom.write_byte(address + 7, animal_map[animals[current_animal]])


room_data = [
    0x346711,
    0x3365b5,
    0x2d2d0a,
    0x3513aa,
    0x2d7256,
    0x2c1c53,

    0x3240a3,
    0x2eafe5,
    0x345ead,
    0x2d51ad,
    0x3698a6,
    0x2d4229,
    0x2c0f25,

    0x300f8b,
    0x30e74b,
    0x30d442,
    0x2d29a8,
    0x2d7531,
    0x2dbe33,
    0x2f124c,
    0x2c1e35,

    0x34f7b4,
    0x346f71,
    0x2e60a9,
    0x38cdda,
    0x326e14,
    0x35608f,
    0x30387f,
    0x2e5299,
    0x2d9ee2,
    0x2e70be,
    0x2c12e9,

    0x32688d,
    0x2e850e,
    0x32c42b,
    0x2d43bb,
    0x2d5f45,
    0x2d33af,
    0x2c0c52,
    0x31ac7f,

    0x3386e8,
    0x33ce35,
    0x338049,
    0x32b461,
    0x354403,
    0x2ef2a1,
    0x2e8098,
    0x2e203d,
    0x2c03d9,

    0x2d88a9,

    0x320bef,
    0x36c250,
    0x2d1a48,
    0x364dac,
    0x2d623f,
    0x2e8ff9,
    0x2e896e,
    0x2eca27,
    0x2c15bc,

    0x330000,
    0x2f0f43,
    0x34a947,
    0x3810d7,
    0x2d5c48,
    0x2f734e,
    0x2d5dc7,
    0x2c1a71,

    0x35ab46,
    0x370000,
    0x38b164,
    0x2edfaf,
    0x2d54ba,
    0x2d95ee,
    0x2c13da,
    0x303c20,

    0x2f092c,
    0x2d3d6e,
    0x2e0f07,
    0x2d9886,
    0x2c079d,
    0x2e6c2d,
    0x315bf5,
    0x30260c,
    0x331e0f,
    0x2e8b9d,
    0x2e9225,
    0x33ae5e,
    0x305853,
    0x2d248e,

    0x3171b1,
    0x362188,
    0x371abf,
    0x3be88d,
    0x2e2ecf,
    0x30f0a5,
    0x3530c8,
    0x3942fa,
    0x2e754a,
    0x2d36f9,
    0x2e6e76,
    0x2c0a70,

    0x2d01c8,
    0x2d5640,
    0x3781f5,
    0x2f3054,
    0x2fcf3f,
    0x358632,
    0x310000,
    0x36b7f7,
    0x37426b,
    0x2d151b,
    0x2ed5fe,
    0x2c0b61,

    0x302d7a,

    0x35c6ab,
    0x3046d4,
    0x3598d4,
    0x38bfea,
    0x34341c,
    0x30e0fd,
    0x2fe3dc,
    0x2d9b16,
    0x2c06ac,

    0x37f992,
    0x2d0e22,
    0x35e194,
    0x31ccf3,
    0x2ef0cc,
    0x3262f5,
    0x39fe24,
    0x2ee760,
    0x2eb616,
    0x34b166,
    0x2db285,
    0x2c2017,

    0x361664,
    0x2d4097,
    0x38dbbe,
    0x3422e6,
    0x366383,
    0x2d60c3,
    0x318f61,
    0x2c1016,
    0x2d49f9,

    0x35bda2,
    0x2d1c01,
    0x357cd0,
    0x341189,
    0x32791c,
    0x2d188f,
    0x2f3943,
    0x352724,
    0x2dcee6,
    0x2c088e,

    0x37e296,
    0x2e944e,
    0x2ea788,
    0x342b83,
    0x379af5,
    0x2e7304,
    0x3379a9,
    0x2d3a3c,
    0x2c1980,
    0x37a720,

    0x329449,
    0x2d6c91,
    0x2d73c5,
    0x307e62,
    0x308bfb,
    0x307af9,
    0x3092bb,
    0x30741d,
    0x308532,
    0x30778e,
    0x3081ca,
    0x2d9c5d,
    0x2e050b,
    0x2d6b1b,
    0x2e3d40,
    0x2d5ac9,
    0x2d0fe2,
    0x2d11a1,
    0x2da65b,
    0x2d63bb,
    0x2d5026,
    0x2d69a3,
    0x2d071a,
    0x328979,
    0x2efba6,
    0x2ec82a,
    0x2ebe33,
    0x2ecc24,
    0x2ece21,
    0x2d0390,
    0x2d9204,
    0x2edbd2,
    0x2e9ce1,
    0x2e9675,
    0x2e9899,
    0x2e9abd,
    0x2d90b4,
    0x2ee949,
    0x2d57c5,
    0x2ec032,
    0x2ec230,
    0x2ec42e,
    0x2ed40b,
    0x2d99cf,
    0x2c0d43,

    0x2da51d,

    0x3069bb,
    0x2ef813,
    0x32237a,
    0x2ebc2f,
    0x33d479,
    0x2e5e55,
    0x35f378,
    0x2d1360,
    0x34e0bf,
    0x2ef9dd,
    0x3211d6,
    0x35b478,
    0x2d2642,
    0x2c097f,

    0x2ff32b,
    0x316055,
    0x3251de,
    0x32fb1f,
    0x34c17c,
    0x31f496,
    0x2d8a05,
    0x2d8e0a,
    0x2da2a1,
    0x2c179e,

    0x2f50bb,
    0x30f9f7,
    0x311339,
    0x2db020,
    0x3145df,
    0x2d4e9c,
    0x3eff12,
    0x2c05bb,

    0x2ee389,
    0x2eeb2f,
    0x327e99,
    0x324c23,
    0x32d3b4,
    0x32d8cc,
    0x31a43e,
    0x2d486a,
    0x2d7f0c,
    0x2de601,
    0x2c11f8,

    0x30b736,
    0x2e8dcc,
    0x36fee2,
    0x2fc76a,
    0x2da024,
    0x2d66b2,
    0x306d33,
    0x2da8d4,
    0x2c1f26,

    0x31e4d7,
    0x31a018,
    0x2e360e,
    0x2fca07,
    0x2f8998,
    0x3186f1,
    0x3164b4,
    0x31c8f1,
    0x2e313b,
    0x2f2460,
    0x2fcca3,
    0x2e0c8a,
    0x2e54f4,
    0x2d3f03,
    0x2ef474,
    0x2eb822,
    0x2c14cb,

    0x2dc19a,

    0x335127,
    0x36e0ec,
    0x322f30,
    0x2ed217,
    0x315791,
    0x33f935,
    0x2d8f5f,
    0x2c2108,

    0x2f67f0,
    0x32e2b9,
    0x350000,
    0x2e574e,
    0x2e503e,
    0x2fbce7,
    0x31e8c9,
    0x3104d5,
    0x2db153,
    0x2ea9a4,
    0x2c0e34,

    0x34b972,
    0x2e13f9,
    0x373549,
    0x37b340,
    0x2e5c00,
    0x2dfd32,
    0x374f55,
    0x2d9da0,
    0x2c188f,

    0x31f87f,
    0x337304,
    0x321d9a,
    0x30434d,
    0x31c4ef,
    0x3117f6,
    0x2f6da9,
    0x330f1a,
    0x2ea127,
    0x2ea349,
    0x31b4ac,
    0x2f0c3a,
    0x3007cc,
    0x336c5d,
    0x2ea56a,
    0x2f8c5c,
    0x2ed7f1,
    0x2ee19d,
    0x33f331,
    0x2eeef2,
    0x2c1107,

    0x3299a7,
    0x2e59a7,
    0x2f5c62,
    0x2fd99b,
    0x308897,
    0x2f6510,
    0x320000,
    0x2f5f49,
    0x30c0f1,
    0x2f1b5e,
    0x32af0c,
    0x2fe66a,
    0x2f9497,
    0x2e1b5a,
    0x2e29f6,
    0x3054d5,
    0x2e4b86,
    0x2f4dcf,
    0x2e3fa3,
    0x2f622e,
    0x2f9750,
    0x30ddd5,
    0x2e0000,
    0x305156,
    0x2e3876,
    0x3029c4,
    0x2fba45,
    0x31b097,
    0x2e3adb,
    0x35cfa8,
    0x2e1dcd,
    0x2e2c63,
    0x2e62fc,
    0x2e0286,
    0x309ccc,
    0x3afc23,
    0x2e251a,
    0x2c1b62,

    0x33a7d9,
    0x30ca9f,
    0x2f4219,
    0x30cdd6,
    0x30fd0b,
    0x30c768,
    0x30f3c2,
    0x2facfe,
    0x2f761f,
    0x2fe8f8,
    0x2f9a08,
    0x2fee13,
    0x2faa4c,
    0x2ff83d,
    0x2f9cbf,
    0x2fd706,
    0x2fa798,
    0x2ffac5,
    0x2f9f76,
    0x2e0a0c,
    0x2fa22d,
    0x2ffd4c,
    0x2f8f1e,
    0x2e778f,
    0x2c16ad,

    0x2d796f,

    0x2eff36,

    0x2d85f1,
    0x301360,
    0x2da3df,
    0x2dc2b9,
    0x2d7c3f,
    0x2c29d2
]
