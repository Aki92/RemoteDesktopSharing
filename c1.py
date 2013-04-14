from PIL import ImageGrab
from subprocess import *
from Tkinter import *
from socket import *
import win32api, win32con
import Image, ImageTk
import thread
import os

PORT = 5025
LPORT = PORT + 10
liveuser = []
cflag = 0
    
#recieving msg from live nodes in network
def recieve():
    global liveuser
    #checking till Tk window is not closed
    while cflag != 1:
        try:
            msg,addr = slive.recvfrom(1024)
            if msg == 'yes':
                #Label(root,text = gethostbyaddr(addr[0])+" is live").pack(side=TOP)
                print gethostbyaddr(addr[0])+" is CONNECTED"
            elif msg == 'live':
                slive.sendto('yes',addr)
                #Label(root,text = gethostbyaddr(addr[0])+" is live").pack(side=TOP)
                print gethostbyaddr(addr[0])+" is CONNECTED"
                liveuser.append(gethostbyaddr(addr[0]))
            elif msg == 'going':
                print gethostbyaddr(addr[0])+" has GONE"
                liveuser.remove(gethostbyaddr(addr[0]))
        except:
            continue

#check for systems running same soft.   
def connected():
    global liveuser
    #Label(node,text = gethostname()+" is live").pack(side=TOP)
    call('net view > conn.tmp', shell=True)
    f = open('conn.tmp', 'r')
    if f.readline()[0]=='S':
        f.readline();f.readline()
        host = f.readline()
        while host[0] == '\\':
            liveuser.append(host[2:host.find(' ')])
            host = f.readline()
        print liveuser
        liveuser.remove(gethostname().upper())
        print liveuser
        for i in liveuser:
            slive.sendto("live",(i,LPORT))
    f.close()

'''
def livenodes():    
    #GUI to show connected users
    live = Tk()
    live.title(string = "po")
    live.geometry("200x200")
    live.mainloop()
'''

print '''
Press * 1 * to work as *SERVER*
Press * 2 * to work as *CLIENT*
Press * 3 * to EXIT

Enter your Choice: ''',
choice = raw_input()

if choice == '1':
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(("", PORT))
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.listen(1)

    #socket for checking live nodes
    slive = socket(AF_INET, SOCK_DGRAM)
    slive.bind(("", LPORT))
    
    def main():
        global cflag
        #starting thread for accepting msg from live nodes
        thread.start_new_thread(recieve,())
        #sending msg to all nodes connected
        connected()
        #main code
        conn,addr = sock.accept()
        print gethostname() + ' Connected by: ',gethostbyname(addr[0])
        while True:
            try:
                #taking screenshot
                ImageGrab.grab().save("images\\img1.jpg", "JPEG")
                #sending image to client
                fp = open("images\\img1.jpg","rb")
                data = fp.read()
                fp.close()
                conn.sendall(data)
                #recieving mouse coordinates or keypressed
                rec = conn.recv(1024)
                while rec != "start":
                    if '~' in rec:
                        lr = rec[0]
                        rec = rec[1:]
                        x,y = map(int, rec.split('~'))
                        #mouse pos. set nd single click done
                        win32api.SetCursorPos((x,y))
                        if lr == 'l':
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
                        elif lr == 'r':
                            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,x,y,0,0)
                            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,x,y,0,0)
                    elif rec == 'close':
                        cflag = 1
                        break
                    elif rec:
                        keypress = int(rec)
                        #particular key pressed
                        win32api.keybd_event(keypress,0,0,0)
                    rec = conn.recv(1024)
            except:
                continue
            if cflag == 1:
                break

    main()
    for i in liveuser:
        slive.sendto("going",(i,LPORT))
    sock.close()

elif choice == '2':
    host = ("localhost",PORT)
    sock = socket(AF_INET,SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1) 
    #socket for checking live nodes
    slive = socket(AF_INET, SOCK_DGRAM)
    #connecting with server
    sock.connect(host)
    
    def start():
        #mouse is clicked
        def leftclick(event):
            #outputting x and y coords to console
            x = event.x
            y = event.y
            sock.send('l' + str(x) + '~' + str(y))
            #root.quit()

        def rightclick(event):
            #outputting x and y coords to console
            x = event.x
            y = event.y
            sock.send('r' + str(x) + '~' + str(y))
            #root.quit()

        #key is pressed
        def key(event):
            keypress = event.keycode
            sock.send(str(keypress))
            #root.quit()

        def image():
            root.quit()    

        try:
            #adding the image
            img = Image.open(os.getcwd()+'\\downloads\\img1.jpg')
            img = img.resize((root.winfo_screenwidth(),root.winfo_screenheight()-50),Image.ANTIALIAS)
            img = ImageTk.PhotoImage(img)
            label.config(image = img)
            
            #mouseclick and keyboard event
            label.bind("<Button-1>",leftclick)
            label.bind("<Button-3>",rightclick)
            label.bind("<Key>", key) 
            label.pack()
            root.focus_set()
            label.focus_set()
            
            #updating img after every 3 sec.
            root.after(2000,image)
            root.mainloop()
            return 0
        except:
            return 1

    #image display gui
    root = Tk()
    root.geometry("%dx%d"%(root.winfo_screenwidth(), root.winfo_screenheight()-50))
    label = Label(root)

    def main():
        #starting thread for accepting msg from live nodes
        thread.start_new_thread(recieve,())
        #sending msg to all nodes connected 
        connected()        
        while True:
            msg = sock.recv(256456)
            data = msg
            #writing image file
            fp = open("downloads\\img1.jpg","wb")
            fp.write(data)
            fp.close()
            if start() == 0:
                #sending new start msg
                sock.send("start")
            else:
                sock.send("close")
                break

    main()
    cflag = 1
    for i in liveuser:
        slive.sendto("going",(i,LPORT))
    sock.close()
    
else:
    print 'Thanks for using REMOTE SOFTWARE SHARING'
