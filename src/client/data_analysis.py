"""
    Author: Gavin Heidenreich
    Email: gheidenr@uottawa.ca
    Organization: University of Ottawa (Silasi Lab)
"""

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

'''
This class takes the h5 file created by deeplabcut.triangulate() and extracts a csv from the x, y, z coordinates within.
You can add metrics to the csv that this class outputs by passing their names in a list to the metrics argument. List of metrics can be seen below.

metrics:
sd: standard deviation over a specified rolling window
peak_velocity_point: takes the difference between each value as data[n+1] - data[n], gets the mean over a specified rolling window,
    then normalizes the data between -1 and 1. 1 is the point of peak velocity forwards, and -1 is the point of peak velocity moving
    backwards.
'''


h5_file_path = '/home/gavin/Documents/python_projects/DLC/stereo_2nd-silasi_lab-2020-07-31-3d/2020-07-29_(15-41-23)_00783A32F484_16_2024_DLC_3D.h5'
set_of_metrics = {'peak_velocity_point'}
list_of_bodyparts = ['index', 'pinky', 'hand']

class h5_to_csv:
    def __init__(self, h5_file_path, list_of_bodyparts, list_of_metrics, sliding_window_num_frames):
        self.set_of_metrics = set_of_metrics
        self.df = pd.read_hdf(h5_file_path)
        self.df.dropna(how='all', inplace=True)
        self.sliding_window_num_frames = sliding_window_num_frames
        self.list_of_bodyparts = list_of_bodyparts

    def print_csv_output(self):
        print(self.df.isna().sum())
        print(self.df[500:550])

    # requires 50% of data in window or will fill as NaN
    # change dimensions to 2 if using 2D data, 3 for 3D data
    def add_metrics(self):
        coords = ['x', 'y', 'z']
        col_names = []
        dimensions = 3
        N = len(self.list_of_bodyparts)
        idx = pd.IndexSlice
        if 'peak_velocity_point' in self.set_of_metrics:  
            for bp in self.list_of_bodyparts:
                for coord in coords:
                    self.df['metrics', bp, coord + '_diff'] = self.df.loc[:, ('DLC_3D', bp, coord)].diff()
                    self.df['metrics', bp, coord + '_diff_ma'] = self.df.loc[:, ('metrics', bp, coord + '_diff')].rolling(self.sliding_window_num_frames, self.sliding_window_num_frames//2).mean()
                    tmp = self.df['metrics', bp, coord + '_diff_ma']
                    self.df['metrics', bp, coord + '_diff_ma_scaled'] = 2 * ((tmp - tmp.min())/ (tmp.max() - tmp.min())) - 1
                    self.df.drop(columns= coord + '_diff_ma', level=2, inplace=True)
                    self.df.drop(columns= coord + '_diff', level=2, inplace=True)
                    col_names.extend(['metrics', bp, coord + '_diff_ma_scaled'])

            self.df['velocity'] = self.df.loc[:, idx['metrics', 4:6, (N*dimensions)+1:]] # .apply(lambda x: abs(x)).sum()/(N*dimensions)
            

        if 'sd' in self.set_of_metrics:
            for bp in self.list_of_bodyparts:
                for coord in coords:
                    self.df['metrics', bp, coord + '_std'] = self.df.loc[:, ('DLC_3D', bp, coord)].rolling(self.sliding_window_num_frames, self.sliding_window_num_frames//2).std()

        

csvMaker = h5_to_csv(h5_file_path, list_of_bodyparts, set_of_metrics, 15)
csvMaker.add_metrics()
csvMaker.print_csv_output()

