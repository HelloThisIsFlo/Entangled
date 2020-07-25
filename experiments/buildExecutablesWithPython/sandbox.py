from infi.systray import SysTrayIcon
from pystray import Icon, Menu, MenuItem
import rumps
import pystray
from PIL import Image, ImageDraw


def create_systray_icon():
    # Generate an image and draw a pattern
    width = 400
    height = 400
    color1 = (0, 0, 0)
    color2 = (200, 200, 200)
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)

    return image


class AwesomeStatusBarApp(rumps.App):
    @rumps.clicked("Preferences")
    def prefs(self, _):
        rumps.alert("jk! no preferences available!")

    @rumps.clicked("Silly button")
    def onoff(self, sender):
        sender.state = not sender.state

    @rumps.clicked("Say hi")
    def sayhi(self, _):
        rumps.notification("Awesome title", "amazing subtitle", "hi!!1")


state = False


def on_clicked(icon, item):
    global state
    state = not item.checked


def on_quit(icon):
    icon.stop()


def item_checkable():
    return MenuItem(
        'Checkable',
        on_clicked,
        checked=lambda item: state
    )


def item_quit():
    return MenuItem(
        'Quit',
        on_quit
    )


# Update the state in `on_clicked` and return the new state in
# a `checked` callable
icon = Icon(
    'test',
    create_systray_icon(),
    menu=Menu(
        item_checkable(),
        item_quit()
    )
)


def say_hello(systray):
    print("Hello, World!")


menu_options = (("Say Hello", None, say_hello),)
systray = SysTrayIcon("icon.ico", "Example tray icon", menu_options)


def systray_with_pystray():
    icon.run()


def systray_with_rumps():
    AwesomeStatusBarApp("Awesome App").run()


def systray_with_infisystray():
    systray.start()


if __name__ == "__main__":
    import platform

    def on_mac_os():
        return platform.system() == 'Darwin'

    def on_windows():
        return platform.system() == 'Windows'

    if on_mac_os():
        # systray_with_pystray()
        systray_with_rumps()
    elif on_windows():
        systray_with_infisystray()
    else:
        raise f'Platform Not Supported - {platform.system()}'


# import tkinter as tk
# print('hello')

# root = tk.Tk()
# root.title("Sandbox")
# root.geometry('350x200')
# lbl = tk.Label(root, text="Some text")
# lbl.grid(column=0, row=0)
# tk.mainloop()
