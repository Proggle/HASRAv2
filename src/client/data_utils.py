import cv2
import os
from copy import deepcopy
from tqdm import tqdm
import numpy as np
from collections import Counter, defaultdict
from random import sample, seed


'''
What does this class do?
1. loads video input in avi form from stereo camera
2. splits the video in 2 and pseudo-randomly samples frames between start_time and end_time.
   You can change the factor by which the sampling is fixed to prevent consecutive sampling in
   the gen_sample method.
3. sampled frames are outputted to [your project dir]/calibration_images with the naming convention; camera-[cam number]-[frame number].jpg


note1: filenames from camera may contain brackets and other characters, failing to handle for
       this will cause the load_vid method to throw an OSErr
note2: if you want to use >99 calibration images (num_cal_imgs > 99), please change zfill(2)-> zfill(3)
       in the load_vid method. I don't know if DeepLabCut can handle for this.
note3: there must be at least num_cal_imgs*3 frames within (end_time - start_time) or
       gen_sample will throw, that is a bare minimum though and should not be used
note4: make sure the lines at the bottom that instantiate this class and run its method are not commented out

params:
vid_name = r'2020-07-21_(09-02-58)_00782B1B4A02_16_2022.avi'
project_name = 'stereo_cam_test1-silasi_lab-2020-07-21-3d'
start_time = 6
end_time = 13

TODO:
'''

project_name = 'stereo_cam_test1-silasi_lab-2020-07-21-3d'
vid_name = r'2020-07-23_(11-45-24)_00783A32F484_16_2015.avi'
start_time = 11
end_time = 29

seed(2020)


