sensor = get_component("pressure_sensor")

value = sensor.get_value()

if value % 2 == 1:
    value += 1

sensor.stabilize(value)