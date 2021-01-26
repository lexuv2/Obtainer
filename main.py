import discord
from discord.ext import commands
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
#import moviepy
print("dupa")
from moviepy.editor import *
print("dupa")
import os
import subprocess
import sys
import re
import tempfile
from redvid import Downloader
import youtube_dl
from collections import deque
from time import sleep
from threading import Thread
import asyncio
import concurrent.futures
activemsg = 0
caudio = 1
cvideo = 1
activeurl = ""
activectx = 0
activeid =0
#config shit
token = 'redacted'


description = '''An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here.'''

text_download_reddit="Downloading reddit video"
text_yt_download = "Downloading YT video"
text_start_download = 'Starting download'
text_description = "Obtainer, best bot for downloading YouTube and reddit videos"
text_start_time = 'Start time'
text_end_time = 'End time'
text_state = 'State'
text_disable_video_compression = 'Disable video compression'
text_waiting_for_start = 'waiting for start'
text_place_in_queue = 'place in queue'
intents = discord.Intents.default()
intents.members = True

#end of config

def pre1():
    subprocess.call(['ffmpeg','-y','-i','out.mp4' ,'-vcodec','libx264','-crf',f'{24}','tmp.mp4'])
    
def pre2():
    subprocess.call(['ffmpeg','-y','-i','tmp.mp4' ,'-profile:v','baseline','out.mp4'])

def pre3():
    subprocess.call(['ffmpeg','-y','-i','out.mp4' ,'-vcodec','h264','-acodec','aac','tmp.mp4'])
    
def prea():
    subprocess.call(['ffmpeg','-y','-i','tmp.mp4' ,'-b:a','48k','out.mp4'])
    
kolejka = deque()

mapa = {}

class to_download:
    starts=-1
    startm=-1
    stops=-1
    stopm=-1
    url = ''
    ctx =None
    msg =''
    state =''
    user_name=''
    user_id =0
    caudio=1
    cvideo=1
    async def waiting(self):
        print("CZEEEEAKM")
        print(self.msg.id)
        while self.msg.id in kolejka:
            print("zmieniam")
            if len(kolejka) - kolejka.index(self.msg.id) <= 1:
                return
            embed = discord.Embed(title=text_start_download, description=text_description, color=0x00ff00)
            embed.add_field(name="Link", value=self.url, inline=False)
            embed.add_field(name=text_start_time, value=f'{startm}:{starts}', inline=False)
            embed.add_field(name=text_end_time, value=f'{stopm}:{stops}', inline=False)
            embed.add_field(name=text_place_in_queue, value=len(kolejka) - kolejka.index(self.msg.id) -1)
            await self.msg.edit(embed=embed)
            asyncio.sleep(5)
    

bot = commands.Bot(command_prefix='!', description=description, intents=intents)



startm = 0
starts = 0
stopm = 0
stops = 0



async def zrobembed(ctx,url,glos,bass,wiad,old):
    global startm
    global starts
    global stopm
    global stops
    global caudio
    global cvideo
    embed = discord.Embed(title=text_start_download, description=text_description, color=0x00ff00)
    embed.add_field(name="Link", value=url, inline=False)
    embed.add_field(name=text_start_time, value=f'{startm}:{starts}', inline=False)
    embed.add_field(name=text_end_time, value=f'{stopm}:{stops}', inline=False)
    komp = ""
    if (not caudio) and (not cvideo):
        komp="Nothing WTF"
    if caudio and not cvideo:
        komp="Audio"
    if cvideo and not caudio:
        komp="Video"
    if cvideo and caudio:
        komp= 'Video and audio'
    embed.add_field(name="Compressing:", value=komp, inline=False)   
    #embed.add_field(name="Glośność", value=f'+{glos}dB', inline=False)
    #embed.add_field(name="Bass", value=f'+{bass}dB', inline=False)
    embed.add_field(name=text_state, value=wiad, inline=False)
    await old.edit(embed=embed)
    return old


print("dupa")


