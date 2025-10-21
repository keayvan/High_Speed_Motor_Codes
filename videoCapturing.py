from obsws_python import ReqClient
import time

# OBS WebSocket connection
host = "localhost"
port = 4455
password = "L8f5Xih2spGtUk15"

client = ReqClient(host=host, port=port, password=password)
print("✅ Connected to OBS.")

# Scene names
screen_scene = "Scene 2"   # contains Display Capture
webcam_scene = "Scene"     # contains Webcam

# Set both scenes to record using separate outputs
print("🎬 Preparing separate recordings...")

# Switch to screen scene and start recording
client.set_current_program_scene(screen_scene)
print(f"🖥️ Recording scene: {screen_scene}")
client.start_record()
print("🟢 Screen recording started.")

# Wait 1 second before starting the webcam recording
# time.sleep(1)

# Switch to webcam scene and start a second recording output (if configured)
# This assumes you have another “Recording Output” in OBS (e.g. Output 2)
try:
    client.trigger_hotkey_by_name("OBSBasic.StartRecording2")  # second output
    print("🎥 Webcam recording started (separate file).")
except Exception as e:
    print("⚠️ Could not start second recording automatically. "
          "Make sure you've configured a 2nd recording output in OBS.")
    print(e)

# Wait for user to stop both
input("Press Enter to STOP both recordings...")

# Stop screen recording
res = client.stop_record()
print("🟥 Screen recording stopped.")
if hasattr(res, "output_path"):
    print(f"💾 Saved screen file: {res.output_path}")

# Stop webcam recording
try:
    client.trigger_hotkey_by_name("OBSBasic.StopRecording2")
    print("🟥 Webcam recording stopped.")
except Exception:
    print("⚠️ Could not stop second recording automatically. Please stop it manually in OBS.")
