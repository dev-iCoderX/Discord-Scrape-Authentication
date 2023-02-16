from getmessage import GetMessageToDB, GetNewestMessage
from sendmessage import SendMessage
from datetime import datetime, timedelta
from config import *

#Read file and Setup
with open(path, "r") as f:
    lines = f.read()
rawLine = lines.split("\n")
linesData = []
for r in rawLine:
    linesData.append(r.split("|"))
firstRun = True
limitTimestamp = limitDate
#Get next time to run
if runBy == "day":
    theNext = datetime.timestamp(datetime.today()+ timedelta(days=1))
elif runBy == "hour":
    theNext = datetime.timestamp(datetime.today()+ timedelta(hours=1))
now = datetime.timestamp(datetime.now())
#Loop
while True:
    now = datetime.timestamp(datetime.now())
    if now >= theNext or firstRun:
        if runBy == "day":
            theNext = datetime.timestamp(datetime.today()+ timedelta(days=1))
        elif runBy == "hour":
            theNext = datetime.timestamp(datetime.today()+ timedelta(hours=1))
        for line in linesData:
            #Add time of last message for each channel
            if firstRun:
                line.append(GetNewestMessage(privateKey, line[3]))
            else:
                line[4] = GetNewestMessage(privateKey, line[3])
                limitTimestamp = line[4]
            #Update data to database
            allData = GetMessageToDB(mongodb, dbName, dbColum, privateKey, line[0], line[1], line[2], line[3], limitTimestamp)
            #Send a message to your own channel and the first time you run the script it just updates the database but doesn't send the message
            if not firstRun:
                SendMessage(allData, ownChannelID, botToken)
        if firstRun:
            firstRun = False
        nextRunString = datetime.fromtimestamp(theNext).strftime('%d-%m-%Y %H:%M:%S')
        print(nextRunString)