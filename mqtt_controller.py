import paho.mqtt.client as mqtt


def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

client = mqtt.Client()
client.on_message = on_message

# Set username and password
client.username_pw_set("admin", "raven")

client.connect("192.168.1.115", 1883, 60)  # change the IP address to your MQTT server's IP address and port if required

# Subscribe to a topic.
client.subscribe("your/topic")

# Publish a message to a topic.
client.publish("your/topic", "your message")

# Blocking call that processes network traffic, dispatches callbacks, and
# handles reconnecting. Other loop*() functions are available that give a
# threaded interface and a manual interface.
client.loop_forever()