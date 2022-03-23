def write_trc(trc_data):
    content = trc_data.Header.copy()
    line3 = [trc_data.DataRate, trc_data.CameraRate, trc_data.NumFrames, trc_data.NumMarkers, trc_data.Units, trc_data.OrigDataRate, trc_data.OrigDataStartFrame, trc_data.OrigNumFrames]
    content.append('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(*line3))
    # trc_data.MarkerNames = cont[3].rstrip('\n').split('\t')
    # trc_data.Channels = cont[4].rstrip('\n').split('\t')

    return content
