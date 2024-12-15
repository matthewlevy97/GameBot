import platform
from PIL import ImageGrab
import time

if platform.system() == "Windows":
    import pygetwindow as gw
elif platform.system() == "Darwin":
    from AppKit import NSApplication, NSWorkspace, NSScreen
    from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
else:
    raise NotImplementedError("Unsupported platform")

class WindowManager:
    def __init__(self, title: str):
        self._title = title

    def getGeometry(self):
        geo = None
        if platform.system() == "Windows":
            windows = gw.getAllWindows()
            for win in windows:
                if self._title in win.title:
                    geo = (win.left, win.top, win.right, win.bottom)
                    break
        elif platform.system() == "Darwin":
            for window in CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID):
                if window.get("kCGWindowName", None) == self._title:
                    bounds = window.get("kCGWindowBounds", {})
                    x = int(bounds["X"])
                    y = int(bounds["Y"])
                    width = int(bounds["Width"])
                    height = int(bounds["Height"])
                    geo = (x, y, x+width, y+height)
        if geo:
            return geo
        raise ValueError(f"No window found with title: {self._title}")

    def CaptureImage(self, outputFile: str):
        bounds = self.getGeometry()
        screenshot = ImageGrab.grab(bbox=bounds)
        screenshot.save(outputFile)

    @staticmethod
    def GetAllTitles():
        if platform.system() == "Windows":
            return [win.title for win in gw.getAllWindows()]
        elif platform.system() == "Darwin":
            return [window.get("kCGWindowName", None)
                    for window in CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
                    if window.get("kCGWindowName", None) and
                    window.get("kCGWindowIsOnscreen", False) and
                    window.get("kCGWindowOwnerName", "") not in ("Spotlight", "Control Center", "Dock", "Window Server", "Wallpaper")]
        return None

if __name__ == "__main__":
    # Ask for the window title
    titles = WindowManager.GetAllTitles()
    for i in range(len(titles)):
        print(f"{i+1:2}: {titles[i]}")
    
    selectedTitle = input("Target Window: ")
    if int(selectedTitle):
        title = titles[int(selectedTitle) - 1]
    else:
        title = selectedTitle

    from pathlib import Path
    import os
    outputPath = Path(__file__).parent.joinpath("images")
    os.makedirs(outputPath.as_posix(), exist_ok=True)

    wm = WindowManager(title)
    try:
        while True:
            wm.CaptureImage(outputPath.joinpath(f"{title.replace(' ', '_')}_{int(time.time())}.png").as_posix())
            time.sleep(2)
    except KeyboardInterrupt:
        print("Screenshot capture stopped.")