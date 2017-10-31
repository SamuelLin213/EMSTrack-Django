
from ambulances.management.commands._client import BaseClient

from ambulances.models import Ambulances, User
from ambulances.serializers import MQTTAmbulanceLocSerializer, MQTTAmbulanceListSerializer

from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

class UpdateClient(BaseClient):

    def __init__(self,
                 broker,
                 stdout,
                 style,
                 signal_func,
                 obj,
                 verbosity = 1):
        super().__init__(broker, stdout, style, verbosity)

        self.signal_func = getattr(self, signal_func)
        self.obj = obj
        self.pubcount = 0

    # The callback for when the client receives a CONNACK
    # response from the server.
    def on_connect(self, client, userdata, flags, rc):

        # is connected?
        if not super().on_connect(client, userdata, flags, rc):
            return False

        self.signal_func(self.obj)

        return True

    def publish(self, topic, message, *vargs, **kwargs):
        # increment pubcount then publish
        self.pubcount += 1
        self.client.publish(topic, message, *vargs, **kwargs)

    def create_ambulance(self, obj):

        # Publish location
        serializer = MQTTAmbulanceLocSerializer(obj)
        json = JSONRenderer().render(serializer.data)
        self.publish('ambulance/{}/location'.format(obj.id), json, qos=2, retain=True)

        # Publish status
        self.publish('ambulance/{}/status'.format(obj.id), obj.status.name, qos=2, retain=True)

    def edit_ambulance(self, obj):
        # Change ambulance lists for all users
        for user in User.objects.filter(ambulances=obj.id):
            serializer = MQTTAmbulanceListSerializer(user)
            json = JSONRenderer().render(serializer.data)
            self.publish('user/{}/ambulances'.format(user.username), json, qos=2, retain=True)

    # Message publish callback
    def on_publish(self, client, userdata, mid):
        # make sure all is published before disconnecting
        self.pubcount -= 1
        # print("on_publish: '{}', '{}'".format(client, userdata))
        if self.pubcount == 0:
            self.disconnect()
        