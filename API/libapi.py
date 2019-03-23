#!/usr/bin/python3
# -*- coding: latin-1 -*-
import sys, posix, time, binascii, socket, select
import hashlib

class ApiRos:
    "Routeros api"
    def __init__(self, sk):
        self.sk = sk
        self.currenttag = 0

    def login(self, username, pwd):
        for repl, attrs in self.talk(["/login", "=name=" + username,
                                      "=password=" + pwd]):
          if repl == '!trap':
            print("    Authentication: failed")
            return False
          elif '=ret' in attrs.keys():
        #for repl, attrs in self.talk(["/login"]):
            chal = binascii.unhexlify((attrs['=ret']).encode(sys.stdout.encoding))
            md = hashlib.md5()
            md.update(b'\x00')
            md.update(pwd.encode(sys.stdout.encoding))
            md.update(chal)
            for repl2, attrs2 in self.talk(["/login", "=name=" + username,
                   "=response=00" + binascii.hexlify(md.digest()).decode(sys.stdout.encoding) ]):
              if repl2 == '!trap':
                print("    Authentication: failed")
                return False
        print("    Authentication: done")
        return True

    def talk(self, words):
        if self.writeSentence(words) == 0: return
        r = []
        while 1:
            i = self.readSentence();
            if len(i) == 0: continue
            reply = i[0]
            attrs = {}
            for w in i[1:]:
                j = w.find('=', 1)
                if (j == -1):
                    attrs[w] = ''
                else:
                    attrs[w[:j]] = w[j+1:]
            r.append((reply, attrs))
            if reply == '!done': return r

    def writeSentence(self, words):
        ret = 0
        for w in words:
            self.writeWord(w)
            ret += 1
        self.writeWord('')
        return ret

    def readSentence(self):
        r = []
        while 1:
            w = self.readWord()
            if w == '': return r
            r.append(w)

    def writeWord(self, w):
        #print(("<<< " + w))
        self.writeLen(len(w))
        self.writeStr(w)

    def readWord(self):
        ret = self.readStr(self.readLen())
        #print((">>> " + ret))
        return ret

    def writeLen(self, l):
        if l < 0x80:
            self.writeByte((l).to_bytes(1, sys.byteorder))
        elif l < 0x4000:
            l |= 0x8000
            tmp = (l >> 8) & 0xFF
            self.writeByte(((l >> 8) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte((l & 0xFF).to_bytes(1, sys.byteorder))
        elif l < 0x200000:
            l |= 0xC00000
            self.writeByte(((l >> 16) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte(((l >> 8) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte((l & 0xFF).to_bytes(1, sys.byteorder))
        elif l < 0x10000000:
            l |= 0xE0000000
            self.writeByte(((l >> 24) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte(((l >> 16) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte(((l >> 8) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte((l & 0xFF).to_bytes(1, sys.byteorder))
        else:
            self.writeByte((0xF0).to_bytes(1, sys.byteorder))
            self.writeByte(((l >> 24) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte(((l >> 16) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte(((l >> 8) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte((l & 0xFF).to_bytes(1, sys.byteorder))

    def readLen(self):
        c = ord(self.readStr(1))
        # print (">rl> %i" % c)
        if (c & 0x80) == 0x00:
            pass
        elif (c & 0xC0) == 0x80:
            c &= ~0xC0
            c <<= 8
            c += ord(self.readStr(1))
        elif (c & 0xE0) == 0xC0:
            c &= ~0xE0
            c <<= 8
            c += ord(self.readStr(1))
            c <<= 8
            c += ord(self.readStr(1))
        elif (c & 0xF0) == 0xE0:
            c &= ~0xF0
            c <<= 8
            c += ord(self.readStr(1))
            c <<= 8
            c += ord(self.readStr(1))
            c <<= 8
            c += ord(self.readStr(1))
        elif (c & 0xF8) == 0xF0:
            c = ord(self.readStr(1))
            c <<= 8
            c += ord(self.readStr(1))
            c <<= 8
            c += ord(self.readStr(1))
            c <<= 8
            c += ord(self.readStr(1))
        return c

    def writeStr(self, str):
        n = 0;
        while n < len(str):
            r = self.sk.send(bytes(str[n:], 'UTF-8'))
            if r == 0: raise RuntimeError("connection closed by remote end")
            n += r

    def writeByte(self, str):
        n = 0;
        while n < len(str):
            r = self.sk.send(str[n:])
            if r == 0: raise RuntimeError("connection closed by remote end")
            n += r

    def readStr(self, length):
        ret = ''
        # print ("length: %i" % length)
        while len(ret) < length:
            s = self.sk.recv(length - len(ret))
            if s == b'': raise RuntimeError("connection closed by remote end")
            # print (b">>>" + s)
            # atgriezt kaa byte ja nav ascii chars
            if s >= (128).to_bytes(1, "big") :
               return s
            # print((">>> " + s.decode(sys.stdout.encoding, 'ignore')))
            ret += s.decode(sys.stdout.encoding, "replace")
        return ret

def socketOpen(ip, port="8728"):
    s = None
    
    for res in socket.getaddrinfo(ip, port, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        try:
             s = socket.socket(af, socktype, proto)
        except (socket.error, msg):
            s = None
            continue
        try:
            s.connect(sa)
        except (socket.error, msg):
            s.close()
            s = None
            continue
        break

    if s is None:
        print ('    Socket open: failed')
        sys.exit(1)

    print('    Socket open: done')
    return s

def socketClose(socket):
    print("    Socket closed: done")
    socket.close()
    
def readResponse(api):
    res_list = []
    while 1:
        response = api.readSentence()
        if response[0] != '!done':
            res_list.append(response)
            #print("    ", end='')
            #print(response)
        else:
            print("    Command complete: done")
            break
    return res_list

