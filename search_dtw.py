import os
import numpy as np
import fastdtw
import pickle
from lib import trc_parser, sign_dictionary, dtw_compare

if __name__ == '__main__':
    dict_file = '/home/jedle/data/ELG/DATABASE/GLOBAL/dict.pkl'
    # in_trc = '/home/jedle/data/ELG/DATABASE/TRC/2021-08-17-ELG-WF-PK-2/2016-10-02-c-JK.trc'
    # in_eaf = '/home/jedle/data/ELG/DATABASE/ANNOT/2021-08-17-ELG-WF-PK-2/2016-10-02-c-KN.eaf'

    target_trc = os.path.join('/home/jedle/data/ELG/DATABASE/TRC/2021-06-24-ELG-WF-PK/2016-09-20-b-PJ.trc')

    src_trc = '2021-06-24-ELG-WF-PK/2016-09-20-a'
    dictionary = sign_dictionary.load_dictionary(dict_file)
    omitted_signs = ['transition', 'T', 'rest']

    results = []
    for sign in dictionary:
        if src_trc in sign['annot_file'] and sign['annot_default'] not in omitted_signs:
            print('searching for : {}'.format(sign['annot_default']))
            in_trc = os.path.join('/home/jedle/data/ELG/DATABASE/TRC/', sign['mocap_source_file'])
            pars = trc_parser.trc(in_trc)
            trajectory_query, channels_query = pars.trajectory(sign['mocap_time_stamp'][0], sign['mocap_time_stamp'][1])
            res = dtw_compare.query(trajectory_query, target_trc, channels_query, topN=1, delta=[-1, 1])
            print('Best match: {}'.format(res))
            results.append([sign, res])
            # break

    # print(results[0][0]['annot_default'])
    # print(results[0][1])
    with open('anot.pkl', 'bw') as f:
         pickle.dump(results, f)
