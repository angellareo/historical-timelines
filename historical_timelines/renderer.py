from bokeh.plotting import figure, save, show
from bokeh.models import LabelSet, ColumnDataSource, CustomJSTickFormatter
from bokeh.models import BoxZoomTool, PanTool, ResetTool
from bokeh.core.properties import value
from bokeh.io import output_notebook as on

# from .graphics import * 

from .timeline import HistoricalTimeline

class HistoricalTimelineRenderer:

    def __init__(self, tl: HistoricalTimeline, bg_color:str = "white", bg_alpha:float = 1, period_color: str = "red", event_color: str = "blue") -> None:
        """Initialization function"""
        self.tl = tl
        self.bg_color = bg_color
        self.bg_alpha = bg_alpha
        self.period_color = period_color
        self.event_color = event_color
        self.tools = [BoxZoomTool(), ResetTool(),PanTool(dimensions="width")]

    def get_source_from_event_dict(self, event_dict: dict) -> ColumnDataSource:
        """Convert a dictionary into a ColumnDataSource

        Args:
            event_dict (dict): The dictionary input

        Returns:
            ColumnDataSource: The converted data
        """
        return ColumnDataSource(data=event_dict)

    def setup_figure(self, *args, **kwargs) -> figure:
        """Create plot with which to create the timeline on.

        This function is essentially a wrapper for the bokeh function figure.
        See its documentation for more information.

        Returns:
            figure: A plot on which to create a timeline
        """
        fig = figure(*args, **kwargs)
        fig.toolbar.logo = None
        return fig

    def get_y_range(self, event_dict: dict, period_list: list) -> list[str]:
        """Get the labels that populate the y range

        Args:
            event_dict (dict): The event dictionary
            period_list (list): The period list

        Returns:
            list[str]: A list of labels to populate the dictionary
        """
        y_range = []
        for i in range(len(period_list)):
            y_range.append("p" + str(i))

        for label in event_dict['label']:
            if label not in y_range:
                y_range.append(label)

        return y_range

    def render_events(self, plot: figure, source: ColumnDataSource, x: str, y: str, size: int) -> None:
        """Render events on the plot

        Args:
            plot (figure): The plot events are rendered on
            source (ColumnDataSource): The data to be rendered
            x (str): The name of the column of source that lists the event x axis
            y (str): The name of the column of source that lists the event y axis
            size (int): The size of the events
        """
        plot.scatter(x=x, y=y, size=size, source=source, color=self.event_color)

    def event_tooltips(self, plot: figure, tooltip_names: list[str]) -> None:
        """Give the plot hoverable tooltips for events

        Args:
            plot (figure): The plot to be modified
            tooltip_names (list[str]): The categories to be shown in the tooltip
        """
        tooltips = []
        for tool in tooltip_names:
            tooltips.append((tool, "@" + tool))
        plot.hover.tooltips = tooltips


    def event_labels(
        self, 
        plot: figure,
        source: ColumnDataSource,
        x: str,
        y: str,
        text: str,
        y_offset: int = 0,
        text_font_size: str = "13px",
        text_color: str = "#555555",
        text_align: str = 'center',
    ) -> None:
        """Give events on the plot labels

        Args:
            plot (figure): The plot events are rendered on
            source (ColumnDataSource): The data to be rendered
            x (str): The name of the column of source that lists the event x axis
            y (str): The name of the column of source that lists the event y axis
            text (str): The name of the column of source that lists the event label text
            y_offset (int, optional): The y offset of the labels. Defaults to 0.
            text_font_size (str, optional): The font size of the labels. Defaults to "11px".
            text_color (str, optional): The color of the labels. Defaults to "#555555".
            text_align (str, optional): The text alignment of the labels. Defaults to 'center'.
        """
        labels = LabelSet(
            x=x,
            y=y,
            text=text,
            y_offset=y_offset,
            text_font_size=text_font_size,
            text_color=text_color,
            text_align=text_align,
            source=source,
        )
        plot.add_layout(labels)


    def render_periods(self, plot: figure, period_list: list, height: float = 0.3) -> None:
        """Render the periods on the plot

        Args:
            plot (figure): The plot to be rendered on
            period_list (list): The list of periods to be rendered
            height (float, optional): The height of the rendered periods. Defaults to 0.3.
        """
        for i in range(len(period_list)):
            period_group = period_list[i]
            source = self.get_source_from_event_dict(period_group)
            plot.hbar(right='start', left='end', y=value("p" + str(i)), height=height, color=self.period_color, source=source)


    def period_labels(
        self, 
        plot: figure,
        period_list: list,
        text: str,
        y_offset: int = -8,
        text_font_size: str = "11px",
        text_color: str = "#555555",
        text_align: str = 'center',
    ) -> None:
        """Give labels to the periods on the plot

        Args:
            plot (figure): The plot events are rendered on
            period_list (list): The list of periods to be given labels
            text (str): The name of the column of source that lists the period label text
            y_offset (int, optional): The y offset of the labels. Defaults to -8.
            text_font_size (str, optional): The font size of the labels. Defaults to "11px".
            text_color (str, optional): The text color of the labels. Defaults to "#555555".
            text_align (str, optional): The text alignment of the labels. Defaults to 'center'.
        """
        for i in range(len(period_list)):
            period_group = period_list[i]
            source = self.get_source_from_event_dict(period_group)
            labels = LabelSet(
                x='mid',
                y=value("p" + str(i)),
                text=text,
                y_offset=y_offset,
                text_font_size=text_font_size,
                text_color=text_color,
                text_align=text_align,
                source=source,
            )
            plot.add_layout(labels)


    def format_xaxis(self, plot: figure, scientific: bool = False) -> figure:
        """Modifies a plot to format the x axis as dates.

        Args:
            plot (figure): The plot to be modified
            scientific (bool, optional): If true, dates use BCE/CE, if false, dates use BC/AD.
            Defaults to False.

        Returns:
            figure: The modified plot
        """
        code = ""
        if scientific:
            code = '''return tick < 0 ? Math.abs(tick) + " BCE" : tick +  " CE"'''
        else:
            code = '''return tick < 0 ? Math.abs(tick) + " BC" : tick +  " AD"'''
        plot.xaxis.formatter = CustomJSTickFormatter(code=code)
        return plot


    def output_timeline(self,
        output: str, show_timeline: bool = False
    ) -> figure:
        """Render a timeline as an image

        Args:
            output (str): The filename to save the timeline as
            show_timeline (bool): Whether to display the timeline rather than saving it
        """
        p = self.render_timeline()
        if show_timeline:
            show(p, title=self.tl.title)
        else:
            save(p, output, title=self.tl.title)

    def render_timeline(self) -> figure:
        """Render a timeline as a figure

        Args:
            timeline (str): The HistoricalTimeline object to render

        Returns:
            figure: The resulting plot
        """
        event_dict = self.tl.create_event_dict()
        period_list = self.tl.create_period_list()

        source = self.get_source_from_event_dict(event_dict)
        y_range = self.get_y_range(event_dict, period_list)
        p = self.setup_figure(
            title=self.tl.title, 
            x_axis_label="year",
            y_axis_label="category",
            height=400, width=1600, 
            y_range=y_range,
            background_fill_color = self.bg_color,
            border_fill_color = self.bg_color,
            background_fill_alpha = self.bg_alpha,
            border_fill_alpha = self.bg_alpha,
            tools=self.tools
        )
        self.event_tooltips(p, tooltip_names=["title", "description"])
        self.render_events(p, source, x='dates', y='label', size=20)
        self.render_periods(p, period_list)
        self.period_labels(p, period_list, text="title")
        self.event_labels(p, source, x="dates", y="label", text="title")
        self.format_xaxis(p, False)
        
        return p