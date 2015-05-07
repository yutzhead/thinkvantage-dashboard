# ThinkVantage Dashboard: A system tool for ThinkPads.

ThinkVantage Dashboard works best with acpi_call, akmod-tp_smapi, akmod-acpi_call
and tp_smapi installed.

![Image of System Overview](http://i.imgur.com/QBbEaVz.png)
![Image of Memory](http://i.imgur.com/xHA5CHk.png)

If the ThinkVantage button is usele... err, unused, it will automatically use it
as a hotkey.

ThinkVantage Dashboard can be extended via plugins which are pythonic classes.

```python
from gi.repository import Gtk
from utils import TextRow, PercentageRow

class MyPlugin():
    def __init__(self):
        # Perform basic initialization
        self.autoupdate = -1 # Reloads data via getListboxRows every self.autoupdate seconds

    def getHeader(self):
        # Return a title as shown in the sidebar
        return 'My Plugin'

    def shouldDisplay(self):
        # Perform checks whether this plugin is available on this ThinkPad
        return True

    def getListboxRows(self):
        # Yields GtkWidgets for the main area

        # Displays a title ('Nothing') on the left, and the content of the
        # file ('/dev/null') on the right
        yield TextRow('Nothing', '/dev/null')

        # Adds a title on the left, and a progressbar with subtitle
        # on the right
        yield PercentageRow('How full is the glass?',
                50.0,
                "volume of liquid"
        )

        # Custom row with a GtkBox
        box = Gtk.Box()
        box.add(Gtk.Label("Hello"))
        box.add(Gtk.Label("World"))
        yield box

# Add an instance of the plugin for auto-discovery with priority 99
PLUGINS.append((99, MyPlugin()))
```

If someone doesn't have anything better to do: It will be hours and hours of fun
to write the fingerprint sensor plugin. [In-depth description of fprint](http://www.reactivated.net/fprint/academic-project/fprint_report.pdf)
