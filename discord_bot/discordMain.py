import discord
from validator_collection import validators, checkers
from TokenDistributer import TokenDistributer
import sys
import os
import difflib
from difflib import SequenceMatcher
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from amadeus.Amadeus import Amadeus
import traceback
import concurrent
import discord.utils


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

#TODO revisit naming convention of functions and variables
#TODO add rename tag function
#TODO Should we be using **kwargs to simplify optionals as more
# i.e. !stack+ myanime myanimehome -prio 3 -ep 2 -season 3
@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    try:
        if message.content.startswith('!help'):
            await help(message)
            return
        elif message.content.startswith('!stack'):
            await parseStackMessage(message)
            return
        elif message.content.startswith('!alias'):
            await parseAlias(message)
            return
        elif message.content.startswith('!setEp'):
            await setCurrEp(message)
            return
        elif message.content.startswith('!setSeason'):
            await setCurrSeason(message)
            return
        elif message.content.startswith('!watch'):
            await getCurrEpAndIncrement(message)
            return
        elif message.content.startswith('!pop'):
            await pop(message)
            return
        elif message.content.startswith('!prio'):
            await parsePrio(message)
            return
        elif message.content.startswith('!home'):
            await getHomeURL(message)
            return
        elif message.content.startswith('!exit') or message.content.startswith('!quit'):
            await client.logout()
        elif message.content.startswith('!'):
            await diagnoseMessage(message)
    except concurrent.futures._base.CancelledError as e:
        return
    except Exception as e:
        # traceback.print_exc()
        stacktrace = traceback.extract_stack()
        stacktrace_string = ''.join(stacktrace.format())
        print(stacktrace_string)
        channel = client.get_channel(632649941986050048)
        await channel.send("Exception occured when {0} said: \"{1}\". Stack trace:".format(message.author, message.content))
        await channel.send(stacktrace_string)

async def diagnoseMessage(message):
    stripped_message = message.content.replace("!", "")
    possibilities = [
        "help", "stack", "stack+", "stack-", "alias", "setEp", "setSeason", 
        "pop", "prio", "prio+", "prio-", "home", "exit", "quit"
    ]
    matches = difflib.get_close_matches(stripped_message, possibilities, 3, .6)
    if len(matches) != 0:
        formatting = "Unknown command. Did you mean to type one of the following: {0}?".format(", ".join(matches))
    else:
        formatting = "Unknown command. Type !help for assistance"
    await message.channel.send(formatting)

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

# Calls proper stack function
async def parseStackMessage(message):
    if message.content.startswith('!stack+'):
        await addAnimeToStack(message)
        return
    elif message.content.startswith('!stack-'):
        await removeAnimeFromStack(message)
        return
    await printStack(message)

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

async def parseAlias(message):
    if message.content.startswith('!alias+'):
        await addAlias(message)
        return
    await printAlias(message)

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

async def returnEpToUser(message, animeEpisodeName, currEpLink, currEpNum, currSeasonNum):
    embedEpisode = discord.Embed(url=currEpLink, title = "Webscrape me from the link trasher", description = "Oh No! See above!", color = 16175669)
    embedEpisode.set_author(name = "Crunchyroll", url = "https://www.crunchyroll.com")
    embedEpisode.set_thumbnail(url = "https://img1.ak.crunchyroll.com/i/spire1/fd7423d5f07a46fcdacb5159517626e51538197757_full.jpg")
    succMsg = 'Please enjoy Season {0}, Episode {1} of "{2}".\n'.format(currSeasonNum, currEpNum, animeEpisodeName)
    await message.channel.send(succMsg)
    await message.channel.send(embed = embedEpisode)

