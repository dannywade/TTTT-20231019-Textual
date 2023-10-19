import os
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widgets import Input, TextArea, Button, Footer
from textual.worker import get_current_worker
import time

# local imports
from helpers import device_connection


class NetDemo(App):
    """A simple app to configure a network device provided the device hostname/IP and configuration."""

    CSS = """
    Screen {
        background: $panel;
    }
    VerticalScroll {
        align-horizontal: center;
    }
    Input {
        margin: 1 1;
    }
    TextArea {
        margin: 2 2;
    }
    Button {
        width: 25;
        margin: 1 2;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Widgets to create when app is loaded."""

        yield VerticalScroll(
            Input(placeholder="Enter device hostname/IP...", id="hostname_input"),
            TextArea(
                text="! Do not include 'conf t', as config mode will automatically be entered and exited\n",
                theme="vscode_dark",
                id="config_area",
            ),
            Button(label="Configure!", variant="primary", id="cfg_btn"),
        )
        yield Footer()

    def on_mount(self):
        """Once app and widgets are loaded, perform last minute activities."""

        # Focus on hostname input first
        self.query_one("#hostname_input").focus()
        # Move cursor to second line below comment
        self.query_one("#config_area", TextArea).cursor_location = (1, 0)

    @on(Button.Pressed, "#cfg_btn")
    def send_button(self) -> None:
        """Actions to perform when 'Configure!' button is pressed."""

        # Extract device hostname and configuration from input and textarea
        host = self.query_one("#hostname_input").value
        config_text = self.query_one("#config_area", TextArea)
        # Show loading indicator while device is being configured
        config_text.loading = True
        # Convert configuration from string to list of commands
        print(config_text.text)
        config_list = config_text.text.split("\n")
        print(config_list)
        # Configure the devices
        self.configure_device(host, config_list)

    @work(thread=True)
    def configure_device(self, hostname: str, config: list) -> str:
        """Create thread to configure device."""

        # Get login creds from env vars
        user = os.getenv("NET_TEXT_USER", "admin")
        pw = os.getenv("NET_TEXT_PASS", "admin")
        creds = {"username": user, "password": pw}
        # Get current worker obj to update app when work completes
        worker = get_current_worker()
        config_text = self.query_one("#config_area", TextArea)
        # Create device connection (ConnectHandler) obj
        dev_connect = device_connection(host_id=hostname, credentials=creds)
        # If device fails fast, simulate device configuration (for demo purposes)
        time.sleep(5)
        # Connect and configure the device
        if dev_connect is not None:
            with dev_connect as device:
                with dev_connect as device:
                    output = device.send_config_set(config)
            if not worker.is_cancelled:
                # Update textarea widget from thread
                config_text.loading = False
                self.call_from_thread(config_text.load_text, output)
        else:
            output = "Could not connect to device!"
            if not worker.is_cancelled:
                # Update textarea widget from thread
                config_text.loading = False
                self.call_from_thread(config_text.load_text, output)
        return output


if __name__ == "__main__":
    app = NetDemo()
    app.run()
