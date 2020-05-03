from .player import MediaPlayer


async def play(url, loop=None):
    player = MediaPlayer(loop=loop)
    await player.start(url)
