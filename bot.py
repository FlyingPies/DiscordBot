import discord
import asyncio
import pprint
from googleapiclient.discovery import build
client = discord.Client()
player = None
paused = False
skipped = False
voice = None
token = None
queue = []
musicChan= None

f = open('config','r')
token = f.readline()
token=  token[token.index(' ')+1:len(token)-1]
print(token)
musicChan = f.readline()
musicChan = musicChan[musicChan.index(': ')+2:len(musicChan)]
print(musicChan)
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
        if message.author.top_role.name != '@everyone':
            await client.purge_from(message.channel, limit=999,check=None)
        else:
            await client.send_message(message.channel,'You do not have access to this command.')
    elif message.content.lower().startswith('!rules'):
        await client.send_message(message.channel, 'No rules\nlol')
    elif message.content.lower().startswith('!google'):
        query = message.content[message.content.index(' ')+1:len(message.content)]
        service = build('customsearch', 'v1', developerKey='AIzaSyB62VLWUp-7FXnsGZGHH59KysOWAHREkP0')
        res = service.cse().list(q=query,cx='013388782467450060570:cc_bo6ma8uk').execute() 

        if 'items' in res.keys():
            result= res['items'][0]['link']
            print(result) 
            await client.send_message(message.channel, result)
        else:
            await client.send_message(message.channel, 'No link was found.')

    elif message.content.lower().startswith('!play'):
        query = message.content[message.content.index(' ')+1:len(message.content)]
        service = build('customsearch', 'v1', developerKey='AIzaSyB62VLWUp-7FXnsGZGHH59KysOWAHREkP0')
        res = service.cse().list(q=query,cx='013388782467450060570:2jw06f1dfj4').execute() 
        if 'items' in res.keys():
            for x in range(0,len(res['items'])):
                if 'youtube' in res['items'][x]['link'] and 'watch' in res['items'][x]['link'] :
                    result = res["items"][x]["link"]
                    title = res['items'][x]['title']
                    break
                elif 'soundcloud' in res["items"][x]["link"] and res["items"][x]["link"].count('/')==4:
                    result = res["items"][x]["link"]
                    title = res['items'][x]['title']
                    break
            global queue
            queue.append(result)
            print(queue)
            pprint.pprint(result)
            global player
            if (len(queue)==1 and player == None) or (len(queue)==1 and player.is_done()):
                await client.send_message(message.channel, 'I will now play `' + title+'`')
            else:
                await client.send_message(message.channel, 'A song is already playing, so `'+title+'` will be added to the queue')
            if not player ==None:
                print("is_done :: "+str(not player.is_playing()))
            print("queue length :: "+str(len(queue)))
            await Play()
        else:
            await client.send_message(message.channel, 'No link was found.')
    elif message.content.lower().startswith('!skip'):
        if player==None:
            await client.send_message(message.channel,'No song is currently playing.')
        elif player.is_playing():
            player.stop()
            global paused
            global skipped
            paused = False
            skipped = True
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
            await client.send_message(message.channel, '`'+player.title+'` is currently playing')
        else:
            await client.send_message(message.channel, '`'+player.title+'` is currently playing')
async def Play():
    global player
    global queue
    global voice
    global skipped
    global paused
    if ((len(queue)>0 and player==None) or (len(queue)>0 and not player.is_playing())) and paused == False:
        player = await voice.create_ytdl_player(queue[0])
        paused = False
        del queue[0]
        skipped = False
        player.start()
        print(str(skipped))
        while True:
            if player==None or not player.is_playing():
                break
            await asyncio.sleep(1)
        if not skipped:
            await Play()
    else:
        print("something already playing")
client.run(token)