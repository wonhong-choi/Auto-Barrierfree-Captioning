# consumers.py

import os
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
from ai.barrier_free_caption_gen import BarrierFreeCaptionGenerator

class CaptionProcessingConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.caption_generator = BarrierFreeCaptionGenerator()

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        # Perform caption processing here
        filepath = text_data

        # Generate captions from file
        captions = self.caption_generator.make_caption_from_file(filepath)

        # Write captions to a file
        output_file = filepath.split("/")
        output_file[-2] = "subtitle"
        output_file[-1] = output_file[-1][:-3] + "vtt"
        output_file = "/".join(output_file)
        # output_file = '/path/to/output/captions.txt'  # Replace with the desired output file path
        with open(output_file, mode="w", encoding="utf-8") as f:
            f.write(captions)

        # Send completion message to the client
        await self.send(text_data="Caption processing completed")

    async def caption_processing_notification(self, event):
        # Send a notification to the client
        await self.send(text_data=event["message"])