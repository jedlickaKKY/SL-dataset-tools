import os

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

        # print(len(cont[5].rstrip('\n').split('\t')[2:]))
        # print((cont[5].rstrip('\n').split('\t')[2:]))
        val = [a for a in cont[5].rstrip('\n').split('\t')[2:] if a is not '']
        # print(len(val))
        self.Motion = []
        for i in range(int(self.NumFrames)):
            tmp_cont = cont[5+i].rstrip('\n').split('\t')  # 5 is first data line Structure: Frame#, Time, MarkerName1, '', '' MarkerName2, ...
            frame_tmp = []
            for j in range(2, len(val)+2):
                if self.MarkerNames[j] is not '':
                    marker_name_memory = self.MarkerNames[j]
                # frame_tmp.append([self.MarkerNames[j], self.Channels[j], tmp_cont[j]])
                frame_tmp.append([marker_name_memory, self.Channels[j], tmp_cont[j]])
            self.Motion.append([tmp_cont[1], frame_tmp])

    def trajectory(self):
        """
        Changes data type rom string to float, channels contains ordered list of marker names and channels.
        Note: if marker is missing from frame the list is shortened for given frame
        :return: list of lists of floats, list of [marker name, channel]
        """
        trajectory = []
        channels = []
        for j in range(len(self.Motion)):
            frame = self.Motion[j]
            frame_values = []
            valid_channels = []
            for i in range(len(frame[1])):
                if frame[1][i][2] is not '':
                    tmp = float(frame[1][i][2])
                    frame_values.append(tmp)
                    valid_channels.append([frame[1][i][0], frame[1][i][1]])
            trajectory.append(frame_values)
            channels.append(valid_channels)
        return trajectory, channels

