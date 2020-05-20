import discord
from validator_collection import validators, checkers
import TokenDistributer
import sys
import os
import difflib
from difflib import SequenceMatcher
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from amadeus.Amadeus import Amadeus
import traceback
import concurrent
import discord.utils
import argparse


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-d', '--data_directory', default='', type=str, help="enables python stack trace")
args = arg_parser.parse_args()

data_directory = None
if args.data_directory:
    data_directory = args.data_directory
client = discord.Client()
amadeusDriver = None

@client.event
async def on_ready():
    global amadeusDriver
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    amadeusDriver = Amadeus(data_directory)
    print('------')

# TODO revisit naming convention of functions and variables
# TODO add rename tag function
# TODO Should we be using **kwargs to simplify optionals as more
# i.e. !stack+ myanime myanimehome -prio 3 -ep 2 -season 3
# TODO We have a lot of repeat code for scrubbing anime names and makingsure they blong to the stack. DRY
# Resource files for strings
@client.event
async def on_message(message):
    # on_message can run prior to on_ready finishing
    if amadeusDriver == None:
        return
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    try:
        if not message.content.startswith("!"):
            return
        args = message.content.split()
        first_arg = args[0]

        if first_arg == '!help':
            await help(message, args)
            return
        elif first_arg.startswith('!undo'):
            await undo(message, args)
            return
        elif first_arg.startswith('!redo'):
            await redo(message, args)
            return
        elif first_arg.startswith('!stack'):
            await parseStackMessage(message, args)
            return
        elif first_arg.startswith('!alias'):
            await parseAlias(message, args)
            return
        elif first_arg.startswith('!prio'):
            await parsePrio(message, args)
            return
        elif first_arg == '!setEp':
            await setCurrEp(message, args)
            return
        elif first_arg == '!setSeason':
            await setCurrSeason(message, args)
            return
        elif first_arg == '!pop':
            await pop(message, args)
            return
        elif first_arg == '!home':
            await getHomeURL(message, args)
            return
        elif first_arg == '!exit' or first_arg == '!quit':
            await client.logout()
            exit()
        await diagnoseMessage(message)
    except concurrent.futures._base.CancelledError as e:
        return
    except Exception as e:
        stacktrace = traceback.format_exc()
        print(stacktrace)
        channel = client.get_channel(632649941986050048)
        await channel.send("Exception occured when {0} said: \"{1}\". Stack trace:".format(message.author, message.content))
        await channel.send(stacktrace)

async def diagnoseMessage(message):
    stripped_message = message.content.replace("!", "")
    possibilities = [
        "help", "stack+", "stack-", "alias", "setEp", "setSeason", 
        "pop", "prio+", "prio-", "home", "exit", "quit", "undo", "redo"
    ]
    matches = difflib.get_close_matches(stripped_message, possibilities, 3, .6)
    if len(matches) != 0:
        formatting = "Unknown command. Did you mean to type one of the following: {0}?".format(", ".join(matches))
    else:
        formatting = "Unknown command. Type !help for assistance"
    await message.channel.send(formatting)

async def help(message, args):
    helpMsg = 'Hello {0.author.mention}, I am Amadeus!'.format(message)
    helpMsg += '\nI exist to facilitate anime. 大やばい\n'

    stackMsg = '\nTo get started, take a look at the stack with **"!stack"**'
    stackMsg += '\nThe stack shows all the currently watched anime and the next episode to watch.'

    addAnimeMsg = "\nTo add an anime to the stack, you will need the CrunchyRoll page corresponding to the anime you want to add."
    addAnimeMsg += "\nOnce you have your anime url, add it to the stack in the form of: \"**!stack+ www.url-to-anime-home.com\"**."
    addAnimeMsg += "\nAlternatively, if you would like to set an alias while adding the anime, use the syntax: \"!stack+ www.url-to-anime-home.com customAlias\".\n"

    aliasMsg = "\nAliases are anouther way to refer to, and interact with, an anime on the stack. Alias provide an alternative to using the full stack name for an anime."
    aliasMsg += "\nAn alias can be added to an existing stack entry with either:\n**{0}**\n**{1}**".format("!alias+ anime-stack-name newAlias","!alias+ currAlias newAlias")
    
    popMsg = '\nTo retrieve an anime from the stack according to the numerical priority, type: **"!pop"**'
    popMsg += '\nTo retrieve a specific anime, type: **"!pop anime_name_or_alias"**'
    popMsg += '\nTo retrieve an anime from the stack according to a tag priority, type: **"!pop tag_priority"** (anime_name_or_alias takes priority)'

    undoRedoMsg = '\nType **"!undo"** or **"!redo"** to step backward or forward (actions only live for process life)'


    helpMsg += stackMsg
    helpMsg += addAnimeMsg
    helpMsg += aliasMsg
    helpMsg += popMsg
    helpMsg += undoRedoMsg
    await message.channel.send(helpMsg)

