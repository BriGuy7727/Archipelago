from __future__ import annotations

import json
import struct
import zipfile

from typing import ClassVar, Dict, Tuple, Any, Optional, Union, BinaryIO, List

import bsdiff4


class AutoPatchRegister(type):
    patch_types: ClassVar[Dict[str, AutoPatchRegister]] = {}
    file_endings: ClassVar[Dict[str, AutoPatchRegister]] = {}

    def __new__(mcs, name: str, bases: Tuple[type, ...], dct: Dict[str, Any]) -> AutoPatchRegister:
        # construct class
        new_class = super().__new__(mcs, name, bases, dct)
        if "game" in dct:
            AutoPatchRegister.patch_types[dct["game"]] = new_class
            if not dct["patch_file_ending"]:
                raise Exception(f"Need an expected file ending for {name}")
            AutoPatchRegister.file_endings[dct["patch_file_ending"]] = new_class
        return new_class

    @staticmethod
    def get_handler(file: str) -> Optional[AutoPatchRegister]:
        for file_ending, handler in AutoPatchRegister.file_endings.items():
            if file.endswith(file_ending):
                return handler
        return None


current_patch_version: int = 6


class AutoPatchExtensionRegister(type):
    extension_types: ClassVar[Dict[str, AutoPatchExtensionRegister]] = {}
    required_extensions: List[str]

    def __new__(mcs, name: str, bases: Tuple[type, ...], dct: Dict[str, Any]) -> AutoPatchExtensionRegister:
        # construct class
        new_class = super().__new__(mcs, name, bases, dct)
        if "game" in dct:
            AutoPatchExtensionRegister.extension_types[dct["game"]] = new_class
        return new_class

    @staticmethod
    def get_handler(game: str) -> Union[AutoPatchExtensionRegister, List[AutoPatchExtensionRegister]]:
        for extension_type, handler in AutoPatchExtensionRegister.extension_types.items():
            if extension_type == game:
                if len(handler.required_extensions) > 0:
                    handlers = [handler]
                    for required in handler.required_extensions:
                        if required in AutoPatchExtensionRegister.extension_types:
                            handlers.append(AutoPatchExtensionRegister.extension_types[required])
                        else:
                            raise NotImplementedError(f"No handler for {required}.")
                    return handlers
                else:
                    return handler
        return APPatchExtension


class APContainer:
    """A zipfile containing at least archipelago.json"""
    version: int = current_patch_version
    compression_level: int = 9
    compression_method: int = zipfile.ZIP_DEFLATED
    game: Optional[str] = None

    # instance attributes:
    path: Optional[str]
    player: Optional[int]
    player_name: str
    server: str

    def __init__(self, path: Optional[str] = None, player: Optional[int] = None,
                 player_name: str = "", server: str = ""):
        self.path = path
        self.player = player
        self.player_name = player_name
        self.server = server

    def write(self, file: Optional[Union[str, BinaryIO]] = None) -> None:
        zip_file = file if file else self.path
        if not zip_file:
            raise FileNotFoundError(f"Cannot write {self.__class__.__name__} due to no path provided.")
        with zipfile.ZipFile(zip_file, "w", self.compression_method, True, self.compression_level) \
                as zf:
            if file:
                self.path = zf.filename
            self.write_contents(zf)

    def write_contents(self, opened_zipfile: zipfile.ZipFile) -> None:
        manifest = self.get_manifest()
        try:
            manifest_str = json.dumps(manifest)
        except Exception as e:
            raise Exception(f"Manifest {manifest} did not convert to json.") from e
        else:
            opened_zipfile.writestr("archipelago.json", manifest_str)

    def read(self, file: Optional[Union[str, BinaryIO]] = None) -> None:
        """Read data into patch object. file can be file-like, such as an outer zip file's stream."""
        zip_file = file if file else self.path
        if not zip_file:
            raise FileNotFoundError(f"Cannot read {self.__class__.__name__} due to no path provided.")
        with zipfile.ZipFile(zip_file, "r") as zf:
            if file:
                self.path = zf.filename
            self.read_contents(zf)

    def read_contents(self, opened_zipfile: zipfile.ZipFile) -> None:
        with opened_zipfile.open("archipelago.json", "r") as f:
            manifest = json.load(f)
        if manifest["compatible_version"] > self.version:
            raise Exception(f"File (version: {manifest['compatible_version']}) too new "
                            f"for this handler (version: {self.version})")
        self.player = manifest["player"]
        self.server = manifest["server"]
        self.player_name = manifest["player_name"]

    def get_manifest(self) -> Dict[str, Any]:
        return {
            "server": self.server,  # allow immediate connection to server in multiworld. Empty string otherwise
            "player": self.player,
            "player_name": self.player_name,
            "game": self.game,
            # minimum version of patch system expected for patching to be successful
            "compatible_version": 5,
            "version": current_patch_version,
        }


