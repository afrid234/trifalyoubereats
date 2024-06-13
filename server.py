from http.server import BaseHTTPRequestHandler, HTTPServer
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import hmac
import requests
import hashlib
import json
import os
import base64

client_secret = b'i6oVqcAHwvbae2l7CC9kuNg_Lm_8HAPffW3USVQS'

cred = credentials.Certificate("/etc/secrets/credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Read and verify the signature
        signature = self.headers.get('X-Uber-Signature')
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        expected_signature = hmac.new(client_secret, body, hashlib.sha256).hexdigest()

        if signature != expected_signature:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid signature'}).encode())
            return

        # Parse the webhook event
        print("Response sent to the server:")
        print(body.decode())
        event_data = json.loads(body)
        db.collection("users").document("afridfaruk649@gmail.com").collection("Realtime Notification").document("Uber Eats").update({"json": event_data})
        event_id = event_data['event_id']
        event_time = event_data['event_time']
        meta = event_data['meta']
        user_id = meta['user_id']
        resource_id = meta['resource_id']
        status = meta['status']
        resource_href = event_data['resource_href']

        # Process the event here and acknowledge receipt with a 200 response
        self.send_response(200)
        self.end_headers()

def run(server_class=HTTPServer, handler_class=WebhookHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting http server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()

