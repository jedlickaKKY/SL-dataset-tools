import os
import numpy as np

class trc:
    def __init__(self, trc_file):
        if trc_file == '':
            print('Please set trc file path and name')
            return 0
        self.trc_file = trc_file

        with open(self.trc_file, 'r') as f:
            cont = f.readlines()

        self.Header = cont[0:2]
        params = cont[2].strip().split('\t')
        self.DataRate = params[0]
        self.CameraRate = params[1]
        self.NumFrames = params[2]
        self.NumMarkers = params[3]
        self.Units = params[4]
        self.OrigDataRate = params[5]
        self.OrigDataStartFrame = params[6]
        self.OrigNumFrames = params[7]

        self.MarkerNames = cont[3].rstrip('\n').split('\t')
        self.Channels = cont[4].rstrip('\n').split('\t')

        self.Motion = []
        for i in range(int(self.NumFrames)):
            tmp_cont = cont[5+i].rstrip('\n').split('\t')  # 5 is first data line Structure: Frame#, Time, MarkerName1, '', '' MarkerName2, ...
            frame_tmp = []
            for j in range(2, len(tmp_cont)):
                if self.MarkerNames[j] is not '':
                    marker_name_memory = self.MarkerNames[j]
                frame_tmp.append([marker_name_memory, self.Channels[j], tmp_cont[j]])
            self.Motion.append([tmp_cont[1], frame_tmp])

    def trajectory(self, start=0, end=-1, normalize=''):
        """
        Changes data type rom string to float, channels contains ordered list of marker names and channels.
        Note: if marker is missing from frame the list is shortened for given frame
        :return: list of lists of floats, list of [marker name, channel]
        """
        if end == -1:
            end = len(self.Motion)
        if (0 <= start < end) and end <= len(self.Motion):
            trajectory = []
            channels = []

            invalid_channels = []
            for j in range(start, end):
                frame = self.Motion[j]
                for channel in frame[1]:
                    if channel[2] == '':
                        invalid_channels.append(channel[0])

            invalid_channels = set(invalid_channels)

            for j in range(start, end):
                frame = self.Motion[j]
                frame_values = []
                for i in range(len(frame[1])):
                    if frame[1][i][0] not in invalid_channels:
                        tmp = float(frame[1][i][2])
                        frame_values.append(tmp)
                        if j == start:
                            channels.append([frame[1][i][0], frame[1][i][1]])
                trajectory.append(frame_values)
            trajectory_array = np.array(trajectory)

            if normalize != '':
                x_zero = [i for i, ch in enumerate(channels) if normalize in ch and 'X' in ch[1]]
                y_zero = [i for i, ch in enumerate(channels) if normalize in ch and 'Y' in ch[1]]
                z_zero = [i for i, ch in enumerate(channels) if normalize in ch and 'Z' in ch[1]]

                x_coords = [i for i, ch in enumerate(channels) if 'X' in ch[1]]
                y_coords = [i for i, ch in enumerate(channels) if 'Y' in ch[1]]
                z_coords = [i for i, ch in enumerate(channels) if 'Z' in ch[1]]

                for i in range(len(x_zero)):
                    trajectory_array[:, x_coords] = trajectory_array[:, x_coords] - trajectory_array[:, x_zero]
                    trajectory_array[:, y_coords] = trajectory_array[:, y_coords] - trajectory_array[:, y_zero]
                    trajectory_array[:, z_coords] = trajectory_array[:, z_coords] - trajectory_array[:, z_zero]

            return trajectory_array, channels
        else:
            print('start or end is out of bounds.')

