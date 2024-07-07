import os
import numpy as np
import carla
import random
import queue
import pandas as pd
from PIL import Image
from carla import ColorConverter
from datetime import datetime

date_str = datetime.today().strftime('%y%m%d_%H%M%S')
export_folder = "images_and_boxes/" + date_str + "/"

# Define tag values
TAGS = {15: 'large_vehicle', 14: 'small_vehicle', 12: 'pedestrian', 18: 'motorcycle', 13: 'bicycle'}

OBJECTS = {
    'motorcycle': ['vehicle.yamaha.yzf', 'vehicle.vespa.zx125', 'vehicle.kawasaki.ninja',
                   'vehicle.harley-davidson.low_rider'],
    'small_vehicle': ['vehicle.toyota.prius', 'vehicle.tesla.model3', 'vehicle.seat.leon', 'vehicle.nissan.micra',
                      'vehicle.mini.cooper_s_2021', 'vehicle.mini.cooper_s', 'vehicle.micro.microlino',
                      'vehicle.mercedes.coupe', 'vehicle.lincoln.mkz_2020', 'vehicle.lincoln.mkz_2017',
                      'vehicle.ford.mustang', 'vehicle.ford.crown', 'vehicle.dodge.charger_police_2020',
                      'vehicle.dodge.charger_2020', 'vehicle.citroen.c3', 'vehicle.chevrolet.impala',
                      'vehicle.bmw.grandtourer', 'vehicle.audi.tt', 'vehicle.audi.etron', 'vehicle.audi.a2'],
    'large_vehicle': ['vehicle.volkswagen.t2_2021', 'vehicle.volkswagen.t2', 'vehicle.tesla.cybertruck',
                      'vehicle.nissan.patrol_2021', 'vehicle.nissan.patrol', 'vehicle.mercedes.sprinter',
                      'vehicle.mercedes.coupe_2020', 'vehicle.jeep.wrangler_rubicon', 'vehicle.ford.ambulance',
                      'vehicle.carlamotors.firetruck', 'vehicle.carlamotors.carlacola'],
    'bicycle': ['vehicle.gazelle.omafiets', 'vehicle.diamondback.century', 'vehicle.bh.crossbike']
}

FREQS = {'large_vehicle': 0.3, 'small_vehicle': 0.3, 'motorcycle': 0.2, 'bicycle': 0.2}

global df

# Create an Excel sheet to save the detected objects and their tags
df = pd.DataFrame(
    columns=['Camera ID', 'Time After Starting(Second)', 'Object', 'Tag', 'Min X', 'Max X', 'Min Y', 'Max Y',
             'Cropped Image'])


def crop_image(image_path, x1, y1, x2, y2, type, id):
    print("Cropped Started")
    # Open the image
    with Image.open(image_path) as image:
        # Set the crop region
        left = x1
        bottom = y1
        right = x2
        top = y2

        if ((top - bottom) * (right - left) < 200):
            return "None"

        # Crop the image
        cropped_image = image.crop((left, bottom, right, top))

        # Get the directory of the original image
        directory = os.path.dirname(image_path)

        # Create the "Cropped Images" directory if it doesn't exist
        cropped_directory = os.path.join(directory, "Cropped Images")
        if not os.path.exists(cropped_directory):
            os.mkdir(cropped_directory)

        # Create the "Cropped Images" directory if it doesn't exist
        cropped_directory = os.path.join(cropped_directory, type)
        if not os.path.exists(cropped_directory):
            os.mkdir(cropped_directory)

        # Get the name of the original image
        image_name = os.path.basename(image_path)

        # Get the file extension of the original image
        file_extension = os.path.splitext(image_name)[1]

        # Create the name of the cropped image with the type parameter
        cropped_image_name = f"{os.path.splitext(image_name)[0]}_{type}_{id}{file_extension}"

        # Save the cropped image to the "Cropped Images" directory
        cropped_image_path = os.path.join(cropped_directory, cropped_image_name)
        cropped_image.save(cropped_image_path)

        print("Cropped Finished")
        return cropped_image_path


