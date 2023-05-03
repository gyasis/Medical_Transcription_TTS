import open3d as o3d
import numpy as np
import time

# Read the recorded data
reader = o3d.io.AzureKinectMKVReader()
reader.open('recorded_data.mkv')

# Default Azure Kinect camera parameters
depth_camera_params = o3d.camera.PinholeCameraIntrinsic(
    o3d.camera.PinholeCameraIntrinsicParameters.PrimeSenseDefault)

# Initialize the visualizer
vis = o3d.visualization.Visualizer()
vis.create_window('PointCloud', 1920, 540)
vis_geometry_added = False

while not reader.is_eof():
    raw_rgbd = reader.next_frame()
    if raw_rgbd is None:
        continue

    # Convert the depth image format to a supported format
    depth_image = o3d.geometry.Image(np.asarray(raw_rgbd.depth).astype('float32'))
    color_image = raw_rgbd.color
    rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(color_image, depth_image)

    # Convert depth image to point cloud
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(
        rgbd,
        depth_camera_params)

    # Add point cloud to visualizer
    if not vis_geometry_added:
        vis.add_geometry(pcd)
        vis_geometry_added = True
    else:
        vis.update_geometry(pcd)

    vis.poll_events()
    vis.update_renderer()
    time.sleep(0.1)  # Adjust this value to control the delay between frames

# Close the reader
reader.close()
