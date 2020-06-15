# Amadeus
Discord bot for managing anime to-watch lists. 

Add anime to the "Stack" to track episodes. Get the current episode to watch.

## Install dependancies
pip install -r requirements.txt

## Creating and inviting a discord bot
Visit `https://discordapp.com/developers/applications/` for instructions on how to create the bot

Then, with the client_id go to `https://discordapp.com/oauth2/authorize?client_id=BOT_ID_HERE&scope=bot&permissions=0` to invite the bot to your server. (0 is no permissions)

## Running the bot
To pass in a data directory use the `-d` flag. Example:
`python discordMain.py -d C:/storage/amadeus_data`
The last directory does not have to exist. The program will create it for you. 

For the server to turn back on on filesystem refresh run: `hupper -m discordMain.py -d C:/storage/amadeus_data`

## Required cert for python 3.8 in windows for discord.py
https://crt.sh/?id=2835394