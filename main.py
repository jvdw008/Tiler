# Tiler is an image slicing tool. It takes an image, allows you to choose how many tiles you want the image to be cut into. 
# It also lets you choose to recombine the slices into spritesheets. This is handy for game makers who can grab pixel art/animations and import them easily.

from tkinter import *
from PIL import ImageTk,Image
from tkinter import filedialog
import tkinter.messagebox
import math
import sys, os
from os import *
from os.path import isfile, join
import hashlib
import time

class Tiler(Frame):

    def __init__(self):
        super().__init__()

        self.setup()

    def setup(self):
        self.version = 1.0

        self.master.title("Tiler -V." + str(self.version))
        self.master.iconbitmap(self.resource_path("tiler_logo.ico"))

        self.scrollbar = Scrollbar(self.master)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.stepStatus = 0
        self.checkBoxVal = IntVar()
        self.checkBoxVal.set(1)
        self.checkboxText = "Check for duplicates"
        self.makeSheetsVal = IntVar()
        self.makeSheetsVal.set(1)
        self.makeSheetsText = "Make spritesheet(s)"
        self.statusText = StringVar()
        self.statusText.set("Welcome to Tiler -V." + str(self.version))
        self.strPath = "c:/"
        self.rootPath = StringVar()
        self.rootPath.set(self.strPath)
        self.fileName = StringVar()
        self.fileName.set("No file")
        self.fullFileNameAndPath = ""
        self.howManyTiles = StringVar()
        self.howManyTiles.set("How many tiles per row?")
        self.newWidth = 400
        self.duplicatedHashList = []
        self.spriteSheetFiles = []                           # Create a list of files for new spritesheet
        self.sliceFolderName = ""
        self.hidden = False                                  # Show/hide option for log label

        # Instantiate a menu
        self.menu = Menu(self.master)
        self.master.config(menu=self.menu)

        # Create sub menus
        self.subMenu = Menu(self.menu, tearoff=0) # tearoff stops menu from floated

        # Attach the submenu to the main menu
        self.menu.add_cascade(label="File", menu=self.subMenu)

        # Now add first sub menu options
        self.subMenu.add_command(label="Open Image", command=self.openDialog)
        self.subMenu.add_command(label="About", command=self.about)
        self.subMenu.add_separator()
        self.subMenu.add_command(label="Quit", command=self.quitApp)

        # Add a toolbar
        self.toolbar = Frame(self.master)

        # Add buttons for the frame
        self.openBtnImg = PhotoImage(file=self.resource_path("tiler-open.png"))
        self.btn01 = Button(self.toolbar, text="Open Image", image=self.openBtnImg, compound="left", command=self.openDialog)
        # Attach this button to the toolbar with padding
        self.btn01.pack(side=LEFT, padx=20, pady=2)

        # Show file name
        self.fileLabel = Label(self.toolbar, textvariable=self.fileName, fg="green", borderwidth=2, relief="groove")
        self.fileLabel.pack(side=LEFT, padx=10, pady=2)

        # Add input
        self.inputLabel = Label(self.toolbar, textvariable=self.howManyTiles)
        self.inputLabel.pack(side=LEFT, padx=2, pady=2)
        self.inputBox = Entry(self.toolbar, width=4)
        self.inputBox.insert(0, 16)
        self.inputBox.pack(side=LEFT, padx=20, pady=2)

        # Max width for new spritesheet
        self.maxWidthLabel = Label(self.toolbar, text="Spritesheet max width (px):")
        self.maxWidthLabel.pack(side=LEFT, padx=20, pady=2)

        # Max width input
        self.maxWidthInputBox = Entry(self.toolbar, width=4)
        self.maxWidthInputBox.insert(0, 256)
        self.maxWidthInputBox.pack(side=LEFT, padx=10, pady=2)

        # Checkbox for duplicates
        self.checkBtn = Checkbutton(self.toolbar, text=self.checkboxText, variable=self.checkBoxVal, onvalue=1, offvalue=0)
        self.checkBtn.pack(side=LEFT, padx=10, pady=2)

        # Make spritesheets
        self.makeSheetsBtn = Checkbutton(self.toolbar, text=self.makeSheetsText, variable=self.makeSheetsVal, onvalue=1, offvalue=0)
        self.makeSheetsBtn.pack(side=LEFT, padx=10, pady=2)

        # Add buttons for the frame
        self.splitBtnImg = PhotoImage(file=self.resource_path("tiler-split.png"))
        self.btn02 = Button(self.toolbar, text="Split!", image=self.splitBtnImg, compound="left", command=self.splitImage)
        self.btn02.pack(side=LEFT, padx=20, pady=4)

        # Show/hide log
        self.showHideLogImg = PhotoImage(file=self.resource_path("tiler-showhide.png"))
        self.showHideLogBtn = Button(self.toolbar, text="Show/Hide Log", image=self.showHideLogImg, compound="left", command=self.showLog)
        self.showHideLogBtn.pack(side=RIGHT, padx=8, pady=2)

        # Clear log text box
        self.logBtnImg = PhotoImage(file=self.resource_path("tiler-log.png"))
        self.logBtn = Button(self.toolbar, text="Clear All", image=self.logBtnImg, compound="left", command=self.clearLog)
        self.logBtn.pack(side=RIGHT, padx=2, pady=2)

        # Now attach the toolbar to the window with full width
        self.toolbar.pack(side=TOP, fill=X)

        # Large textarea box for log
        self.progressText = Text(self.master, width=90, yscrollcommand=self.scrollbar.set)
        self.progressText.pack(side=RIGHT, fill=Y)

        # Add a status bar with a border, sunken look and aligned left
        self.status = Label(self.master, textvariable=self.statusText, bd=1, relief=SUNKEN, anchor=W)

        # Atta this to the main window full width
        self.status.pack(side=BOTTOM, fill=X)

    # Use this for the images to work with exe or dev
    def resource_path(self, relative_path):
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            self.base_path = sys._MEIPASS
        except Exception:
            self.base_path = os.path.abspath(".")

        return os.path.join(self.base_path, relative_path)

    # Confirm popup
    def areYouSure(self, title, content):
        self.msgBox = tkinter.messagebox.askquestion(title, content, icon="warning")
        if (self.msgBox == "yes"):
            return True
        else:
            return False

    # Delete files in a given folder
    def deleteFiles(self, thePath):
        for root, dirs, files in os.walk(thePath):
            for file in files:
                os.remove(os.path.join(root, file))

    # Get file
    def openDialog(self):
        self.strPath = ""
        self.fullFileNameAndPath = ""
        self.master.filename = filedialog.askopenfilename(initialdir=self.rootPath, title="Select an image", filetypes=(("gif files", "*.gif"),("png files", "*.png"),("jpg files", "*.jpg"),("All files", "*.*")))
        self.clearLog()

        # Take the filename and show the image
        if (self.master.filename != ""):
            self.fullFileNameAndPath = self.master.filename
            self.tmpPath = self.master.filename.split("/")
            self.newPath = self.tmpPath[:-1]

            # Store the new path as the default
            if (self.strPath != self.newPath):
                self.strPath = self.concatPath(self.newPath)
                self.rootPath.set(self.strPath)

            # Show name
            self.fileName.set(self.tmpPath[len(self.tmpPath) - 1])

            # Show the image
            self.load = Image.open(self.master.filename)
            self.newHeight = int(self.load.height * (self.newWidth / self.load.width))
            self.newSize = (self.newWidth, self.newHeight)
            self.newImg = self.load.resize(self.newSize)
            self.render = ImageTk.PhotoImage(self.newImg)

            # Delete instance of image if already exists
            if (len(self.master.winfo_children()) == 6):
                self.master.winfo_children()[5].destroy()
            self.img = Label(self.master, image=self.render)
            self.img.image = self.render
            self.img.pack(side=LEFT, padx=20, pady=20)


    # The main function
    def splitImage(self):
        self.tmpFile = self.fileName.get()
        self.spriteSheetVal = self.maxWidthInputBox.get()
        self.totalTiles = 0
        self.duplicatedHashList = []

        if (int(self.spriteSheetVal) <= 0):
            self.statusText.set("No spritesheet size!")
            return

        if (self.tmpFile == "" or self.tmpFile == "No file"):
            self.statusText.set("No file selected!")
        else:
            self.file = self.tmpFile.split(".")
            self.statusText.set("")

            # Check for duplicates?
            self.chkDupes = self.checkBoxVal.get()

            # Make dir of file name
            self.tmpDir = os.path.join(self.strPath, self.file[0])
            self.sliceFolderName = self.tmpDir
            try:
                os.mkdir(self.tmpDir)
            except:
                if(self.areYouSure("Existing files in folder " + self.file[0], "Are you sure you want to delete the files in folder " + self.tmpDir + "?")):
                    self.deleteFiles(self.tmpDir)
                    self.statusText.set("Deleted files in folder " + self.file[0])
                else:
                    self.statusText.set("Image slicing cancelled")
                    return

            # now the file
            if (self.fullFileNameAndPath != ""):

                # Load original image
                self.ogload = Image.open(self.fullFileNameAndPath)
                # Now convert to 8 bit
                self.load = self.ogload.convert("P")

                self.startX = 0
                self.startY = 0
                self.imgWidth, self.imgHeight = self.load.size

                self.tileSize = int(self.inputBox.get())

                if (self.tileSize > 64):
                    self.tileSize = 64
                if (self.tileSize <= 0):
                    return
                # Set pixels width/height for each tile based on image and pixel tile size
                self.pixelsPerTileX = math.floor(self.imgWidth / self.tileSize)
                self.pixelsPerTileY = math.floor(self.imgHeight / self.tileSize)
                self.boundWidth = self.pixelsPerTileX
                self.boundHeight = self.pixelsPerTileY
                self.progressText.insert(INSERT, "Output (" + str(self.pixelsPerTileX) + "px per tile):\n")

                #now split them!
                for y in range(self.tileSize):
                    for x in range(self.tileSize):
                        self.boundingBox = (self.startX, self.startY, self.startX + self.boundWidth, self.startY + self.boundWidth)
                        self.workingSlice = self.load.crop(self.boundingBox)
                        self.progressText.insert(END, self.file[0] + "_" + str(x) + "_" + str(y) + ":")
                        self.progressText.insert(END, "left: " + str(self.startX) + " upper: " + str(self.startY) + " right: " + str(self.startX + self.boundWidth) + " lower: " + str(self.startY + self.boundWidth) + "\n")

                        # Filename
                        self.fn = os.path.join(self.tmpDir, self.file[0] + "_" + str(x) + "_" + str(y) + ".png")

                        # MD5 of file
                        self.md5 = hashlib.md5(self.workingSlice.tobytes())
                        self.exists = False

                        # Save file if not a duplicate
                        for hash in range(len(self.duplicatedHashList)):
                            if (self.chkDupes == 1):
                                if (self.md5.hexdigest() == self.duplicatedHashList[hash]):
                                    self.progressText.insert(END, "Hash " + self.md5.hexdigest() + " already exists. SKIPPING.\n\n")
                                    self.exists = True
                                    break

                        if (not self.exists):
                            self.workingSlice.save(self.fn)
                            self.totalTiles += 1

                            if (self.chkDupes == 1):
                                # Add to hash list
                                self.duplicatedHashList.append(self.md5.hexdigest())
                                # Add to sprite sheet file list
                                self.spriteSheetFiles.append([self.fn, self.boundWidth, self.boundWidth])

                            self.progressText.insert(END, "md5: " + self.md5.hexdigest() + "\n\n")

                        self.scrollbar.config(command=self.progressText.yview)

                        self.startX += self.pixelsPerTileX

                        if (self.startX + self.pixelsPerTileX <= self.imgWidth):
                            self.boundWidth = self.pixelsPerTileX
                        else:
                            self.boundWidth = self.imgWidth - self.startX - 1

                    self.startX = 0
                    self.boundWidth = self.pixelsPerTileX
                    self.startY += self.pixelsPerTileX #pixelsPerTileY

                    if (self.startY + self.pixelsPerTileY <= self.imgHeight):
                        self.boundHeight = self.pixelsPerTileY
                    else:
                        #boundHeight = imgHeight - startY - 1
                        break

                self.statusText.set("Slicing done!")

                self.progressText.insert(END, "Total tiles: " + str(self.totalTiles) + "\n\n")

                # Now make spritesheet
                if (self.makeSheetsVal.get() == 1):
                    self.progressText.insert(END, "Making spritesheets...\n")
                    self.progressText.see("end")
                    self.newSpriteSheet()
                else:
                    self.progressText.insert(END, "DONE\n")
                    self.progressText.see("end")

        return

    # Split one long array into multiple smaller ones
    def split(self, arr, size):
         self.arrs = []
         while len(arr) > size:
             self.pice = arr[:size]
             self.arrs.append(self.pice)
             arr = arr[size:]
         self.arrs.append(arr)
         return self.arrs

    # Create spritesheet
    def newSpriteSheet(self):
        time.sleep(1)
        self.x = 0
        self.index = 0
        self.imageFiles = [f for f in listdir(self.sliceFolderName)]
        self.maxSheetWidth = int(self.maxWidthInputBox.get())
        self.tileSizeTotal = int(self.inputBox.get())

        for i in range(len(self.imageFiles)):
            self.imageFiles[i] = os.path.join(self.sliceFolderName, self.imageFiles[i])

        self.tmpSheets = self.split(self.imageFiles, self.tileSizeTotal)

        for i in range(len(self.tmpSheets)):
            self.images = [Image.open(pic) for pic in self.tmpSheets[i]]
            self.w, self.h = zip(*(i.size for i in self.images))
            self.totalWidth = sum(self.w)
            self.maxHeight = max(self.h)

            self.newImg = Image.new("RGB", (self.totalWidth, self.maxHeight))
            self.x_offset = 0
            for img in self.images:
                self.newImg.paste(img, (self.x_offset, 0))
                self.x_offset += img.size[0]

            self.newImg.save(os.path.join(self.sliceFolderName, "sheet" + str(self.index) + ".png"))

            self.index += 1

        self.progressText.insert(END, "Total sheets: " + str(self.index) + "\n\n")
        self.progressText.insert(END, "DONE\n")
        self.progressText.see("end")

    # Join path variables
    def concatPath(self, listItems):
        self.strTmp = ""
        for i in listItems:
            self.strTmp += i + "/"

        return self.strTmp

    # Show or hide text area log
    def showLog(self):
        if (self.hidden == True):
            self.hidden = False
            self.progressText.pack(side=RIGHT, fill=Y)

        else:
            self.hidden = True
            self.progressText.pack_forget()

    # Clear text area
    def clearLog(self):
        self.progressText.delete(1.0,END)
        self.strPath = "c:/"
        self.rootPath.set(self.strPath)
        self.fileName.set("No file")
        self.fullFileNameAndPath = ""
        self.duplicatedHashList = []
        self.spriteSheetFiles = []                           # Create a list of files for new spritesheet
        self.sliceFolderName = ""

    # Message box
    def about(self):
        tkinter.messagebox.showinfo("About", "Tiler V." + str(self.version) + " by Blackjet in 2020")

    # Quit
    def quitApp(self):
        self.master.destroy()

def main():

    root = Tk()
    root.geometry("1300x500")

    app = Tiler()
    root.mainloop()

if __name__ == '__main__':
    main()