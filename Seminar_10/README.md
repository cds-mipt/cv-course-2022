Проверено на версии [CARLA 0.9.12](https://carla.readthedocs.io/en/0.9.12/).

## Установка

Эти действия необходимо выполнить один раз

```bash
export CARLA_ROOT=~/carla
export CARLA_VERSION=0.9.12

mkdir -p ${CARLA_ROOT}/catkin_ws/src && ln -s `pwd` ${CARLA_ROOT}/catkin_ws/src/carla && cd ${CARLA_ROOT}/catkin_ws/src
git clone https://github.com/carla-simulator/ros-bridge.git --recurse-submodules

cd ${CARLA_ROOT}/catkin_ws/src/carla/scripts
bash install_carla.sh
```

## Сборка и запуск контейнера с CARLA API и ROS Bridge

Эти действия нужно выполнять каждый раз при начале работы с симулятором, либо закоммитить контейнер после сборки.

```bash
export CARLA_ROOT=~/carla
export CARLA_VERSION=0.9.12

cd ${CARLA_ROOT}/catkin_ws/src/carla/docker
bash build.sh
bash start.sh
bash into.sh

cd carla/catkin_ws
rosdep update
rosdep install --from-paths src --ignore-src -r
catkin_make -DCMAKE_BUILD_TYPE=Release
```

## Запуск среды симуляции

Симулятор запускается на рабочей машине вне докера каждый раз при начале работы с симулятором.

```bash
export CARLA_ROOT=~/carla
export CARLA_VERSION=0.9.12

cd ${CARLA_ROOT}/CARLA_${CARLA_VERSION}
./CarlaUE4.sh
```

## Работа с симулятором

Дальнейшее взаимодействие с симулятором осуществляется Python API симулятора. К нему можно обращаться либо непосредстенно, либо используя ROS Bridge. Все обращения должны производиться из запущенного контейнера с установленным API и зависимостями, а также собранным ROS Bridge. Для начала нужно войти в контейнер:

```bash
export CARLA_ROOT=~/carla
export CARLA_VERSION=0.9.12

cd ${CARLA_ROOT}/catkin_ws/src/carla/docker
bash into.sh
cd ~/carla
```

### Python API

Примеры работы с API можно найти в директории `${CARLA_ROOT}/CARLA_${CARLA_VERSION}/PythonAPI/examples`. 

```bash
cd ~/carla/CARLA_0.9.12/PythonAPI
```

Например, сгенерировать траффик (пешеходов и автомобили) можно следующим образом:
```bash
python examples/generate_traffic.py
```

Запустить управление автомобилем в ручном режиме:
```bash
python examples/manual_control.py
```

Базовое конфигурирование симулятора можно осуществлять с помощью скрипта `util/config.py`. Например, чтобы отключить рендеринг в отдельном окне:
```bash
python util/config.py --no-rendering
```
Изменить число циклов отрисовки:
```bash
python util/config.py --fps=10
```
Загрузить другую карту:
```bash
python util/config.py --map Town02
```

### ROS Bridge

```bash
cd ~/carla/catkin_ws
source devel/setup.bash
```

Запуск bridge и загрузка карты `Town07`:
```bash
roslaunch carla_ros_bridge carla_ros_bridge.launch \
    town:=Town07 \
    fixed_delta_seconds:=0.1 \
    timeout:=60
```

Создание объектов на карте (в т.ч. собственного авто):
```bash
roslaunch carla_spawn_objects carla_spawn_objects.launch \
    objects_definition_file:=/home/docker_carla/carla/catkin_ws/src/carla/config/objects.json
```

Режим ручного управления (после запуска нажать B для активации ручного управления)
```bash
roslaunch carla_manual_control carla_manual_control.launch
```

Запуск RViz:
```bash
rviz -d src/carla/rviz/carla.rviz
```

### Регулировка частот сенсоров

Частоты задаются через параметр `sensor_tick`. Пример его использования можно найти в файле [lidar_gyro_debug.json](config/lidar_gyro_debug.json). В нем частота лидара установлена в 10 Гц, камеры - 10 Гц, всех 8-ми IMU - 100 Гц. Кроме того, при запуске ROS Bridge необходимо параметр `fixed_delta_seconds` установить равным (или меньшим) минимальному `sensor_tick`. Можно установить равным 0, но при этом будут наблюдаться незначительные колебания частоты данных в ROS, что, в целом, приближено к реальности. А также необходимо ROS Bridge запускать в асинхронном режиме `synchronous_mode:=False`, так как в синхронном наблюдались проблемы с публикацией данных камеры (они не публиковались, так как bridge считал их устаревшими).

Запуск ROS Bridge:
```bash
roslaunch carla_ros_bridge carla_ros_bridge.launch \
    town:=Town05 \
    fixed_delta_seconds:=0.005 \\
    timeout:=60 \
    synchronous_mode:=False
```

Создание собственного авто:
```bash
roslaunch carla_spawn_objects carla_spawn_objects.launch \
    objects_definition_file:=/home/docker_carla/carla/catkin_ws/src/carla/config/lidar_gyro_debug.json
```

### Данные лидара

Если хочется, чтобы в ROS публиковалось полное облако, то необходимо заполнить параметры следующим образом: пусть h - число лучей лидара (высота облака), w - ширина облака, тогда нужно чтобы 
1. `fixed_delta_seconds * rotation_frequency == 1`
2. `points_per_second == w * h * rotation_frequency`

## Работа с bag файлом

Информацию по работе с bag файлами можно найти здесь: [Материалы RAII Summer School 2021, Sochi, Sirius](https://github.com/cds-mipt/raai_summer_school_cv_2021/tree/main/ros_basics)

Запустим запись BAG файла с данными лидара и камеры:
rosbag record -O town07 /carla/ego_vehicle/camera_left/image /carla/ego_vehicle/os64central/sensor

Пример работы с BAG файлом в Python - [Unpacking rosbag.ipynb](./notebook/Unpacking%20rosbag.ipynb)
