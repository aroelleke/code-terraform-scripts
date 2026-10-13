transmitter = get_component("transmitter")
thermometer = get_component("thermometer")

transmitter.connect("earth")
transmitter.transmit("current_temperature", thermometer.get_value())