import numpy as np


def EAF_parse(eaf_file_name):
    """

    :param eaf_file_name:
    :return:
    """
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
    """

    :param _annotation:
    :param custom_tiers:
    :return:
    """
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
        if line[2] == 'Right hand':
            new_item['right_hand'] = line[3]
            rh_ts = [line[0], line[1]]
            if rh_ts != tmp_ts:
                print('right hand has different time-stamps then default: {} vs {}'.format(rh_ts, tmp_ts))
        if line[2] == 'Left hand':
            new_item['left_hand'] = line[3]
            lh_ts = [line[0], line[1]]
            if lh_ts != tmp_ts:
                print('left hand has different time-stamps then default: {} vs {}'.format(lh_ts, tmp_ts))
    time_list.append(new_item)
    return time_list


def process_eaf(eaf_file):
    """
    Reads EAF file and returns annotation
    :param eaf_file:
    :return:
    """
    read_annot = EAF_parse(eaf_file)
    timed_annotations = annotation2signs(read_annot)
    return timed_annotations


def EAF_write(eaf_reference_file, eaf_outfile, annotation, dictionary, media_orig, media_target):
    """

    :param eaf_reference_file:
    :param eaf_outfile:
    :param annotation:
    :param dictionary:
    :param media_orig:
    :param media_target:
    :return:
    """
    with open(eaf_reference_file, 'r') as f:
        src_eaf = f.readlines()
    header = []
    for i, line in enumerate(src_eaf):
        if media_orig in line:
            line = line.replace(media_orig, media_target)
        header.append(line)
        if '</HEADER>' in line:
            break
    tss = np.zeros(2*len(annotation))
    default_tier = []
    rh = []
    lh = []
    print(np.shape(tss))
    for i, line in enumerate(annotation):
        print('{} : {}'.format(line['default'], line['time_stamps']))
        tss[2*i] = int(line['time_stamps'][0])
        tss[2*i+1] = int(line['time_stamps'][1])
        default_tier.append(line['default'])
        if line['default'] == 'T':
            rh.append('')
            lh.append('')
        elif line['default'] == 'transition':
            rh.append('')
            lh.append('')
        else:
            match = [d for d in dictionary if d['annot_default'] == line['default'] and media_orig.split('.')[0] in d['mocap_source_file']]
            if len(match) < 1:
                print(line)
            else:
                if 'annot_right_hand' in match[0].keys():
                    print('RH: {}'.format(match[0]['annot_right_hand']))
                    rh.append(match[0]['annot_right_hand'])
                else:
                    rh.append('')    
                if 'annot_left_hand' in match[0].keys():
                    print('LH: {}'.format(match[0]['annot_left_hand']))
                    lh.append(match[0]['annot_left_hand'])
                else:
                    lh.append('')
    output_ts = ['    <TIME_ORDER>\n']
    for i in range(len(tss)):
        output_ts.append('        <TIME_SLOT TIME_SLOT_ID="ts{}" TIME_VALUE="{}"/>\n'.format(i+1, int(tss[i])))
    output_ts.append('    </TIME_ORDER>\n')
    output_def = ['    <TIER LINGUISTIC_TYPE_REF="default-lt" TIER_ID="default">\n']
    output_rh = ['    <TIER LINGUISTIC_TYPE_REF="default-lt" TIER_ID="Right hand">\n']
    output_lh = ['    <TIER LINGUISTIC_TYPE_REF="default-lt" TIER_ID="Left hand">\n']
    alignment_incremetor = 1
    for i, (line, r, l) in enumerate(zip(default_tier, rh, lh)):
        output_def.append('        <ANNOTATION>\n')
        output_def.append('            <ALIGNABLE_ANNOTATION ANNOTATION_ID="a{}"\n'.format(alignment_incremetor))
        output_def.append('                TIME_SLOT_REF1="ts{}" TIME_SLOT_REF2="ts{}">\n'.format(2*i+1, 2*i+2))
        output_def.append('                <ANNOTATION_VALUE>{}</ANNOTATION_VALUE>\n'.format(line))
        output_def.append('            </ALIGNABLE_ANNOTATION>\n        </ANNOTATION>\n')
        alignment_incremetor += 1
        if r is not '':
            output_rh.append('        <ANNOTATION>\n')
            output_rh.append('            <ALIGNABLE_ANNOTATION ANNOTATION_ID="a{}"\n'.format(alignment_incremetor))
            output_rh.append('                TIME_SLOT_REF1="ts{}" TIME_SLOT_REF2="ts{}">\n'.format(2*i+1, 2*i+2))
            output_rh.append('                <ANNOTATION_VALUE>{}</ANNOTATION_VALUE>\n'.format(r))
            output_rh.append('            </ALIGNABLE_ANNOTATION>\n')
            output_rh.append('        </ANNOTATION>\n')
            alignment_incremetor += 1
        if l is not '':
            output_lh.append('        <ANNOTATION>\n')
            output_lh.append('            <ALIGNABLE_ANNOTATION ANNOTATION_ID="a{}"\n'.format(alignment_incremetor))
            output_lh.append('                TIME_SLOT_REF1="ts{}" TIME_SLOT_REF2="ts{}">\n'.format(2*i+1, 2*i+2))
            output_lh.append('                <ANNOTATION_VALUE>{}</ANNOTATION_VALUE>\n'.format(l))
            output_lh.append('            </ALIGNABLE_ANNOTATION>\n')
            output_lh.append('        </ANNOTATION>\n')
            alignment_incremetor += 1
    output_def.append('    </TIER>\n')
    output_rh.append('    </TIER>\n')
    output_lh.append('    </TIER>\n')
    
    end_statement = src_eaf[-10:]
    
    new_content = header+output_ts+output_def+output_rh+output_lh+end_statement
   
    with open(eaf_outfile, 'w') as f:
        for line in new_content:
            f.write(line)