class APDeltaPatch(APContainer, metaclass=AutoPatchRegister):
    """An APContainer that additionally has delta.bsdiff4
    containing a delta patch to get the desired file, often a rom."""

    hash: Optional[str]  # base checksum of source file
    patch_file_ending: str = ""
    delta: Optional[bytes] = None
    result_file_ending: str = ".sfc"
    source_data: bytes

    def __init__(self, *args: Any, patched_path: str = "", **kwargs: Any) -> None:
        self.patched_path = patched_path
        super(APDeltaPatch, self).__init__(*args, **kwargs)

    def get_manifest(self) -> Dict[str, Any]:
        manifest = super(APDeltaPatch, self).get_manifest()
        manifest["base_checksum"] = self.hash
        manifest["result_file_ending"] = self.result_file_ending
        manifest["patch_file_ending"] = self.patch_file_ending
        return manifest

    @classmethod
    def get_source_data(cls) -> bytes:
        """Get Base data"""
        raise NotImplementedError()

    @classmethod
    def get_source_data_with_cache(cls) -> bytes:
        if not hasattr(cls, "source_data"):
            cls.source_data = cls.get_source_data()
        return cls.source_data

    def write_contents(self, opened_zipfile: zipfile.ZipFile):
        super(APDeltaPatch, self).write_contents(opened_zipfile)
        # write Delta
        opened_zipfile.writestr("delta.bsdiff4",
                                bsdiff4.diff(self.get_source_data_with_cache(), open(self.patched_path, "rb").read()),
                                compress_type=zipfile.ZIP_STORED)  # bsdiff4 is a format with integrated compression

    def read_contents(self, opened_zipfile: zipfile.ZipFile):
        super(APDeltaPatch, self).read_contents(opened_zipfile)
        self.delta = opened_zipfile.read("delta.bsdiff4")

    def patch(self, target: str):
        """Base + Delta -> Patched"""
        if not self.delta:
            self.read()
        result = bsdiff4.patch(self.get_source_data_with_cache(), self.delta)
        with open(target, "wb") as f:
            f.write(result)


class APProcedurePatch(APContainer, metaclass=AutoPatchRegister):
    """
    An APContainer that defines a procedure to produce the desired file.
    """
    procedure: List[Tuple[str, List[Any]]]
    tokens: List[Tuple[int, bytes]]
    hash: Optional[str]  # base checksum of source file
    source_data: bytes
    patch_file_ending: str = ""
    result_file_ending: str = ".sfc"
    files: Dict[str, bytes] = dict()

    @classmethod
    def get_source_data(cls) -> bytes:
        """Get Base data"""
        raise NotImplementedError()

    @classmethod
    def get_source_data_with_cache(cls) -> bytes:
        if not hasattr(cls, "source_data"):
            cls.source_data = cls.get_source_data()
        return cls.source_data

    def __init__(self, *args: Any, patched_path: str = "", **kwargs: Any):
        super(APProcedurePatch, self).__init__(*args, **kwargs)
        self.tokens = list()

    def get_manifest(self) -> Dict[str, Any]:
        manifest = super(APProcedurePatch, self).get_manifest()
        manifest["compatible_version"] = 6
        manifest["base_checksum"] = self.hash
        manifest["result_file_ending"] = self.result_file_ending
        manifest["patch_file_ending"] = self.patch_file_ending
        manifest["procedure"] = self.procedure
        return manifest

    def read_contents(self, opened_zipfile: zipfile.ZipFile) -> None:
        super(APProcedurePatch, self).read_contents(opened_zipfile)
        with opened_zipfile.open("archipelago.json", "r") as f:
            manifest = json.load(f)
        if manifest["version"] < 6:
            # support patching files made before moving to procedures
            self.procedure = [("apply_bsdiff4", ["delta.bsdiff4"])]
        else:
            self.procedure = manifest["procedure"]
        for file in opened_zipfile.namelist():
            if file not in ["archipelago.json"]:
                self.files[file] = opened_zipfile.read(file)

    def write_contents(self, opened_zipfile: zipfile.ZipFile) -> None:
        super(APProcedurePatch, self).write_contents(opened_zipfile)
        for file in self.files:
            opened_zipfile.writestr(file, self.files[file])

    def get_file(self, file: str) -> bytes:
        if file not in self.files:
            self.read()
        return self.files[file]

    def write_file(self, file_name: str, file: bytes) -> None:
        self.files[file_name] = file

    def get_token_binary(self) -> bytes:
        data = bytearray()
        data.extend(struct.pack("I", len(self.tokens)))
        for offset, bin_data in self.tokens:
            data.extend(struct.pack("I", offset))
            data.extend(struct.pack("I", len(bin_data)))
            data.extend(bin_data)
        return data

    def write_token(self, offset, data):
        self.tokens.append((offset, data))

    def patch(self, target: str):
        self.read()
        base_data = self.get_source_data_with_cache()
        patch_extender = AutoPatchExtensionRegister.get_handler(self.game)
        for step, args in self.procedure:
            if isinstance(patch_extender, List):
                extension = next((item for item in [getattr(extender, step, None) for extender in patch_extender]
                                 if item is not None), None)
            else:
                extension = getattr(patch_extender, step, None)
            if extension is not None:
                base_data = extension(self, base_data, *args)
            else:
                raise NotImplementedError(f"Unknown procedure {step} for {self.game}.")
        with open(target, 'wb') as f:
            f.write(base_data)


class APPatchExtension(metaclass=AutoPatchExtensionRegister):
    game: str
    required_extensions: List[str] = list()

    @staticmethod
    def apply_bsdiff4(caller: APProcedurePatch, rom: bytes, patch: str):
        return bsdiff4.patch(rom, caller.get_file(patch))

    @staticmethod
    def apply_tokens(caller: APProcedurePatch, rom: bytes, token_file: str) -> bytes:
        token_data = caller.get_file(token_file)
        rom_data = bytearray(rom)
        token_count = struct.unpack("I", token_data[0:4])[0]
        bpr = 4
        for _ in range(token_count):
            offset = struct.unpack("I", token_data[bpr:bpr + 4])[0]
            size = struct.unpack("I", token_data[bpr + 4:bpr + 8])[0]
            data = token_data[bpr + 8:bpr + 8 + size]
            rom_data[offset:offset + len(data)] = data
            bpr += 8 + size
        return rom_data
