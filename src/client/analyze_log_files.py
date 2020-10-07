import pandas as pd
import numpy as np
import os
import datetime
import argparse

'''
root_dir - Wave_1 - 001_Sham_Day42.csv
                  - 002_Sham_Day42.csv
         - Wave_2 - 003_Stroke_Day42.csv
                  - 004_Stroke_Day42.csv

Make your directory structure look like this and then pass this program the path of root_dir.

Steps to run:
    1: Navigate to the directory containing the program files
    cd [the directory containing main.py]

    In my case I did this with:
    cd /home/gavin/log_file_analyzer

    2: Run the program. 
    python3 main.py [root_dir]

    In my case I ran it with:
    python3 main.py '/home/gavin/log_file_analyzer/log_files'

    3: Check the results
    This program will create a csv file called "transposed_log_files.csv" in your current working directory.
    It might take a while to run so be patient.
'''


class get_files_list:
    def __init__(self, root_dir):
        self.filenames = []
        self.root_dir = root_dir

    def get_files(self):
        base_path = self.root_dir
        for wave in os.listdir(base_path):
            for f in os.listdir(base_path + os.sep + wave):
                self.filenames.append(base_path + os.sep + wave + os.sep + f)
    
    def get_wave_id_status_day(self, wave, fn):
        split_fn = fn.split('_')
        wave = wave
        animal_id = split_fn[0]
        status = split_fn[1]
        day = ''.join([x for x in split_fn[2] if x.isnumeric()])
        return wave, animal_id, status, day


class mod_df:
    def __init__(self, path, wave, animal_id, surgery_status, day_of_surgery):
        self.path = path
        self.wave = str(wave)
        self.animal_id = str(animal_id)
        self.surgery_status = surgery_status
        self.day_of_surgery = str(day_of_surgery)

    def create_df(self):
        df = pd.read_csv(self.path, header=None)
        df['session_time_in_tunnel'] = '' # datetime.datetime.strptime(str(df[7]) + ' ' + str(df[8]), '%d-%b-%Y %H:%M:%S')
        df['parsed_start'] = ''
        df['parsed_end'] = ''
        df['daily_time_in_tunnel'] = ''
        df['daily_time_in_tunnel_with_presentations'] = ''
        df['session_time_in_tunnel_with_presentations'] = ''
        df['num_entries'] = ''
        df['daily_presentations'] = ''
        df['parsed_start'] = df[5] + ' ' + df[6]
        df['parsed_end'] = df[7] + ' ' + df[8]
        df['parsed_start'].apply(lambda x: datetime.datetime.strptime(x, '%d-%b-%y %H:%M:%S'))
        df['parsed_end'].apply(lambda x: datetime.datetime.strptime(x, '%d-%b-%y %H:%M:%S'))
        df['parsed_start'] = pd.to_datetime(df['parsed_start'])
        df['parsed_end'] = pd.to_datetime(df['parsed_end'])
        df['session_time_in_tunnel'] = (df['parsed_end'] - df['parsed_start']).astype(int)//10**9
        df['session_time_in_tunnel_with_presentations'] = (df['parsed_end'] - df['parsed_start']).astype(int)//10**9

        # df['session_time_in_tunnel_with_presentations'] = np.where(df[4] > 0, (df['parsed_end'] - df['parsed_start']).astype(int)//10**9, np.where(df['session_time_in_tunnel_with_presentations'] == 0, 0))
        df['session_time_in_tunnel_with_presentations'] = np.where(df[4].between(1, 10**9, inclusive=True), (df['parsed_end'] - df['parsed_start']).astype(int)//10**9, np.where(df[4].between(0, 0, inclusive=False), 0, 0))

        df['daily_presentations'] = df.groupby([7])[4].cumsum()
        df['daily_time_in_tunnel'] = df.groupby([7])['session_time_in_tunnel'].cumsum()
        df['daily_time_in_tunnel_with_presentations'] = df.groupby([7])['session_time_in_tunnel_with_presentations'].cumsum()
        
        df2 = df.loc[df.groupby([7], sort=False)["parsed_end"].idxmax()]
        df2['num_entries'] = df2[0].diff()

        saved_val = df2[0]

        saved_val = saved_val.iloc[0]

        # print(saved_val)

        start_day = df[7][0]
        start_day = datetime.datetime.strptime(start_day, '%d-%b-%y')
        constant_data = {'animal_id': [self.animal_id], 'wave': [self.wave], 'cage_num': [df[1][0]], 'rfid': [df[3][0]], 'mouse_num': [df[2][0]], 'surgery_status': [self.surgery_status], 'surgery_day': [self.day_of_surgery]}
        for x, y in df2.iterrows():
            day_delta = (datetime.datetime.strptime(y[7], '%d-%b-%y') - start_day).days + 1# //10**9
            rowwise_data = {str(day_delta) + '_daily_time_in_tunnel': [y['daily_time_in_tunnel']], str(day_delta) + '_num_entries': [y['num_entries']], str(day_delta) + '_daily_time_in_tunnel_with_presentations': [y['daily_time_in_tunnel_with_presentations']], str(day_delta) + '_daily_presentations': [y['daily_presentations']]}
            tmp_df = pd.DataFrame(rowwise_data)
            df2 = pd.concat([df2, tmp_df], axis=1)

        # df2['1_num_entries'][0] = saved_val
        df2.loc[:, ('1_num_entries', 0)] = saved_val


        for i in range(9):
            del df2[i]

        del df2['session_time_in_tunnel']
        del df2['parsed_start']
        del df2['parsed_end']
        del df2['daily_time_in_tunnel']
        del df2['daily_time_in_tunnel_with_presentations']
        del df2['session_time_in_tunnel_with_presentations']
        del df2['num_entries']
        del df2['daily_presentations']

        df2 = df2[:1]

        df2 = df2.reindex(sorted(df2.columns, key=lambda x: x.split('_')[2]), axis=1)

        constant_df = pd.DataFrame(constant_data)

        constant_df = pd.concat([constant_df, df2], axis=1)

        return constant_df


def main(root_dir_path):
    DEBUG = False

    if DEBUG:
        gfl = get_files_list(root_dir_path)
        gfl.get_files()
    else:
        gfl = get_files_list(root_dir_path)
        gfl.get_files()

        main_df = pd.DataFrame()

        for csv in gfl.filenames:
            wave, animal_id, status, day = gfl.get_wave_id_status_day(csv.split(os.sep)[-2], csv.split(os.sep)[-1].split('.')[0])
            md = mod_df(csv, wave, animal_id, status, day)
            tmp_df = md.create_df()
            main_df = pd.concat([main_df, tmp_df], axis=0)


        main_df = main_df.sort_values(by='animal_id')
        main_df.to_csv('transposed_log_file.csv')
        print('done!')
parser = argparse.ArgumentParser()
parser.add_argument('path', help='enter the path to the root directory containing all the wave folders',
                    type=str)
args = parser.parse_args()

if __name__ == "__main__":
    main(args.path)