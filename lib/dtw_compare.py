import numpy as np
import fastdtw
import sys
from lib import trc_parser

def channels_compare(channels1, channels2):
    match = []
    for item1 in channels1:
        for item2 in channels2:
            if item2 == item1:
                match.append(item1)
                break
    return match


def remove_markers_from_trajectory(trajectory, channels, allowed_channels):
    if len(channels) == len(allowed_channels):
        return trajectory, channels
    elif len(channels) > len(allowed_channels):
        allowed_indexes = []
        for i, item in enumerate(channels):
            for item_allowed in allowed_channels:
                if item_allowed == item:
                    allowed_indexes.append((i))

        new_trajectory = trajectory[:, allowed_indexes]
        new_channels = [ch for i, ch in enumerate(channels) if i in allowed_indexes]

        return new_trajectory, new_channels


def compare(trajectory1, channel_list1, trajectory2, channel_list2):
    valid_channels = channels_compare(channel_list1, channel_list2)
    trajectory1, channel_list1 = remove_markers_from_trajectory(trajectory1, channel_list1, valid_channels)
    trajectory2, channel_list2 = remove_markers_from_trajectory(trajectory2, channel_list2, valid_channels)
    alignment, path = fastdtw.dtw(trajectory1, trajectory2)
    return alignment, path


def query(query, target_trc, channels_query, topN=-1, delta=[-2, 2]):
    pars = trc_parser.trc(target_trc)
    trajectory_long, channels_long = pars.trajectory(0, -1)

    trajectory_query, channels_query = remove_markers_from_trajectory(query, channels_query, channels_long)
    result = []
    query_length = np.size(query, 0)
    maxFrame = int(pars.NumFrames)
    progress = 0
    total = (maxFrame-query_length) * (delta[1] - delta[0])
    for tmp_delta in range(query_length+delta[0], query_length+delta[1]):
        for i in range(0, maxFrame-tmp_delta):
            sys.stdout.write('\r{:.2f} %'.format(100*progress/total))
            progress += 1
            trajectory_target, channels_target = pars.trajectory(i, i+tmp_delta)
            trajectory_target, channels_target = remove_markers_from_trajectory(trajectory_target, channels_target, channels_long)
            alignment, _ = fastdtw.dtw(trajectory_query, trajectory_target)
            result.append([i, i+tmp_delta, alignment])
    sys.stdout.write('\r')
    result.sort(key=lambda x: x[2])
    return result[:topN]