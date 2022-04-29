def EAF_parse(eaf_file_name):
    with open(eaf_file_name, 'r') as f:
        tmp = f.readlines()
    time_stamps = []
    annotation = []
    tier = ''
    for i, line in enumerate(tmp):
        if '<TIME_SLOT TIME_SLOT_ID=' in line:
            stamp = line.split('"')[3]
            time_stamps.append(stamp)
        elif '<TIER LINGUISTIC_TYPE_REF="default-lt" TIER_ID=' in line:
            tier = line.split('"')[3]
        elif 'ANNOTATION_ID=' in line:
            ts_line = tmp[i+1].split('"')
            ts_values = (int(ts_line[1].replace('ts', '')), int(ts_line[3].replace('ts', '')))
        elif '<ANNOTATION_VALUE>' in line:
            line = line.replace('>', '<')
            annotation_value = line.split('<')
            annotation.append((int(time_stamps[ts_values[0]-1]), int(time_stamps[ts_values[1]-1]), tier, annotation_value[2]))
    return annotation


def annotation2signs(_annotation, custom_tiers=None):
    if custom_tiers:
        if len(custom_tiers) != 3:
            print('dim of tiers must be 3, using default tiers')
            tiers = ['default', 'Right Hand', 'Left Hand']
    else:
        tiers = ['default', 'Right Hand', 'Left Hand']

    _annotation = sorted(_annotation, key=lambda x: x[0])
    time_list = []
    for i, line in enumerate(_annotation):
        if 'new_item' in locals() and line[2] == 'default':
            time_list.append(new_item)
        if line[2] == 'default':
            tmp_ts = [line[0], line[1]]
            new_item = {'time_stamps' : tmp_ts, 'default' : line[3]}
        if line[2] == 'Right Hand':
            new_item['right_hand'] = line[3]
            rh_ts = [line[0], line[1]]
            if rh_ts != tmp_ts:
                print('right hand has different time-stamps then default: {} vs {}'.format(rh_ts, tmp_ts))
        if line[2] == 'Left Hand':
            new_item['left_hand'] = line[3]
            lh_ts = [line[0], line[1]]
            if lh_ts != tmp_ts:
                print('left hand has different time-stamps then default: {} vs {}'.format(lh_ts, tmp_ts))
    time_list.append(new_item)
    return time_list


def process_eaf(eaf_file):
    read_annot = EAF_parse(eaf_file)
    timed_annotations = annotation2signs(read_annot)
    return timed_annotations
