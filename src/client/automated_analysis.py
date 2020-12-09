"""
    Author: Gavin Heidenreich
    Email: gheidenr@uottawa.ca
    Organization: University of Ottawa (Silasi Lab)
"""

# import deeplabcut
from subprocess import Popen, PIPE
from datetime import date
from random import sample
import math
import os
import time
from data_utils import thirds_w_handedness

# edit these values to choose what action you want this script to do
# needed for main()
download = False
analyze = True
upload = False

# need these if filtering by date (range is inclusive, so to sample from one day just make both dates the same)
start_date = '2020-11-26'
end_date = '2020-11-27'

# need these for analysis
cage_num_to_3d_project_path_dict = {19: '/path/to/3d_project_config', 22: '/path/to/3d_project_config'}
output_dir_path = '/mnt/4T/automated_analysis/'

# need this to split videos
handedness_file_path = '/path/to/handedness.txt'
split_videos_output_path = '/mnt/4T/split_videos_to_analyze'

# can use this for testing download_videos
vid_paths = ['2020-11-28_(00-44-18)_002FBE7331D3_22_753.avi', '2020-11-27_(23-54-05)_002FBE7331D3_22_747.avi', '2020-11-27_(23-25-56)_002FBE7331D3_22_741.avi', '2020-11-27_(22-52-57)_002FBE7331D3_22_736.avi', '2020-11-27_(21-38-59)_002FBE7331D3_22_725.avi', '2020-11-27_(20-35-00)_002FBE7331D3_22_712.avi', '2020-11-28_(00-28-32)_002FBE7331D3_22_752.avi', '2020-11-28_(00-05-48)_002FBE7331D3_22_748.avi', '2020-11-27_(23-50-31)_002FBE7331D3_22_746.avi', '2020-11-27_(23-36-08)_002FBE7331D3_22_742.avi', '2020-11-27_(23-18-39)_002FBE7331D3_22_740.avi', '2020-11-27_(23-07-02)_002FBE7331D3_22_738.avi', '2020-11-27_(22-14-37)_002FBE7331D3_22_734.avi', '2020-11-27_(20-13-30)_002FBE7331D3_22_708.avi', '2020-11-27_(21-52-18)_002FBE7331D3_22_727.avi', '2020-11-27_(21-33-04)_002FBE7331D3_22_722.avi', '2020-11-27_(20-56-58)_002FBE7331D3_22_716.avi', '2020-11-27_(22-13-43)_002FBE7331D3_22_733.avi', '2020-11-27_(21-54-59)_002FBE7331D3_22_728.avi', '2020-11-27_(21-43-35)_002FBE7331D3_22_726.avi', '2020-11-27_(21-36-09)_002FBE7331D3_22_724.avi', '2020-11-27_(21-24-10)_002FBE7331D3_22_720.avi', '2020-11-27_(20-25-01)_002FBE7331D3_22_710.avi', '2020-11-27_(21-06-09)_002FBE7331D3_22_718.avi', '2020-11-27_(20-48-25)_002FBE7331D3_22_714.avi', '2020-11-27_(20-08-24)_002FBE7331D3_22_705.avi', '2020-11-27_(20-54-17)_002FBE7331D3_22_715.avi', '2020-11-27_(20-45-30)_002FBE7331D3_22_713.avi', '2020-11-27_(20-32-33)_002FBE7331D3_22_711.avi', '2020-11-27_(20-05-26)_002FBE7331D3_22_703.avi', '2020-11-27_(20-19-10)_002FBE7331D3_22_709.avi', '2020-11-27_(20-13-06)_002FBE7331D3_22_707.avi', '2020-11-27_(20-03-17)_002FBE7331D3_22_702.avi', '2020-11-27_(20-06-46)_002FBE7331D3_22_704.avi', '2020-11-27_(19-40-13)_002FBE7331D3_22_700.avi', '2020-11-27_(19-39-16)_002FBE7331D3_22_699.avi', '2020-11-27_(19-16-02)_002FBE7331D3_22_698.avi', '2020-11-27_(19-15-05)_002FBE7331D3_22_697.avi', '2020-11-27_(17-08-50)_002FBE7331D3_22_694.avi', '2020-11-27_(16-53-48)_002FBE7331D3_22_693.avi', '2020-11-27_(10-39-35)_002FBE7331D3_22_683.avi', '2020-11-27_(14-20-00)_002FBE7331D3_22_691.avi', '2020-11-27_(05-29-28)_002FBE7331D3_22_650.avi', '2020-11-27_(11-33-10)_002FBE7331D3_22_689.avi', '2020-11-27_(09-45-08)_002FBE7331D3_22_674.avi', '2020-11-27_(00-15-58)_002FBE7331D3_22_621.avi', '2020-11-27_(14-19-05)_002FBE7331D3_22_690.avi', '2020-11-27_(11-23-27)_002FBE7331D3_22_687.avi', '2020-11-27_(10-20-27)_002FBE7331D3_22_679.avi', '2020-11-27_(06-25-40)_002FBE7331D3_22_663.avi', '2020-11-27_(01-59-29)_002FBE7331D3_22_638.avi', '2020-11-26_(21-34-48)_002FBE7331D3_22_592.avi', '2020-11-27_(11-30-46)_002FBE7331D3_22_688.avi', '2020-11-27_(10-47-50)_002FBE7331D3_22_685.avi', '2020-11-27_(10-36-07)_002FBE7331D3_22_681.avi', '2020-11-27_(10-02-09)_002FBE7331D3_22_677.avi', '2020-11-27_(09-39-17)_002FBE7331D3_22_672.avi', '2020-11-27_(06-04-45)_002FBE7331D3_22_657.avi', '2020-11-27_(05-12-30)_002FBE7331D3_22_643.avi', '2020-11-27_(00-57-14)_002FBE7331D3_22_631.avi', '2020-11-26_(23-05-19)_002FBE7331D3_22_611.avi', '2020-11-26_(11-40-18)_002FBE7331D3_22_553.avi', '2020-11-27_(10-46-50)_002FBE7331D3_22_684.avi', '2020-11-27_(10-39-05)_002FBE7331D3_22_682.avi', '2020-11-27_(10-24-06)_002FBE7331D3_22_680.avi', '2020-11-27_(10-16-26)_002FBE7331D3_22_678.avi', '2020-11-27_(09-58-39)_002FBE7331D3_22_675.avi', '2020-11-27_(09-42-56)_002FBE7331D3_22_673.avi', '2020-11-27_(06-41-34)_002FBE7331D3_22_669.avi', '2020-11-27_(06-16-14)_002FBE7331D3_22_661.avi', '2020-11-27_(05-56-40)_002FBE7331D3_22_655.avi', '2020-11-27_(05-20-58)_002FBE7331D3_22_646.avi', '2020-11-27_(02-28-31)_002FBE7331D3_22_640.avi', '2020-11-27_(01-16-36)_002FBE7331D3_22_636.avi', '2020-11-27_(00-31-53)_002FBE7331D3_22_626.avi', '2020-11-26_(23-35-52)_002FBE7331D3_22_615.avi', '2020-11-26_(22-28-51)_002FBE7331D3_22_602.avi', '2020-11-26_(20-48-34)_002FBE7331D3_22_583.avi', '2020-11-26_(00-30-09)_002FBE7331D3_22_504.avi']


