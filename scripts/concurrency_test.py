import threading
import requests

BASE_URL = "http://localhost:8001"  # confirm this matches your docker-compose port mapping

# same resource + same time slot for both — this is the whole point
BOOKING_PAYLOAD = {
    "b_r_id": 1,       # pick a resource id that exists in your DB
    "b_user_id": None,     # use two DIFFERENT user ids for the two threads (more realistic)
    "start_time": "2026-08-12T02:00:00",
    "end_time": "2026-08-12T03:00:00"# ISO datetime string, e.g. "2026-08-15T10:00:00"
}

barrier = threading.Barrier(2)
results = {}  # thread name -> (status_code, response_json)

def fire_booking(thread_id, payload):
    barrier.wait()
    resp = requests.post(f"{BASE_URL}/bookings", json=payload)
    try:
        body = resp.json()
    except ValueError:
        body = resp.text
    results[thread_id] = (resp.status_code, body)
# build two payloads — same slot, different user_id
payload_a = {**BOOKING_PAYLOAD, "b_user_id": 99}
payload_b = {**BOOKING_PAYLOAD, "b_user_id": 1000}

t1 = threading.Thread(target=fire_booking, args=("thread-1", payload_a))
t2 = threading.Thread(target=fire_booking, args=("thread-2", payload_b))

t1.start()
t2.start()
t1.join()
t2.join()

for name, (status, body) in results.items():
    print(name, status, body)