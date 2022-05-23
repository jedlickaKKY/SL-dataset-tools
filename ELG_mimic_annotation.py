import os
import argparse
import numpy as np
import pickle
from lib import trc_parser, trc_writer, sign_dictionary, dtw_compare, eaf_processing


def read_time_synchro_file(file_path, synchro_take):
    with open(file_path, 'r') as f:
        content = f.readlines()

    synchro_list = []
    for line in content:
        tmp = line.strip().split('\t')
        synchro_list.append(tmp)

    searched_synchro = [s for s in synchro_list if (s[0] == synchro_take[0] and s[1] in synchro_take[1])]
    if not searched_synchro:
        return -1
    if searched_synchro[0][4] == '':
        return -1
    return searched_synchro[0]


def recalculate_time_stamps(synchro, in_time, in_units='ms', out_fps=100):
    if len(synchro) > 2:
        if synchro[5] != '':
            if in_units == 'ms':
                in_units2seconds = 0.001
            else:
                print('Bad units!')

            ts = float(synchro[5].replace(',','.'))
            fs = int(synchro[4])

            out_time = ((np.asarray(in_time)*in_units2seconds - ts) * out_fps + fs).astype(int)

            return out_time
        else:
            return -1

        
def create_dictionary(trc_path, mocap_session, eaf_path, synchro, dictionary):

    the_dict = []
    take_name = os.path.splitext(os.path.split(trc_path)[1])[0]
    loaded_annot = eaf_processing.process_eaf(eaf_path)
    session = mocap_session
    synchro = read_time_synchro_file(synchro, [session, take_name[:-3]])

    for line in loaded_annot:
        new_sign = {}
        new_sign['mocap_source_file'] = os.path.join(session, take_name)
        new_sign['annot_file'] = os.path.join(session, os.path.splitext(eaf_path)[0])
        # new_sign['sl_annotator'] = annotator_code
        new_sign['video_time_stamp'] = line['time_stamps']
        new_sign['mocap_time_stamp'] = recalculate_time_stamps(synchro, line['time_stamps'])
        new_sign['mocap_cleaner'] = synchro[6]
        new_sign['signer'] = session[-2:]
        new_sign['annot_default'] = line['default']
        if 'right_hand' in line.keys():
            new_sign['annot_right_hand'] = line['right_hand']
        if 'left_hand' in line.keys():
            new_sign['annot_left_hand'] = line['left_hand']
        new_sign['codified_meaning'] = ''

        for dict_item in the_dict:
            if (new_sign['mocap_source_file'] == dict_item['mocap_source_file']) \
                    and (new_sign['mocap_time_stamp'] == dict_item['mocap_time_stamp']).all():
                print('match found : {}'.format(new_sign))
                continue
        the_dict.append(new_sign)

    sign_dictionary.save_dictionary(the_dict, dictionary)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Makes annotation based on template annotation and dtw matching of TRC files.')
    parser.add_argument('src_eaf', type=str, help='Template EAF file path')
    parser.add_argument('tar_eaf', type=str, help='New EAF file path')
    parser.add_argument('src_trc', type=str, help='Template TRC file path')
    parser.add_argument('tar_trc', type=str, help='Target TRC file path')
    parser.add_argument('session', type=str, help='MoCap session name')
    parser.add_argument('synchro', type=str, help='Synchronization file path')
    args = parser.parse_args()

    src_eaf_file = args.src_eaf
    new_eaf_file = args.tar_eaf
    src_trc = args.src_trc
    tar_trc = args.tar_trc
    session = args.session

    synchro_file = args.synchro
    dictionary_file = '/home/jedle/data/ELG/TEST/dict_tmp.pkl'

    normalize_data = 'STRN'
    annotator_name = 'A0'

    old_media_name = os.path.split(src_trc)[1][:-7] + '.mp4'
    new_media_name = os.path.split(tar_trc)[1][:-7] + '.mp4'
    signer = tar_trc.split('.')[0][-2:]

#     os.system('python3 create_dict.py {} {} {} {} {}'.format(src_trc, session, src_eaf_file, synchro_file, dictionary_file))
    create_dictionary(src_trc, session, src_eaf_file, synchro_file, dictionary_file)

    dictionary = sign_dictionary.load_dictionary(dictionary_file)
    path = dtw_compare.annotation_matching(src_trc, tar_trc, normalization=normalize_data)

    ret = []
    for item in dictionary:
        if item['annot_default'] not in ['T', 'transition', 'rest']:
            tmpS, tmpE = tuple(item['mocap_time_stamp'])
            newS = ([a[1] for a in path if a[0] == tmpS])
            newE = ([a[1] for a in path if a[0] == tmpE])
            resp = [item['annot_default'], newS, newE]
            if 'annot_right_hand' in item.keys():
                resp.append(item['annot_right_hand'])
            else:
                resp.append('-1')
            if 'annot_left_hand' in item.keys():
                resp.append(item['annot_left_hand'])
            else:
                resp.append('-1')
            ret.append(resp)
            for item_tar in dictionary:
                if item_tar['annot_default'] == item['annot_default']:
                    ret.append(item_tar['mocap_time_stamp'])

    new_annot = []
    new_ts = []
    tmp = []
    for i, line in enumerate(ret):
        if len(line) > 2:
            if tmp != []:
                new_ts.append(tmp)
            new_annot.append([line[0], line[3], line[4]])
            tmp = []
        else:
            tmp.append(line)

    time_pointer = 0
    new_annot_simple = []
    for k, l in zip(new_annot, new_ts):
        if len(l) == 1:
            new_annot_simple.append([k, l[0]])
            time_pointer = l[0][1]
        else:
            l_arr = abs(np.asarray(l) - time_pointer)
            choice = (np.argmin(l_arr[:,0]))
            new_annot_simple.append([k, l[choice]])
            time_pointer = l[choice][1]

    with open(synchro_file, 'r') as f:
        cont = f.readlines()

    for i, line in enumerate(cont):
        if len(line.split('\t')) < 2:
            del cont[i]

    match = [c for c in cont if c.split('\t')[1] in new_media_name][0].split('\t')
    cut_time = float(match[5].replace(',','.'))
    cut_frame = float(match[4])

    annotation_to_write = []
    for line in new_annot_simple:
        ts = line[1][0]
        te = line[1][1]
        new_ts = int((ts-cut_frame)*10 + cut_time*1000)
        new_te = int((te-cut_frame)*10 + cut_time*1000)
        new_item = {'default' : line[0][0], 'time_stamps' : [new_ts, new_te]}
        if line[0][1] is not '-1':
            new_item['annot_right_hand'] = line[0][1]
        if line[0][2] is not '-1':
            new_item['annot_reft_hand'] = line[0][2]
        annotation_to_write.append(new_item)

    filled_annotation = []
    for i, line in enumerate(annotation_to_write):
        filled_annotation.append(line)
        if len(annotation_to_write) > i+1:
            filled_annotation.append({'default' : 'transition', 'time_stamps' : [line['time_stamps'][1], annotation_to_write[i+1]['time_stamps'][0]]})

    eaf_processing.EAF_write(src_eaf_file, new_eaf_file, filled_annotation, dictionary, old_media_name, new_media_name)