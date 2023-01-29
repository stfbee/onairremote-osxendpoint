from http.server import BaseHTTPRequestHandler, HTTPServer
import AVFoundation
import CoreAudio
import struct
import json


def is_microphone_recording():
    mic_ids = {
        mic.connectionID(): mic
        for mic in AVFoundation.AVCaptureDevice.devicesWithMediaType_(
            AVFoundation.AVMediaTypeAudio
        )
    }

    opa = CoreAudio.AudioObjectPropertyAddress(
        CoreAudio.kAudioDevicePropertyDeviceIsRunningSomewhere,
        CoreAudio.kAudioObjectPropertyScopeGlobal,
        CoreAudio.kAudioObjectPropertyElementMaster
    )

    def extract(mic_id):
        response = CoreAudio.AudioObjectGetPropertyData(mic_id, opa, 0, [], 4, None)
        return bool(struct.unpack('I', response[2])[0])

    extracted = list(map(extract, mic_ids))

    return extracted.count(True) > 0


class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    # GET sends back a Hello world message
    def do_GET(self):
        self._set_headers()
        response = {'on_air': is_microphone_recording()}
        self.wfile.write(bytes(json.dumps(response), 'utf-8'))


def run(server_class=HTTPServer, handler_class=Server, port=4200):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    print('Listening on *:%d' % port)
    httpd.serve_forever()


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
