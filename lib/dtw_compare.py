import numpy as np
import fastdtw
import sys
from lib import trc_parser, sign_dictionary

def channels_compare(channels1, channels2):
    """
    Compares two channel list
    :param channels1:
    :param channels2:
    :return: common channels
    """
    match = []
    for item1 in channels1:
        for item2 in channels2:
            if item2 == item1:
                match.append(item1)
                break
    return match


def remove_markers_from_trajectory(trajectory, channels, allowed_channels):
    """
    Reves channels that are not in list of allowed channels
    :param trajectory:
    :param channels:
    :param allowed_channels:
    :return:
    """
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
    """
    DTW comparison of trajectories. Channels that are not common for both are excluded.
    :param trajectory1:
    :param channel_list1:
    :param trajectory2:
    :param channel_list2:
    :return:
    """
    valid_channels = channels_compare(channel_list1, channel_list2)
    trajectory1, channel_list1 = remove_markers_from_trajectory(trajectory1, channel_list1, valid_channels)
    trajectory2, channel_list2 = remove_markers_from_trajectory(trajectory2, channel_list2, valid_channels)
    alignment, path = fastdtw.dtw(trajectory1, trajectory2)
    return alignment, path


def query(query, target_trc, channels_query, topN=-1, delta=[-2, 2]):
    """
    Finds best matching sign (query) in trc file.
    :param query: trajectory NxM
    :param target_trc: file name
    :param channels_query: list of channels len M
    :param topN: return topN results
    :param delta: difference in length of searched item compared to query
    :return: topN results
    """
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


def annotation_matching(src_trc, target_trc, normalization=''):
    """
    Loads TRC files and runs comparison
    :param src_trc:
    :param target_trc:
    :param normalization:
    :return:
    """
    src_parser = trc_parser.trc(src_trc)
    src_trajectory, src_channels = src_parser.trajectory(normalize=normalization)
    target_parser = trc_parser.trc(target_trc)
    target_trajectory, target_channels = target_parser.trajectory(normalize=normalization)

    _, path = compare(src_trajectory, src_channels, target_trajectory, target_channels)

    return path


def match_annotation():
    """
    Matches annotation from one trc to other (same speech and speaker, different take)
    """
    return -1