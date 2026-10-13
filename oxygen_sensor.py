oxygen_sensor = get_component("oxygen_sensor")

oxygen_sensor.calibrate(oxygen_sensor.get_value() * 100)