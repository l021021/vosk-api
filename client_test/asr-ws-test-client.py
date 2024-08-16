#!/usr/bin/env python3

import wave
import sys
import traceback

from websocket import create_connection

ws = create_connection("ws://127.0.0.1:2900")

# wf = wave.open(sys.argv[1], "rb")
wf = wave.open('D:\\CODE\\my-vosk-api\\test_recording.wav', "rb")
ws.send('{ "config" : { "sample_rate" : %d } }' % (wf.getframerate()))
buffer_size = int(wf.getframerate() * 0.2)  # 0.2 seconds of audio

try:

    while True:
        data = wf.readframes(buffer_size)

        if len(data) == 0:
            break

        ws.send_binary(data)
        print(ws.recv())
    ws.send('{"eof" : 1}')
    print(ws.recv())

except Exception as err:
    print(''.join(traceback.format_exception(type(err), err, err.__traceback__)))
