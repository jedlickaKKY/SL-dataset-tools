import os
import numpy as np
from lib import eaf_processing, sign_dictionary

def read_time_synchro_file(file_path, synchro_take):
    with open(file_path, 'r') as f:
        content = f.readlines()

    synchro_list = []
    for line in content:
        tmp = line.strip().split('\t')
        synchro_list.append(tmp)

    searched_synchro = [s for s in synchro_list if (s[0] == synchro_take[0] and s[1] == synchro_take[1][:-3])]
    if not searched_synchro:
        return -1
    if searched_synchro[0][4] == '':
        return -1
    return searched_synchro[0]


def recalculate_time_stamps(synchro, in_time, in_units='ms', out_fps=100):
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


if __name__ == '__main__':
    path_root = '/home/jedle/data/ELG/DATABASE'
    mocap_path = os.path.join(path_root, 'TRC')
    annot_path = os.path.join(path_root, 'ANNOT')
    glo_path = os.path.join(path_root, 'GLOBAL')
    time_synchro_file = os.path.join(glo_path, 'synchro.txt')
    dictionary_file = os.path.join(glo_path, 'dict_tmp2.pkl')

    load_dictionary = False
    if load_dictionary:
        the_dict = sign_dictionary.load_dictionary(dictionary_file)
    else:
        the_dict = []

    # mocap_session_list = os.listdir(mocap_path)
    mocap_session_list = ['2021-06-18-ELG-WF-FB']

#     signer = 'FB'
#     cleaner = 'TZ'


    for session in mocap_session_list:
        mocap_file_list = os.listdir(os.path.join(mocap_path, session))

        for mocap_take in mocap_file_list:
            take_name = os.path.splitext(mocap_take)[0]  # check naming convention
            tmp_mocap_file = os.path.join(mocap_path, session, mocap_take)
            annot_file_list = os.listdir(os.path.join(annot_path, session))
            tmp_annot_file = [n for n in annot_file_list if take_name[:-3] in n]
            if len(tmp_annot_file) > 0:  # existuje anotace k mocap souboru
                annotator_code = tmp_annot_file[0][13:15]

                if tmp_annot_file:
                    if len(tmp_annot_file) > 1:
                        print("confused naming")
                tmp_annot_file_name = os.path.join(annot_path, session, tmp_annot_file[0])
                tmp_annot = eaf_processing.process_eaf(tmp_annot_file_name)

                synchro = read_time_synchro_file(time_synchro_file, [session, take_name])
#                 print(synchro)
                if synchro == -1:
                    print('synchro not found. skipping {}'.format(tmp_mocap_file))
                    continue

                for line in tmp_annot:
                    new_sign = {}
                    new_sign['mocap_source_file'] = os.path.join(session, mocap_take)
                    new_sign['annot_file'] = os.path.join(session, tmp_annot_file[0])
                    new_sign['sl_annotator'] = annotator_code
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

    sign_dictionary.save_dictionary(the_dict, dictionary_file)
