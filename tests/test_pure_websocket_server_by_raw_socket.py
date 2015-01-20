# coding: utf-8

import socket

# coding:utf-8
# 實作 HTTP Daemon

import socket,re,sys
import hashlib,base64
import threading,binascii
import struct
import time

def web_socket_handle(con):
    # WebSocket Handle
    data=con.recv(1024);print data

    # handler
    sha1=hashlib.sha1()
    host=re.findall('Host:.*?([A-z0-9].*?)\r\n',data)[0]
    key=re.findall('Sec-WebSocket-Key:.*?([A-z0-9].*?)\r\n',data)[0]
    sha1.update(key+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11')
    SWSA=base64.b64encode(sha1.digest())

    # Response
    con.send('HTTP/1.1 101 Switching Protocols\r\n')
    con.send('Upgrade: websocket\r\n')
    con.send('Connection: Upgrade\r\n')
    con.send('Sec-WebSocket-Accept: '+SWSA+'\r\n')
    con.send('Sec-WebSocket-Origin: null\r\n\r\n')
    # con.send('Sec-WebSocket-Location: ws://'+host+'/\r\n\r\n')

# 處裡接收資料
def web_socket_data_frame_recv_processor(con):
    # 先啟動一個回應中心
    threading.Thread(target=server_push_processor,args=(con,)).start()

    while True:
        # 讓 Buffer 大一點可以一次處裡比較大的 Client Send Data Frame, Python 最大也只能到 32768 Bytes
        data=con.recv(32768)
        if(len(data)==0):
            # 當 Client 斷線的時候, con.recv(1024) 會 non-blocking 並返回 nil
            break
        else:
            # 將 Bytes 或 String 轉換為 16 進為編碼文字
            print data.encode('hex')

            # Payload Size
            payloadSize=int(data[1].encode('hex'),16) & 0b01111111
            print payloadSize,len(data)
            if payloadSize == 126:          # 126 bytes 至 65535 bytes：會以「111 1110」即「126」表示，並指示下兩個 byte 後才載有實際的內容長度
                masks = data[4:8]           # 簡單來說就是 Payload Len 將延長 2 個 Byte ( ...|payload size|extend payload length 2 Bytes|data frame|... )
                pData = data[8:]
            elif payloadSize == 127:        # 65536 bytes 至 2^64 - 1 bytes：會以「111 1111」即「127」表示，並指示下八個 bytes 後才載有實際的內容長度
                masks = data[10:14]         # 簡單來說就是 Payload Len 將 Extend 額外 8 個 Byte ( ...|payload size|extend payload length 8 Bytes|data frame|... )
                pData = data[14:]
            else:                           # 0 byte 至 125 bytes：會以 000 0000 至 111 1101 表示，並代表下一個 byte 即為 frame 內容的開始
                masks = data[2:6]           # 簡單來說就是 Payload Len 將 Extend 額外 8 個 Byte ( ...|payload size|data frame|... )
                pData = data[6:]
            
            # 使用 Mask 解析出文字, ord() 取一個Byte的 ANSCII 十進位
            raw_str = ""
            i=0
            for d in pData:
                raw_str+=chr(ord(d) ^ ord(masks[i%4])) # chr(Number) 取 ANSCII (0~255), 基本上在組 Bytes
                i+=1
            print raw_str.decode('utf-8')

    con.close() # WebSocket 不關閉

# 處理發送資料
def web_socket_data_frame_send_processor(pData,con):
    if(pData == False):
        return False
    else:
        pData = str(pData)  
    token = "\x81"
    length = len(pData)
    if length < 126:
        token += struct.pack("B", length)
    elif length <= 0xFFFF:
        token += struct.pack("!BH", 126, length)
    else:
        token += struct.pack("!BQ", 127, length)
    pData = '%s%s' % (token,pData)
    con.send(pData)
    return True

# Server Push Center
def server_push_processor(con):
    while True:
        web_socket_data_frame_send_processor('我收到了!',con)
        time.sleep(1)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("127.0.0.1", 8888))
sock.listen(10)

while True:
    print 'wait...'
    con, address = sock.accept()
    print 'connected a client...'
    try:
        # 因為要避免 con 斷線的時候 host send client 拋錯
        print con, address

        # WebSocket 通信協定實作
        web_socket_handle(con)

        # 建立一個 Thread 來處理這個 WebSocket 以免被下一個連線變數名稱給取代了
        threading.Thread(target=web_socket_data_frame_recv_processor,args=(con,)).start()
    except:
        pass

sock.close()
