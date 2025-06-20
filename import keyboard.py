import keyboard

def on_key(event):
    print(f"Name: {event.name} | Scan Code: {event.scan_code} | Event Type: {event.event_type}")

print("اضغط على أي زر من السماعة...")
keyboard.hook(on_key)
keyboard.wait()
