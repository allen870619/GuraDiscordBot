import discord
from Utils import log
from discord import voice_client
from discord.player import FFmpegPCMAudio
from youtube_dl import YoutubeDL

# main voice client
vc : voice_client.VoiceClient = None

# alarm variable
is_playing = False
audioSource : FFmpegPCMAudio = None
playlist = []

# voice channel
async def joining(ctx):
    global vc, is_playing
    try:
        channel = ctx.author.voice.channel
        if vc != None:
            await ctx.channel.send("鯊鯊已經在別的地方唱歌了ˋˊ")
        else:
            vc = await channel.connect()
            is_playing = False
    except Exception as e:
        # trigger when channel is None, meaning that user isn't in voice channel
        log(e)
        await ctx.channel.send("找個地方聽我的聲音吧ˊˇˋ")

async def leaving(ctx):
    global vc, is_playing
    # call by voice status changed
    if ctx is None: 
        vc = None
        is_playing = False
        return

    if vc is None:
        await joining(ctx)
           
    # stop playing first
    playlist.clear()
    try:
        if is_playing:
            vc.stop()
            is_playing = False
    except Exception as e:
        log(e)

    # disconnect
    try:
        await vc.disconnect(force=True)
    except Exception as e:
        log(e)
    vc = None

def playSource(url):
    global vc, is_playing, audioSource
    audioSource = discord.FFmpegPCMAudio(url)
    # play
    if is_playing and len(playlist) != 0:
        playlist.append(url)
    else:
        vc.play(audioSource, after=playFinished)
    is_playing = True

def playYT(url):
    global vc, is_playing, audioSource, playlist
    ydl_opts = {'format': 'bestaudio', 'noplayplaylist':'True'}
    FFMPEG_OPTIONS = {'bitrate': '512', 'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn -filter:a "volume=0.5"',}
    if not is_playing:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        # audioSource = discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS) # creepy quality
        audioSource = discord.FFmpegOpusAudio(URL, **FFMPEG_OPTIONS)
        is_playing = True
        vc.play(audioSource, after=playFinished)
    else:
        playlist.append(url)
    
# after play
def playFinished(_):
    global is_playing, audioSource, playlist
    is_playing = False
    audioSource = None
    if len(playlist) != 0:
        playYT(playlist.pop(0))

# playlist
def getPlaylist():
    return playlist

def clearPlaylist():
    global playlist
    playlist.clear()