class VidLoader:
    def __init__(self, project_path, vid_path, start_time, end_time, num_cal_imgs=70):
        self.project_path = project_path
        self.vid_path = vid_path
        self.start_time = start_time
        self.end_time = end_time
        self.num_cal_imgs = num_cal_imgs

    # Divided sample interval by 3 so sampled frames have at least a small degree of randomness to them
    # but also aren't consecutive frames... This could be a bad idea but idk
    def gen_sample(self, fps):
        sample_range = (int(fps*self.start_time), int(fps*self.end_time))
        sample_interval = (sample_range[1] - sample_range[0]) // int((self.num_cal_imgs*3))
        return set(sample(range(sample_range[0]+1, sample_range[1]+2, sample_interval), k=self.num_cal_imgs)) # +1 and +2 cause frame indices start on 1

    def load_vid(self):
        # Playing video from file:
        cap = cv2.VideoCapture(os.getcwd() + os.sep + self.project_name + os.sep + self.vid_name)

        # get height and width from opencv and print to console
        if cap.isOpened():
            w = cap.get(3) # 3 = cv2.CAP_PROP_FRAME_WIDTH
            h = cap.get(4) # 4 = cv2.CAP_PROP_FRAME_HEIGHT
            fps = cap.get(5) # 5 is FPS and returned 60 (correct)... but 7 is frame count and returned 1206fps for some reason
            print('video height and width: {}, {}'.format(h, w))

        sample_frames = self.gen_sample(fps)

        # output jpgs will be stored in [your project dir]/calibration_images
        try:
            if not os.path.exists(os.getcwd() + os.sep + self.project_name + os.sep + 'calibration_images'):
                os.makedirs(os.getcwd() + os.sep + self.project_name + os.sep + 'calibration_images')
        except OSError:
            print ('Error: Creating directory of data')

        current_frame = 1
        sample_frame_cnt = 1
        while(True):
            # Capture frame-by-frame
            ret, frame = cap.read()

            # this logic limits cap to fps from video input, aka output will not have unecessarily high fps
            if not ret:
                break

            # h, w = frame.shape[:2]

            # # pixel coords of left cam
            # start_row, start_col = int(0), int(0)
            # end_row, end_col = int(h), int(w * .5)
            # cropped_left = frame[start_row:end_row , start_col:end_col]

            # # pixel coords of right cam
            # start_row, start_col = int(0), int(w * .5)
            # end_row, end_col = int(h), int(w)
            # cropped_right = frame[start_row:end_row , start_col:end_col]

            ###################### cropping inner ~1/3 of each 1/2 of the combined frames
            # pixel coords of left cam
            start_row, start_col = int(h//2 - h//5.5), int(w//2 - w//5.5)
            end_row, end_col = int(h), int(w * .5)
            cropped_left = frame[start_row:end_row , start_col:end_col]

            # pixel coords of right cam
            start_row, start_col = int(h//2 - h//5.5), int(w * .5)
            end_row, end_col = int(h), int(w//2 + w//5.5)
            cropped_right = frame[start_row:end_row , start_col:end_col]

            # Saves image of the current frame in jpg file if frame # is in the sample

            if current_frame in sample_frames:
                name1 = os.getcwd() + os.sep + self.project_name + os.sep + 'calibration_images' + os.sep + 'camera-1-' + str(sample_frame_cnt).zfill(3) + '.jpg'
                cv2.imwrite(name1, cropped_left)

                name2 = os.getcwd() + os.sep + self.project_name + os.sep + 'calibration_images' + os.sep + 'camera-2-' + str(sample_frame_cnt).zfill(3) + '.jpg'
                cv2.imwrite(name2, cropped_right)
                sample_frame_cnt += 1


            # # print sth encouraging to console
            # if current_frame % 10 == 0 and current_frame != 0:
            #     print(str(current_frame / 70) + r'% done...')

            # To stop duplicate images
            current_frame += 1

        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()


'''
What does this class do?
1. Counts all the images in the ./[project_name]/corners dir
2. Deletes any images that don't have a pair image (i.e. deeplabcut.calibrate_cameras/opencv
   corresponding method was only able to find corners on the image from 1 of the lenses)

note1: the delete_frames method must be called after the deeplabcut.calibrate_cameras/corresponding
       opencv method has been called
note2: make sure that the lines at the bottom to instantiate this class and call its method arent commmented out
note3: (IMPORTANT) make sure you go over the images after deleting the singles to delete the
       incorrectly labeled corners (and their pairs)
'''


class del_single_frames:
    def __init__(self, project_name):
        self.project_name = project_name
        self.corners = os.getcwd() + os.sep + project_name + os.sep + 'corners'
        self.singles = []
        self.frame_nums = []
        self.d = defaultdict(list)

    def del_corner_singles(self):
        for f in os.listdir(self.corners):
            self.frame_nums.append(f[9:12])
            self.d[f[9:12]].append(f[7])

        c = Counter(self.frame_nums)

        # add frame number of frames that are single to list
        for k, v in c.items():
            if v == 1:
                self.singles.append(k)

        # delete all frames from corners dir that are in the singles list
        for s in self.singles:
            file2remove = self.corners + os.sep + 'camera-' + str(self.d[s][0]) + '-' + s + '_corner.jpg'
            print('deleted: {}'.format(file2remove))
            os.remove(file2remove)
        
        return

    def del_no_corner_images(self):
        cornered_image_names = set()
        del_cnt = 0

        for f in os.listdir(self.corners):
            f = f.replace('_corner', '')
            cornered_image_names.add(f)
            print(f)

        for f in os.listdir(self.project_name + os.sep + 'calibration_images'):
            if f not in cornered_image_names:
                os.remove(self.project_name + os.sep + 'calibration_images' + os.sep + f)
                del_cnt += 1
        
        print('deleted {} images from ./[project_name]/calibration_images'.format(del_cnt))

        return


'''
This class splits videos along the y-axis into thirds.
To use this class simple make an instance of the class and pass the directory of the videos
you want to split and the project name. Then call the video_file_splitter method.
The output will be saved as avi files to
[your project dir]/split_videos.
Be careful if you want to change the variables because the
videowriter object will break very easily.
'''


class split_vids_in_thirds:
    def __init__(self, videos_dir_path, project_name):
        self.videos_dir_path = videos_dir_path
        self.project_name = project_name

    def video_file_splitter(self):
        # output avis will be stored in [your project dir]/split_videos
        try:
            if not os.path.exists(os.getcwd() + os.sep + self.project_name + os.sep + 'split_videos'):
                os.makedirs(os.getcwd() + os.sep + self.project_name + os.sep + 'split_videos')
        except OSError:
            print ('Error: Creating directory of data')
        
        output_dir = os.getcwd() + os.sep + self.project_name + os.sep + 'split_videos'

        vids2split = []
        num_vids = 0
        for f in os.listdir(os.getcwd() + os.sep + self.project_name + os.sep + self.videos_dir_path):
            if f[-3:] == 'mp4' or f[-3:] == 'avi':
                vids2split.append(f)
                num_vids += 1
        if num_vids < 1:
            print('videos not found: please check path to videos folder and try again')
        else:
            print('splitting {} video(s)'.format(num_vids))
        
        while vids2split:
            curr = vids2split.pop()

            cap = cv2.VideoCapture(os.getcwd() + os.sep + self.project_name + os.sep + self.videos_dir_path + os.sep + curr)

            # get height and width from opencv
            if cap.isOpened():
                w = cap.get(3) # 3 = cv2.CAP_PROP_FRAME_WIDTH
                h = cap.get(4) # 4 = cv2.CAP_PROP_FRAME_HEIGHT
                fps = cap.get(5) # 5 is FPS and returned 60 (correct)
                print('video height and width: {}, {}'.format(h, w))
                print('fps: ', fps)

            left_fn = output_dir + os.sep + 'camera-1-' + curr[:-4] + '.avi'
            mid_fn = output_dir + os.sep + 'camera-2-' + curr[:-4] + '.avi'
            right_fn = output_dir + os.sep + 'camera-3-' + curr[:-4] + '.avi'

            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            out1 = cv2.VideoWriter(left_fn, fourcc, fps, (int(w//3 + 10),int(h)), False)
            out2 = cv2.VideoWriter(mid_fn, fourcc, fps, (int(w//3 + 10),int(h)), False)
            out3 = cv2.VideoWriter(right_fn, fourcc, fps, (int(w//3 + 10),int(h)), False)


            while(True):
                ret, frame = cap.read()
                if ret:
                    gray = cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2GRAY)
                    
                    # pixel coords of left cam
                    start_row, start_col = int(0), int(0)
                    end_row, end_col = int(h), int(w//3 + 10)
                    cropped_left = gray[start_row:end_row , start_col:end_col]

                    # pixel coords of mid cam
                    start_row, start_col = int(0), int(w//3 - 5)
                    end_row, end_col = int(h), int((w//3)*2 + 5)
                    cropped_mid = gray[start_row:end_row , start_col:end_col]

                    # pixel coords of right cam
                    start_row, start_col = int(0), int((w//3)*2 - 10)
                    end_row, end_col = int(h), int(w)
                    cropped_right = gray[start_row:end_row , start_col:end_col]

                    cropped_left = cv2.resize(cropped_left, (int(w//3 + 10),int(h)))
                    cropped_mid = cv2.resize(cropped_mid, (int(w//3 + 10),int(h)))
                    flipped_mid = cv2.flip(cropped_mid, 1)
                    cropped_right = cv2.resize(cropped_right, (int(w//3 + 10),int(h)))

                    out1.write(cropped_left)
                    out2.write(flipped_mid)
                    out3.write(cropped_right)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    break

            cap.release()
            out1.release()
            out2.release()
            out3.release()
            cv2.destroyAllWindows()

'''
What does this class do?
This crops the region of interest in videos for the pellet tracking task training data.

note1: The pathing may not be totally conventional so if you're getting errors in your paths just check the path
       variable lines and fix as needed.
note2: You may need to adjust the ROI of the video and possibly the resolution. So check that before you run it.
note3: This saves to 224*224*1 cause that's the optimal input for mobilenetv2 (the other color channels are added later)
note4: You may need to change the fourcc depending on what your computer is compatible with. Try XVID if MJPG doesnt work.
'''


class crop2Size:
    def __init__(self, input_folder, output_folder):
        self.input_folder = input_folder
        self.output_folder = output_folder

    def video_file_splitter(self):
        # output avis will be stored in [current dir]/cropped_vids
        output_dir = os.getcwd() + os.sep + 'cropped_videos'

        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
        except OSError:
            print('Error: Creating directory [cropped_videos]')

        # output_dir = os.getcwd() + os.sep + 'cropped_videos'

        vids2split = []
        num_vids = 0
        for f in os.listdir(os.getcwd() + os.sep + self.input_folder):
            if f[-3:] == 'mp4' or f[-3:] == 'avi':
                vids2split.append(f)
                num_vids += 1
        if num_vids < 1:
            print('videos not found: please check path to videos folder and try again')
        else:
            print('splitting {} video(s)'.format(num_vids))

        while vids2split:
            curr = vids2split.pop()

            cap = cv2.VideoCapture(
                os.getcwd() + os.sep + self.input_folder + os.sep + curr)

            # get height and width from opencv
            if cap.isOpened():
                w = cap.get(3)  # 3 = cv2.CAP_PROP_FRAME_WIDTH
                h = cap.get(4)  # 4 = cv2.CAP_PROP_FRAME_HEIGHT
                fps = cap.get(5)  # 5 is FPS and returned 60 (correct)... but 7 is frame count and returned 1206fps for some reason
                print('video height and width: {}, {}'.format(h, w))
                print('fps: ', fps)

            fn = output_dir + os.sep + 'pelcam_' + curr[:-4] + '.avi'

            # fourcc = cv2.VideoWriter_fourcc(*'MJPG') # this doesn't work on the titan computer... idk why
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(fn, fourcc, int(fps), (224, 224), False)

            while (True):
                ret, frame = cap.read()
                if ret:
                    gray = cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2GRAY)

                    # pixel coords of pellet cam
                    start_row, start_col = int(720 - 448), int((1280 // 2) - (448 // 2))
                    end_row, end_col = int(h), int((1280 // 2) + (448 // 2))
                    cropped_frame = gray[start_row:end_row, start_col:end_col]
                    cropped_frame = cv2.resize(cropped_frame, (224, 224))
                    out.write(cropped_frame)

                    if cv2.waitKey(int(1000/fps)) & 0xFF == ord('q'):
                        break
                else:
                    break

            cap.release()
            out.release()
            cv2.destroyAllWindows()

'''
What does this class do?
This class takes the absolute path to a video and splits it up into multiple videos based on the time frames passed
in the times_arr argument. If you want to run this on multiple videos use a for loop in the main func.
'''

class sampleReachVids:
    def __init__(self, vid_path, start_times_arr, end_times_arr):
        self.vid_path = vid_path
        self.start_times_arr = start_times_arr
        self.end_times_arr = end_times_arr
        self.recording = False

    def load_vid(self):
        print(self.vid_path)
        # Playing video from file:
        cap = cv2.VideoCapture(self.vid_path)
        frame_cnt = 0
        # get height and width from opencv and print to console
        if cap.isOpened():
            w = cap.get(3)  # 3 = cv2.CAP_PROP_FRAME_WIDTH
            h = cap.get(4)  # 4 = cv2.CAP_PROP_FRAME_HEIGHT
            fps = cap.get(5)  # 5 is FPS and returned 60 (correct)... but 7 is frame count and returned 1206fps for some reason
            print('video height and width: {}, {}'.format(h, w))

        output_dir = os.getcwd() + os.sep + 'sampled_training_videos'
        print(f'vids will be saved to {output_dir}')

        # output jpgs will be stored in [your project dir]/calibration_images
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
        except OSError:
            print('Error: Creating directory of data')

        starts = [x*fps for x in self.start_times_arr]
        ends = [x*fps for x in self.end_times_arr]

        left_fn = output_dir + os.sep + 'camera-1_' + self.vid_path[-45:-4] + '_reaches' + '.avi'
        mid_fn = output_dir + os.sep + 'camera-2_' + self.vid_path[-45:-4] + '_reaches' + '.avi'
        right_fn = output_dir + os.sep + 'camera-3_' + self.vid_path[-45:-4] + '_reaches' + '.avi'
        print(left_fn)

        # fourcc = cv2.VideoWriter_fourcc(*'MJPG') # this doesn't work on the titan computer... idk why
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out1 = cv2.VideoWriter(left_fn, fourcc, fps, (int(w // 3 + 10), int(h)), False)
        out2 = cv2.VideoWriter(mid_fn, fourcc, fps, (int(w // 3 + 10), int(h)), False)
        out3 = cv2.VideoWriter(right_fn, fourcc, fps, (int(w // 3 + 10), int(h)), False)

        while (True):
            ret, frame = cap.read()
            frame_cnt += 1
            if frame_cnt in starts:
                self.recording = True
            if frame_cnt in ends:
                self.recording = False
            if ret:
                gray = cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2GRAY)

                # pixel coords of left cam
                start_row, start_col = int(0), int(0)
                end_row, end_col = int(h), int(w // 3 + 10)
                cropped_left = gray[start_row:end_row, start_col:end_col]

                # pixel coords of mid cam
                start_row, start_col = int(0), int(w // 3 - 5)
                end_row, end_col = int(h), int((w // 3) * 2 + 5)
                cropped_mid = gray[start_row:end_row, start_col:end_col]

                # pixel coords of right cam
                start_row, start_col = int(0), int((w // 3) * 2 - 10)
                end_row, end_col = int(h), int(w)
                cropped_right = gray[start_row:end_row, start_col:end_col]

                cropped_left = cv2.resize(cropped_left, (int(w // 3 + 10), int(h)))
                cropped_mid = cv2.resize(cropped_mid, (int(w // 3 + 10), int(h)))
                flipped_mid = cv2.flip(cropped_mid, 1)
                cropped_right = cv2.resize(cropped_right, (int(w // 3 + 10), int(h)))

                if self.recording:
                    out1.write(cropped_left)
                    out2.write(flipped_mid)
                    out3.write(cropped_right)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                break

        cap.release()
        out1.release()
        out2.release()
        out3.release()
        cv2.destroyAllWindows()

def generate_dataset(input_folder, output_folder):
    assert os.path.isdir(input_folder) and os.path.isdir(output_folder)
    output_folder_1 = os.path.join(output_folder, "1")
    if not os.path.exists(output_folder_1):
        os.mkdir(output_folder_1)

    output_folder_0 = os.path.join(output_folder, "0")
    if not os.path.exists(output_folder_0):
        os.mkdir(output_folder_0)

    video_files = [os.path.join(input_folder, item) for item in os.listdir(input_folder) if item.endswith('.avi')]
    # video_files = [os.path.join(input_folder, item) for item in os.listdir(input_folder) if
    #                item == '2020-01-18_(07-04-58)_002FBE71E101_85136_12950.avi']

    print(video_files)

    for video_file in tqdm(video_files):
        video_stream = cv2.VideoCapture(video_file)
        grab, frame = video_stream.read()

        cnt = 0

        while frame is not None:
            if cnt % 60 == 0:
                showframe = deepcopy(frame)
                # text coords were 40, 40
                showframe = cv2.putText(showframe, "1: Move,2: Idle,3: Discard", (40, 40),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), lineType=cv2.LINE_AA)
                cv2.imshow('frame', showframe)
                img_path = os.path.basename(video_file).replace(".avi", "") + "%d.jpg" % video_stream.get(
                    cv2.CAP_PROP_POS_FRAMES)
                frame = cv2.resize(frame, (224, 224))
                if cv2.waitKey(0) == 49:
                    img_path = os.path.join(output_folder_1, img_path)
                    frame = cv2.resize(frame, (224, 224))
                    cv2.imwrite(img_path, frame)
                elif cv2.waitKey(0) == 50:
                    img_path = os.path.join(output_folder_0, img_path)
                    frame = cv2.resize(frame, (224, 224))
                    cv2.imwrite(img_path, frame)

            grab, frame = video_stream.read()
            cnt += 15
            # if frame is not None:
            #     print('has frame')
    
    time.sleep(3)
    video_stream.release()


# TODO: remember to cvt to 3 channels
def prepare_for_training(output_folder):
    pos_folder = os.path.join(output_folder, '1')
    neg_folder = os.path.join(output_folder, '0')
    assert os.path.exists(pos_folder) and os.path.exists(neg_folder)

    x = []
    y = []

    for img_path in os.listdir(pos_folder):
        img_path = os.path.join(pos_folder, img_path)
        x.append(cv2.imread(img_path))
        y.append(1)
    for img_path in os.listdir(neg_folder):
        img_path = os.path.join(neg_folder, img_path)
        x.append(cv2.imread(img_path))
        y.append(0)

    x = np.asarray(x)
    y = np.asarray(y)

    index = np.random.permutation(x.shape[0])
    x = x[index]
    y = y[index]
    return x, y

if __name__ == '__main__':
    input_folder = 'raw_vids'
    output_folder = ""
    # generate_dataset(input_folder, output_folder)
    # prepare_for_training(output_folder)
    c2s = crop2Size(input_folder, output_folder)
    c2s.video_file_splitter()

    # sv = split_vids_in_thirds(videos_dir_path, project_name)
    # sv.video_file_splitter()

    # dsf = del_single_frames(project_name)
    # dsf.del_corner_singles()
    # dsf.del_no_corner_images()

    # v = VidLoader(project_name, vid_name, start_time, end_time)
    # v.load_vid()

    # v = VidLoader(project_path, vid_path, start_time, end_time)
    # v.load_vid()