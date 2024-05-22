import paho.mqtt.publish as publish

mqtt_broker_address = "192.168.0.113"
mqtt_channel = "kv/channel"
message = "Send this message to your Jetson/Raspberry: "
publish.single(mqtt_channel, message, hostname=mqtt_broker_address)