def getVideoDetails(filepath):
    tmpf = tempfile.NamedTemporaryFile('r')
    os.system("ffmpeg -i \"%s\" 2> %s" % (filepath, tmpf.name))
    lines = tmpf.readlines()
    tmpf.close()
    metadata = {}
    for l in lines:
        l = l.strip()
        if l.startswith('Duration'):
            metadata['duration'] = re.search('Duration: (.*?),', l).group(0).split(':',1)[1].strip(' ,')
            metadata['bitrate'] = re.search("bitrate: (\d+ kb/s)", l).group(0).split(':')[1].strip()
        if l.startswith('Stream #0:0'):
            metadata['video'] = {}
            metadata['video']['codec'], metadata['video']['profile'] = \
                [e.strip(' ,()') for e in re.search('Video: (.*? \(.*?\)),? ', l).group(0).split(':')[1].split('(')]
            metadata['video']['resolution'] = re.search('([1-9]\d+x\d+)', l).group(1)
            metadata['video']['bitrate'] = re.search('(\d+ kb/s)', l).group(1)
            metadata['video']['fps'] = re.search('(\d+ fps)', l).group(1)
        if l.startswith('Stream #0:1'):
            metadata['audio'] = {}
            metadata['audio']['codec'] = re.search('Audio: (.*?) ', l).group(1)
            metadata['audio']['frequency'] = re.search(', (.*? Hz),', l).group(1)
            metadata['audio']['bitrate'] = re.search(', (\d+ kb/s)', l).group(1)
    return metadata