class download_videos:
    def __init__(self, cage_num, mouse_num, output_dir_path, start_date=None, end_date=None, sample_percentage=1, vid_paths=None):
        self.cage_num = cage_num
        self.mouse_num = mouse_num
        self.start_date = self.parse_date(start_date)
        self.end_date = self.parse_date(end_date)
        self.sample_percentage = sample_percentage
        self.vid_paths = vid_paths
        self.output_dir_path = output_dir_path + os.sep + 'HASRA' + str(cage_num) + os.sep + 'AnimalProfiles' + os.sep + 'MOUSE' + str(mouse_num) + os.sep + 'Videos' + os.sep

    def date_in_range(self, path):
        date_string = path.split('_')[0]
        date_obj = self.parse_date(date_string)
        if self.start_date <= date_obj <= self.end_date:
            return True
        else:
            return False
    
    def parse_date(self, date_string): # 2020-11-27 format
        date_string = date_string.split('-')
        y, m, d = int(date_string[0]), int(date_string[1]), int(date_string[2])
        date_obj = date(y, m, d)
        return date_obj

    def get_video_paths_from_rclone(self):
        cmd = ['rclone', 'ls', 'HASRA' + str(self.cage_num) + ':homecage_' + str(self.cage_num) + '_sync/AnimalProfiles/MOUSE' + str(self.mouse_num) + '/Videos']
        p = Popen(cmd, stdin=PIPE, stdout=PIPE)
        output = p.stdout.read().decode()
        output = output.replace('\n', ',')
        output = output.split(',')
        tmp = []

        for el in output:
            tmp_el = el.split(' ')
            tmp_el = [x for x in tmp_el if x != '']
            if len(tmp_el) > 0:
                tmp.append(tmp_el[1])
        
        self.vid_paths = tmp
        # output = tmp

        # return output

    def remove_paths_outside_date_range(self):
        if self.start_date not None and self.end_date not None:
            self.vid_paths = [x for x in self.vid_paths if self.date_in_range(x)]

    def select_sample(self):
        N = len(self.vid_paths)
        sample_size = int(math.floor((self.sample_percentage / 100) * N))
        s = sample(self.vid_paths, sample_size)

        self.vid_paths = s

    def download(self, vid_path):
        try:
            if not os.path.exists(self.output_dir_path):
                os.makedirs(self.output_dir_path)
        except OSError:
            print ('Error: Creating directory of data')
        cmd = ['rclone', '-P', 'copy', 'HASRA' + str(self.cage_num) + ':homecage_' + str(self.cage_num) + '_sync/AnimalProfiles/MOUSE' + str(self.mouse_num) + '/Videos/' + vid_path, self.output_dir_path]

    def download_loop(self):
        for vid in self.vid_paths:
            try:
                if not os.path.exists(self.output_dir_path):
                    os.makedirs(self.output_dir_path)
            except OSError:
                print ('Error: Creating directory of data')
            cmd = ['rclone', '-P', 'copy', 'HASRA' + str(self.cage_num) + ':homecage_' + str(self.cage_num) + '_sync/AnimalProfiles/MOUSE' + str(self.mouse_num) + '/Videos/' + vid, self.output_dir_path]

            p = Popen(cmd, stdin=PIPE)
            # have to wait until this p is finished before starting the next.. or at least cant call them all at once. Can I use barrier type obj?

            # A None value indicates that the process hasn't terminated yet.
            # poll = p.poll()
            # while poll is None: # p.subprocess is alive
            #     time.sleep(1)

            p.wait()



