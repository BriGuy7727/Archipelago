import asyncio
import subprocess
from typing import Any, Coroutine, Dict, Type
import colorama
from NetUtils import ClientStatus
import Utils
from CommonClient import CommonContext, server_loop, gui_enabled, \
    ClientCommandProcessor, logger, get_base_parser

from zilliandomizer.zri.memory import Memory
from zilliandomizer.zri import events
from zilliandomizer.utils.loc_name_maps import id_to_loc
from zilliandomizer.logic_components.items import id_to_item as id_to_zz_item
from zilliandomizer.patch import RescueInfo

from worlds.zillion.id_maps import item_pretty_id_to_useful_id
from worlds.zillion.config import base_id

# TODO: how to get rescue names (and other item names)
# TODO: test multiple yamls specifying zillion with no other games
# (reported causes archipelago to say that it can't beat the game)
# TODO: make sure close button works on ZillionClient window


class ZillionCommandProcessor(ClientCommandProcessor):
    def _cmd_test_command(self) -> None:
        """ test command processor """
        logger.info("text command executed")


class ZillionContext(CommonContext):
    game = "Zillion"
    command_processor: Type[ClientCommandProcessor] = ZillionCommandProcessor
    to_game: "asyncio.Queue[events.EventToGame]"
    items_handling = 1  # receive items from other players
    rescues: Dict[int, RescueInfo] = {}
    loc_mem_to_id: Dict[int, int] = {}
    got_slot_data: asyncio.Event

    def __init__(self,
                 server_address: str,
                 password: str,
                 to_game: "asyncio.Queue[events.EventToGame]"):
        super().__init__(server_address, password)
        self.to_game = to_game
        self.got_slot_data = asyncio.Event()

    # override
    def on_deathlink(self, data: Dict[str, Any]) -> None:
        self.to_game.put_nowait(events.DeathEventToGame())
        return super().on_deathlink(data)

    # override
    async def server_auth(self, password_requested: bool = False) -> None:
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        if not self.auth:
            # TODO: get auth name from game
            print("asking for slot name")
            logger.info('Enter slot name:')
            self.auth = await self.console_input()
            print(f"got slot name: {self.auth}")

        await self.send_connect()

    # override
    def run_gui(self) -> None:
        from kvui import GameManager

        class ZillionManager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago")
            ]
            base_title = "Archipelago Zillion Client"

        self.ui = ZillionManager(self)
        run_co: Coroutine[Any, Any, None] = self.ui.async_run()  # type: ignore
        # kivy types missing
        self.ui_task = asyncio.create_task(run_co, name="UI")

    def on_package(self, cmd: str, args: Dict[str, Any]) -> None:
        if cmd == "Connected":
            logger.info("logged in to Archipelago server")
            if "slot_data" not in args:
                logger.warn("`Connected` packet missing `slot_data`")
                return
            slot_data = args["slot_data"]

            if "rescues" not in slot_data:
                logger.warn("invalid Zillion `slot_data` in `Connected` packet")
                return
            rescues = slot_data["rescues"]
            self.rescues = {}
            for rescue_id, json_info in rescues.items():
                assert rescue_id in ("0", "1"), f"invalid rescue_id in Zillion slot_data: {rescue_id}"
                ri = RescueInfo(json_info["start_char"],
                                json_info["room_code"],
                                json_info["mask"])
                self.rescues[0 if rescue_id == "0" else 1] = ri

            if "loc_mem_to_id" not in slot_data:
                logger.warn("invalid Zillion `slot_data` in `Connected` packet")
                return
            loc_mem_to_id = slot_data["loc_mem_to_id"]
            self.loc_mem_to_id = {}
            for mem_str, id_str in loc_mem_to_id.items():
                mem = int(mem_str)
                id_ = int(id_str)
                room_i = mem // 256
                assert 0 <= room_i < 74
                assert id_ in id_to_loc
                self.loc_mem_to_id[mem] = id_

            self.got_slot_data.set()


async def zillion_sync_task(ctx: ZillionContext, to_game: "asyncio.Queue[events.EventToGame]") -> None:
    logger.info("started zillion sync task")
    from_game: "asyncio.Queue[events.EventFromGame]" = asyncio.Queue()

    logger.info("waiting for connection to server")
    await ctx.got_slot_data.wait()
    with Memory(ctx.rescues, ctx.loc_mem_to_id, from_game, to_game) as memory:
        next_item = 0
        while not ctx.exit_event.is_set():
            await memory.check()
            if from_game.qsize():
                event_from_game = from_game.get_nowait()
                if isinstance(event_from_game, events.AcquireLocationEventFromGame):
                    server_id = event_from_game.id + base_id
                    loc_name = id_to_loc[event_from_game.id]
                    ctx.locations_checked.add(server_id)
                    # TODO: progress number "(1/146)" or something like that
                    if server_id in ctx.missing_locations:
                        logger.info(f'New Check: {loc_name}')
                        await ctx.send_msgs([{"cmd": 'LocationChecks', "locations": [server_id]}])
                    else:
                        logger.info(f"DEBUG: {loc_name} not in missing")
                elif isinstance(event_from_game, events.DeathEventFromGame):
                    try:
                        await ctx.send_death()
                    except KeyError:
                        logger.warning("KeyError sending death")
                elif isinstance(event_from_game, events.WinEventFromGame):
                    if not ctx.finished_game:
                        await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
                        ctx.finished_game = True
                else:
                    logger.warning(f"WARNING: unhandled event from game {event_from_game}")
            if len(ctx.items_received) > next_item:
                zz_item_ids = [item_pretty_id_to_useful_id[item.item - base_id] for item in ctx.items_received]
                for index in range(next_item, len(ctx.items_received)):
                    zz_item = id_to_zz_item[zz_item_ids[index]]
                    # TODO: use zz_item.name with info on rescue changes
                    logger.info(f'received item {zz_item.debug_name}')
                ctx.to_game.put_nowait(
                    events.ItemEventToGame(zz_item_ids)
                )
                next_item += 1
            await asyncio.sleep(0.09375)


async def run_game(rom_file: str) -> None:
    # TODO: fix this
    subprocess.Popen(["retroarch", rom_file],
                     stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)


async def main() -> None:
    parser = get_base_parser()
    parser.add_argument('diff_file', default="", type=str, nargs="?",
                        help='Path to a .apzl Archipelago Binary Patch file')
    # SNI parser.add_argument('--loglevel', default='info', choices=['debug', 'info', 'warning', 'error', 'critical'])
    args = parser.parse_args()
    print(args)

    if args.diff_file:
        import Patch
        logger.info("patch file was supplied - creating sms rom...")
        meta, rom_file = Patch.create_rom_file(args.diff_file)
        if "server" in meta:
            args.connect = meta["server"]
        logger.info(f"wrote rom file to {rom_file}")

        asyncio.create_task(run_game(rom_file))

    to_game: "asyncio.Queue[events.EventToGame]" = asyncio.Queue()
    ctx = ZillionContext(args.connect, args.password, to_game)
    if ctx.server_task is None:
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="ServerLoop")

    if gui_enabled:
        ctx.run_gui()
    ctx.run_cli()

    sync_task = asyncio.create_task(zillion_sync_task(ctx, to_game))

    await ctx.exit_event.wait()

    ctx.server_address = None
    await sync_task
    await ctx.shutdown()


if __name__ == "__main__":
    Utils.init_logging("ZillionClient", exception_logger="Client")

    colorama.init()
    asyncio.run(main())
    colorama.deinit()