async def donwload(td):
    global caudio
    global cvideo
    global activeid 
    activeid = td.msg.id
    fps = 60
    cont = 24
    url = td.url
    glos =0
    bass =0
    ctx=td.ctx
    old=td.msg
    starts = td.starts + (td.startm*60)
    stop = td.stops+(td.stopm*60)
    print('=============================================================================')
    if 'reddit' in url:
        try:
            old = await zrobembed(ctx,url,glos,bass,text_download_reddit,old)
            reddit = Downloader(max_q=True)
            reddit.url = url
            file_name = reddit.download()
            os.rename(file_name,'pre.mp4')
        except Exception as e:
            print(e)
            os.system('rm pre.mp4')
            await zrobembed(ctx,url,glos,bass,f"Invalid link",old)
            kolejka.pop()
            if len(kolejka)!=0:
                await donwload(mapa[kolejka[-1]])
            return
    else:
        old = await zrobembed(ctx,url,glos,bass,text_yt_download,old)
        print('=============================================================================')
        try:
            ydl = youtube_dl.YoutubeDL({'outtmpl': 'pre.mp4','format':'mp4'})
            ydl.download([url])
        except:
            os.system('rm pre.mp4')
            await zrobembed(ctx,url,glos,bass,f"Invalid link",old)
            kolejka.pop()
            if len(kolejka)!=0:
                await donwload(mapa[kolejka[-1]])
            return
        #subprocess.call(['youtube-dl','-f','bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4', '-o' 'pre',url ])


    if not os.path.isfile('pre.mp4'):
        os.system('rm pre.mp4')
        await zrobembed(ctx,url,glos,bass,f"Invalid link",old)
        kolejka.pop()
        if len(kolejka)!=0:
            await donwload(mapa[kolejka[-1]])
        return

    print('====================================')
    print(caudio)
    print(cvideo)
    #ffmpeg_extract_subclip("pre.mp4", starts, stop, targetname="out.mp4")
    old =await zrobembed(ctx,url,glos,bass,"Finished downloading, preprocessing",old)
    if stop>0:
        clip = VideoFileClip("pre.mp4").subclip(starts,stop)
        clip.write_videofile("out.mp4")
    else:
        os.rename('pre.mp4' , 'out.mp4')

    info = getVideoDetails('out.mp4')
    vbi = int(info['video']['bitrate'].replace('kb/s' , ''))
    if 'audio' in info:
        bi = int(info['audio']['bitrate'].replace('kb/s' , ''))
    old =await zrobembed(ctx,url,glos,bass,"Initial compression",old)
    loop = asyncio.get_running_loop()
    with concurrent.futures.ProcessPoolExecutor() as pool:
        await loop.run_in_executor(pool,pre1)
    #subprocess.call(['ffmpeg','-y','-i','out.mp4' ,'-vcodec','libx264','-crf',f'{cont}','tmp.mp4'])
    with concurrent.futures.ProcessPoolExecutor() as pool:
        await loop.run_in_executor(pool,pre2)
        
    with concurrent.futures.ProcessPoolExecutor() as pool:
        await loop.run_in_executor(pool,pre3)
    
    #old =await zrobembed(ctx,url,glos,bass,"Zmiana głośności",old)
    #if glos!=0 or bass !=0:
    #    subprocess.call(['ffmpeg','-y','-i','tmp.mp4' ,'-filter:a',f'volume={glos}dB','out.mp4'])
    #    subprocess.call(['ffmpeg','-y','-i','out.mp4' ,'-af',f'equalizer=f=100:width_type=h:width=200:g={bass}','tmp.mp4'])
    if caudio:
        with concurrent.futures.ProcessPoolExecutor() as pool:
            await loop.run_in_executor(pool,subprocess.call,['ffmpeg','-y','-i','tmp.mp4' ,'-b:a','48k','out.mp4'])
        bi=48*2
    #os.rename('tmp.mp4' , 'out.mp4')
    old =await zrobembed(ctx,url,glos,bass,"Preprocessing finished",old)
    print('=============================================================================')
    presiz = ((os.path.getsize('out.mp4') >> 20))
    while ((os.path.getsize('out.mp4') >> 20)>7 ):
        clip = VideoFileClip("out.mp4") 
        bi=int(bi//2)
        vbi=int(vbi//2)
        fps//=2

        #clip = clip.fx( vfx.resize, 0.5)
        #clip.write_videofile("out.mp4",audio_bitrate = str(bi)+'k' )
        print("dupa")
        w = int(clip.w)//2
        h = int(clip.h)//2
        
        cont//=2
        if w%2==1:
            w+=1
        if h%2==1:
            h+=1
        print(os.path.getsize('out.mp4') >> 20)
        print(w)
        print(h)
        print(bi)
        if caudio:
            old =await zrobembed(ctx,url,glos,bass,f"Video weights {(os.path.getsize('out.mp4') >> 20)}MB - Compressing audio\n Resolution: {int(clip.w)}x{int(clip.h)}\n Bitrate audio: {bi}\nBitrate video: {vbi*2}",old)
            with concurrent.futures.ProcessPoolExecutor() as pool:
                await loop.run_in_executor(pool,subprocess.call,['ffmpeg','-y','-i','tmp.mp4' ,'-b:a',f'{bi}k','out.mp4'])
            #subprocess.call(['ffmpeg','-y','-i','tmp.mp4' ,'-b:a',f'{bi}k','out.mp4'])

        #subprocess.call(['ffmpeg','-y','-i','out.mp4','-vf',f'scale=iw/{2}:ih/{2}','tmp.mp4'])
        if cvideo:
            old =await zrobembed(ctx,url,glos,bass,f"Video weights {(os.path.getsize('out.mp4') >> 20)}MB - Compressing video\n Resolution: {int(clip.w)}x{int(clip.h)}\n Bitrate audio: {bi}\nBitrate video: {vbi*2}",old)
            with concurrent.futures.ProcessPoolExecutor() as pool:
                await loop.run_in_executor(pool,subprocess.call,['ffmpeg','-y','-i','out.mp4' ,'-s',f'{w}x{h}','-c:a','copy','tmp.mp4'])
                await loop.run_in_executor(pool,subprocess.call,['ffmpeg','-y','-i','tmp.mp4' ,'-b:v',f'{vbi}k','out.mp4'])
            #subprocess.call(['ffmpeg','-y','-i','out.mp4' ,'-s',f'{w}x{h}','-c:a','copy','tmp.mp4'])
            #subprocess.call(['ffmpeg','-y','-i','tmp.mp4' ,'-b:v',f'{vbi}k','out.mp4'])
        #os.rename('tmp.mp4' , 'out.mp4')
        #os.rename('tmp.mp4' , 'out.mp4')
        if presiz == (os.path.getsize('out.mp4') >> 20):
            os.system('rm pre.mp4')
            await zrobembed(ctx,url,glos,bass,f"File to big",old)
            kolejka.pop()
            if len(kolejka)!=0:
                await donwload(mapa[kolejka[-1]])
            return
        presiz = (os.path.getsize('out.mp4') >> 20)
    clip = VideoFileClip("out.mp4") 
    old =await zrobembed(ctx,url,glos,bass,f"Finished Resolution: {int(clip.w)}x{int(clip.h)}\n Bitrate audio: {bi}\nBitrate video: {vbi}",old)
    #subprocess.call(['ffmpeg','-y','-i','out.mkv' ,'copy','tmp.mp4'])
    #os.rename('tmp.mkv' , 'out.mkv')
    #subprocess.call(['ffmpeg','-y','-i','out.mkv' ,'-c','copy','tmp.mp4'])
    #os.rename('tmp.mp4' , 'out.mp4')
    os.system('rm pre.mp4')
    await old.delete()
    file = discord.File("out.mp4" , f'{td.user_name}.mp4')
    os.system('rm out.mp4')
    await td.ctx.send(file=file)
    kolejka.pop()
    if len(kolejka)!=0:
        await donwload(mapa[kolejka[-1]])
    #os.system('rm out.mp4')


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.event
async def on_raw_reaction_add( payload):
    global activemsg
    global activeid
    emoji = payload.emoji
    user = payload.user_id
    chnl = await bot.fetch_channel(payload.channel_id)
    msg = await chnl.fetch_message(payload.message_id)
    print("REAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACT")
    if user != bot.user.id and msg.author.id==bot.user.id and msg.id != activeid:
        print(msg)
        print(activeid )
        if str(emoji)=='❌':
            print("delet")
            await msg.delete()
    else:
        print("nie przeszło")


@bot.event
async def on_reaction_add(reaction, user):
    global activeurl
    global activectx
    global activemsg
    global caudio
    global cvideo
    global startm
    global starts
    global stopm
    global stops 
    if reaction.message.id in mapa and user.id != bot.user.id:
        print(reaction.emoji)
        if reaction.emoji == '✅':
            await reaction.message.clear_reaction('')
            await reaction.message.clear_reaction('')
            await reaction.message.clear_reaction('')
            if len(kolejka)==0:
                kolejka.appendleft(reaction.message.id)
                asyncio.get_event_loop().create_task(donwload(mapa[reaction.message.id]))
            else:
                kolejka.appendleft(reaction.message.id)
                await mapa[reaction.message.id].waiting()
        
        if reaction.emoji == '🇻':
            mapa[reaction.message.id].cvideo=1
        
        if reaction.emoji == '🇦':
            mapa[reaction.message.id].caudio=0

@bot.event
async def on_reaction_remove(reaction, user):
    global activeurl
    global activectx
    global activemsg
    global startm
    global starts
    if reaction.message.id in mapa and user.id != bot.user.id:
        if reaction.emoji == '🇻':
            mapa[reaction.message.id].cvideo=1
        
        if reaction.emoji == '🇦':
            mapa[reaction.message.id].caudio=1

@bot.command()
async def gib(ctx, url: str, start : str='0:0', stop : str='-1:-1' ):
    print(kolejka)
    global activemsg
    global activeurl
    global activectx
    td = to_download()
    await ctx.message.delete()
    embed = discord.Embed(title=text_start_download, description=text_description, color=0x00ff00)
    p = start.split(':')
    starts = int(p[1])
    startm = int(p[0])
    p = stop.split(':')
    stops = int(p[1])
    stopm = int(p[0])
    td.starts=starts
    td.startm=startm
    td.stops=stops
    td.stopm=stopm
    embed.add_field(name="Link", value=url, inline=False)
    embed.add_field(name=text_start_time, value=f'{startm}:{starts}', inline=False)
    embed.add_field(name=text_end_time, value=f'{stopm}:{stops}', inline=False)
    #embed.add_field(name="Glośność", value=f'+{glosnosc}dB', inline=False)
    #embed.add_field(name="Bass", value=f'+{bass}dB', inline=False)
    embed.add_field(name=text_state, value='Starting', inline=False)

    #embed.add_field(name=text_disable_video_compression, value=':regional_indicator_v:', inline=False)
    embed.add_field(value=":regional_indicator_a:", name='Disable audio compression:', inline=False)
    embed.add_field(value=":white_check_mark:", name='Accept: ', inline=False)
    embed.add_field(value=":x:", name='Cancel: ', inline=False)
    msg = await ctx.send(embed=embed)
    activemsg = msg
    #await msg.add_reaction('\N{Regional Indicator Symbol Letter V}')
    await msg.add_reaction('\N{Regional Indicator Symbol Letter A}')
    await msg.add_reaction('\N{CROSS MARK}')
    await msg.add_reaction('\N{WHITE HEAVY CHECK MARK}')
    activectx=ctx
    activeurl=url
    #await donwload(ctx, url , starts+(startm*60) , stops+(stopm*60),glosnosc,bass,msg)
    #file = discord.File("out.mp4" , "out.mp4")
    #await ctx.send(file=file)
    td.url=url
    td.ctx=ctx
    td.msg=msg
    td.user_id=ctx.author.id
    td.user_name=ctx.author.name
    td.state=text_waiting_for_start
    mapa[msg.id]=td




bot.run(token)
