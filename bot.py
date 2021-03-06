import discord
import asyncio
import aiohttp
from discord.ext import commands
from googleapiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
from bs4 import BeautifulSoup
player = None
paused = False
skipped = False
voice = None
token = None
queues = []
flairs=[]
musicChan= None
author = None
djmodez = False
repeat = False
asdf = False
processing = False
prevmessage = None

def loadFlairs():
    with open("flairs","r") as f:
        file = f.read().splitlines()
    f.close()
    global flairs
    flairs=[]
    for line in file:
        count = 0
        lastcomma=0
        emojis=[]
        for x in range (0,len(line)):
            if count==0 and line[x:x+1]==',':
                id=line[:x]
                count+=1
                lastcomma=x
            elif line[x:x+1]==',':
                if ':' in line[lastcomma+1:x]:
                    emojis.append(line[lastcomma+1:x])
                    lastcomma=x
                else:
                    f=line[lastcomma+1:x]
                    f=f.replace('\\U','')
                    f=f.replace('\\u','')
                    lastcomma=x
                    g=''
                    for y in range (0,int(len(f)/8)):
                        g+=chr(int(f[y*8:(y+1)*8],16))
                    emojis.append(g)
            if x==len(line)-1:
                if ':' in line[lastcomma+1:]:
                    emojis.append(line[lastcomma+1:])
                    lastcomma=x
                else:
                    f=line[lastcomma+1:]
                    f=f.replace('\\U','')
                    f=f.replace('\\u','')
                    lastcomma=x
                    h=''
                    for z in range (0,int(len(f)/8)):
                        h+=chr(int(f[z*8:(z+1)*8],16))
                    emojis.append(h)
        flairs.append({'id':id,'emojis':emojis})  
f = open('config','r')
token = f.readline()
token=  token[token.index('=')+1:len(token)-1]
print('Token - '+token)
musicChan = f.readline()
musicChan = musicChan[musicChan.index('=')+1:len(musicChan)-1]
print('Channel ID - '+musicChan)
key = f.readline()
key = key[key.index('=')+1:len(key)]
print('Google API Key  - '+key)
description = 'Bot made by Arjun Lalith'
bot = commands.Bot(command_prefix='!',description=description)
loadFlairs()
@bot.event
async def on_ready():

    global musicChan
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print(bot.get_channel(musicChan))
    global voice
    voice = await bot.join_voice_channel(bot.get_channel(musicChan))
    gamez = discord.Game()
    gamez.name = 'the internet'
    gamez.type = 1
    gamez.url = 'https://www.twitch.tv/loltyler1'
    print(gamez.url)
    await bot.change_presence(game=gamez, status=False)

@bot.command(pass_context=True)
async def test(ctx):
    '''Tests to see if the bot is online'''
    counter = 0
    tmp = await bot.say('Calculating messages...')
    async for log in bot.logs_from(ctx.message.channel, limit=100):
        if log.author == ctx.message.author:
            counter += 1

    await bot.edit_message(tmp, 'You have {} messages.'.format(counter))
@bot.command()
async def sleep():
     '''Testing command'''
     await asyncio.sleep(5)
     await bot.say('Done sleeping')
@bot.command(pass_context=True)
async def clear_chat(ctx):
    '''Clears the chat. Admin only command.'''
    highestrole = len(ctx.message.server.roles)-1
    if ctx.message.author.top_role.position==highestrole:
        await bot.purge_from(ctx.message.channel, limit=999,check=None)
    else:
        await bot.say('You do not have access to this command.')
@bot.command()
async def google(*,query : str,):
    '''Returns first google search results of query'''
    global key
    service = build('customsearch', 'v1', developerKey=key)
    res = service.cse().list(q=query,cx='013388782467450060570:cc_bo6ma8uk').execute()
    if 'items' in res.keys():
        result= res['items'][0]['link']
        print(result)
        await bot.say(result)
    else:
        await bot.say('No link was found.')
