import os

# path = '/home/jedle/data/ELG/DATABASE_tmp/ANNOT/'
path = '/home/jedle/data/ELG/DATABAZE/TRC/'
# dir_list = os.listdir(path)
# dir_list = ['2021-10-11-ELG-MartinKulda-zvirata3']
dir_list = ['2021-12-09-ELG-ZOO-MS-2']
do_swap = True

for tmp_directory in dir_list:
    tmp_file_list = os.listdir(os.path.join(path, tmp_directory))
    for tmp_file in tmp_file_list:
        if do_swap:
            new_name = tmp_file[:-6] + 'A.trc'
        elif tmp_file[0] == '2' and 'split' not in tmp_file:
            tmp_file[0:15].replace('.', '-')
            tmp_file[0:15].replace('_', '-')
            tmp_file[0:15].replace('--', '-')
            tmp_file.replace(' ', '')
            year = tmp_file[:4]
            month = tmp_file[5:7]
            day = tmp_file[8:10]
            variant = tmp_file[11]
            annotator = tmp_file[13:15]

            # print(tmp_file)
            new_name = '{:04d}-{:02d}-{:02d}-{}-{}.eaf'.format(int(year), int(month), int(day), variant, annotator)
            # print(new_name)
        else:
            new_name = tmp_file[:-7] + '_' + tmp_file[-6:-4] + '.eaf'
        print(tmp_file)
        print(new_name)

        os.rename(os.path.join(path, tmp_directory, tmp_file), os.path.join(path, tmp_directory, new_name))