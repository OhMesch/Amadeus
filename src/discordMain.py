import discord
import validators
from TokenDistributer import TokenDistributer
from Amadeus import Amadeus

client = discord.Client()
amadeusDriver = None

@client.event
async def on_ready():
    global amadeusDriver
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    amadeusDriver = Amadeus()
    print('------')

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    # should get a status message from subfunctions and return those so we don't have to pass in message
    if message.author == client.user:
        return

    if message.content.startswith('!help'):
        await help(message)

    elif message.content.startswith('!stack+'):
        await addAnimeToStack(message)

    elif message.content.startswith('!stack'):
        await printStack(message)

async def help(message):
    helpMsg = 'Hello {0.author.mention}, I am Amadeus!'.format(message)
    helpMsg += '\nI exist to facilitate anime. Please kill me.\n'

    stackMsg = '\nTo get started, take a look at the stack with "!stack"'
    stackMsg += '\nThe stack shows all the currently watched anime and the next episode to watch.\n'

    helpMsg += stackMsg
    await client.send_message(message.channel, helpMsg)

async def addAnimeToStack(message):
    words = message.content.split()
    if len(words) != 2:
        errMsg = 'Please enter the form of: "!stack+ www.url-to-anime-home.com".'
        await client.send_message(message.channel, errMsg)
        return
    url = words[-1]
    if validators.url(url):
        animeNameDirty = url.split("/")[-1]
        animeNameClean = animeNameDirty.replace('-',' ').lower()
        amadeusDriver.addUrl(animeNameClean, url)
        amadeusDriver.addStack(animeNameClean)
    else:
        errMsg = 'Please confirm you have entered a valid url address.'
        await client.send_message(message.channel, errMsg)

async def printStack(message):
    stack = amadeusDriver.getStack()
    await client.send_message(message.channel, stack)

client.run(TokenDistributer.getToken())