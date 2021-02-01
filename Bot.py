import asyncio
import youtube_dl
import os
import discord
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from os import system

Bot_Token = ('Replace with Discord bot Token')
client = commands.Bot(command_prefix = '!')
#allows interuption of commands while playing music
players = {}

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

@classmethod
async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']


def load_opus_lib(opus_libs=OPUS_LIBS):
    if opus.is_loaded():
        return True

    for opus_lib in opus_libs:
        try:
            opus.load_opus(opus_lib)
            return
        except OSError:
            pass

        raise RuntimeError('Could not load an opus lib. Tried %s' % (', '.join(opus_libs)))

@client.command(pass_context=True, brief="This will play a song 'play [url]'", aliases=['pl'])
async def play(ctx, url: str):
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("Please wait for the current song to end or issue the 'stop' command")
        return
    await ctx.send("```css\n Collecting everything... The audio will play soon.```")
    print("Someone wants to play music let me get that ready for them...")
    voice = get(client.voice_clients, guild=ctx.guild)
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir('./'):
        if file.endswith(".mp3"):
            song_title = file
            os.rename(file, 'song.mp3')            
#./
       
    source = await discord.FFmpegOpusAudio.from_probe("song.mp3")            
    voice = get(client.voice_clients, guild=ctx.guild)
    voice.play(source)
    
    song_title_f = song_title.rsplit("-", 2)
    await ctx.channel.purge(limit=2)
    await ctx.send(f"```Playing: {song_title_f[0]}-{song_title_f[1]}```")
    print("playing\n")

#connect to current channel
@client.command(pass_context=True, aliases=['c'])
async def connect(ctx):
    channel = ctx.message.author.voice.channel
    voice_client = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await ctx.send(f"```diff\n- I am already in the {voice_client} channel```")
    else:    
        await channel.connect()

#disconnect from currrent channel
@client.command(pass_context=True, aliases=['d'])
async def disconnect(ctx):
    guild = ctx.message.guild
    voice_client = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await ctx.send(f"```diff\n- I have left the {voice_client} channel```")
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("```diff\n- I am not currently in a voice channel```")
        
#clear chat in selected channel
@client.command()
async def clear(ctx, amount=10):
    await ctx.channel.purge(limit=amount)
#pause
@client.command(pass_context=True, aliases=['p','pa'])
async def pause(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    voice.pause()
#resume
@client.command(pass_context=True, aliases=['r'])
async def resume(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    voice.resume()
#stop
@client.command(pass_context=True, aliases=['s'])
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    voice.stop()
#volume
@client.command(pass_context=True, aliases=['v'])
async def volume(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    voice.source.volume = 0.1

client.run(Bot_Token)
