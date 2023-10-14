import discord
import asyncio
import os
from discord.ext import commands
from discord.utils import get
from datetime import datetime
import GetServerStatus

client = commands.Bot(command_prefix = "?")

QuarryLoop = None
# ChannelID = None

#pinged = "Servustatus-ping"
defaultPinged = "Servustatus-ping"
servustatus = "servustatus"
ehdotukset = "ehdotukset"

@client.event
async def on_ready():
    print("GorillaBot is ready.")
    await ServerStatus(client)

@client.event
async def on_message(message):
    if(((str(message.channel)).split()[0] != "Direct") and str(message.channel.name) == ehdotukset):
        await message.add_reaction("\U0001F44D")
        await message.add_reaction("\U0001F44E")
    await client.process_commands(message)

#########################    Client Commands   ######################

#ServerStatus
@client.command()
@commands.has_permissions(manage_channels=True)
async def ServerStatus(ctx, chan = servustatus, pinged = defaultPinged):
    print("Start Steam Quarry")
    Bot = client
    global QuarryLoop
    # client.loop.create_task(GetServerStatus.Steamquarry(client, chan, pinged))
    QuarryLoop = client.loop.create_task(GetServerStatus.Steamquarry(Bot, chan, pinged))

# maintenancemode
@client.command()
@commands.has_permissions(manage_channels=True)
async def maintenancemode(ctx):
    #await ctx.message.delete()
    
    #global PingMessage
    global QuarryLoop
    
    QuarryLoop.cancel()
    QuarryLoop = None
    
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    rel_path = "GorillaData.txt"
    abs_file_path = os.path.join(script_dir, rel_path)

    if os.path.isfile(abs_file_path):
        f = open(abs_file_path, "r")
        id1 = f.read()
        f.read()
        f.close()
        
        if not (not id1):
            #ChannelID, embedMessageID = id1.split(",")
            gorilladata = id1.split(",")

            ChannelID = int(gorilladata[0])
            embedMessageID = int(gorilladata[1])
            
            Curchannel = client.get_channel(ChannelID)
            embedMessage = discord.utils.get(await Curchannel.history(limit=100).flatten() , id = embedMessageID)
            await embedMessage.delete()
            
            if (len(gorilladata) > 2):
                PingMessageID = int(gorilladata[2])
                PingMessage = discord.utils.get(await Curchannel.history(limit=100).flatten() , id = PingMessageID)
                await PingMessage.delete()

    await Curchannel.send("Under Maintenance")
    print("Under Maintenance")

# ResetServerStatus
@client.command()
@commands.has_permissions(manage_channels=True)
async def ResetServerStatus(ctx, chan = servustatus, pinged = defaultPinged):
    await clearbotmessages(ctx, 3, chan)
    await ServerStatus(ctx, chan, pinged)
    
# shutdown
@client.command()
@commands.has_permissions(administrator=True)
async def shutdown(ctx):
    await ctx.bot.logout()

# clear commands
@client.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, channel, amount=0,):
    if (isinstance(channel, str)):
        channel = discord.utils.get(ctx.guild.channels, name=channel)
    await channel.purge(limit=amount)

@client.command()
@commands.has_permissions(manage_channels=True)
async def clearbotmessages(ctx, limit=0, chan = servustatus):
    #await ctx.message.delete()
    Curchannel = discord.utils.get(ctx.guild.channels, name=chan)
    msg = []
    async for m in Curchannel.history():
        if len(msg) == limit:
            break
        if m.author == client.user:
            msg.append(m)
    await Curchannel.delete_messages(msg)
    #await ctx.send(f"Purged {limit} messages of {client.user.mention}", delete_after=3)

# need discord bot id 
client.run("Discord_Bot_ID")