@bot.group(pass_context=True,invoke_without_command=True)
async def play(ctx,*, query : str):
    '''Plays requested song in the Music Channel'''
    global djmodez
    if ctx.invoked_subcommand is None:
        if (djmodez==True and hasRole(ctx.message.author,'DJ')) or djmodez==False:
            query=query.replace(' ','+')
            link = "https://www.youtube.com/results?search_query="+query
            print(link)
            async with  aiohttp.get(link) as r:
                 soup = BeautifulSoup(await r.text(), "lxml")
                 try:
                     datas=soup.find_all('a',{'class':'yt-uix-tile-link'})
                     for g in datas:
                         if not 'googleads' in g.get("href"):
                            link='https://www.youtube.com'+g.get("href")
                            title=g.text
                            data = {'link':link,'title':title}
                            break
                     global queues
                     queues.append(data)
                     print(queues[0]['title']+" - "+queues[0]['link'])
                     global player
                     if (len(queues)==1 and player == None) or (len(queues)==1 and player.is_done()):
                         await bot.say('I will now play **' + title+'**')
                     else:
                         await bot.say('A song is already playing, so **'+title+'** will be added to the queue')
                     if not player ==None:
                          print("is_done :: "+str(not player.is_playing()))
                     print("queue length :: "+str(len(queues)))
                     await Play()
                 except:
                     await bot.say('No link was found.')
        else:
            print(str(djmodez))
            await bot.say('NOT AUTHORIZED')
@play.command(pass_context=True,name='-s')
async def soundcloud(ctx,*,query : str):
    '''Plays Music from Soundcloud'''
    if (djmodez==True and hasRole(ctx.message.author, 'DJ')) or djmodez==False:
        query=query.replace(' ','+')
        link = 'https://soundcloud.com/search/sounds?q='+query
        async with  aiohttp.get(link) as r:
            try:
                soup = BeautifulSoup(await r.text(), "lxml")
                datas=soup.find_all('ul')
                song=datas[1].find('a')
                lonk="https://soundcloud.com"+song.get('href')
                title=song.text
                data = {'link':lonk,'title':title}
                global queues
                queues.append(data)
                print(queues[0]['title']+" - "+queues[0]['link'])
                global player
                if (len(queues)==1 and player == None) or (len(queues)==1 and player.is_done()):
                    await bot.say('I will now play **' + title+'**')
                else:
                    await bot.say('A song is already playing, so **'+title+'** will be added to the queue')
                if not player ==None:
                     print("is_done :: "+str(not player.is_playing()))
                print("queue length :: "+str(len(queues)))
                await Play()
            except:
                await bot.say('No link was found.')
@bot.command(pass_context=True,name='repeat')
async def _repeat(ctx):
    '''Puts the currently played song on repeat'''
    if(djmodez==True and hasRole(ctx.message.author,'DJ')) or djmodez==False:
        global repeat
        repeat = True
        await bot.say('The song is now on repeat')
    else:
        await bot.say('NOT AUTHORIZED')
@bot.command(pass_context=True)
async def skip(ctx):
    '''Skips the song that is currently being played'''
    if(djmodez==True and hasRole(ctx.message.author,'DJ')) or djmodez==False:
        if player==None:
            await bot.say('No song is currently playing.')
        elif player.is_playing():
            player.stop()
            global paused
            global processing
            global repeat
            processing = False
            paused = False
            skipped = True
            if repeat:
                repeat = False
            print(str(len(queues)))
            print(player.is_playing())
        else:
            await bot.say('No song is currently playing.')
    else:
        await bot.say('NOT AUTHORIZED')
@bot.command()
async def pause():
    '''Pauses the song that is curently being played'''
    global paused
    if player==None:
        await bot.say('No song is currently playing.')
    elif player.is_playing():
        player.pause()
        paused = True
    else:
        await bot.say('No song is currently playing.')
@bot.command()
async def resume():
    '''Resumes the song that is currently paused'''
    global paused
    if player==None:
        await bot.say('No song is currently playing.')
    elif paused==True:
        player.resume()
        paused = False
    else:
        await bot.say('No song is currently playing.')
@bot.command()
async def np():
    '''Returns the song that is currently being played'''
    if player == None:
        await bot.say('No song is currently playing.')
    elif player.is_playing():
        await bot.say('**'+player.title+'** is currently playing ')
    else:
        await bot.say('**'+player.title+'** is currently playing ')
