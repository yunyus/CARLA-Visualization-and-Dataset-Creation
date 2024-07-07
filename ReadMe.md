# CARLA Simulation Visualization and Dataset Creation Tools

This repository contains various tools to generate and visualize data from CARLA simulations. The tools include scripts for data generation, 2D simulation visualization, GIF creation, graph generation, and dataset creation from CARLA simulations.

## Project Structure

```
carla_simulation_tools/
│
├── src/
│   ├── 2d_generator.py         # Generates a 2D simulation of the ride
│   ├── data_generator.py       # Generates data from a single simulation in CARLA
│   ├── gif_generator.py        # Creates a GIF of the ride
│   ├── graph_generator.py      # Generates graphs of speed, acceleration, etc., of the ride
│   ├── dataset.py              # Generates a general dataset for CARLA road, collects object photos and data
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

## Setup

1. Clone the repository:

2. Install the required packages:

3. Ensure you have CARLA installed. Follow the instructions on the [CARLA website](https://carla.org/) to set up CARLA on your system.

## Usage

### Data Generation

To generate data from a single simulation in CARLA, run:

```
python src/data_generator.py
```

#### 2D Simulation Visualization

To generate a 2D simulation of the ride, run:

```
python src/2d_generator.py
```

#### GIF Creation

To create a GIF of the ride, run:

```
python src/gif_generator.py
```

#### Graph Generation

To generate graphs of speed, acceleration, etc., of the ride, run:

```
python src/graph_generator.py
```

### Dataset Creation

To generate a general dataset for CARLA road, collect object photos, and data from the simulation, run:

```
python src/dataset.py
```

**Note:** Ensure that you are careful about the file names and locations as the scripts depend on specific file structures and paths.

Make sure to have a CARLA server running before executing any scripts. You can start the CARLA server using:

```
./CarlaUE4.sh
```

or for Windows:

```
CarlaUE4.exe
```
