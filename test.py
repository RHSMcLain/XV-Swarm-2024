import tkinter as tk
from collections import deque

class GlowButton(tk.Button):
    def __init__(self, master, **kwargs):
        tk.Button.__init__(self, master, **kwargs)
        #store background color
        self.bg_idle = self.cget('background')
        
        #list of glow colors to cycle through
        self.colors    = ['#aa88aa', '#aa99aa', '#aaaaaa', '#aabbaa', '#aaccaa', '#aaddaa', '#aaeeaa', '#aaffaa']
        #deque to use as an offset
        self.col_index = deque(range(len(self.colors)))
        #eventual reference to after
        self.glow      = None
        
        #add MouseOver, MouseOut events
        self.bind('<Enter>', lambda e: self.__glow(True))
        self.bind('<Leave>', lambda e: self.__glow(False))
        
    def __glow(self, hover):
        if hover:
            #get rotation offset
            ofs = self.col_index.index(0)
            #apply color from rotation offset
            self.configure(background=self.colors[ofs])
            #if the offset has not reached the end of the color list
            if ofs != len(self.colors)-1:
                #rotate
                self.col_index.rotate(1)
                #do all of this again in 50ms
                self.glow = self.after(50, self.__glow, hover)
        else:
            #kill any expected after
            self.after_cancel(self.glow)
            #rewind
            self.col_index.rotate(-self.col_index.index(0))
            #reset to idle color
            self.configure(background=self.bg_idle)

        
root = tk.Tk()
GlowButton(root, text='button', font='Helvetica 10 bold', bg='#aa88aa').grid()

if __name__ == '__main__':
    root.mainloop()