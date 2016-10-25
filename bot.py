import discord
import asyncio
import pprint
from googleapiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
client = discord.Client()
player = None
paused = False
skipped = False
voice = None
token = None
queue = []
musicChan= None
repeat = False
asdf = False
processing = False

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
    if message.content.lower().startswith('!help'):
        await client.send_message(message.channel,'Here are a list of commands:\n**!help** - Returns the list of working commands\n**!clear_chat** - Clears the chat __**(Only Admins are allowed to do this)**__\n**!google** `[query]` - Returns first Google search result of search query\n**!play** `[query]` - Plays first Youtube result in the Music Channel\n**!repeat** `[query]` Plays first Youtube result in the Music Channel on repeat. This will skip all songs in the queue before it. The loop can be ended with the **!skip** command\n**!skip** - Skips song that is currently being played\n**!pause** - Paused song that is currently being played\n**!resume** - Resumes currently paused song\n**!np** - Returns the name of song that is now playing')
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
        query = message.content[message.content.index(' ')+1:len(message.content)]
        youtube = build('youtube', 'v3',developerKey=key)
        search_response = youtube.search().list(q=query,part="id,snippet",maxResults=50).execute()
        items=search_response.get('items',[])
        if items:
            for x in range(0,len(items)):
                if items[x]['id']['kind']=='youtube#video' :
                    result = 'https://www.youtube.com/watch?v='+items[x]['id']['videoId']
                    title = items[x]['snippet']['title']
                    data = items[x]
                    break
            global queue
            queue.append(data)
            print(title)
            print(result)
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
    elif message.content.lower().startswith('!repeat'):
        query = message.content[message.content.index(' ')+1:len(message.content)]
        youtube = build('youtube', 'v3',developerKey=key)
        search_response = youtube.search().list(q=query,part="id,snippet",maxResults=50).execute()
        items=search_response.get('items',[])
        if items:
            for x in range(0,len(items)):
                if items[x]['id']['kind']=='youtube#video' :
                    result = 'https://www.youtube.com/watch?v='+items[x]['id']['videoId']
                    title = items[x]['snippet']['title']
                    data = items[x]
                    break
            global asdf
            if len(queue)>0:
                asdf = True
                skipped = True
            queue=[]
            queue.append(data)
            global repeat
            repeat = True
            if (len(queue)==1 and player == None) or (len(queue)==1 and player.is_done()):
                await client.send_message(message.channel, 'I will now play **' + title+'**'+' on repeat')
            else:
                await client.send_message(message.channel, 'Skipping all songs to put **'+title+'** on repeat')
            if not player ==None:
                print("is_done :: "+str(not player.is_playing()))
            print("queue length :: "+str(len(queue)))
            if player==None:
                await Play()
            elif not player.is_playing():
                await Play()
            elif player.is_playing():
                player.stop()
                print('f')
            else:
                await Play()
        else:
            await client.send_message(message.channel, 'No link was found.')
    elif message.content.lower().startswith('!skip'):
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
                del queue[0]
            await Play()
            print(str(len(queue)))
            print(player.is_playing())
        else:
            await client.send_message(message.channel,'No song is currently playing.')
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
            await client.send_message(message.channel, '**'+player.title+'** is currently playing')
        else:
            await client.send_message(message.channel, '**'+player.title+'** is currently playing')
    elif message.content.lower().startswith('!queue'):
        output='Queue list:\n'
        if len(queue)==0:
            await client.send_message(message.channel, 'The queue is empty')
        else:
            if player.is_playing():
                output='*Now Playing* - **'+player.title+'**\nQueue list:\n'
            for x in range(0,len(queue)):
                output += str(x+1)+'. **'+queue[x]['snippet']['title']+'**\n'
            await client.send_message(message.channel, output)
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
        player = await voice.create_ytdl_player('https://www.youtube.com/watch?v='+queue[0]['id']['videoId'])
        asdf = False
        paused = False
        if not repeat:
            del queue[0]
        skipped = False
        player.start()
        print(str(skipped))
        while True:
            if player==None or not player.is_playing():
                break
            processing = False
            await asyncio.sleep(1)
        if not skipped:
            await Play()
    else:
        print("something already playing")
client.run(token)