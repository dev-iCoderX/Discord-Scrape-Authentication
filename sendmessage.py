import discord


def SendMessage(allData, channelID, botToken):
    client = discord.Client(intents=discord.Intents.default())
    @client.event
    async def on_ready():
        dm = client.get_channel(channelID)
        count = 0
        message = ""
        for a in allData:
            count += 1
            if count < 10:
                message+= f"\n```{a['sender']}: {a['message']}```"
            else:
                await dm.send(message)
                count = 0
                message = ""
        if count != 0:
            await dm.send(message)
            count = 0
            message = ""
        print('------')
        await client.close()
    client.run(botToken)