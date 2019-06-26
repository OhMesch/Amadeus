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

    elif message.content.startswith('!stack+'): #option to add alias and or episode with addition
        await addAnimeToStack(message)

    elif message.content.startswith('!stack-'):
        await removeAnimeFromStack(message)

    elif message.content.startswith('!stack'):
        await printStack(message)

    elif message.content.startswith('!alias+'):
        await addAlias(message)

    elif message.content.startswith('!alias'):
        await printAlias(message)

    elif message.content.startswith('!get+'):
        await getCurrEpAndIncriment(message)

    elif message.content.startswith('!set'):
        await setCurrEp(message)

    elif message.content.startswith('!home'):
        await getHomeURL(message)

    elif message.content.startswith('!exit'):
        await client.logout()

async def help(message):
    helpMsg = 'Hello {0.author.mention}, I am Amadeus!'.format(message)
    helpMsg += '\nI exist to facilitate anime. 大　やばい\n'

    stackMsg = '\nTo get started, take a look at the stack with "!stack"'
    stackMsg += '\nThe stack shows all the currently watched anime and the next episode to watch.\n'

    helpMsg += stackMsg
    await client.send_message(message.channel, helpMsg)

async def addAnimeToStack(message):
    words = message.content.split()

    if len(words) < 2:
        errMsg = 'Please enter the form of: "!stack+ www.url-to-anime-home.com" "optional Alias".'
        await client.send_message(message.channel, errMsg)
        return

    url = words[1]

    if validators.url(url):
        animeNameClean = cleanAnimeName(url.split("/")[-1])
        amadeusDriver.addUrl(animeNameClean, url)
        amadeusDriver.addStack(animeNameClean)
        amadeusDriver.setSeason(animeNameClean, "1")
    else:
        errMsg = 'Please confirm you have entered a valid url address.'
        await client.send_message(message.channel, errMsg)

    potentialAlias = " ".join(words[2:])
    if potentialAlias:
        amadeusDriver.addAlias(animeNameClean, potentialAlias)

async def removeAnimeFromStack(message):
    errMsg = 'Not currently implimented.'
    await client.send_message(message.channel, errMsg)

async def printStack(message):
    stack = amadeusDriver.getStack()
    await client.send_message(message.channel, stack)

async def printAlias(message):
    allAlias = amadeusDriver.getAllAlias()
    await client.send_message(message.channel, allAlias)

async def addAlias(message):
    words = message.content.split()
    if len(words) < 3:
        errMsg = 'Please enter the form of: "!alias+ anime-stack-name newAlias"\nOr:\n"!alias+ currAlias newAlias".'
        await client.send_message(message.channel, errMsg)
        return
    newAlias = "".join(words[2:])
    animeNameClean = cleanAnimeName(words[1])
    if animeNameClean in amadeusDriver.getStack():
        amadeusDriver.addAlias(animeNameClean, newAlias)
        succMsg = 'Added "{0}" as an alias for "{1}".'.format(newAlias, animeNameClean)
        await client.send_message(message.channel, succMsg)
    else:
        errMsg = 'Please confirm you have entered a valid anime name.'
        await client.send_message(message.channel, errMsg)

async def getCurrEpAndIncriment(message):
    words = message.content.split()
    if len(words) < 2:
        errMsg = 'Please enter the form of: "!get+ animeTitle/animeAlias".'
        await client.send_message(message.channel, errMsg)

    key = "".join(words[1:])
    print("Entered key:", key)
    trueKey = amadeusDriver.getTitleFromKey(key)
    print("True key:", trueKey)

    if trueKey:
        currEpNum = amadeusDriver.getCurrEpNumber(trueKey)
        print("Curr Ep:", currEpNum)
        currEpLink = amadeusDriver.getEpisodeFromTitle(trueKey, currEpNum)
        if currEpLink:
            embedEpisode = discord.Embed(url=currEpLink, title = "Webscrap me from the link trasher", description = "Oh No! See above!", color = 16175669)
            embedEpisode.set_author(name = "Crunchyroll", url = "https://www.crunchyroll.com")
            embedEpisode.set_thumbnail(url = "https://img1.ak.crunchyroll.com/i/spire1/fd7423d5f07a46fcdacb5159517626e51538197757_full.jpg")
            succMsg = 'Please enjoy episode {0} of "{1}".\n'.format(currEpNum,trueKey)
            await client.send_message(message.channel, succMsg)
            await client.send_message(message.channel, embed = embedEpisode)
            amadeusDriver.incrimentStack(trueKey)
        else:
            errMsg = 'Could not find episode {0} of "{1}". Please double check it exists.\n{2}'.format(currEpNum,trueKey,amadeusDriver.getUrlFromTitle(trueKey))
            await client.send_message(message.channel, errMsg)
    else:
        errMsg = '"{0}" not found in stack or alias list, please confirm the anime and try again.'.format(key)
        await client.send_message(message.channel, errMsg)

async def setCurrEp(message):
    words = message.content.split()
    if len(words) < 3:
        errMsg = 'Please enter the form of: "!set animeTitle/animeAlias epNum".'
        await client.send_message(message.channel, errMsg)
    ep = words[-1]
    try:
        int(ep)
        isValidEp = True
    except:
        isValidEp = False

    if isValidEp:
        key = "".join(words[1:-1])
        trueKey = amadeusDriver.getTitleFromKey(key)
        amadeusDriver.setStack(trueKey, ep)
        succMsg = 'Updated stack of {0} to episode {1}'.format(trueKey,ep)
        await client.send_message(message.channel, succMsg)
    else:
        errMsg = 'Please ensure "{0}" is a valid number'.format(ep)
        await client.send_message(message.channel, errMsg)

def cleanAnimeName(dirtyName):
    animeNameLower = dirtyName.replace('-',' ').lower()
    animeNameClean = " ".join(list(map(lambda x: x.capitalize(), animeNameLower.split())))
    return(animeNameClean)


client.run(TokenDistributer.getToken())