@bot.group(pass_context=True)
async def queue(ctx):
    '''Returns a list of the currently queued songs'''
    if ctx.invoked_subcommand is None:
        global queues
        output='Queue list:\n'
        if len(queues)==0:
            await bot.say( 'The queue is empty')
        else:
            if player.is_playing():
                output='*Now Playing* - **'+player.title+'**\nQueue list:\n'
            for x in range(1,len(queues)):
                output += str(x)+'. **'+queues[x]['title']+'**\n'
            await bot.say(output)
@queue.command(pass_context=True)
async def remove(ctx,f : str):
    '''Removes a song or multiple songs from the queue'''
    if(djmodez==True and hasRole(ctx.message.author,'DJ')) or djmodez==False:
        if not ',' in f:
            slot = int(f)
            if not (slot>len(queues) or slot<1):
                del queues[slot]
            else:
                await bot.say('This is not a valid place in the queue')
        else:
            f=f.split(',')
            print(f)
            for x in range(1,len(f)):
                hole=x
                while(hole>0 and f[hole]<f[hole-1]):
                    val=f[hole]
                    f[hole]=f[hole-1]
                    f[hole-1]=val
                    hole-=1
            print(f)
            for x in range(len(f)-1,-1,-1):
                if not (int(f[x])>len(queues) or int(f[x])<1):
                    del queues[int(f[x])]
                else:
                    await bot.say('One of the entries you put in are not valid')
    else:
        await bot.say('NOT AUTHORIZED')
@bot.command(pass_context=True)
async def djmode(ctx):
    '''Turns on DJ Mode which only allows DJs to play and skip music'''
    global djmodez
    if hasRole(ctx.message.author,'DJ'):
        if not djmodez:
            djmode = True
            await bot.say('DJ Mode is now on. Only designated DJs are allowed to queue and skip')
        elif djmodez:
            djmodez = False
            await bot.say('DJ Mode is now off. Now anyone can queue and skip songs.')
    else:
        await bot.say('NOT AUTHORIZED')
@bot.command(pass_context=True)
async def cq(ctx):
    '''Clears the queue'''
    global queues
    if(djmodez==True and hasRole(ctx.message.author,'DJ')) or djmodez==False:
        queues=[]
        await bot.say('Queue has been cleared')
    else:
        await bot.say('NOT AUTHORIZED')
@bot.group(pass_context=True)
async def flair(ctx):
    '''Allows user to view current flairs that they have'''
    output='Here are the following flairs that you currently have set\n'
    global flairs
    if ctx.invoked_subcommand is None:
        uid=True
        for items in flairs:
            if items['id']==ctx.message.author.id:
                uid=False
                for x in range (0,len(items['emojis'])):
                    if ':' in items['emojis'][x]:
                        output+= str(x+1)+'. <:'+items['emojis'][x]+'> \n'
                    else:
                        output+=str(x+1)+'. '+items['emojis'][x]+'\n'
                await bot.say(output)
                break
        if uid:
            await bot.say('You do not have any flairs')
@flair.command(pass_context=True,name='add')
async def flairadd(ctx,emoji : str):
    '''Adds given flair to the user'''
    uid=True
    print(bytes(emoji,'unicode-escape').decode('utf-8'))
    global flairs
    if '<:' in emoji or '\\U' in bytes(emoji,'unicode-escape').decode('utf-8') or '\\u' in bytes(emoji,'unicode-escape').decode('utf-8'):
        if "<" in emoji:
            emoji=emoji.replace("<:",'')
            emoji=emoji.replace(">",'')
        for items in flairs:
            if items['id']==ctx.message.author.id:
                uid=False
                duplicate=False
                for emojis in items['emojis']:
                    if emojis==emoji:
                        duplicate=True
                        print('emoji already present')
                        await bot.say('The following emoji is already a flair')
                        break
                if duplicate==False:
                    items['emojis'].append(emoji)
                    await bot.say('The new flair has been added')
                break
        if uid:
            id=ctx.message.author.id
            emojis=[]
            emojis.append(emoji)
            flairs.append({'id':id,'emojis':emojis})
            await bot.say('The new flair has been added')
        saveFlairs()
    else:
        await bot.say('This is not a valid emoji')
