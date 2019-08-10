import discord
from validator_collection import validators, checkers
from TokenDistributer import TokenDistributer
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from amadeus.Amadeus import Amadeus
from amadeus.PriorityManager import NumericPriorityManger, TagPriorityManger

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

#TODO Should we be using **kwargs to simplify optionals as more
# i.e. !stack+ myanime myanimehome -prio 3 -ep 2 -season 3
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
        await getCurrEpAndIncrement(message)

    elif message.content.startswith('!setEp'):
        await setCurrEp(message)

    elif message.content.startswith('!setSeason'):
        await setCurrSeason(message)

    elif message.content.startswith('!pop'):
        await pop(message)

#TODO - Have one input for stack / prio ect, parse, then call the proper functions, dont try to parse here
    elif message.content.startswith('!prio+'):
        await setPrio(message)

    elif message.content.startswith('!prio-'):
        await removePrio(message)

    #TODO
    elif message.content.startswith('!prio'):
        await getPrio(message)

    #TODO
    elif message.content.startswith('!home'):
        await getHomeURL(message)

    elif message.content.startswith('!exit') or message.content.startswith('!quit'):
        await client.logout()

async def help(message):
    helpMsg = 'Hello {0.author.mention}, I am Amadeus!'.format(message)
    helpMsg += '\nI exist to facilitate anime. 大やばい\n'

    stackMsg = '\nTo get started, take a look at the stack with "!stack"'
    stackMsg += '\nThe stack shows all the currently watched anime and the next episode to watch.'

    addStackMsg = "\nTo add an anime to the stack, you will need the CrunchyRoll page corresponding to the anime you want to add."
    addStackMsg += "\nOnce you have your anime url, add it to the stack in the form of: \"!stack+ www.url-to-anime-home.com\"."
    addStackMsg += "\nAlternatively, if you would like to set an alias while adding the anime, use the syntax: \"!stack+ www.url-to-anime-home.com customAlias\".\n"

    aliasMsg = "\nAliases are anouther way to refer to, and interact with, an anime on the stack. Alias provide an alternative to using the full stack name for an anime."
    aliasMsg += "\nAn alias can be added to an existing stack entry with either:\n{0}\n{1}".format("!alias+ anime-stack-name newAlias","!alias+ currAlias newAlias")

    helpMsg += stackMsg
    helpMsg += addStackMsg
    helpMsg += aliasMsg
    await message.channel.send(helpMsg)

#TODO we should add anouther scraper for kiss and have more options
async def addAnimeToStack(message):
    words = message.content.split()

    if len(words) < 2:
        errMsg = 'Please enter the form of: "!stack+ www.url-to-anime-home.com" "optional Alias".'
        await message.channel.send(errMsg)
        return

    url = words[1]

    if validators.url(url):
        animeNameClean = cleanAnimeName(url.split("/")[-1])
        amadeusDriver.addUrl(animeNameClean, url)
        amadeusDriver.addStack(animeNameClean)
        amadeusDriver.setSeason(animeNameClean, "1")
    else:
        errMsg = 'Please confirm you have entered a valid url address.'
        await message.channel.send(errMsg)

    potentialAlias = " ".join(words[2:])
    if potentialAlias:
        amadeusDriver.addAlias(animeNameClean, potentialAlias)

async def removeAnimeFromStack(message):
    errMsg = 'Not currently implimented.'
    await message.channel.send(errMsg)

async def printStack(message):
    stack = amadeusDriver.stack
    await message.channel.send(stack)

async def printAlias(message):
    allAlias = amadeusDriver.alias
    await message.channel.send(allAlias)

async def addAlias(message):
    words = message.content.split()
    if len(words) < 3:
        errMsg = 'Please enter the form of: "!alias+ anime-stack-name newAlias"\nOr:\n"!alias+ currAlias newAlias".'
        await message.channel.send(errMsg)
        return
    newAlias = "".join(words[2:])
    animeNameClean = cleanAnimeName(words[1])
    if animeNameClean in amadeusDriver.stack:
        amadeusDriver.addAlias(animeNameClean, newAlias)
        succMsg = 'Added "{0}" as an alias for "{1}".'.format(newAlias, animeNameClean)
        await message.channel.send(succMsg)
    else:
        errMsg = 'Please confirm you have entered a valid anime name.'
        await message.channel.send(errMsg)

async def getCurrEpAndIncrement(message):
    words = message.content.split()
    if len(words) < 2:
        errMsg = 'Please enter the form of: "!get+ animeTitle/animeAlias".'
        await message.channel.send(errMsg)

    key = "".join(words[1:])
    print("Entered key:", key)
    trueKey = amadeusDriver.getTitleFromKey(key)
    print("True key:", trueKey)

