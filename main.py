from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
import re
import getyarn
from pathlib import Path
import traceback

VERSION_REGEX = re.compile("Minecraft Version: ([\d\w\.]+)", re.IGNORECASE)

CLASS_REGEX = re.compile("CLASS ([\w/]+) ([\w/]+)")
METHOD_REGEX = re.compile("METHOD (\w+) (\w+)")
FIELD_REGEX = re.compile("FIELD (\w+) (\w+)")

MAPPING_MARK_REGEX = re.compile("~\[intermediary-minecraft-[\d\w\.]+-.+]", re.IGNORECASE)

class App:
    def __init__(self, master):
        label = Label(master, text="Minecraft crash report mapper")
        label.pack()

        inputFrame = Frame(master)
        inputFrame.pack()

        self.fileInput = Entry(inputFrame, width=35)
        self.fileInput.pack(fill=X, side=LEFT)
        self.promptFile = Button(
            inputFrame,
            width=8,
            text="Browse",
            command=self.browseForFile
        )
        self.promptFile.pack(fill=X, side=RIGHT)

        buttonFrame = Frame(master)
        buttonFrame.pack()

        self.button = Button(
            buttonFrame,
            text="QUIT",
            fg="red",
            command=buttonFrame.quit,
            width=8
        )
        self.button.pack(side=LEFT)

        self.convertButton = Button(
            buttonFrame,
            text="Convert",
            command=self.convert,
            width=8
        )
        self.convertButton.pack(side=RIGHT)

    def convert(self):
        if (len(self.fileInput.get()) > 0):
            print("Starting conversion")
            self.convertButton["state"] = DISABLED
            self.convertButton.config(relief=SUNKEN)
            
            try:
                with open(self.fileInput.get(), encoding="utf8") as f:
                    filetext = f.read()
                    version = VERSION_REGEX.search(filetext)
                    mcVersion = version[0].split(" ")[2]
                    print(f"Detected version {mcVersion}")

                    getyarn.getYarnMappings(mcVersion)

                    def doMap(mapping):
                        nonlocal filetext
                        original = mapping.group(1).replace("/", ".")
                        new = mapping.group(2).replace("/", ".")
                        if "." in original:
                            original_simple = mapping.group(1).split("/")[-1]
                            if (re.search(original_simple + "[\.$(]", filetext)):
                                simple_tmp = re.sub(original_simple, new, filetext)
                                if (simple_tmp != filetext):
                                    print(f"Matching: {original_simple} -> {new}")
                                    filetext = simple_tmp
                        if (re.search(original + "[\.$(]", filetext)):
                            tmp = re.sub(original, new, filetext)
                            if (tmp != filetext):
                                print(f"Matching: {original} -> {new}")
                                return tmp
                        return filetext

                    for path in Path(f"yarn-{mcVersion}/mappings/").rglob('*.mapping'):
                        with open(path, encoding="utf8") as f:
                            mappingtext = f.read()
                            for classMap in CLASS_REGEX.finditer(mappingtext):
                                filetext = doMap(classMap)
                            for methodMap in METHOD_REGEX.finditer(mappingtext):
                                filetext = doMap(methodMap)
                            for fieldMap in FIELD_REGEX.finditer(mappingtext):
                                filetext = doMap(fieldMap)

                    filetext = re.sub(MAPPING_MARK_REGEX, "", filetext)
                    with open("stiched_file.txt", "w", encoding="utf8") as final:
                        final.write(filetext)
                print("Done mapping")
            except Exception as e:
                messagebox.showerror("Unhandled Exception", e)
                traceback.print_exc()
            finally:
                self.fileInput.delete(0, END)
                self.convertButton["state"] = NORMAL
                self.convertButton.config(relief=RAISED)
        else:
            messagebox.showerror("Error", "File input is empty! Please enter a file for conversion")

    def browseForFile(self):
        print("Browsing for file")
        filename = askopenfilename()
        self.fileInput.delete(0, END)
        self.fileInput.insert(0, filename)


root = Tk()

app = App(root)

root.mainloop()
try:
    root.destroy()
except:
    ...
