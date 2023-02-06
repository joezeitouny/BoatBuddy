import time

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from BoatBuddy import utils
from BoatBuddy.plugin_manager import PluginManagerStatus


class ConsoleManager:

    def __init__(self, options, args, plugin_manager):
        self._options = options
        self._args = args
        self._plugin_manager = plugin_manager

        self._console = Console()

        with Live(self.make_layout(), refresh_per_second=4) as live:
            try:
                while True:
                    time.sleep(0.4)
                    live.update(self.make_layout())
            except KeyboardInterrupt:  # on keyboard interrupt...
                utils.get_logger().warning("Ctrl+C signal detected!")
            finally:
                # Notify the plugin manager
                self._plugin_manager.finalize()

    def make_header(self) -> Layout:
        application_name = utils.get_application_name()
        application_version = utils.get_application_version()
        curr_time = time.strftime("%H:%M:%S", time.localtime())
        status = self._plugin_manager.get_status()
        status_string = ''
        status_style = 'white'

        if status == PluginManagerStatus.IDLE:
            status_string = 'Idle'
            status_style = 'yellow'
        elif status == PluginManagerStatus.SESSION_ACTIVE:
            status_string = 'Session active'
            status_style = 'red'

        grid = Table.grid(expand=True)
        grid.add_column(justify="left", style=status_style)
        grid.add_column(justify="center", ratio=1, style='blue')
        grid.add_column(justify="right")
        grid.add_row(
            f'Status: {status_string}',
            f'[b]{application_name} (version {application_version})[/b]',
            f'Local time: {curr_time}'
        )
        return Layout(grid)

    def make_summary(self) -> Layout:
        summary_table = Table.grid(expand=True)
        summary_table.add_column()
        summary_key_value_list = self._plugin_manager.get_summary_metrics()
        for key in summary_key_value_list:
            summary_table.add_row(f'[b]{key}[/b]: {summary_key_value_list[key]}')
        return Layout(Panel(summary_table, title=f'{self._plugin_manager.get_session_name()} Summary'))

    @staticmethod
    def make_footer() -> Panel:
        footer_table = Table.grid(expand=True)
        footer_table.add_column()
        last_log_entries = utils.get_last_log_entries(3)
        for entry in last_log_entries:
            footer_table.add_row(f'{entry}')
        return Panel(footer_table, title=f'Last 3 log entries')

    def make_layout(self) -> Layout:
        layout = Layout()

        if self._options.verbose:
            layout.split_column(
                Layout(name="header", size=1),
                Layout(name="body", ratio=1),
                Layout(name="footer", size=5)
            )

            layout["footer"].update(self.make_footer())
        else:
            layout.split_column(
                Layout(name="header", size=1),
                Layout(name="body", ratio=1),
            )

        layout["header"].update(self.make_header())

        if self._options.nmea_server_ip and self._options.victron_server_ip:
            if self._plugin_manager.get_status() == PluginManagerStatus.SESSION_ACTIVE:
                layout["body"].split_row(
                    Layout(name="victron"),
                    Layout(name="nmea"),
                    Layout(name="summary")
                )
            else:
                layout["body"].split_row(
                    Layout(name="victron"),
                    Layout(name="nmea"),
                )

            # Populate the victron layout
            victron_table = Table.grid(expand=True)
            victron_table.add_column()
            victron_metrics_key_value_list = self._plugin_manager.get_victron_metrics()
            for key in victron_metrics_key_value_list:
                victron_table.add_row(f'[b]{key}[/b]: {victron_metrics_key_value_list[key]}')
            layout["victron"].update(Panel(victron_table, title='Victron Metrics'))

            nmea_table = Table.grid(expand=True)
            nmea_table.add_column()
            nmea_metrics_key_value_list = self._plugin_manager.get_nmea_metrics()
            for key in nmea_metrics_key_value_list:
                nmea_table.add_row(f'[b]{key}[/b]: {nmea_metrics_key_value_list[key]}')
            layout["nmea"].update(Panel(nmea_table, title='NMEA Metrics'))
        elif self._options.nmea_server_ip:
            if self._plugin_manager.get_status() == PluginManagerStatus.SESSION_ACTIVE:
                layout["body"].split_row(
                    Layout(name="nmea"),
                    Layout(name="summary"),
                )

            nmea_table = Table.grid(expand=True)
            nmea_table.add_column()
            nmea_metrics_key_value_list = self._plugin_manager.get_nmea_metrics()
            for key in nmea_metrics_key_value_list:
                nmea_table.add_row(f'[b]{key}[/b]: {nmea_metrics_key_value_list[key]}')
            if self._plugin_manager.get_status() == PluginManagerStatus.SESSION_ACTIVE:
                layout["nmea"].update(Panel(nmea_table, title='NMEA Metrics'))
            else:
                layout["body"].update(Panel(nmea_table, title='NMEA Metrics'))
        elif self._options.victron_server_ip:
            if self._plugin_manager.get_status() == PluginManagerStatus.SESSION_ACTIVE:
                layout["body"].split_row(
                    Layout(name="victron"),
                    Layout(name="summary"),
                )

            # Populate the victron layout
            victron_table = Table.grid(expand=True)
            victron_table.add_column()
            victron_metrics_key_value_list = self._plugin_manager.get_victron_metrics()
            for key in victron_metrics_key_value_list:
                victron_table.add_row(f'[b]{key}[/b]: {victron_metrics_key_value_list[key]}')
            if self._plugin_manager.get_status() == PluginManagerStatus.SESSION_ACTIVE:
                layout["victron"].update(Panel(victron_table, title='Victron Metrics'))
            else:
                layout["body"].update(Panel(victron_table, title='Victron Metrics'))
        if self._plugin_manager.get_status() == PluginManagerStatus.SESSION_ACTIVE:
            layout["summary"].update(self.make_summary())

        return layout
