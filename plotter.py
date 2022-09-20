import matplotlib.figure
from matplotlib.axes._subplots import Axes
import matplotlib.lines as lines
import matplotlib.transforms as mtransforms
import matplotlib.text as mtext
import matplotlib.pyplot as plt
import numpy as np

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

class MyLine(lines.Line2D):
    def __init__(self, *args, **kwargs):
        # we'll update the position when the line data is set
        self.text = mtext.Text(0, 0, '')
        super().__init__(*args, **kwargs)

        # we can't access the label attr until *after* the line is
        # initiated
        self.text.set_text(self.get_label())

    def set_figure(self, figure):
        self.text.set_figure(figure)
        super().set_figure(figure)

    def set_axes(self, axes):
        self.text.set_axes(axes)
        super().set_axes(axes)

    def set_transform(self, transform):
        # 2 pixel offset
        texttrans = transform + mtransforms.Affine2D().translate(2, 2)
        self.text.set_transform(texttrans)
        super().set_transform(transform)

    def set_data(self, x, y):
        if len(x):
            self.text.set_position((x[-1], y[-1]))

        super().set_data(x, y)

    def draw(self, renderer):
        # draw my label at the end of the line with 2 pixel offset
        super().draw(renderer)
        self.text.draw(renderer)

def plot_metrics(logs_metrics: [dict], database_name: str, num_queries: str, workers: int, query_type: str, save: bool = False, legends: [str] = None) -> None:

    # Collect the data
    y_max = [np.array(x['max']) for x in logs_metrics]
    y_min = [np.array(x['min']) for x in logs_metrics]
    y_mean = [np.array(x['mean']) for x in logs_metrics]
    y_sum = [np.array(x['sum']) for x in logs_metrics]
    x = np.array([i*100 for i in range(len(logs_metrics[0]['sum']))])

    # Create the figure
    fig: matplotlib.figure.Figure = plt.figure()
    fig.set_figheight(12)
    fig.set_figwidth(12)
    title = f"{database_name} \n Query Type: \"{query_type}\",  Total Queries: {num_queries},  Worker(s): {workers}"
    fig.suptitle(title, fontsize=20)    # fontweight="bold"

    # Adds subplot on position 1
    max_time_plot: Axes = fig.add_subplot(311)
    max_time_plot.title.set_text("Max time of a Query")
    max_time_plot.set_xlabel("Number of Queries")
    max_time_plot.set_ylabel("Milliseconds")
    for i, values in enumerate(y_max):
        line, = max_time_plot.plot(x, values, linewidth='2.5')
        line.set_label(legends[i])
        max_time_plot.legend()
    # plt.xticks(x)

    # Adds subplot on position 2
    min_time_plot: Axes = fig.add_subplot(312)
    min_time_plot.title.set_text("Min time of a Query")
    min_time_plot.set_xlabel("Number of Queries")
    min_time_plot.set_ylabel("Milliseconds")
    for i, values in enumerate(y_min):
        line, = min_time_plot.plot(x, values, linewidth='2.5')
        line.set_label(legends[i])
        min_time_plot.legend()
    # plt.xticks(x)

    # Adds subplot on position 3
    mean_time_plot: Axes = fig.add_subplot(313)
    mean_time_plot.title.set_text("Mean time of a Query")
    mean_time_plot.set_xlabel("Number of Queries")
    mean_time_plot.set_ylabel("Milliseconds")
    for i, values in enumerate(y_mean):
        line, = mean_time_plot.plot(x, values, linewidth='2.5')
        line.set_label(legends[i])
        mean_time_plot.legend()
    # plt.xticks(x)

    """
    # Adds subplot on position 4
    sum_time_plot: Axes = fig.add_subplot(224)
    sum_time_plot.title.set_text("Sum time of all Queries")
    sum_time_plot.set_xlabel("Number of Queries")
    sum_time_plot.set_ylabel("Seconds")
    for i, values in enumerate(y_sum):
        line, = sum_time_plot.plot(x, values, linewidth='2.5')
        line.set_label(legends[i])
        sum_time_plot.legend()
    # plt.xticks(x)
    """

    # set the spacing between subplots
    plt.subplots_adjust(left=0.1,
                        bottom=0.15,
                        right=0.9,
                        top=0.85,
                        wspace=0.4,
                        hspace=0.4)

    if save:
        plt.savefig(f"./images_big_dataset/{database_name}_{query_type}_{num_queries}_{workers}")
    else:
        plt.show()
