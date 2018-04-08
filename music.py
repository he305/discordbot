from discord.ext import commands
import discord
import asyncio
import urllib
import re


if not discord.opus.is_loaded():
    discord.opus.load_opus('opus/lib/libopus.so')
    discord.opus.load_opus('opus')


class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = '*{0.title}* uploaded by {0.uploader} and requested by {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)


class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set()
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.bot.send_message(self.current.channel, 'Now playing ' + str(self.current))
            self.current.player.start()
            await self.play_next_song.wait()


class Music:
    def __init__(self, client):
        self.bot = client
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    @commands.command(pass_context=True, no_pm=True)
    async def join(self, ctx, *, channel : discord.Channel):
        try:
            await self.create_voice_client(channel)
        except discord.ClientException:
            await self.bot.say('Already in a voice channel...')
        else:
            await self.bot.say('Ready to play audio in ' + channel.name)

    @commands.command(pass_context=True, no_pm=True)
    async def summon(self, ctx):
        """Summons the bot to join your voice channel."""
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            await self.bot.say('You are not in a voice channel.')
            return False

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)

        return True

    def crawl(self, url):
        sTUBE = ''
        cPL = ''
        final_url = []

        if 'list=' in url:
            eq = url.rfind('=') + 1
            cPL = url[eq:]

        else:
            print('Incorrect Playlist.')
            exit(1)

        try:
            yTUBE = urllib.request.urlopen(url).read()
            sTUBE = str(yTUBE)
        except urllib.error.URLError as e:
            print(e.reason)

        tmp_mat = re.compile(r'watch\?v=\S+?list=' + cPL)
        mat = re.findall(tmp_mat, sTUBE)

        if mat:

            for PL in mat:
                yPL = str(PL)
                if '&' in yPL:
                    yPL_amp = yPL.index('&')
                final_url.append('http://www.youtube.com/' + yPL[:yPL_amp])

            all_url = list(set(final_url))

            return all_url

        else:
            return []


    @commands.command(pass_context=True, no_pm=True)
    async def play(self, ctx, *, url: str):
        """Plays a song.
        If there is a song currently in the queue, then it is
        queued until the next song is done playing.
        This command automatically searches as well from YouTube.
        The list of supported sites can be found here:
        https://rg3.github.io/youtube-dl/supportedsites.html
        """
        await self.bot.say('Start song adding')
        state = self.get_voice_state(ctx.message.server)
        opts = {
            'default_search': 'auto',
            'quiet': True
        }

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
                return

        data = []
        if 'list=' in url:
            data = self.crawl(url)

        if len(data) == 0:
            data.append(url)

        for song in data:
            if self.get_voice_state(ctx.message.server).voice is None:
                continue
            try:
                player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
            except Exception as e:
                fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
                await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
            else:
                player.volume = 0.2
                entry = VoiceEntry(ctx.message, player)
                await self.bot.say('Enqueued ' + str(entry))
                await state.songs.put(entry)

                await state.play_next_song.wait()

    @commands.command(pass_context=True, no_pm=True)
    async def volume(self, ctx, value: int):
        """Sets the volume of the currently playing song."""

        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.volume = value / 100
            await self.bot.say('Set the volume to {:.0%}'.format(player.volume))

    @commands.command(pass_context=True, no_pm=True)
    async def stop(self, ctx):
        """Stops playing audio and leaves the voice channel.
        This also clears the queue.
        """
        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
        except:
            pass

    @commands.command(pass_context=True, no_pm=True)
    async def skip(self, ctx):
        """Vote to skip a song. The song requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """

        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say('Not playing any music right now...')
            return

        voter = ctx.message.author
        if voter == state.current.requester:
            await self.bot.say('Requester requested skipping song...')
            state.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 1:
                await self.bot.say('Skip vote passed, skipping song...')
                state.skip()
            else:
                await self.bot.say('Skip vote added, currently at [{}/3]'.format(total_votes))
        else:
            await self.bot.say('You have already voted to skip this song.')