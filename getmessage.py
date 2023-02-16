import pymongo
import cfscrape, json
from time import sleep
import datetime

  
def GetTimestamp(strTimestamp):
    element = datetime.datetime.strptime(strTimestamp,"%Y-%m-%dT%H:%M:%S.%f%z")
    return datetime.datetime.timestamp(element)

def ConvertDatabase(messages, serverName, serverID, channelName, channelID, limitDate):
    newDB = []
    status = True
    for m in messages:
        messageTimestamp = GetTimestamp(m["timestamp"])
        if messageTimestamp >= limitDate:
            newDB.append({
                "server_name": serverName,
                "server_id": serverID,
                "channel_name": channelName,
                "channel_id": channelID,
                "sender": m["author"]["username"],
                "sender_id": m["author"]["id"],
                "message": m["content"],
                "quote_message_sender":  m["referenced_message"]["author"]["username"],
                "quote_message_sender_id": m["referenced_message"]["author"]["id"],
                "quote_message": m["referenced_message"]["content"],
                "datetime": m["timestamp"]
            })
        else:
            status = False
            break
    return status, newDB



def GetMessageToDB(mongodb, dbName, dbColum, privateKey, serverName, serverID, channelName, channelID, limitDate):
    myClient = pymongo.MongoClient(mongodb)
    print(myClient.list_database_names())
    mydb = myClient[dbName] #Your Database Name
    mycol = mydb[dbColum]     #Your Column Name

    rq = cfscrape.create_scraper()
    url = f"http://discord.com/api/v9/channels/{channelID}/messages" #API to your channel
    headers ={
        "authorization": privateKey
    }
    r = rq.get(f"{url}?limit=100", headers=headers)
    messages = json.loads(r.content.decode('utf-8')) #Get last 100 Messages

    allData = []
    status, needed = ConvertDatabase(messages, serverName, serverID, channelName, channelID, limitDate)
    mycol.insert_many(needed)
    last = messages[-1]["id"]
    hasDone = 100
    allData += needed
    print("Done: ",hasDone)

    while len(messages)>0:
        r = rq.get(f"{url}?before={last}&limit=100", headers=headers) #Get last 100 Messages before the first one of last 100 messages
        messages = json.loads(r.content.decode('utf-8'))
        hasDone += len(messages)
        print("Done: ",hasDone)
        try:
            last = messages[-1]["id"]
            status ,needed = ConvertDatabase(messages, serverName, serverID, channelName, channelID, limitDate)
            mycol.insert_many(needed) #Insert to Database
            allData += needed
            if not status:
                break
            sleep(0.1)
        except:
            break
    return allData

def GetNewestMessage(privateKey, channelID):
    rq = cfscrape.create_scraper()
    url = f"http://discord.com/api/v9/channels/{channelID}/messages" #API to your channel
    headers ={
        "authorization": privateKey
    }
    r = rq.get(f"{url}?limit=100", headers=headers)
    messages = json.loads(r.content.decode('utf-8')) #Get last 100 Messages
    return GetTimestamp(messages[0]["timestamp"])