async def redo(message, args):
    actionTaken = amadeusDriver.redo()
    await message.channel.send('Took action "{0}" again'.format(actionTaken))

async def undo(message, args):
    actionTaken = amadeusDriver.undo()
    await message.channel.send('Undid action "{0}"'.format(actionTaken))

# Calls proper stack function
async def parseStackMessage(message, args):
    if message.content.startswith('!stack+'):
        await addAnimeToStack(message, args)
        return
    elif message.content.startswith('!stack-'):
        await removeAnimeFromStack(message, args)
        return
    await printStack(message, args)

#TODO we should add anouther scraper for kiss and have more options
async def addAnimeToStack(message, args):
    if len(args) != 2 and len(args) != 3:
        errMsg = 'Please enter the form of: "!stack+ www.url-to-anime-home.com" "optional Alias".'
        await message.channel.send(errMsg)
        return
    potential_url = args[1]
    potential_alias = ''
    if len(args) == 3:
        potential_alias = args[2]
    try:
        nameOfAnime = amadeusDriver.addNewAnime(potential_url, potential_alias)
        await message.channel.send('added anime: {0}'.format(nameOfAnime))
    except ValueError as e:
        errMsg = 'Please confirm you have entered a valid url address, the link provided failed URL validation'
        await message.channel.send(errMsg)
    except UnboundLocalError as e:
        errMsg = 'alias provided: {0} has whitespace in it, please remove the whitespace'.format(potential_alias)
        await message.channel.send(errMsg)

async def removeAnimeFromStack(message, args):
    potential_name = args[1]
    result = amadeusDriver.removeAnime(potential_name)
    if result == False:
        await message.channel.send('couldn\'t remove anime / alias titled: {0}'.format(potential_name))
    else:
        await message.channel.send('removed anime: {0}'.format(potential_name))

async def printStack(message, args):
    stringified_information = amadeusDriver.stringifyAnimeInformation().rstrip().lstrip()
    if not stringified_information or stringified_information.isspace():
        stringified_information = 'Theres nothing on the stack! {0} This {0} is {0} a {0} literal {0} tragedy {0}'.format('<:virus:702269312924123186>')
    await message.channel.send(stringified_information)

async def parseAlias(message, args):
    if message.content.startswith('!alias+'):
        await addAlias(message, args)
    else:
        await message.channel.send('Use "!alias+ (anime name) (new alias)" to add an alias')
    # await printAlias(message, args)

# async def printAlias(message, args):
#     allAlias = amadeusDriver.alias
#     await message.channel.send(allAlias)

async def addAlias(message, args):
    if len(args) != 3:
        errMsg = 'Please enter the form of: "!alias+ anime-stack-name newAlias"\nOr:\n"!alias+ currAlias newAlias".'
        await message.channel.send(errMsg)
        return
    newAlias = " ".join(args[2:])
    animeNameClean = cleanAnimeName(args[1])

    try:
        aliasOrTitle = amadeusDriver.addAlias(animeNameClean, newAlias)
    except UnboundLocalError as e:
        errMsg = 'alias provided: {0} has whitespace in it, please remove the whitespace'.format(potential_alias)
        await message.channel.send(errMsg)

    if aliasOrTitle:
        succMsg = 'Added "{0}" as an alias for "{1}".'.format(newAlias, aliasOrTitle)
        await message.channel.send(succMsg)
    else:
        errMsg = 'Please confirm you have entered a valid anime name. Could not find {0}'.format(animeNameClean)
        await message.channel.send(errMsg)

async def returnEpToUser(message, animeEpisodeName, currEpLink, currEpNum, currSeasonNum):
    embedEpisode = discord.Embed(url=currEpLink, title = "Webscrape me from the link trasher", description = "Oh No! See above!", color = 16175669)
    embedEpisode.set_author(name = "Crunchyroll", url = "https://www.crunchyroll.com")
    embedEpisode.set_thumbnail(url = "https://img1.ak.crunchyroll.com/i/spire1/fd7423d5f07a46fcdacb5159517626e51538197757_full.jpg")
    succMsg = 'Please enjoy Season {0}, Episode {1} of "{2}".\n'.format(currSeasonNum, currEpNum, animeEpisodeName)
    await message.channel.send(succMsg)
    await message.channel.send(embed = embedEpisode)

async def setCurrEp(message, args):
    args = message.content.split()
    if len(args) != 3:
        errMsg = 'Please enter the form of: "!setEp animeTitle/animeAlias epNum".'
        await message.channel.send(errMsg)
    ep = args[-1]

    if checkers.is_integer(ep):
        key = "".join(args[1:-1])
        trueKey = amadeusDriver.getTitleFromKey(key)
        amadeusDriver.setEpisode(trueKey, ep)
        succMsg = 'Updated stack of {0} to episode {1}'.format(trueKey,ep)
        await message.channel.send(succMsg)
    else:
        errMsg = 'Please ensure "{0}" is a valid number'.format(ep)
        await message.channel.send(errMsg)