#TODO this can be broken up
    if trueKey:
        currEpNum = amadeusDriver.getCurrEpNumber(trueKey)
        print("Curr Ep:", currEpNum)
        currEpLink = amadeusDriver.getEpisodeFromTitle(trueKey, currEpNum)
        if currEpLink:
            embedEpisode = discord.Embed(url=currEpLink, title = "Webscrap me from the link trasher", description = "Oh No! See above!", color = 16175669)
            embedEpisode.set_author(name = "Crunchyroll", url = "https://www.crunchyroll.com")
            embedEpisode.set_thumbnail(url = "https://img1.ak.crunchyroll.com/i/spire1/fd7423d5f07a46fcdacb5159517626e51538197757_full.jpg")
            succMsg = 'Please enjoy episode {0} of "{1}".\n'.format(currEpNum,trueKey)
            await message.channel.send(succMsg)
            await message.channel.send(embed = embedEpisode)
            amadeusDriver.incrementStack(trueKey)
        else:
            errMsg = 'Could not find episode {0} of "{1}". Please double check it exists.\n{2}'.format(currEpNum,trueKey,amadeusDriver.getUrlFromTitle(trueKey))
            await message.channel.send(errMsg)
    else:
        errMsg = '"{0}" not found in stack or alias list, please confirm the anime and try again.'.format(key)
        await message.channel.send(errMsg)

async def setCurrEp(message):
    words = message.content.split()
    if len(words) < 3:
        errMsg = 'Please enter the form of: "!setEp animeTitle/animeAlias epNum".'
        await message.channel.send(errMsg)
    ep = words[-1]

    if checkers.is_integer(ep):
        key = "".join(words[1:-1])
        trueKey = amadeusDriver.getTitleFromKey(key)
        amadeusDriver.setStack(trueKey, ep)
        succMsg = 'Updated stack of {0} to episode {1}'.format(trueKey,ep)
        await message.channel.send(succMsg)
    else:
        errMsg = 'Please ensure "{0}" is a valid number'.format(ep)
        await message.channel.send(errMsg)

def cleanAnimeName(dirtyName):
    animeNameLower = dirtyName.replace('-',' ').lower()
    animeNameClean = " ".join(list(map(lambda x: x.capitalize(), animeNameLower.split())))
    return(animeNameClean)

async def setCurrSeason(message):
    words = message.content.split()
    if len(words) < 3:
        errMsg = 'Please enter the form of: "!setSeason animeTitle/animeAlias seasonNum".'
        await message.channel.send(errMsg)
    season = words[-1]
    #TODO Replace with validators / checkers
    try:
        int(season)
        isValidSeason = True
    except:
        isValidSeason = False

    if isValidSeason:
        key = "".join(words[1:-1])
        trueKey = amadeusDriver.getTitleFromKey(key)
        amadeusDriver.setStack(trueKey, season)
        succMsg = 'Updated stack of {0} to season {1}'.format(trueKey,season)
        await message.channel.send(succMsg)
    else:
        errMsg = 'Please ensure "{0}" is a valid integer'.format(season)
        await message.channel.send(errMsg)

#TODO
async def pop(message):
    words = message.content.split()
    if len(words) > 2:
        errMsg = 'Please enter the form of: "!pop <optionalTag>".'
        await message.channel.send(errMsg)

#TODO this smells
    potentialTag = words[1:]
    if potentialTag:
        prioManager = TagPriorityManger()
        popOrder = prioManager.getTitleSequence(potentialTag)
    else:
        prioManager = NumericPriorityManger()
        popOrder = prioManager.getTitleSequence()

    #TODO DRY
    for anime in popOrder:
        currEpNum = amadeusDriver.getCurrEpNumber(anime)
        currEpLink = amadeusDriver.getEpisodeFromTitle(anime, currEpNum)
        if currEpLink:
            embedEpisode = discord.Embed(url=currEpLink, title="Webscrap me from the link trasher",
                                         description="Oh No! See above!", color=16175669)
            embedEpisode.set_author(name="Crunchyroll", url="https://www.crunchyroll.com")
            embedEpisode.set_thumbnail(
                url="https://img1.ak.crunchyroll.com/i/spire1/fd7423d5f07a46fcdacb5159517626e51538197757_full.jpg")
            succMsg = 'Please enjoy episode {0} of "{1}".\n'.format(currEpNum, anime)
            await message.channel.send(succMsg)
            await message.channel.send(embed=embedEpisode)
            amadeusDriver.incrementStack(anime)
            break
    errMsg = '"Currently caught up on this stack. Weeb.'
    await message.channel.send(errMsg)

#TODO
async def setPrio(message):
    pass

#TODO
async def removePrio(message):
    pass

client.run(TokenDistributer.getToken())