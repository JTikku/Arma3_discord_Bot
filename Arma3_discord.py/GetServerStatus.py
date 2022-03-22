import discord
import asyncio
import os
from discord.ext import commands
from discord.utils import get
from valve.source.a2s import ServerQuerier
from valve.source.master_server import MasterServerQuerier
from valve.source.messages import BrokenMessageError
from datetime import datetime
import os.path

# keepLooping = true
# port needs to be Query Port
address = ()

PingMessage = None
embedMessage = None
Curchannel = None

PingMessageID = None
embedMessageID = None
ChannelID = None

pinged = "Servustatus-ping"
#move to file getserverstatus?
# Steamquarry loop

async def Steamquarry(client, chan, ping):
    global Curchannel
    global pinged
    global ChannelID
    global embedMessageID
    global PingMessageID
    
    #global keepLooping
    keepLooping = True
    
    # re add ping func
    #pinged = discord.utils.get(ctx.guild.roles,name=ping)
    #Curchannel = client.get_channel(ChannelID)
    
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    rel_path = "GorillaData.txt"
    abs_file_path = os.path.join(script_dir, rel_path)

    if os.path.isfile(abs_file_path):
        f = open(abs_file_path, "r")
        id1 = f.read()
        f.read()
        f.close()
        
        if not (not id1):
            gorilladata = id1.split(",")
            
            ChannelID = int(gorilladata[0])
            embedMessageID = int(gorilladata[1])
            PingMessageID = None
            
            if (len(gorilladata) > 2):
                PingMessageID = int(gorilladata[2])

    if chan is None:
        Curchannel = client.get_channel(ChannelID)
    else:
        Curchannel = discord.utils.get(client.get_all_channels(), name=chan)
        
    #Curchannel = discord.utils.get(ctx.guild.channels, name=chan)
    while keepLooping:
        try:
            #await get_server_stats(ctx, address, chan)
            message = await ReturnServerStatus(client, chan, Curchannel, pinged)
        except Exception as e:
            #print(e)
            await asyncio.sleep(60)
            continue
        # except:
            # print("Uknown exception")
            # continue
        # await asyncio.sleep(90)

async def clearServerstatus(client):
    limit=10
    global Curchannel
    global embedMessageID
    global PingMessageID
    
    #msgnum = 0
    async for m in Curchannel.history():
        if 0 == limit:
            break
        if (m.author == client.user) and ((m.id != embedMessageID) and (m.id != PingMessageID)):
            await m.delete()
            limit = limit - 1
    #await Curchannel.delete_messages(msg)

# Clear up code
# Console messages are overlapping
async def ReturnServerStatus(client, chan, Curchannel, pinged):
        now = datetime.now()
        global address
        global embedMessage
        
        # global Curchannel
        # global pinged
        global embedMessageID
        global PingMessageID
        
        try:
            server = ServerQuerier(address, timeout=15.0)

            print(f"Done: {now.strftime('%H:%M')}", end = "\r")
            
            embed=discord.Embed(title= server.info()["server_name"])
            embed.set_footer(text= f"{now.strftime('%d.%m.%Y %H:%M')}")
            embed.add_field(name= "Status", value= "Online", inline=False)
            
            if (server.info()["map"] != ""):
                embed.add_field(name= "Kartta:", value= server.info()["map"], inline=False)
            else:
                embed.add_field(name= "Kartta:", value= "-", inline=False)

            if (server.info()["game"] != ""):
                embed.add_field(name= "Tehtävä:", value= server.info()["game"], inline=False)
            else:
                embed.add_field(name= "Tehtävä:", value= "-", inline=False)
            
            embed.add_field(name= "Pelaajamäärä:", value= f"{server.info()['player_count']}/{server.info()['max_players']}", inline=False)
            embed.add_field(name= "\u200B", value= "\u200B", inline=True)
            PlayerList = []
            for player in server.players()["players"]:
                PlayerList.append(f"{player['name']} {'{:02d}:{:02d}'.format(*divmod(round((player['duration'] / 60)), 60))}")

            if (len(PlayerList) > 0):
                playernames = '\n'.join(PlayerList)
                embed.add_field(name= "Pelaajalista:", value= f"```{playernames}```", inline=False)
            else:
                embed.add_field(name= "Pelaajalista:", value= "```Ei pelaajia```", inline=False)
        # except valve.source.NoResponseError:
            # server.close()
            # print("NoResponseError")
            # raise
        except Exception as e:
            print(f"{now.strftime('%H:%M')}: {e}", end = "\r")
            # print(e)
            server.close()
            embed=discord.Embed(title= "Server didn't respond")
            embed.add_field(name= "Status:", value= "Offline", inline=False)
            embed.set_footer(text= f"{now.strftime('%d.%m.%Y %H:%M')}")
            
            embedMessage = discord.utils.get(await Curchannel.history(limit=100).flatten() , id = embedMessageID)
            if embedMessage is None:
                await clearServerstatus(client)
                embedMessage = await Curchannel.send(embed=embed)
            else:
                await embedMessage.edit(embed=embed)
            embedMessageID = embedMessage.id
            
            raise  
        
        embedMessage = discord.utils.get(await Curchannel.history(limit=100).flatten() , id = embedMessageID)
        # print(embedMessage)
        if embedMessage is None:
            await clearServerstatus(client)
            embedMessage = await Curchannel.send(embed=embed)
        else:
            await embedMessage.edit(embed=embed)
        embedMessageID = embedMessage.id
        
        global PingMessage
        if (len(PlayerList) > 3):
            if PingMessage is None:
                PingMessage = await Curchannel.send(f"{pinged.mention} 4 Pelaajan raja on täyttynyt, hyppää palvelimelle!")
        elif PingMessageID is not None:
            PingMessage = discord.utils.get(await Curchannel.history(limit=100).flatten() , id = PingMessageID)
            await PingMessage.delete()
            PingMessage = None
        
        # add check if noting has changed
        script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
        rel_path = "GorillaData.txt"
        abs_file_path = os.path.join(script_dir, rel_path)
        f = open(abs_file_path, "w")
        
        # save ping message if message was posted
        if (PingMessage is None):
            f.write(f"{Curchannel.id},{embedMessage.id}")
        else:
            f.write(f"{Curchannel.id},{embedMessage.id},{PingMessage.id}")
        f.close()
        return embedMessage
