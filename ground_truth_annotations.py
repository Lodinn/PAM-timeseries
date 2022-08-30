from datetime import datetime
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import matplotlib.dates as mdates


def annotate_gt(colorbar_baseline: int, colorbar_height: int, star_baseline: int, 
                axes=None, custom_xscale: dict = None,
                colorbar_phases: bool = True,
                dashed_transitions: bool = True,
                destructive_markers: bool = True) -> None:
    if axes is None:
        ax = plt.gca()
    else:
        ax = axes
    ourmodel_dates = [datetime(2020, 1, 29), datetime(2020, 12, 9), datetime(2021, 12, 12)]
    groundtruth_dormant = [datetime(2019, 11, 25), datetime(2019, 12, 27), 
                           datetime(2020, 10, 21), datetime(2020, 12, 16),
                           datetime(2021, 11, 2), datetime(2021, 12, 20)]
    groundtruth_release = [datetime(2020, 1, 27), 
                           datetime(2021, 1, 15), datetime(2021, 1, 26),
                           datetime(2022, 1, 11), datetime(2022, 1, 24)]
    veg_phases = [(datetime(2020, 3, 15), datetime(2020, 9, 1)),
                  (datetime(2021, 3, 15), datetime(2021, 9, 1)),
                  (datetime(2022, 3, 15), datetime(2022, 4, 21))]
    # release midway between gt_dormant and gt_release
    end_phases = [(datetime(2019, 10, 17), datetime(2020, 1, 15)),
                  (datetime(2020, 9, 2), datetime(2021, 1, 1)),
                  (datetime(2021, 9, 2), datetime(2022, 1, 4))]
    # fill in between
    ecd_phases = [(datetime(2020, 1, 16), datetime(2020, 3, 14)),
                  (datetime(2021, 1, 2), datetime(2021, 3, 14)),
                  (datetime(2022, 1, 5), datetime(2022, 3, 14))]
    ymin, ymax = ax.get_ylim()
    xmin, xmax = ax.get_xlim()
    handles_old, _ = ax.get_legend_handles_labels()
    offset_scale = 1.
    def transform_date(d):
        if custom_xscale:
            return (mdates.date2num(d) - custom_xscale['min']) * custom_xscale['factor']
            offset_scale = custom_xscale['factor']
        else:
            return mdates.date2num(d)
    if dashed_transitions:
        for d in ourmodel_dates:
            d = transform_date(d)
            ax.plot([d, d], [ymin, (ymin + ymax) / 2], 'k--')
        model_label = Line2D([0], [0], color='k', linestyle='--', label='Dormancy release according to our model (based on DIo/RC)')
        handles_old.append(model_label)
    legend_old = ax.legend(handles=handles_old, loc='upper left')
    if destructive_markers:
        gt_dormant_axes = [transform_date(d) for d in groundtruth_dormant]
        gt_release_axes = [transform_date(d) for d in groundtruth_release]
        ax.scatter(gt_dormant_axes, [star_baseline] * len(groundtruth_dormant), s=240, c='k', marker='*', zorder=98, label='No budbreak')
        ax.scatter(gt_release_axes, [star_baseline] * len(groundtruth_release), s=240, edgecolors='k', marker='*', facecolors='none', zorder=99, label='Budbreak')
        gt_handles, _ = ax.get_legend_handles_labels()
        ax.legend(handles=gt_handles[-2:], loc='upper right', title='Destructive tests:')
    if colorbar_phases:
        def color_patch(d_start, d_end, color, label):
            start = mdates.date2num(d_start)
            end = mdates.date2num(d_end)
            if start > xmax or end < xmin:
                return
            end = min(transform_date(d_end), xmax)
            start = max(transform_date(d_start), xmin)
            width = end - start
            rect = Rectangle((start, colorbar_baseline), width, colorbar_height, color=color, clip_on=False)
            ax.add_patch(rect)
            ax.text(x=(start+end)/2 - 5 * len(label) * offset_scale, 
                    y=colorbar_baseline + colorbar_height - colorbar_height / 4, 
                    s=label, fontsize=14)
        for d_start, d_end in veg_phases:
            color_patch(d_start, d_end, '#9bbb59', 'V')
        for d_start, d_end in end_phases:
            color_patch(d_start, d_end, '#8064a2', 'EnD')
            release_x = transform_date(d_end) - 10 * offset_scale
            if xmin < release_x < xmax:
                ax.text(x=release_x, y=colorbar_baseline + colorbar_height / 4, s="R", c='r', fontsize=20)
        for d_start, d_end in ecd_phases:
            color_patch(d_start, d_end, '#4bacc6', 'EcD')
#     ax.add_artist(legend_old)