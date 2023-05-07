import argparse
import datetime
import open3d as o3d


class RecorderWithCallback:

    def __init__(self, config, device, filename, align_depth_to_color):
        self.flag_exit = False
        self.flag_record = False
        self.filename = filename

        self.align_depth_to_color = align_depth_to_color
        self.recorder = o3d.io.AzureKinectRecorder(config, device)
        if not self.recorder.init_sensor():
            raise RuntimeError('Failed to connect to sensor')

    def escape_callback(self, vis):
        self.flag_exit = True
        if self.recorder.is_record_created():
            print('Recording finished.')
        else:
            print('Nothing has been recorded.')
        return False

    def space_callback(self, vis):
        if self.flag_record:
            print('Recording paused. '
                  'Press [Space] to continue. '
                  'Press [ESC] to save and exit.')
            self.flag_record = False

        elif not self.recorder.is_record_created():
            if self.recorder.open_record(self.filename):
                print('Recording started. '
                      'Press [SPACE] to pause. '
                      'Press [ESC] to save and exit.')
                self.flag_record = True

        else:
            print('Recording resumed, video may be discontinuous. '
                  'Press [SPACE] to pause. '
                  'Press [ESC] to save and exit.')
            self.flag_record = True

        return False

    def run(self, vis):
        vis_geometry_added = False
        while not self.flag_exit:
            rgbd = self.recorder.record_frame(self.flag_record,
                                              self.align_depth_to_color)
            if rgbd is None:
                continue

            if not vis_geometry_added:
                vis.add_geometry(rgbd)
                vis_geometry_added = True

            vis.update_geometry(rgbd)
            vis.poll_events()
            vis.update_renderer()

        self.recorder.close_record()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Azure kinect mkv recorder.')
    parser.add_argument('--config', type=str, help='input json kinect config')
    parser.add_argument('--output', type=str, help='output mkv filename')
    parser.add_argument('--list',
                        action='store_true',
                        help='list available azure kinect sensors')
    parser.add_argument('--device',
                        type=int,
                        default=0,
                        help='input kinect device id')
    parser.add_argument('-a',
                        '--align_depth_to_color',
                        action='store_true',
                        help='enable align depth image to color')
    parser.add_argument('--cameras',
                        type=str,
                        default='0',
                        help='comma-separated list of kinect device ids to record')
    args = parser.parse_args()

    if args.list:
        o3d.io.AzureKinectSensor.list_devices()
        exit()

    if args.config is not None:
        config = o3d.io.read_azure_kinect_sensor_config(args.config)
    else:
        config = o3d.io.AzureKinectSensorConfig()

    if args.output is not None:
        filename = args.output
    else:
        filename = '{date:%Y-%m-%d-%H-%M-%S}.mkv'.format(
            date=datetime.datetime.now())
    print('Prepare writing to {}'.format(filename))

    camera_indices = [int(x) for x in args.cameras.split(',')]
    recorders = [
        RecorderWithCallback(config, device, f"{device}_{filename}",
                             args.align_depth_to_color)
        for device in camera_indices
    ]

    vis = o3d.visualization.VisualizerWithKeyCallback()
    vis.create_window('recorder', 1920, 540)

    glfw_key_escape = 256
    glfw_key_space = 32

    for r in recorders:
        vis.register_key_callback(glfw_key_escape, r.escape_callback)
        vis.register_key_callback(glfw_key_space, r.space_callback)

    print("Recorder initialized. Press [SPACE] to start. "
          "Press [ESC] to save and exit.")

    vis_geometry_added = [False] * len(recorders)

    while not all(r.flag_exit for r in recorders):
        for i, r in enumerate(recorders):
            rgbd = r.recorder.record_frame(r.flag_record,
                                            r.align_depth_to_color)
            if rgbd is None:
                continue

            if not vis_geometry_added[i]:
                vis.add_geometry(rgbd)
                vis_geometry_added[i] = True

            vis.update_geometry(rgbd)
            vis.poll_events()
            vis.update_renderer()

        for r in recorders:
            r.recorder.close_record()
