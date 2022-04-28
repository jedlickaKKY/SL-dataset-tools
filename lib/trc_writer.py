import numpy as np

def write_trc(trc_file, trc_data, trajectory, channels, startFrameNumber=1):
    content = trc_data.Header.copy()

    line3 = [trc_data.DataRate, trc_data.CameraRate, str(len(trajectory)), trc_data.NumMarkers, trc_data.Units, trc_data.OrigDataRate, trc_data.OrigDataStartFrame, trc_data.OrigNumFrames]
    content.append('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(*line3))
    line = ''
    for item in trc_data.MarkerNames:
        line += item + '\t'
    line = line[:-1] + '\n'
    content.append(line)
    line = ''
    for item in trc_data.Channels:
        line += item + '\t'
    line = line[:-1] + '\n'
    content.append(line)

    for i in range(np.size(trajectory, 0)):
        line = str(i+startFrameNumber) + '\t' + str(float(i)/float(trc_data.CameraRate)) +'\t'  # frame number, time
        for e, ch in enumerate(trc_data.Channels[2:]):
            column = ([ex for ex, x in enumerate(channels) if x[1] == ch])
            if column:
                line += str(trajectory[i, column[0]]) + '\t'
            else:
                line += '\t'
        line = line[:-2] + '\n'
        content.append(line)
    with open(trc_file, 'w') as f:
        f.writelines(content)
