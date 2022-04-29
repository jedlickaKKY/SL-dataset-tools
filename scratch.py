import os
import numpy as np
import pickle
from lib import trc_parser, trc_writer, sign_dictionary

if __name__ == '__main__':
    dict_file = '/home/jedle/data/ELG/DATABASE/GLOBAL/dict.pkl'
    # in_trc = '/home/jedle/data/ELG/DATABASE/TRC/2021-08-17-ELG-WF-PK-2/2016-10-02-c-JK.trc'
    # in_eaf = '/home/jedle/data/ELG/DATABASE/ANNOT/2021-08-17-ELG-WF-PK-2/2016-10-02-c-KN.eaf'
    cont = sign_dictionary.load_dictionary(dict_file)

    pick = 4
    picked_sign = cont[4]

    # print(picked_sign)
    in_trc = os.path.join('/home/jedle/data/ELG/DATABASE/TRC/', picked_sign['mocap_source_file'])

    pars = trc_parser.trc(in_trc)
    # trajectory, channels = pars.trajectory(picked_sign['mocap_time_stamp'][0], picked_sign['mocap_time_stamp'][1])
    trajectory, channels = pars.trajectory(0, 20)

    # print(len(channels))
    # print(channels)
    # print(np.shape(trajectory))

# # print(pars.MarkerNames)
    #
    # # print(picked_sign['mocap_time_stamp'])
    # # print(np.shape(trajectory))
    # picked_trajectory = trajectory[picked_sign['mocap_time_stamp'][0]:picked_sign['mocap_time_stamp'][1], :]
    # picked_channels = channels[picked_sign['mocap_time_stamp'][0]:picked_sign['mocap_time_stamp'][1]]
    #
    # # print(len(picked_trajectory))
    # # print(trajectory[0])
    #
    trc_writer.write_trc('/home/jedle/data/ELG/pokus2.trc', pars, trajectory, channels)

