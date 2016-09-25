import discord
import asyncio
import pprint
from googleapiclient.discovery import build
client = discord.Client()
player = None
paused = False
voice = None
queue = []

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    print(client.get_channel('207949179014610944'))
    global voice
    voice = await client.join_voice_channel(client.get_channel('207949179014610944'))
    gamez = discord.Game()
    gamez.name = 'the internet'
    gamez.type = 1
    gamez.url = 'https://www.twitch.tv/loltyler1'
    print(gamez.url)
    await client.change_status(game=gamez, idle=False)

@client.event
async def on_message(message):
    if message.content.startswith('!test'):
        counter = 0
        tmp = await client.send_message(message.channel, 'Calculating messages...')
        async for log in client.logs_from(message.channel, limit=100):
            if log.author == message.author:
                counter += 1

        await client.edit_message(tmp, 'You have {} messages.'.format(counter))
    elif message.content.startswith('!sleep'):
        await asyncio.sleep(5)
        await client.send_message(message.channel, 'Done sleeping')
    elif message.content.startswith('!clear_chat'):
        if message.author.top_role.name != '@everyone':
            await client.purge_from(message.channel, limit=999,check=None)
        else:
            await client.send_message(message.channel,'You do not have access to this command.')
    elif message.content.startswith('!rules'):
        await client.send_message(message.channel, 'No rules\nlol')
    elif message.content.startswith('!google'):
        query = message.content[message.content.index(' ')+1:len(message.content)]
        service = build('customsearch', 'v1', developerKey='AIzaSyCaoKYbfX2TdeWTtojigK-btjNBh1qlZjs')
        res = service.cse().list(q=query,cx='013388782467450060570:cc_bo6ma8uk').execute() 

        if 'items' in res.keys():
            result= res['items'][0]['link']
            print(result) 
            await client.send_message(message.channel, result)
        else:
            await client.send_message(message.channel, 'No link was found.')

    elif message.content.startswith('!play'):
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
            if len(queue)==1:
                await client.send_message(message.channel, 'I will now play `' + title+'`')
            else:
                await client.send_message(message.channel, 'A song is already playing, so `'+title+'` will be added to the queue')
            await Play()
        else:
            await client.send_message(message.channel, 'No link was found.')
    elif message.content.startswith('!skip'):
        if player==None:
            await client.send_message(message.channel,'No song is currently playing.')
        elif player.is_playing():
            player.stop()
            queue
            del queue[0]
            global paused
            paused = False
            await Play()
        else:
            await client.send_message(message.channel,'No song is currently playing.')
    elif message.content.startswith('!pause'):
        if player==None:
            await client.send_message(message.channel,'No song is currently playing.')
        elif player.is_playing():
            player.pause()
            paused = True
        else:
            await client.send_message(message.channel,'No song is currently playing.')
    elif message.content.startswith('!resume'):
        if player==None:
            await client.send_message(message.channel,'No song is currently playing.')
        elif paused==True:
            player.resume()
            paused = False
        else:
            await client.send_message(message.channel,'No song is currently playing.')
    elif message.content.startswith('!np'):
        if not queue:
            await client.send_message(message.channel, 'No song is currently playing.')
        else:
            await client.send_message(message.channel, '`'+player.title+'` is currently playing')
async def Play():
    global player
    global queue
    global voice
    if (len(queue)>0 and player==None) or (len(queue)>0 and player.is_done()):
        player = await voice.create_ytdl_player(queue[0])
        global paused
        paused = False
        player.start()
        while True:
            if player.is_done():
                break
            await asyncio.sleep(1)
        del queue[0]
        await Play()
client.run('MjA3NjQ1MjA2OTE5NTEyMDY0.CqyMdQ.K6KjIS5t3DB4fGt1UhGl-26BXuI')