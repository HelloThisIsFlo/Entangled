# import rum

# class AwesomeStatusBarApp(rumps.App):
#     @rumps.clicked("Preferences")
#     def prefs(self, _):
#         rumps.alert("jk! no preferences available!")

#     @rumps.clicked("Silly button")
#     def onoff(self, sender):
#         sender.state = not sender.state

#     @rumps.clicked("Say hi")
#     def sayhi(self, _):
#         rumps.notification("Awesome title", "amazing subtitle", "hi!!1")

# if __name__ == "__main__":
#     AwesomeStatusBarApp("Awesome App").run()

import tkinter as tk
print('hello')

root = tk.Tk()
root.title("Sandbox")
root.geometry('350x200')
lbl = tk.Label(root, text="Some text")
lbl.grid(column=0, row=0)
tk.mainloop()
