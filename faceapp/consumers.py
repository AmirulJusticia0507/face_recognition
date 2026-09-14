import json

from channels.generic.websocket import AsyncWebsocketConsumer


class DetectionNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('detection_notifications', self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard('detection_notifications', self.channel_name)

    async def face_detected(self, event):
        payload = {
            'type': event.get('type', 'face.detected'),
            'scan_id': event.get('scan_id'),
            'camera_id': event.get('camera_id'),
            'camera_name': event.get('camera_name'),
            'building': event.get('building'),
            'room': event.get('room'),
            'face_detected': event.get('face_detected'),
            'face_count': event.get('face_count'),
            'matched_person': event.get('matched_person'),
            'similarity_percent': event.get('similarity_percent'),
            'timestamp': event.get('timestamp'),
        }
        await self.send(text_data=json.dumps(payload))
