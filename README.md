# DiscordBot
This discord bot is for a raspberry pi. Read Installation and Configuration section to learn how to set up bot

# Installation
To install you here is what you need installed:

   Installed through apt-get:  
    `openssl` and/or `libssl-dev`  
    `python3.5` with `pip`  
    `libffi-dev`  
    `ffmpeg`
    
   Installed through pip:  
    `youtube_dl`  
    `lxml`  
    `beautifulsoup4`    
    `discord.py[voice]`  
    `google-api-python-client`  

# Configuration
  So in order to create your bot go to https://discordapp.com and log in.  
  Then go to https://discordapp.com/developers and create a new application.  
  Once you give it a name, click Create a Bot User.  
  This should allow you to get the token that is asked for in the `config` file. 
  
  To make your bot join your server go to https://discordapp.com/oauth2/authorize?client_id=CLIENT_ID&scope=bot but with `CLIENT_ID` replaced with the Client ID found on the same page you found the token.
  
  In order to get the music channel id, you must first set discord in developer mode.  
  Then right click on the voice channel you want to set as the music channel, and click copy id.  
  This is the number you put in the `config` file 