@flair.command(pass_context=True,name='remove')
async def flairremove(ctx,emoji : str):
    '''Removes given flair from the user'''
    uid=True
    global flairs
    if '<:' in emoji or '\\U' in bytes(emoji,'unicode-escape').decode('utf-8') or '\\u' in bytes(emoji,'unicode-escape').decode('utf-8'):
        if "<" in emoji:
            emoji=emoji.replace("<:",'')
            emoji=emoji.replace(">",'')
        for items in flairs:
            if items['id']==ctx.message.author.id:
                uid=False
                duplicate=False
                for emojis in items['emojis']:
                    if emojis==emoji:
                        if len(items['emojis'])==1:
                            duplicate=True
                            flairs.remove(items)
                            print('Removed id from list')
                            await bot.say('The following emoji has been removed')
                            break
                        else:
                            duplicate=True
                            items['emojis'].remove(emoji)
                            print('The emoji has been removed')
                            await bot.say('The following emoji has been removed')
                            break
                if duplicate==False:
                    await bot.say('The following emoji is not currently one of your flairs')
                break
        if uid:
            await bot.say('You do not currently have any flairs on you')
        saveFlairs()
    else:
        await bot.say('This is not a valid emoji')
@bot.event
async def on_message(message):
    global flairs
    global prevmessage
    if (not prevmessage == None) and prevmessage.author.id==message.author.id:
        print('f')
        await bot.clear_reactions(prevmessage)
    for people in flairs:
        if message.author.id==people['id']:
            for reaction in people['emojis']:
                await bot.add_reaction(message,reaction)
            break
    if not message.server.id=='110373943822540800':
        prevmessage = message
        await bot.process_commands(message)
async def Play():
    global player
    global queues
    global voice
    global skipped
    global paused
    global asdf
    global processing
    global repeat
    if (((len(queues)>0 and player==None) or (len(queues)>0 and not player.is_playing())) and paused == False) and processing == False:
        processing = True
        player = await voice.create_ytdl_player(queues[0]['link'])
        asdf = False
        paused = False
        skipped = False
        player.volume = 0.5
        player.start()
        while player.is_playing():
            processing = False
            await asyncio.sleep(1)
        if not repeat:
            print('Moving onto next song...')
            del queues[0]
            await Play()
        else:
            await Play()
    else:
        print("Player is busy")
def hasRole(user,name):
    for x in range(0,len(user.roles)):
            if user.roles[x].name==name:
                result=True
                break
            else:
                result=False
    return result 
def saveFlairs():
    global flairs
    file= open('flairs','w')
    output=''
    for pair in flairs:
        output+=pair['id']+','
        for x in range (0,len(pair['emojis'])):
            if x==len(pair['emojis'])-1 and not ':' in pair['emojis'][x]:
                if '\\u' in bytes(pair['emojis'][x],'unicode-escape').decode('utf-8'):
                    t=bytes(pair['emojis'][x],'unicode-escape').decode('utf-8')
                    t=t.replace('\\u','')
                    while len(str(t))<8:
                        t=str(0)+t
                    t='\\U'+t
                    output+=t
                else:
                    t=bytes(pair['emojis'][x],'unicode-escape').decode('utf-8')
                    output+=t
            elif x==len(pair['emojis'])-1 and ':' in pair['emojis'][x]:
                output+=pair['emojis'][x]
            elif not ':' in pair['emojis'][x]:
                if '\\u' in bytes(pair['emojis'][x],'unicode-escape').decode('utf-8'):
                    u=bytes(pair['emojis'][x],'unicode-escape').decode('utf-8')
                    u=u.replace('\\u','')
                    while len(str(u))<8:
                        u=str(0)+u
                    u='\\U'+u
                    output+=u+','
                else:
                    u=bytes(pair['emojis'][x],'unicode-escape').decode('utf-8')
                    output+=u+','
            else:
                output+=pair['emojis'][x]+','
        output+='\n'
    file.write(output)
    file.close()
bot.run(token)