async def getCurrEpAndIncrement(message):
    words = message.content.split()
    if len(words) < 2:
        errMsg = 'Please enter the form of: "!get+ animeTitle/animeAlias".'
        await message.channel.send(errMsg)
        return

    key = "".join(words[1:])
    print("Entered key:", key)
    animeEpisodeName = amadeusDriver.getTitleFromKey(key)
    print("True key:", animeEpisodeName)

    #TODO this can be broken up
    #TODO Change stack everywhere to episdoes. Stack is a colloquialism we do not need in the code. 
    if animeEpisodeName:
        currEpNum = amadeusDriver.getCurrEpNumber(animeEpisodeName)
        currSeasonNum = amadeusDriver.getCurrSeasonNumber(animeEpisodeName)
        print("Current Ep: {0}, Current season: {1}".format(currEpNum, currSeasonNum))

        currEpLink = amadeusDriver.getEpisodeFromTitle(animeEpisodeName, currEpNum)
        if currEpLink:
            await returnEpToUser(message, animeEpisodeName, currEpLink, currEpNum, currSeasonNum)
            amadeusDriver.incrementStack(animeEpisodeName)
            return
            
        currEpLink = amadeusDriver.getSeasonEpisodeFromTitle(animeEpisodeName, 0, currSeasonNum + 1)
        if currEpLink:
            await returnEpToUser(message, animeEpisodeName, currEpLink, currEpNum, currSeasonNum)
            amadeusDriver.setStack(animeEpisodeName, 0)
            amadeusDriver.setSeason(animeEpisodeName, currSeasonNum + 1)
            return

        currEpLink = amadeusDriver.getSeasonEpisodeFromTitle(animeEpisodeName, 1, currSeasonNum + 1)
        if currEpLink:
            await returnEpToUser(message, animeEpisodeName, currEpLink, currEpNum, currSeasonNum)
            amadeusDriver.setStack(animeEpisodeName, 1)
            amadeusDriver.setSeason(animeEpisodeName, currSeasonNum + 1)
            return

        errMsg = 'Could not find episode {0} of "{1}". Please double check it exists.\n{2}'.format(currEpNum, animeEpisodeName, amadeusDriver.getUrlFromTitle(animeEpisodeName))
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
        
    potentialTag = "".join(words[1:])
    ep, currEpNum, anime = amadeusDriver.pop(potentialTag)
    
    if ep: 
        embedEpisode = discord.Embed(url=ep, title="Webscrap me from the link trasher",
                                                description="Oh No! See above!", color=16175669)
        embedEpisode.set_author(name="Crunchyroll", url="https://www.crunchyroll.com")
        embedEpisode.set_thumbnail(
            url="https://img1.ak.crunchyroll.com/i/spire1/fd7423d5f07a46fcdacb5159517626e51538197757_full.jpg")
        succMsg = 'Please enjoy episode {0} of "{1}".\n'.format(currEpNum, anime)
        await message.channel.send(succMsg)
        await message.channel.send(embed=embedEpisode)
    else:
        errMsg = '"Currently caught up on this stack. Weeb.'
        await message.channel.send(errMsg)

async def parsePrio(message):
    if message.content.startswith('!prio+'):
        await setPrio(message)
        return
    elif message.content.startswith('!prio-'):
        await removePrio(message)
        return
    await getPrio(message)

#TODO -> multi word tags? Is this even supported
async def setPrio(message):
    words = message.content.split()
    if len(words) < 2:
        errMsg = 'Please enter the form of: "!prio+ animeTitle/animeAlias numericValue/Tag".'
        await message.channel.send(errMsg)
        return
    
    anime = "".join(words[1:-1])
    amadeusDriver.setPrio(anime, words[-1])

#TODO -> multi word tags? Is this even supported
async def removePrio(message):
    words = message.content.split()
    if len(words) < 2:
        errMsg = 'Please enter the form of: "!prio- animeTitle/animeAlias numericValue/Tag".'
        await message.channel.send(errMsg)
        return
    
    anime = words[1:-1]
    amadeusDriver.removePrio(anime, words[-1])

#TODO
async def getPrio(message):
    await message.channel.send(amadeusDriver.numPrioManager)
    await message.channel.send("\na")
    await message.channel.send(amadeusDriver.tagPrioManager)

#TODO - No idea if works for titles with spaces
async def getHomeURL(message):
    words = message.content.split()
    if len(words) < 2:
        errMsg = 'Please enter the form of: "!home animeTitle/animeAlias".'
        await message.channel.send(errMsg)
        return

    homepage = amadeusDriver.getUrlFromTitle("".join(message[1:]))
    embedHome = discord.Embed(url=homepage, title="Webscrap me from the link trasher",
                                                description="Oh No! See above!", color=16175669)
    embedHome.set_author(name="Crunchyroll", url="https://www.crunchyroll.com")
    embedHome.set_thumbnail(
        url="https://img1.ak.crunchyroll.com/i/spire1/fd7423d5f07a46fcdacb5159517626e51538197757_full.jpg")
    await message.channel.send(embed=embedHome)


client.run(TokenDistributer.getToken())