def process_instance_camera_data(camera_id, image_loc, rgb_loc, time):
    print("Process Started")

    # Load the image
    image_rgb = Image.open(image_loc)

    # Convert the image to numpy array
    image = np.array(image_rgb)

    # Get the red channel of the image
    red_channel = image[:, :, 0]

    for tag_value, object_type in TAGS.items():
        # Find pixels with tag
        object_pixels = np.where(red_channel == tag_value)

        # Get unique object ids (green and blue channels)
        object_ids = np.unique(image[object_pixels][:, 1:], axis=0)

        x_min = 0
        x_max = 0
        y_min = 0
        y_max = 0

        # Iterate over unique object ids and get bounding boxes
        for obj_id in object_ids:
            obj_pixels = np.where(np.all(image[:, :, 1:] == obj_id, axis=-1))
            y_min, x_min = np.min(obj_pixels, axis=1)
            y_max, x_max = np.max(obj_pixels, axis=1)

        cropped_loc = 'None'
        if (x_min != x_max):
            if (y_min != y_max):
                cropped_loc = crop_image(rgb_loc, x_min, y_min, x_max, y_max, object_type, f"{obj_id[0]}-{obj_id[1]}")

        if (cropped_loc != 'None'):
            df.loc[len(df)] = [camera_id, time, f"{obj_id[0]}-{obj_id[1]}", object_type,
                               x_min, x_max, y_min, y_max, cropped_loc]

        print("Process Finished")


