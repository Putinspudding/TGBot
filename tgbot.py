import requests
import sqlite3
import time
import datetime
import html5lib
from bs4 import BeautifulSoup
import os
from urllib.request import urlretrieve

def sendMessage(token,cid,text):
    r = requests.get("https://api.telegram.org/bot"+token+"/sendMessage?chat_id="+cid+"&text="+text)

def sendPhoto(token,cid,photo,caption=""):
    #print("https://api.telegram.org/bot"+token+"/sendPhoto?chat_id="+cid+"&photo="+photo+"&caption="+caption)
    r = requests.get("https://api.telegram.org/bot"+token+"/sendPhoto?chat_id="+cid+"&photo="+photo+"&caption="+caption)
    return r.json()

token = "1234567"
conn = sqlite3.connect('memory')
c = conn.cursor()
while True:
    cur = c.execute("SELECT id from update_id")
    local_id = next(cur)[0]
    r = requests.get("https://api.telegram.org/bot"+token+"/getUpdates?limit=1&offset="+local_id)
    if not r.json()['result']:
        time.sleep(1)
        continue
    fjson = r.json()['result'][0]
    update_id = fjson['update_id']
    #print(update_id)
    
    '''
    if update_id < int(local_id):
        time.sleep(1)
        continue
    '''

    if 'message' in fjson:
        message = fjson['message']
    else: 
        message = fjson['edited_message']
    chat = message['chat']
    cid = str(chat['id'])

    if "new_chat_participant" in message:
        sendMessage(token,cid,"欢迎我自己加入群聊")
        final_id = str(update_id+1)
        c.execute("UPDATE update_id set id ="+final_id)
        conn.commit()
        time.sleep(1)
        continue
    if 'text' not in message:
        final_id = str(update_id+1)
        c.execute("UPDATE update_id set id ="+final_id)
        conn.commit()
        time.sleep(1)
        continue
    text = message['text']
    cmd = text.split()[0].split("@")

    if cmd[0] == "/bing":
        date = str(datetime.date.today())
        files = os.listdir('bing')
        if date+".jpg" in files:
            f = open("bing/"+date+".txt","r")
            ff = f.readlines()
            f.close()
            photo = ff[0].split("\n")[0]
            cap = ff[1]
            #print(cap)
            sendPhoto(token,cid,photo,cap)
        else:
            fi = None
            while not fi:
                res = requests.get("https://cn.bing.com")
                soup = BeautifulSoup(res.text,"html5lib")
                fi = soup.find("div",{"id":"bgImgProgLoad"})
            Link = "https://cn.bing.com/"+ fi["data-ultra-definition-src"]
            caption = soup.find("a",{"id":"sh_cp"})['title']
            file_id = sendPhoto(token,cid,Link,caption)['result']['photo'][0]['file_id']
            f = open("bing/"+date+".txt","a")
            f.write(file_id+"\n")
            f.write(caption)
            f.close()
            #c.execute('INSERT INTO bing (time) VALUES('+date+')')
            urlretrieve(Link, "./bing/"+date+".jpg")
    elif cmd[0] == "/history":
        files = os.listdir('bing')
        fileset = {f.split(".")[0] for f in files}
        answer = "目前可供选择的日期有"
        for i in fileset:
            answer += "%0A" + i 
        if text.split()[0] == text:
            sendMessage(token,cid,answer)
        elif text.split()[1] not in fileset:
            reply = "日期不存在/输入错误%0A"+answer
            sendMessage(token,cid,reply)
        else:
            fname = "bing/"+text.split()[1]+".txt"
            f = open(fname,"r")
            ff = f.readlines()
            f.close()
            photo = ff[0].split("\n")[0]
            cap = ff[1]
            sendPhoto(token,cid,photo,cap)
    else:
        #sendMessage(token,cid,text)
        pass
    final_id = str(update_id+1)
    c.execute("UPDATE update_id set id ="+final_id)
    conn.commit()
    time.sleep(0.5)