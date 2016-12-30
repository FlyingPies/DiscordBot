import discord
import asyncio
import pprint
from googleapiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import urllib
import urllib.request
from bs4 import BeautifulSoup
client = discord.Client()
player = None
paused = False
skipped = False
voice = None
token = None
queue = []
musicChan= None
author = None
djmode = False
repeat = False
asdf = False
processing = False
prevmessage = None

f = open('config','r')
token = f.readline()
token=  token[token.index('=')+1:len(token)-1]
print(token)
musicChan = f.readline()
musicChan = musicChan[musicChan.index('=')+1:len(musicChan)-1]
print(musicChan)
key = f.readline()
key = key[key.index('=')+1:len(key)]
print(key)
@client.event
async def on_ready():

    global musicChan
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    print(client.get_channel(musicChan))
    global voice
    voice = await client.join_voice_channel(client.get_channel(musicChan))
    gamez = discord.Game()
    gamez.name = 'the internet'
    gamez.type = 1
    gamez.url = 'https://www.twitch.tv/loltyler1'
    print(gamez.url)
    await client.change_presence(game=gamez, status=False)

@client.event
async def on_message(message):
    global prevmessage
    if (not prevmessage == None) and prevmessage.author.id==message.author.id:
        print('f')
        await client.clear_reactions(prevmessage)
    if message.author.id=='145615220189036544':
        await client.add_reaction(message,'\N{PILE OF POO}')
    if message.author.id=='183377500309684225':
        await client.add_reaction(message,'arjun:230098037660188672')
    if message.author.id=='148496704440762368':
        await client.add_reaction(message,u'\U0001F40D')
        await client.add_reaction(message,u'\U0001F32E')
        await client.add_reaction(message,u'\U0001F365')
    if message.author.id=='223287310408613900':
        await client.add_reaction(message,u'\U0001F37C')
    if message.author.id=='183382090837000192':
        await client.add_reaction(message,u'\U0001F37C')
    if message.author.id=='234031196743532555':
        await client.add_reaction(message,u'\U0001F595\U0001F3FF')
    if message.author.id=='139945569463304192':
        await client.add_reaction(message,u'\U0001f371')
    if message.content.lower().startswith('!help'):
        await client.send_message(message.channel,'Here are a list of commands:\n**!help** - Returns the list of working commands\n**!clear_chat** - Clears the chat __**(Only Admins are allowed to do this)**__\n**!google** `[query]` - Returns first Google search result of search query\n**!play** `[query]` - Plays first Youtube result in the Music Channel\n**!repeat** `[query]` Plays first Youtube result in the Music Channel on repeat. This will skip all songs in the queue before it. The loop can be ended with the **!skip** command\n**!skip** - Skips song that is currently being played\n**!pause** - Paused song that is currently being played\n**!resume** - Resumes currently paused song\n**!np** - Returns the name of song that is now playing\n**!queue** - Shows current queue. Say `!queue -h` for my queue commands\n**!cq** - Clears the queue.')
    if message.content.lower().startswith('!test'):
        counter = 0
        tmp = await client.send_message(message.channel, 'Calculating messages...')
        async for log in client.logs_from(message.channel, limit=100):
            if log.author == message.author:
                counter += 1

        await client.edit_message(tmp, 'You have {} messages.'.format(counter))
    elif message.content.lower().startswith('!sleep'):
        await asyncio.sleep(5)
        await client.send_message(message.channel, 'Done sleeping')
    elif message.content.lower().startswith('!clear_chat'):
        highestrole = len(message.server.roles)-1
        if message.author.top_role.position==highestrole:
            await client.purge_from(message.channel, limit=999,check=None)
        else:
            await client.send_message(message.channel,'You do not have access to this command.')
    elif message.content.lower().startswith('!rules'):
        await client.send_message(message.channel, 'No rules\nlol')
    elif message.content.lower().startswith('!google'):
        global key
        query = message.content[message.content.index(' ')+1:len(message.content)]
        service = build('customsearch', 'v1', developerKey=key)
        res = service.cse().list(q=query,cx='013388782467450060570:cc_bo6ma8uk').execute()

        if 'items' in res.keys():
            result= res['items'][0]['link']
            print(result)
            await client.send_message(message.channel, result)
        else:
            await client.send_message(message.channel, 'No link was found.')

    elif message.content.lower().startswith('!play'):
        global djmode
        if(djmode==True and hasRole(message.author,'DJ')) or djmode==False:
            query = message.content[message.content.index(' ')+1:len(message.content)]
            link = "https://www.youtube.com/results?search_query="+query
            link = link.replace(' ','+')
            r = urllib.request.urlopen(link)
            soup = BeautifulSoup(r, "lxml")
            count=0
            for link in soup.find_all('a'):
                if 'watch' in link.get("href") and not 'list' in link.get("href") and not 'googleads' in link.get("href"):
                    if count>0:
                        title=link.text
                        break
                    count+=1
            if count>0:
                global queue
                link='https://www.youtube.com'+link.get('href')
                data={'link':link,'title':title}
                queue.append(data)
                global player
                if (len(queue)==1 and player == None) or (len(queue)==1 and player.is_done()):
                    await client.send_message(message.channel, 'I will now play **' + title+'**')
                else:
                    await client.send_message(message.channel, 'A song is already playing, so **'+title+'** will be added to the queue')
                if not player ==None:
                    print("is_done :: "+str(not player.is_playing()))
                print("queue length :: "+str(len(queue)))
                await Play()
            else:
                await client.send_message(message.channel, 'No link was found.')
        else:
            await client.send_message(message.channel, 'NOT AUTHORIZED')
    elif message.content.lower().startswith('!repeat'):
        if(djmode==True and hasRole(message.author,'DJ')) or djmode==False:
            global repeat
            repeat = True
            await client.send_message(message.channel,'The song is now on repeat')
        else:
            await client.send_message(message.channel, 'NOT AUTHORIZED')
    elif message.content.lower().startswith('!skip'):
        if(djmode==True and hasRole(message.author,'DJ')) or djmode==False:
            if player==None:
                await client.send_message(message.channel,'No song is currently playing.')
            elif player.is_playing():
                player.stop()
                global paused
                global processing
                processing = False
                paused = False
                skipped = True
                if repeat:
                    repeat = False
                print(str(len(queue)))
                print(player.is_playing())
            else:
                await client.send_message(message.channel,'No song is currently playing.')
        else:
            await client.send_message(message.channel,'NOT AUTHORIZED')
    elif message.content.lower().startswith('!pause'):
        if player==None:
            await client.send_message(message.channel,'No song is currently playing.')
        elif player.is_playing():
            player.pause()
            paused = True
        else:
            await client.send_message(message.channel,'No song is currently playing.')
    elif message.content.lower().startswith('!resume'):
        if player==None:
            await client.send_message(message.channel,'No song is currently playing.')
        elif paused==True:
            player.resume()
            paused = False
        else:
            await client.send_message(message.channel,'No song is currently playing.')
    elif message.content.lower().startswith('!np'):
        if player == None:
            await client.send_message(message.channel, 'No song is currently playing.')
        elif player.is_playing():
            await client.send_message(message.channel, '**'+player.title+'** is currently playing '+str(player.duration))
        else:
            await client.send_message(message.channel, '**'+player.title+'** is currently playing '+str(player.duration))
    elif message.content.lower().startswith('!queue') and len(message.content.lower())==6:
        output='Queue list:\n'
        if len(queue)==0:
            await client.send_message(message.channel, 'The queue is empty')
        else:
            if player.is_playing():
                output='*Now Playing* - **'+player.title+'**\nQueue list:\n'
            for x in range(1,len(queue)):
                output += str(x)+'. **'+queue[x]['title']+'**\n'
            await client.send_message(message.channel, output)
    elif message.content.lower().startswith('!queue -r '):
        if(djmode==True and hasRole(message.author,'DJ')) or djmode==False:
            f=message.content[message.content.index('-')+3:]
            if not ',' in f:
                slot = int(f)
                if not (slot>len(queue) or slot<1):
                    del queue[slot-1]
                else:
                    await client.send_message(message.channel,'This is not a valid place in the queue')
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
                    if not (int(f[x])>len(queue) or int(f[x])<1):
                        del queue[int(f[x])]
                    else:
                        await client.send_message(message.channel,'One of the entries you put in are not valid')
        else:
            await client.send_message(message.channel,'NOT AUTHORIZED')
    elif message.content.lower().startswith('!djmode'):
        if hasRole(message.author,'DJ'):
            if not djmode:
                djmode = True
                await client.send_message(message.channel, 'DJ Mode is now on. Only designated DJs are allowed to queue and skip')
            elif djmode:
                djmode = False
                await client.send_message(message.channel, 'DJ Mode is now off. Now anyone can queue and skip songs.')
        else:
            await client.send_message(message.channel,'NOT AUTHORIZED')
    elif message.content.lower().startswith('!cq'):
        if(djmode==True and hasRole(message.author,'DJ')) or djmode==False:
            queue=[]
            await client.send_message(message.channel, 'Queue has been cleared')
        else:
            await client.send_message(message.channel, 'NOT AUTHORIZED')
    if message.server.id=='183378379133681664':
        prevmessage = message
async def Play():
    global player
    global queue
    global voice
    global skipped
    global paused
    global asdf
    global processing
    if (((len(queue)>0 and player==None) or (len(queue)>0 and not player.is_playing())) and paused == False) and processing == False:
        processing = True
        player = await voice.create_ytdl_player(queue[0]['link'])
        asdf = False
        paused = False
        skipped = False
        player.volume = 0.5
        player.start()
        print(str(skipped))
        while True:
            if player==None or not player.is_playing():
                break
            processing = False
            await asyncio.sleep(1)
        if not repeat:
            del queue[0]
        await Play()
    else:
        print("something already playing")
def hasRole(user,name):
    for x in range(0,len(user.roles)):
            if user.roles[x].name==name:
                result=True
                break
            else:
                result=False
    return result
client.run(token)