def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)

    world = client.load_world('Town03')
    # world = client.load_world('Town01')
    # world = client.load_world('Town02')
    # world = client.load_world('Town03')
    # world = client.load_world('Town04')
    # world = client.load_world('Town05')
    # world = client.load_world('Town06')
    # world = client.load_world('Town07')

    # Parameters
    NO_WALKERS = 0
    LESS_WALKERS = 5
    AVERAGE_WALKERS = 10
    MANY_WALKERS = 60

    NO_VEHICLES = 0
    LESS_VEHICLES = 10
    AVERAGE_VEHICLES = 20
    MANY_VEHICLES = 120

    number_of_vehicles = MANY_VEHICLES
    # number_of_vehicles = NO_VEHICLES
    # number_of_vehicles = LESS_VEHICLES
    # number_of_vehicles = AVERAGE_VEHICLES
    # number_of_vehicles = MANY_VEHICLES

    number_of_walkers = MANY_WALKERS
    # number_of_walkers = NO_WALKERS
    # number_of_walkers = LESS_WALKERS
    # number_of_walkers = AVERAGE_WALKERS
    # number_of_walkers = MANY_WALKERS

    world.set_weather(carla.WeatherParameters.ClearSunset)
    # world.set_weather(carla.WeatherParameters.ClearNoon)
    # world.set_weather(carla.WeatherParameters.CloudyNoon)
    # world.set_weather(carla.WeatherParameters.WetNoon)
    # world.set_weather(carla.WeatherParameters.WetCloudyNoon)
    # world.set_weather(carla.WeatherParameters.MidRainyNoon)
    # world.set_weather(carla.WeatherParameters.HardRainNoon)
    # world.set_weather(carla.WeatherParameters.SoftRainNoon)
    # world.set_weather(carla.WeatherParameters.ClearSunset)
    # world.set_weather(carla.WeatherParameters.CloudySunset)
    # world.set_weather(carla.WeatherParameters.WetSunset)
    # world.set_weather(carla.WeatherParameters.WetCloudySunset)
    # world.set_weather(carla.WeatherParameters.MidRainSunset)
    # world.set_weather(carla.WeatherParameters.HardRainSunset)
    # world.set_weather(carla.WeatherParameters.SoftRainSunset)

    NUM_TIME_TICKS = 3000  # overall time steps to execute
    NUM_SAVE_INTERVAL = 50  # save sensor data each X time steps
    NUM_TIME_INITIAL_WAIT = 30  # wait for X time steps before recording (to complete spawn animations)

    DELTA_SECOND = 0.1
    settings = world.get_settings()
    settings.synchronous_mode = True
    settings.fixed_delta_seconds = DELTA_SECOND
    world.apply_settings(settings)

    spawn_points = world.get_map().get_spawn_points()
    blueprint_library = world.get_blueprint_library()

    for tag in FREQS:
        length_vehicle = int(FREQS[tag] * number_of_vehicles)
        # Loop through the number of vehicles for each tag
        for i in range(length_vehicle):
            # Select a random blueprint from the list for the 'motorcycle' tag
            blueprint = random.choice(OBJECTS[tag])
            # Spawn a vehicle using the selected blueprint at a random spawn point
            npc = world.try_spawn_actor(blueprint_library.find(blueprint), random.choice(spawn_points))
            if npc:
                npc.set_autopilot(True)
                print(f"Spawned: {blueprint}")
            else:
                print("Vehicle could not be spawned.")

    # Spawn pedestrians
    blueprintsWalkers = world.get_blueprint_library().filter("walker.pedestrian.*")
    walker_bp = random.choice(blueprintsWalkers)
    # 1. take all the random locations to spawn
    spawn_points = []
    for i in range(MANY_WALKERS):
        spawn_point = carla.Transform()
        spawn_point.location = world.get_random_location_from_navigation()
        if (spawn_point.location != None):
            spawn_points.append(spawn_point)

    # 2. build the batch of commands to spawn the pedestrians
    batch = []
    walkers_list = []
    for spawn_point in spawn_points:
        walker_bp = random.choice(blueprintsWalkers)
        batch.append(carla.command.SpawnActor(walker_bp, spawn_point))
    # apply the batch
    results = client.apply_batch_sync(batch, True)
    for i in range(len(results)):
        if results[i].error:
            pass
        else:
            walkers_list.append({"id": results[i].actor_id})

    # 3. we spawn the walker controller
    batch = []
    walker_controller_bp = world.get_blueprint_library().find('controller.ai.walker')
    for i in range(len(walkers_list)):
        batch.append(carla.command.SpawnActor(walker_controller_bp, carla.Transform(), walkers_list[i]["id"]))

    # apply the batch
    results = client.apply_batch_sync(batch, True)
    for i in range(len(results)):
        if results[i].error:
            pass
        else:
            walkers_list[i]["con"] = results[i].actor_id

    all_id = []
    # 4. we put altogether the walkers and controllers id to get the objects from their id
    for i in range(len(walkers_list)):
        all_id.append(walkers_list[i]["con"])
        all_id.append(walkers_list[i]["id"])
    all_actors = world.get_actors(all_id)
    world.tick()

    # 5. initialize each controller and set target to walk to (list is [controller, actor, controller, actor ...])
    for i in range(0, len(all_actors), 2):
        # start walker
        all_actors[i].start()
        # set walk to random point
        all_actors[i].go_to_location(world.get_random_location_from_navigation())
        # random max speed
        all_actors[i].set_max_speed(1 + random.random())  # max speed between 1 and 2 (default is 1.4 m/s)

    camera_pitch = -30
    camera_rgb = blueprint_library.find('sensor.camera.rgb')
    camera_rgb.set_attribute("image_size_x", str(1920))
    camera_rgb.set_attribute("image_size_y", str(1080))
    camera_rgb.set_attribute('fov', str(120))

    camera_sem = blueprint_library.find('sensor.camera.semantic_segmentation')
    camera_sem.set_attribute("image_size_x", str(1920))
    camera_sem.set_attribute("image_size_y", str(1080))
    camera_sem.set_attribute('fov', str(120))

    camera_ins = world.get_blueprint_library().find('sensor.camera.instance_segmentation')
    camera_ins.set_attribute("image_size_x", str(1920))
    camera_ins.set_attribute("image_size_y", str(1080))
    camera_ins.set_attribute("fov", str(120))

    lidar_pole = world.get_blueprint_library().find('sensor.lidar.ray_cast')
    lidar_pole.set_attribute('channels', str(32))
    lidar_pole.set_attribute('points_per_second', str(90000))
    lidar_pole.set_attribute('rotation_frequency', str(40))
    lidar_pole.set_attribute('range', str(40))
    lidar_pole.set_attribute('upper_fov', str(-20))
    lidar_pole.set_attribute('lower_fov', str(-80))

    actor_list = []
    image_queue = queue.Queue()

    # pole-1
    camera_transform = carla.Transform(carla.Location(x=27.2, y=-0.38, z=6), carla.Rotation(camera_pitch, 180, 0))
    lidar_transform = carla.Transform(carla.Location(27.2, -0.38, 6), carla.Rotation(0, 0, 0))

    camera_pole1_rgb = world.spawn_actor(camera_rgb, camera_transform)
    image_queue_pole1_rgb = queue.Queue()
    camera_pole1_rgb.listen(image_queue_pole1_rgb.put)
    actor_list.append(camera_pole1_rgb)

    camera_pole1_sem = world.spawn_actor(camera_sem, camera_transform)
    image_queue_pole1_sem = queue.Queue()
    camera_pole1_sem.listen(image_queue_pole1_sem.put)
    actor_list.append(camera_pole1_sem)

    camera_pole1_ins = world.spawn_actor(camera_ins, camera_transform)
    image_queue_pole1_ins = queue.Queue()
    camera_pole1_ins.listen(image_queue_pole1_ins.put)
    actor_list.append(camera_pole1_ins)

    lidar_pole1 = world.spawn_actor(lidar_pole, lidar_transform)
    lidar_pole1_queue = queue.Queue()
    lidar_pole1.listen(lidar_pole1_queue.put)
    actor_list.append(lidar_pole1)

    # pole-2
    camera_transform = carla.Transform(carla.Location(x=0.71, y=-28.35, z=6), carla.Rotation(camera_pitch, 90, 0))
    lidar_transform = carla.Transform(carla.Location(0.71, -28.35, 6), carla.Rotation(0, 0, 0))

    camera_pole2_rgb = world.spawn_actor(camera_rgb, camera_transform)
    image_queue_pole2_rgb = queue.Queue()
    camera_pole2_rgb.listen(image_queue_pole2_rgb.put)
    actor_list.append(camera_pole2_rgb)

    camera_pole2_sem = world.spawn_actor(camera_sem, camera_transform)
    image_queue_pole2_sem = queue.Queue()
    camera_pole2_sem.listen(image_queue_pole2_sem.put)
    actor_list.append(camera_pole2_sem)

    camera_pole2_ins = world.spawn_actor(camera_ins, camera_transform)
    image_queue_pole2_ins = queue.Queue()
    camera_pole2_ins.listen(image_queue_pole2_ins.put)
    actor_list.append(camera_pole2_ins)

    lidar_pole2 = world.spawn_actor(lidar_pole, lidar_transform)
    lidar_pole2_queue = queue.Queue()
    lidar_pole2.listen(lidar_pole2_queue.put)
    actor_list.append(lidar_pole2)

    # pole-3
    camera_transform = carla.Transform(carla.Location(x=-28, y=-1.5, z=6), carla.Rotation(camera_pitch, 0, 0))
    lidar_transform = carla.Transform(carla.Location(-28, -1.5, 6), carla.Rotation(0, 0, 0))

    camera_pole3_rgb = world.spawn_actor(camera_rgb, camera_transform)
    image_queue_pole3_rgb = queue.Queue()
    camera_pole3_rgb.listen(image_queue_pole3_rgb.put)
    actor_list.append(camera_pole3_rgb)

    camera_pole3_sem = world.spawn_actor(camera_sem, camera_transform)
    image_queue_pole3_sem = queue.Queue()
    camera_pole3_sem.listen(image_queue_pole3_sem.put)
    actor_list.append(camera_pole3_sem)

    camera_pole3_ins = world.spawn_actor(camera_ins, camera_transform)
    image_queue_pole3_ins = queue.Queue()
    camera_pole3_ins.listen(image_queue_pole3_ins.put)
    actor_list.append(camera_pole3_ins)

    lidar_pole3 = world.spawn_actor(lidar_pole, lidar_transform)
    lidar_pole3_queue = queue.Queue()
    lidar_pole3.listen(lidar_pole3_queue.put)
    actor_list.append(lidar_pole3)

    # pole-4
    camera_transform = carla.Transform(carla.Location(x=-2.3, y=29.3, z=6), carla.Rotation(camera_pitch, -90, 0))
    lidar_transform = carla.Transform(carla.Location(-2.3, 29.3, 6), carla.Rotation(0, 0, 0))

    camera_pole4_rgb = world.spawn_actor(camera_rgb, camera_transform)
    image_queue_pole4_rgb = queue.Queue()
    camera_pole4_rgb.listen(image_queue_pole4_rgb.put)
    actor_list.append(camera_pole4_rgb)

    camera_pole4_sem = world.spawn_actor(camera_sem, camera_transform)
    image_queue_pole4_sem = queue.Queue()
    camera_pole4_sem.listen(image_queue_pole4_sem.put)
    actor_list.append(camera_pole4_sem)

    camera_pole4_ins = world.spawn_actor(camera_ins, camera_transform)
    image_queue_pole4_ins = queue.Queue()
    camera_pole4_ins.listen(image_queue_pole4_ins.put)
    actor_list.append(camera_pole4_ins)

    lidar_pole4 = world.spawn_actor(lidar_pole, lidar_transform)
    lidar_pole4_queue = queue.Queue()
    lidar_pole4.listen(lidar_pole4_queue.put)
    actor_list.append(lidar_pole4)

    # pole-5
    camera_transform = carla.Transform(carla.Location(x=23.31, y=-15.61, z=6), carla.Rotation(camera_pitch, 135, 0))
    lidar_transform = carla.Transform(carla.Location(23.31, -15.61, 6), carla.Rotation(0, 0, 0))

    camera_pole5_rgb = world.spawn_actor(camera_rgb, camera_transform)
    image_queue_pole5_rgb = queue.Queue()
    camera_pole5_rgb.listen(image_queue_pole5_rgb.put)
    actor_list.append(camera_pole5_rgb)

    camera_pole5_sem = world.spawn_actor(camera_sem, camera_transform)
    image_queue_pole5_sem = queue.Queue()
    camera_pole5_sem.listen(image_queue_pole5_sem.put)
    actor_list.append(camera_pole5_sem)

    camera_pole5_ins = world.spawn_actor(camera_ins, camera_transform)
    image_queue_pole5_ins = queue.Queue()
    camera_pole5_ins.listen(image_queue_pole5_ins.put)
    actor_list.append(camera_pole5_ins)

    lidar_pole5 = world.spawn_actor(lidar_pole, lidar_transform)
    lidar_pole5_queue = queue.Queue()
    lidar_pole5.listen(lidar_pole5_queue.put)
    actor_list.append(lidar_pole5)

    # pole-6
    camera_transform = carla.Transform(carla.Location(x=-25.75, y=-19.10, z=6), carla.Rotation(camera_pitch, 45, 0))
    lidar_transform = carla.Transform(carla.Location(-25.75, -19.10, 6), carla.Rotation(0, 0, 0))

    camera_pole6_rgb = world.spawn_actor(camera_rgb, camera_transform)
    image_queue_pole6_rgb = queue.Queue()
    camera_pole6_rgb.listen(image_queue_pole6_rgb.put)
    actor_list.append(camera_pole6_rgb)

    camera_pole6_sem = world.spawn_actor(camera_sem, camera_transform)
    image_queue_pole6_sem = queue.Queue()
    camera_pole6_sem.listen(image_queue_pole6_sem.put)
    actor_list.append(camera_pole6_sem)

    camera_pole6_ins = world.spawn_actor(camera_ins, camera_transform)
    image_queue_pole6_ins = queue.Queue()
    camera_pole6_ins.listen(image_queue_pole6_ins.put)
    actor_list.append(camera_pole6_ins)

    lidar_pole6 = world.spawn_actor(lidar_pole, lidar_transform)
    lidar_pole6_queue = queue.Queue()
    lidar_pole6.listen(lidar_pole6_queue.put)
    actor_list.append(lidar_pole6)

    # pole-7
    camera_transform = carla.Transform(carla.Location(x=-24.38, y=18.88, z=6), carla.Rotation(camera_pitch, -45, 0))
    lidar_transform = carla.Transform(carla.Location(-24.38, 18.88, 6), carla.Rotation(0, 0, 0))

    camera_pole7_rgb = world.spawn_actor(camera_rgb, camera_transform)
    image_queue_pole7_rgb = queue.Queue()
    camera_pole7_rgb.listen(image_queue_pole7_rgb.put)
    actor_list.append(camera_pole7_rgb)

    camera_pole7_sem = world.spawn_actor(camera_sem, camera_transform)
    image_queue_pole7_sem = queue.Queue()
    camera_pole7_sem.listen(image_queue_pole7_sem.put)
    actor_list.append(camera_pole7_sem)

    camera_pole7_ins = world.spawn_actor(camera_ins, camera_transform)
    image_queue_pole7_ins = queue.Queue()
    camera_pole7_ins.listen(image_queue_pole7_ins.put)
    actor_list.append(camera_pole7_ins)

    lidar_pole7 = world.spawn_actor(lidar_pole, lidar_transform)
    lidar_pole7_queue = queue.Queue()
    lidar_pole7.listen(lidar_pole7_queue.put)
    actor_list.append(lidar_pole7)

    # pole-8
    camera_transform = carla.Transform(carla.Location(x=18.54, y=19.99, z=6), carla.Rotation(camera_pitch, -135, 0))
    lidar_transform = carla.Transform(carla.Location(18.54, 19.99, 6), carla.Rotation(0, 0, 0))

    camera_pole8_rgb = world.spawn_actor(camera_rgb, camera_transform)
    image_queue_pole8_rgb = queue.Queue()
    camera_pole8_rgb.listen(image_queue_pole8_rgb.put)
    actor_list.append(camera_pole8_rgb)

    camera_pole8_sem = world.spawn_actor(camera_sem, camera_transform)
    image_queue_pole8_sem = queue.Queue()
    camera_pole8_sem.listen(image_queue_pole8_sem.put)
    actor_list.append(camera_pole8_sem)

    camera_pole8_ins = world.spawn_actor(camera_ins, camera_transform)
    image_queue_pole8_ins = queue.Queue()
    camera_pole8_ins.listen(image_queue_pole8_ins.put)
    actor_list.append(camera_pole8_ins)

    lidar_pole8 = world.spawn_actor(lidar_pole, lidar_transform)
    lidar_pole8_queue = queue.Queue()
    lidar_pole8.listen(lidar_pole8_queue.put)
    actor_list.append(lidar_pole8)

    tick_counter = 0
    for _ in range(0, NUM_TIME_INITIAL_WAIT):
        world.tick()

        tick_counter += DELTA_SECOND

        image_pole1_rgb = image_queue_pole1_rgb.get()
        image_pole1_sem = image_queue_pole1_sem.get()
        image_pole1_ins = image_queue_pole1_ins.get()
        lidar_pole1_img = lidar_pole1_queue.get()

        image_pole2_rgb = image_queue_pole2_rgb.get()
        image_pole2_sem = image_queue_pole2_sem.get()
        image_pole2_ins = image_queue_pole2_ins.get()
        lidar_pole2_img = lidar_pole2_queue.get()

        image_pole3_rgb = image_queue_pole3_rgb.get()
        image_pole3_sem = image_queue_pole3_sem.get()
        image_pole3_ins = image_queue_pole3_ins.get()
        lidar_pole3_img = lidar_pole3_queue.get()

        image_pole4_rgb = image_queue_pole4_rgb.get()
        image_pole4_sem = image_queue_pole4_sem.get()
        image_pole4_ins = image_queue_pole4_ins.get()
        lidar_pole4_img = lidar_pole4_queue.get()

        image_pole5_rgb = image_queue_pole5_rgb.get()
        image_pole5_sem = image_queue_pole5_sem.get()
        image_pole5_ins = image_queue_pole5_ins.get()
        lidar_pole5_img = lidar_pole5_queue.get()

        image_pole6_rgb = image_queue_pole6_rgb.get()
        image_pole6_sem = image_queue_pole6_sem.get()
        image_pole6_ins = image_queue_pole6_ins.get()
        lidar_pole6_img = lidar_pole6_queue.get()

        image_pole7_rgb = image_queue_pole7_rgb.get()
        image_pole7_sem = image_queue_pole7_sem.get()
        image_pole7_ins = image_queue_pole7_ins.get()
        lidar_pole7_img = lidar_pole7_queue.get()

        image_pole8_rgb = image_queue_pole8_rgb.get()
        image_pole8_sem = image_queue_pole8_sem.get()
        image_pole8_ins = image_queue_pole8_ins.get()
        lidar_pole8_img = lidar_pole8_queue.get()

    for i in range(NUM_TIME_TICKS):

        print(i)
        world.tick()
        tick_counter += DELTA_SECOND

        image_pole1_rgb = image_queue_pole1_rgb.get()
        image_pole1_sem = image_queue_pole1_sem.get()
        image_pole1_ins = image_queue_pole1_ins.get()
        lidar_pole1_img = lidar_pole1_queue.get()

        image_pole2_rgb = image_queue_pole2_rgb.get()
        image_pole2_sem = image_queue_pole2_sem.get()
        image_pole2_ins = image_queue_pole2_ins.get()
        lidar_pole2_img = lidar_pole2_queue.get()

        image_pole3_rgb = image_queue_pole3_rgb.get()
        image_pole3_sem = image_queue_pole3_sem.get()
        image_pole3_ins = image_queue_pole3_ins.get()
        lidar_pole3_img = lidar_pole3_queue.get()

        image_pole4_rgb = image_queue_pole4_rgb.get()
        image_pole4_sem = image_queue_pole4_sem.get()
        image_pole4_ins = image_queue_pole4_ins.get()
        lidar_pole4_img = lidar_pole4_queue.get()

        image_pole5_rgb = image_queue_pole5_rgb.get()
        image_pole5_sem = image_queue_pole5_sem.get()
        image_pole5_ins = image_queue_pole5_ins.get()
        lidar_pole5_img = lidar_pole5_queue.get()

        image_pole6_rgb = image_queue_pole6_rgb.get()
        image_pole6_sem = image_queue_pole6_sem.get()
        image_pole6_ins = image_queue_pole6_ins.get()
        lidar_pole6_img = lidar_pole6_queue.get()

        image_pole7_rgb = image_queue_pole7_rgb.get()
        image_pole7_sem = image_queue_pole7_sem.get()
        image_pole7_ins = image_queue_pole7_ins.get()
        lidar_pole7_img = lidar_pole7_queue.get()

        image_pole8_rgb = image_queue_pole8_rgb.get()
        image_pole8_sem = image_queue_pole8_sem.get()
        image_pole8_ins = image_queue_pole8_ins.get()
        lidar_pole8_img = lidar_pole8_queue.get()

        if (i % NUM_SAVE_INTERVAL == 0):
            print("Saving Started")

            image_pole1_rgb.save_to_disk(export_folder + "pole1_rgb_%06d.png" % (image_pole1_rgb.frame))
            image_pole1_sem.save_to_disk(export_folder + "pole1_sem_%06d.png" % (image_pole1_sem.frame),
                                         carla.ColorConverter.CityScapesPalette)
            image_pole1_ins.save_to_disk(export_folder + "pole1_ins_%06d.png" % (image_pole1_ins.frame))
            rgb_loc = export_folder + "pole1_rgb_%06d.png" % (image_pole1_rgb.frame)
            image_loc = export_folder + "pole1_ins_%06d.png" % (image_pole1_ins.frame)
            process_instance_camera_data(1, image_loc, rgb_loc, tick_counter)
            lidar_pole1_img.save_to_disk(export_folder + "pole1_lidar_%06d.ply" % (lidar_pole1_img.frame))
            print("First Pole Saved")

            image_pole2_rgb.save_to_disk(export_folder + "pole2_rgb_%06d.png" % (image_pole2_rgb.frame))
            image_pole2_sem.save_to_disk(export_folder + "pole2_sem_%06d.png" % (image_pole2_sem.frame),
                                         carla.ColorConverter.CityScapesPalette)
            image_pole2_ins.save_to_disk(export_folder + "pole2_ins_%06d.png" % (image_pole2_ins.frame))
            rgb_loc2 = export_folder + "pole2_rgb_%06d.png" % (image_pole2_rgb.frame)
            image_loc2 = export_folder + "pole2_ins_%06d.png" % (image_pole2_ins.frame)
            process_instance_camera_data(2, image_loc2, rgb_loc2, tick_counter)
            lidar_pole2_img.save_to_disk(export_folder + "pole2_lidar_%06d.ply" % (lidar_pole2_img.frame))
            print("Second Pole Saved")

            image_pole3_rgb.save_to_disk(export_folder + "pole3_rgb_%06d.png" % (image_pole3_rgb.frame))
            image_pole3_sem.save_to_disk(export_folder + "pole3_sem_%06d.png" % (image_pole3_sem.frame),
                                         carla.ColorConverter.CityScapesPalette)
            image_pole3_ins.save_to_disk(export_folder + "pole3_ins_%06d.png" % (image_pole3_ins.frame))
            image_loc3 = export_folder + "pole3_ins_%06d.png" % (image_pole3_ins.frame)
            rgb_loc3 = export_folder + "pole3_rgb_%06d.png" % (image_pole3_rgb.frame)
            process_instance_camera_data(3, image_loc3, rgb_loc3, tick_counter)
            lidar_pole3_img.save_to_disk(export_folder + "pole3_lidar_%06d.ply" % (lidar_pole3_img.frame))
            print("Third Pole Saved")

            image_pole4_rgb.save_to_disk(export_folder + "pole4_rgb_%06d.png" % (image_pole4_rgb.frame))
            image_pole4_sem.save_to_disk(export_folder + "pole4_sem_%06d.png" % (image_pole4_sem.frame),
                                         carla.ColorConverter.CityScapesPalette)
            image_pole4_ins.save_to_disk(export_folder + "pole4_ins_%06d.png" % (image_pole4_ins.frame))
            image_loc4 = export_folder + "pole4_ins_%06d.png" % (image_pole4_ins.frame)
            rgb_loc4 = export_folder + "pole4_rgb_%06d.png" % (image_pole4_rgb.frame)
            process_instance_camera_data(4, image_loc4, rgb_loc4, tick_counter)
            lidar_pole4_img.save_to_disk(export_folder + "pole4_lidar_%06d.ply" % (lidar_pole4_img.frame))
            print("Fourth Pole Saved")

            image_pole5_rgb.save_to_disk(export_folder + "pole5_rgb_%06d.png" % (image_pole5_rgb.frame))
            image_pole5_sem.save_to_disk(export_folder + "pole5_sem_%06d.png" % (image_pole5_sem.frame),
                                         carla.ColorConverter.CityScapesPalette)
            image_pole5_ins.save_to_disk(export_folder + "pole5_ins_%06d.png" % (image_pole5_ins.frame))
            image_loc5 = export_folder + "pole5_ins_%06d.png" % (image_pole5_ins.frame)
            rgb_loc5 = export_folder + "pole5_rgb_%06d.png" % (image_pole5_rgb.frame)
            process_instance_camera_data(5, image_loc5, rgb_loc5, tick_counter)
            lidar_pole5_img.save_to_disk(export_folder + "pole5_lidar_%06d.ply" % (lidar_pole5_img.frame))
            print("Fifth Pole Saved")

            image_pole6_rgb.save_to_disk(export_folder + "pole6_rgb_%06d.png" % (image_pole6_rgb.frame))
            image_pole6_sem.save_to_disk(export_folder + "pole6_sem_%06d.png" % (image_pole6_sem.frame),
                                         carla.ColorConverter.CityScapesPalette)
            image_pole6_ins.save_to_disk(export_folder + "pole6_ins_%06d.png" % (image_pole6_ins.frame))
            image_loc6 = export_folder + "pole6_ins_%06d.png" % (image_pole6_ins.frame)
            rgb_loc6 = export_folder + "pole6_rgb_%06d.png" % (image_pole6_rgb.frame)
            process_instance_camera_data(6, image_loc6, rgb_loc6, tick_counter)
            lidar_pole6_img.save_to_disk(export_folder + "pole6_lidar_%06d.ply" % (lidar_pole6_img.frame))
            print("Sixth Pole Saved")

            image_pole7_rgb.save_to_disk(export_folder + "pole7_rgb_%06d.png" % (image_pole7_rgb.frame))
            image_pole7_sem.save_to_disk(export_folder + "pole7_sem_%06d.png" % (image_pole7_sem.frame),
                                         carla.ColorConverter.CityScapesPalette)
            image_pole7_ins.save_to_disk(export_folder + "pole7_ins_%06d.png" % (image_pole7_ins.frame))
            image_loc7 = export_folder + "pole7_ins_%06d.png" % (image_pole7_ins.frame)
            rgb_loc7 = export_folder + "pole7_rgb_%06d.png" % (image_pole7_rgb.frame)
            process_instance_camera_data(7, image_loc7, rgb_loc7, tick_counter)
            lidar_pole7_img.save_to_disk(export_folder + "pole7_lidar_%06d.ply" % (lidar_pole7_img.frame))
            print("Seventh Pole Saved")

            image_pole8_rgb.save_to_disk(export_folder + "pole8_rgb_%06d.png" % (image_pole8_rgb.frame))
            image_pole8_sem.save_to_disk(export_folder + "pole8_sem_%06d.png" % (image_pole8_sem.frame),
                                         carla.ColorConverter.CityScapesPalette)
            image_pole8_ins.save_to_disk(export_folder + "pole8_ins_%06d.png" % (image_pole8_ins.frame))
            image_loc8 = export_folder + "pole8_ins_%06d.png" % (image_pole8_ins.frame)
            rgb_loc8 = export_folder + "pole8_rgb_%06d.png" % (image_pole8_rgb.frame)
            process_instance_camera_data(8, image_loc8, rgb_loc8, tick_counter)
            lidar_pole8_img.save_to_disk(export_folder + "pole8_lidar_%06d.ply" % (lidar_pole8_img.frame))
            print("Eigth Pole Saved")

    print('\nDestroying %d actors...' % len(actor_list))
    client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])

    # Save the detected objects and tags to an Excel sheet
    df.to_excel(export_folder + '/detected_objects.xlsx', index=False)

    settings = world.get_settings()
    settings.synchronous_mode = False
    world.apply_settings(settings)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(' - Exited by user.')