from streamer_utills import TwitchUtills, WasdUtills, GoodgameUtills
import asyncio


class StreamerInfo:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.status = False


class StreamerInfoGoodgame(StreamerInfo):
    def __init__(self, name, id):
        super().__init__(name, id)
        self.title = ""

    async def init_at_start(self):
        sb = f"@everyone\n{self.name} is online\n"

        cur_title = await GoodgameUtills.get_title(self.id)
        sb += f"Title: {cur_title}\n"
        self.title = cur_title

        return sb

    async def process_streamer(self):
        sb = ""

        cur_title = await GoodgameUtills.get_title(self.id)
        if cur_title.lower() != self.title.lower():
            self.title = cur_title
            sb += f"{self.name} changed title to {cur_title}"

        if len(sb) <= 1:
            return ""

        await asyncio.sleep(1)

        sb = "@everyone\n" + sb[0:]

        viewers = await GoodgameUtills.get_viewers(self.id)
        sb += f"\nViewers: {viewers}\n"

        return sb

    async def get_status(self):
        return await GoodgameUtills.get_streaming_status(self.id)


class StreamerInfoWasd(StreamerInfo):
    def __init__(self, name, id):
        super().__init__(name, id)
        self.title = ""

    async def init_at_start(self):
        sb = f"@everyone\n{self.name} is online\n"

        cur_title = await WasdUtills.get_title(self.id)
        sb += f"Title: {cur_title}\n"
        self.title = cur_title

        return sb

    async def process_streamer(self):
        sb = ""

        cur_title = await WasdUtills.get_title(self.id)
        if cur_title.lower() != self.title.lower():
            self.title = cur_title
            sb += f"{self.name} changed title to {cur_title}"

        if len(sb) <= 1:
            return ""

        await asyncio.sleep(1)

        sb = "@everyone\n" + sb[0:]

        viewers = await WasdUtills.get_viewers(self.id)
        sb += f"\nViewers: {viewers}\n"

        return sb

    async def get_status(self):
        return await WasdUtills.get_streaming_status(self.id)


class StreamerInfoTwitch(StreamerInfo):
    def __init__(self, name, id):
        super().__init__(name, id)
        self.game = ""
        self.title = ""

    async def init_at_start(self):
        sb = f"@everyone\n{self.name} is online\n"

        cur_title = await TwitchUtills.get_title(self.id)
        sb += f"Title: {cur_title}\n"
        self.title = cur_title

        await asyncio.sleep(1)

        cur_game = await TwitchUtills.get_game(self.id)
        sb += f"Game: {cur_game}"
        self.game = cur_game

        return sb

    async def process_streamer(self):
        sb = ""

        cur_title = await TwitchUtills.get_title(self.id)
        if cur_title.lower() != self.title.lower():
            self.title = cur_title
            sb += f"{self.name} changed title to {cur_title}"

        await asyncio.sleep(1)

        cur_game = await TwitchUtills.get_game(self.id)
        if cur_game.lower() != self.game.lower():
            self.game = cur_game
            sb += f"{self.name} changed game to {cur_game}"

        await asyncio.sleep(1)

        if len(sb) <= 1:
            return ""

        sb = "@everyone\n" + sb[0:]

        viewers = await TwitchUtills.get_viewers(self.id)
        sb += f"\nViewers: {viewers}\n"

        return sb

    async def get_status(self):
        return await TwitchUtills.get_streaming_status(self.id)