def cleanAnimeName(dirtyName):
    animeNameLower = dirtyName.replace('-',' ').lower()
    animeNameClean = " ".join(list(map(lambda x: x.capitalize(), animeNameLower.split())))
    return animeNameClean

async def setCurrSeason(message, args):
    if len(args) != 3:
        errMsg = 'Please enter the form of: "!setSeason animeTitle/animeAlias seasonNum".'
        await message.channel.send(errMsg)
    season = args[-1]
    #TODO Replace with validators / checkers
    try:
        int(season)
        isValidSeason = True
    except:
        isValidSeason = False

    if isValidSeason:
        key = "".join(args[1:-1])
        trueKey = amadeusDriver.getTitleFromKey(key)
        amadeusDriver.setEpisode(trueKey, season)
        succMsg = 'Updated stack of {0} to season {1}'.format(trueKey,season)
        await message.channel.send(succMsg)
    else:
        errMsg = 'Please ensure "{0}" is a valid integer'.format(season)
        await message.channel.send(errMsg)

async def pop(message, args):
    if len(args) > 2:
        errMsg = 'Please enter the form of: "!pop <optionalTag>".'
        await message.channel.send(errMsg)
        
    animeTitleOrAliasOrTag = "".join(args[1:])
    ep, currEpNum, anime = amadeusDriver.pop(animeTitleOrAliasOrTag)
    
    if ep: 
        embedEpisode = discord.Embed(url=ep, title="Webscrap me from the link trasher", description="Oh No! See above!", color=16175669)
        embedEpisode.set_author(name="Crunchyroll", url="https://www.crunchyroll.com")
        embedEpisode.set_thumbnail(url="https://img1.ak.crunchyroll.com/i/spire1/fd7423d5f07a46fcdacb5159517626e51538197757_full.jpg")
        succMsg = 'Please enjoy episode {0} of "{1}".\n'.format(currEpNum, anime)
        await message.channel.send(succMsg)
        await message.channel.send(embed=embedEpisode)
    else:
        errMsg = 'You are currently caught up on this stack. Probably there is something wrong, or you are the world\'s largest weeb.' 
        await message.channel.send(errMsg)

async def parsePrio(message, args):
    if message.content.startswith('!prio+'):
        await setPrio(message, args)
        return
    elif message.content.startswith('!prio-'):
        await removePrio(message, args)
        return
    await message.channel.send('Use either "!prio+ (anime name) (priority)" or "!prio- (anime name) (priority)" to add or remove a priority')
    # await getPrio(message, args)

#TODO -> multi word tags? Is this even supported
async def setPrio(message, args):
    if len(args) != 3:
        errMsg = 'Please enter the form of: "!prio+ animeTitle/animeAlias numericValue/Tag".'
        await message.channel.send(errMsg)
        return

    animeNameOrAlias = ' '.join(args[1].split('-'))
    if amadeusDriver.setPrio(animeNameOrAlias, args[2]):
        await message.channel.send('{0} is now priority {1}'.format(animeNameOrAlias, args[2]))
    else:
        errMsg = 'Please confirm you have entered a valid anime name or alias.'
        await message.channel.send(errMsg)
        return


#TODO -> multi word tags? Is this even supported
async def removePrio(message, args):
    if len(args) < 2:
        errMsg = 'Please enter the form of: "!prio- animeTitle/animeAlias numericValue/Tag".'
        await message.channel.send(errMsg)
        return
    
    animeTitle = amadeusDriver.getTitleFromKey(args[1:-1])
    if animeTitle in amadeusDriver.stack:
        amadeusDriver.removePrio(animeTitle, args[-1])
    else:
        errMsg = 'Please confirm you have entered a valid anime name or alias.'
        await message.channel.send(errMsg)
        return

# async def getPrio(message, args):
#     await message.channel.send("Numerical Priority List:")
#     await message.channel.send(amadeusDriver.numPrioManager)
#     await message.channel.send("\n\nTagged Priority List:")
#     await message.channel.send(amadeusDriver.tagPrioManager)

#TODO - No idea if works for titles with spaces
#TODO what does this do
async def getHomeURL(message, args):
    args = message.content.split()
    if len(args) < 2:
        errMsg = 'Please enter the form of: "!home animeTitle/animeAlias".'
        await message.channel.send(errMsg)
        return

    animeTitle = amadeusDriver.getTitleFromKey("".join(message[1:]))
    homepage = amadeusDriver.getUrlFromTitle(animeTitle)

    embedHome = discord.Embed(url=homepage, title="Webscrap me from the link trasher", description="Oh No! See above!", color=16175669)
    embedHome.set_author(name="Crunchyroll", url="https://www.crunchyroll.com")
    embedHome.set_thumbnail(url="https://img1.ak.crunchyroll.com/i/spire1/fd7423d5f07a46fcdacb5159517626e51538197757_full.jpg")
    await message.channel.send(embed=embedHome)

client.run(TokenDistributer.getToken())