class cut_vids_on_reaches:
    def __init__(self):
        pass

class split_videos:
    def __init__(self, input_videos_dir):
        self.twh = thirds_w_handedness(input_videos_dir, split_videos_output_path, handedness_file_path)
    
    def split(self):
        self.twh.video_file_splitter()



# need to have a new project created for each hc so that calibration can be done independently
# this will have to be done manually in cli... for now
# need hashmap mapping cage_num -> 3d_project_path as argument for analyze_videos

class analyze_videos:
    def __init__(self, cage_num_to_3d_project_path_dict, input_dir, destfolder, by_mouse=False, mouse_num=None, by_date=False, start_date=None, end_date=None):
        self.cage_num_to_3d_project_path_dict = cage_num_to_3d_project_path_dict
        self.input_dir = input_dir
        self.destfolder = destfolder
        self.by_mouse = by_mouse
        self.mouse_num = mouse_num
        self.by_date = by_date
        self.start_date = start_date
        self.end_date = end_date

    def get_video_paths(self):
        pass

    def analyze(self):
        pass

class upload_videos:
    def __init__(self):
        pass

    def upload(self):
        pass


def main():
    if download:
        for cage_num in range(19, 23):
            for mouse_num in range(1, 6):
                dv = download_videos(cage_num, mouse_num, output_dir_path, start_date, end_date, sample_percentage=5, vid_paths=vid_paths)
                dv.get_video_paths_from_rclone()
                dv.remove_paths_outside_date_range()
                dv.select_sample()
                print(dv.vid_paths)
                dv.download_loop()
    
    if analyze:
        av = analyze_videos(cage_num_to_3d_project_path_dict)
    
    if upload:
        pass

if __name__ == '__main__':
    DEBUG = False

    if DEBUG:
        pass
    else:
        main()
        