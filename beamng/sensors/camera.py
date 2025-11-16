import time

from beamngpy.sensors import Camera

from pyzenoh_bridge import CameraDataPublisher
from beamng.utils.sleep_until_next import sleep_until_next

class CameraManager:
  def __init__(self, bng, vehicle, camera_config, zenoh_config):
    self.camera = Camera(
      camera_config['name'],
      bng,
      vehicle,
      requested_update_time=camera_config['requested_update_time'],
      pos=tuple(camera_config['pos']),
      dir=tuple(camera_config['dir']),
      up=tuple(camera_config['up']),
      resolution=tuple(camera_config['resolution']),
      near_far_planes=tuple(camera_config['near_far_planes']),
      is_using_shared_memory=camera_config['is_using_shared_memory'],
      is_render_annotations=camera_config['is_render_annotations'],
      is_render_instance=camera_config['is_render_instance'],
      is_render_depth=camera_config['is_render_depth'],
      is_visualised=camera_config['is_visualised'],
      is_streaming=camera_config['is_streaming'],
      is_dir_world_space=camera_config['is_dir_world_space'],
    )
    self.frequency = camera_config['frequency']
    self.frame_id = camera_config['frame_id']
    self.width = camera_config['resolution'][0]
    self.height = camera_config['resolution'][1]

    # どのデータを取得するか設定
    self.enable_color = camera_config['is_render_colours']
    self.enable_depth = camera_config['is_render_depth']
    self.enable_annotation = camera_config['is_render_annotations']
    
    # 有効なデータ型のみPublisherを作成
    self.color_publisher = None
    self.depth_publisher = None
    self.annotation_publisher = None
    
    if self.enable_color:
      self.color_publisher = CameraDataPublisher(
        zenoh_config, 
        camera_config['topic_name'] + '/color'
      )
    
    if self.enable_depth:
      self.depth_publisher = CameraDataPublisher(
        zenoh_config, 
        camera_config['topic_name'] + '/depth'
      )
    
    if self.enable_annotation:
      self.annotation_publisher = CameraDataPublisher(
        zenoh_config, 
        camera_config['topic_name'] + '/annotation'
      )

    print(f'{camera_config["name"]}: {camera_config["topic_name"]}')
    
  def send(self, stop_event):
    interval = 1.0 / self.frequency
    base_time = time.time()
    
    while not stop_event.is_set():
      data = self.camera.stream_raw()

      # RGB画像
      if self.enable_color and self.color_publisher is not None:
        color_data = data['colour'].tobytes()
        self.color_publisher.publish_color(
          self.frame_id, color_data, self.width, self.height
        )
      
      # Depth画像
      if self.enable_depth and self.depth_publisher is not None:
        depth_data = data['depth'].tobytes()
        self.depth_publisher.publish_depth(
          self.frame_id, depth_data, self.width, self.height
        )
      
      # Annotation画像
      if self.enable_annotation and self.annotation_publisher is not None:
        annotation_data = data['annotation'].tobytes()
        self.annotation_publisher.publish_annotation(
          self.frame_id, annotation_data, self.width, self.height
        )
      
      base_time = sleep_until_next(interval, base_time)