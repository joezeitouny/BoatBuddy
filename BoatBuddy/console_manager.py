import time

from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
from rich.style import Style
from rich.table import Table
from rich.text import Text

from BoatBuddy import utils, globals
from BoatBuddy.database_manager import DatabaseManager
from BoatBuddy.email_manager import EmailManager
from BoatBuddy.generic_plugin import PluginStatus
from BoatBuddy.log_manager import LogManager
from BoatBuddy.notifications_manager import NotificationsManager, NotificationEntryType
from BoatBuddy.plugin_manager import PluginManager, PluginManagerStatus
from BoatBuddy.sound_manager import SoundManager, SoundType


class ConsoleManager:

    def __init__(self, options):
        self._options = options

        # Create a console instance
        self._console = Console()
        self._console.print(f'[bright_yellow]Application is starting up. Please wait...[/bright_yellow]')

        with self._console.status('[bold bright_yellow]Loading logging module...[/bold bright_yellow]') as status:
            time.sleep(0.1)
            self._log_manager = LogManager(self._options)
            self._console.print(f'[green]Loading logging module...Done[/green]')

        with self._console.status('[bold bright_yellow]Loading sound module...[/bold bright_yellow]'):
            time.sleep(0.1)
            self._sound_manager = SoundManager(self._options, self._log_manager)
            self._console.print(f'[green]Loading sound module...Done[/green]')

        with self._console.status('[bold bright_yellow]Loading email module...[/bold bright_yellow]'):
            time.sleep(0.1)
            self._email_manager = EmailManager(self._options, self._log_manager)
            self._console.print(f'[green]Loading email module...Done[/green]')

        with self._console.status('[bold bright_yellow]Loading notifications module...[/bold bright_yellow]'):
            time.sleep(0.1)
            self._notifications_manager = NotificationsManager(self._options, self._log_manager, self._sound_manager,
                                                               self._email_manager)
            self._console.print(f'[green]Loading notifications module...Done[/green]')

        with self._console.status('[bold bright_yellow]Loading plugins module...[/bold bright_yellow]'):
            time.sleep(0.1)
            self._plugin_manager = PluginManager(self._options, self._log_manager, self._notifications_manager,
                                                 self._sound_manager, self._email_manager)
            self._console.print(f'[green]Loading plugins module...Done[/green]')

        with self._console.status('[bold bright_yellow]Loading database module...[/bold bright_yellow]'):
            time.sleep(0.1)
            self._database_manager = DatabaseManager(self._options, self._log_manager, self._plugin_manager,
                                                     self._notifications_manager)
            self._console.print(f'[green]Loading database module...Done[/green]')

        with self._console.status(f'[bold bright_yellow]Firing up console UI...[/bold bright_yellow]'):
            time.sleep(0.1)
            # Play the application started chime
            self._sound_manager.play_sound_async(SoundType.APPLICATION_STARTED)
            self._console.print(f'[green]Firing up console UI...Done[/green]')

        try:
            with Live(self._make_layout(), refresh_per_second=4) as live:
                while True:
                    time.sleep(0.5)
                    live.update(self._make_layout())
        except KeyboardInterrupt:  # on keyboard interrupt...
            self._log_manager.warning(f'Ctrl+C signal detected!')
            self._console.print(f'[red]Ctrl+C signal detected![/red]')
        except Exception as e:
            self._log_manager.error(f'An unexpected error has occurred and application will shutdown. Details {e}')
            self._console.print(f'[red]An unexpected error has occurred and application will shutdown. '
                                f'Details {e}[/red]')
        finally:
            # Notify the plugin manager
            self._plugin_manager.finalize()
            # Notify the notifications manager
            self._notifications_manager.finalize()
            # Notify the database manager
            self._database_manager.finalize()
            # Notify the sound manager
            self._sound_manager.finalize()
            # Notify the email manager
            self._email_manager.finalize()
            # Inform the user
            self._console.print(f'[red]Modules have been notified and application will exit shortly. '
                                f'Please wait...[/red]')

    def _make_header(self) -> Layout:
        application_name = utils.get_application_name()
        application_version = utils.get_application_version()
        curr_time = time.strftime("%H:%M", time.localtime())
        status = self._plugin_manager.get_status()

        status_renderable = None
        application_info_renderable = None
        local_time_renderable = None
        if status == PluginManagerStatus.IDLE:
            status_style = Style(color='bright_white', bgcolor='default')
            status_renderable = Spinner('dots', text=Text('Idle', style=status_style))
            application_info_style = Style(color='blue', bgcolor='default', bold=True)
            application_info_renderable = Text(f'{application_name} ({application_version})',
                                               style=application_info_style)
            local_time_style = Style(color='bright_yellow', bgcolor='default')
            local_time_renderable = Text(f'Local time: {curr_time}',
                                         style=local_time_style)
        elif status == PluginManagerStatus.SESSION_ACTIVE:
            status_style = Style(color='bright_white', bgcolor='red')
            status_renderable = Spinner('earth', text=Text('Session active', style=status_style))
            application_info_style = Style(color='bright_white', bgcolor='red', bold=True)
            application_info_renderable = Text(f'{application_name} ({application_version})',
                                               style=application_info_style)
            local_time_style = Style(color='bright_white', bgcolor='red')
            local_time_renderable = Text(f'Local time: {curr_time}',
                                         style=local_time_style)

        grid = Table.grid(expand=True)
        grid.add_column(justify="left")
        grid.add_column(justify="center", ratio=1, style='blue')
        grid.add_column(justify="right", style="bright_yellow")
        grid.add_row(
            status_renderable,
            application_info_renderable,
            local_time_renderable
        )
        return Layout(grid)

    def _make_summary(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="summary_header", size=5),
            Layout(name="summary_body", ratio=1),
        )

        summary_header_table = Table.grid(expand=True)
        summary_header_table.add_column()
        summary_header_table.add_column()
        summary_header_key_value_list = utils.get_filtered_key_value_list(
            self._plugin_manager.get_session_clock_metrics(),
            self._options.console_session_header_fields.copy())
        counter = 0
        while counter < len(summary_header_key_value_list):
            key = list(summary_header_key_value_list.keys())[counter]

            if counter + 1 < len(summary_header_key_value_list):
                next_key = list(summary_header_key_value_list.keys())[counter + 1]
                summary_header_table.add_row(
                    f'[bright_white]{key}: {summary_header_key_value_list[key]}[/bright_white]',
                    f'[bright_white]{next_key}: {summary_header_key_value_list[next_key]}[/bright_white]')
            else:
                summary_header_table.add_row(
                    f'[bright_white]{key}: {summary_header_key_value_list[key]}[/bright_white]', '')
            counter += 2

        layout["summary_header"].update(
            Layout(Panel(summary_header_table, title=f'{self._plugin_manager.get_session_name()}')))

        summary_body_table = Table.grid(expand=True)
        summary_body_table.add_column()
        summary_body_table.add_column()
        summary_key_value_list = self._plugin_manager.get_session_summary_metrics()

        if self._options.gps_module:
            gps_dictionary = utils.get_filtered_key_value_list(summary_key_value_list,
                                                               self._options.console_gps_summary_fields.copy())
            summary_key_value_list.update(gps_dictionary)

        if self._options.nmea_module:
            nmea_dictionary = utils.get_filtered_key_value_list(summary_key_value_list,
                                                                self._options.console_nmea_summary_fields.copy())
            summary_key_value_list.update(nmea_dictionary)

        if self._options.victron_module:
            victron_dictionary = utils.get_filtered_key_value_list(summary_key_value_list,
                                                                   self._options.console_victron_summary_fields.copy())
            summary_key_value_list.update(victron_dictionary)

        counter = 0
        while counter < len(summary_key_value_list):
            key = list(summary_key_value_list.keys())[counter]

            if counter + 1 < len(summary_key_value_list):
                next_key = list(summary_key_value_list.keys())[counter + 1]
                summary_body_table.add_row(f'[bright_white]{key}: {summary_key_value_list[key]}[/bright_white]',
                                           f'[bright_white]{next_key}: {summary_key_value_list[next_key]}'
                                           f'[/bright_white]')
            else:
                summary_body_table.add_row(f'[bright_white]{key}: {summary_key_value_list[key]}[/bright_white]', '')
            counter += 2

        layout["summary_body"].update(Layout(Panel(summary_body_table,
                                                   title=f'Session Summary')))
        return layout

    def _make_footer(self) -> Panel:
        footer_table = Table.grid(expand=True)
        footer_table.add_column()
        last_log_entries = self._log_manager.get_last_log_entries(3)
        for entry in last_log_entries:
            colour = 'default'
            if 'INFO' in str(entry).upper():
                colour = 'green'
            elif 'WARNING' in str(entry).upper():
                colour = 'yellow'
            elif 'ERROR' in str(entry).upper():
                colour = 'red'
            footer_table.add_row(f'[{colour}]{entry}[/{colour}]')
        return Panel(footer_table, title=f'Last 3 log entries')

    def _make_key_value_table(self, title, key_value_list, border_style) -> Panel:
        table = Table.grid(expand=True)
        table.add_column()
        colour = 'default'

        for key in key_value_list:
            if self._options.notification_console:
                colour = utils.get_colour_for_key_value_in_dictionary(self._options.metrics_colouring_scheme, key,
                                                                      key_value_list[key])
            if colour != 'default':
                table.add_row(f'[b][{colour}]{key}: ' +
                              f'{key_value_list[key]}[/{colour}][/b]')
            else:
                table.add_row(f'[bright_white]{key}: ' +
                              f'{key_value_list[key]}[/bright_white]')
            self._notifications_manager.notify(key, key_value_list[key], NotificationEntryType.METRIC)
        return Panel(table, title=title, border_style=border_style, box=box.ROUNDED)

    def _make_layout(self) -> Layout:
        layout = Layout()

        if self._options.log_module and self._options.console_show_log:
            layout.split_column(
                Layout(name="header", size=1),
                Layout(name="body", ratio=1),
                Layout(name="footer", size=5)
            )

            layout["footer"].update(self._make_footer())
        else:
            layout.split_column(
                Layout(name="header", size=1),
                Layout(name="body", ratio=1),
            )

        layout["header"].update(self._make_header())

        # Add the plugins layout for the loaded plugins
        victron_layout = None
        gps_layout = None
        nmea_layout = None
        summary_layout = None

        if self._options.victron_module and self._options.console_show_victron_plugin:
            victron_layout = Layout(name="victron")
            # Populate the victron layout
            plugin_status = self._plugin_manager.get_victron_plugin_status()
            formatted_plugin_status_str = self._get_formatted_plugin_status_str(plugin_status)
            border_style = self._get_border_style_from_status(plugin_status)
            ui_filtered_victron_plugin_metrics = utils.get_filtered_key_value_list(utils.get_key_value_list(
                globals.VICTRON_PLUGIN_METADATA_HEADERS, self._plugin_manager.get_victron_plugin_metrics()),
                self._options.console_victron_metrics.copy())
            victron_layout.update(self._make_key_value_table('Victron ESS ' + formatted_plugin_status_str,
                                                             ui_filtered_victron_plugin_metrics,
                                                             border_style))

        if self._options.gps_module and self._options.console_show_gps_plugin:
            gps_layout = Layout(name="gps")
            # Populate the NMEA layout
            plugin_status = self._plugin_manager.get_gps_plugin_status()
            formatted_plugin_status_str = self._get_formatted_plugin_status_str(plugin_status)
            border_style = self._get_border_style_from_status(plugin_status)
            ui_filtered_gps_plugin_metrics = utils.get_filtered_key_value_list(utils.get_key_value_list(
                globals.GPS_PLUGIN_METADATA_HEADERS, self._plugin_manager.get_gps_plugin_metrics()),
                self._options.console_gps_metrics.copy())
            gps_layout.update(self._make_key_value_table('GPS Module ' + formatted_plugin_status_str,
                                                         ui_filtered_gps_plugin_metrics,
                                                         border_style))

        if self._options.nmea_module and self._options.console_show_nmea_plugin:
            nmea_layout = Layout(name="nmea")
            # Populate the NMEA layout
            plugin_status = self._plugin_manager.get_nmea_plugin_status()
            formatted_plugin_status_str = self._get_formatted_plugin_status_str(plugin_status)
            border_style = self._get_border_style_from_status(plugin_status)
            ui_filtered_nmea_plugin_metrics = utils.get_filtered_key_value_list(
                utils.get_key_value_list(globals.NMEA_PLUGIN_METADATA_HEADERS,
                                         self._plugin_manager.get_nmea_plugin_metrics()),
                self._options.console_nmea_metrics.copy())
            nmea_layout.update(self._make_key_value_table('NMEA0183 Network ' + formatted_plugin_status_str,
                                                          ui_filtered_nmea_plugin_metrics,
                                                          border_style))

        if self._plugin_manager.get_status() == PluginManagerStatus.SESSION_ACTIVE:
            summary_layout = Layout(name="summary", ratio=2)
            summary_layout.update(self._make_summary())

        layouts_list = []
        if victron_layout:
            layouts_list.append(victron_layout)

        if nmea_layout:
            layouts_list.append(nmea_layout)

        if gps_layout:
            layouts_list.append(gps_layout)

        if summary_layout:
            layouts_list.append(summary_layout)

        layout["body"].split_row(*layouts_list)

        return layout

    @staticmethod
    def _get_formatted_plugin_status_str(plugin_status: PluginStatus):
        plugin_status_str = ''
        if plugin_status == PluginStatus.DOWN:
            plugin_status_str = '[red](Down)[/red]'
        elif plugin_status == PluginStatus.STARTING:
            plugin_status_str = '[bright_yellow](Starting)[/bright_yellow]'
        elif plugin_status == PluginStatus.RUNNING:
            plugin_status_str = '[green](Running)[/green]'
        return plugin_status_str

    @staticmethod
    def _get_border_style_from_status(plugin_status: PluginStatus):
        border_style = 'default'
        if plugin_status == PluginStatus.DOWN:
            border_style = 'red'
        elif plugin_status == PluginStatus.STARTING:
            border_style = 'bright_yellow'
        elif plugin_status == PluginStatus.RUNNING:
            border_style = 'green'

        return border_style
