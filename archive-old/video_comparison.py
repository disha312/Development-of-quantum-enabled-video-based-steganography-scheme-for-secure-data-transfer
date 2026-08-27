
import cv2

original_path = "input/MyTest_Video.mp4"
reconstructed_path = "output/reconstructed_video.mp4"


def get_video_properties(video_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Failed to open:", video_path)
        return None

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    duration = frame_count / fps if fps > 0 else 0

    cap.release()

    return fps, width, height, frame_count, duration


original = get_video_properties(original_path)
reconstructed = get_video_properties(reconstructed_path)


print("----- ORIGINAL VIDEO -----")
print("FPS:", original[0])
print("Resolution:", original[1], "x", original[2])
print("Frame count:", original[3])
print("Duration:", original[4], "seconds")

print("\n----- RECONSTRUCTED VIDEO -----")
print("FPS:", reconstructed[0])
print("Resolution:", reconstructed[1], "x", reconstructed[2])
print("Frame count:", reconstructed[3])
print("Duration:", reconstructed[4], "seconds")


print("\n----- COMPARISON -----")

print("FPS same:", original[0] == reconstructed[0])
print("Resolution same:",
      original[1] == reconstructed[1] and
      original[2] == reconstructed[2])
print("Frame count same:", original[3] == reconstructed[3])

duration_difference = abs(original[4] - reconstructed[4])
print("Duration difference:", duration_difference, "seconds")
