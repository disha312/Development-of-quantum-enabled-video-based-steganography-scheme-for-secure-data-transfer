
import cv2

video_path = "input/MyTest_Video.mp4"

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Failed to open video.")
else:
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    duration = frame_count / fps if fps > 0 else 0

    print("Video opened successfully.")
    print("FPS:", fps)
    print("Width:", width)
    print("Height:", height)
    print("Frame count:", frame_count)
    print("Duration:", duration, "seconds")


    # Day 10 — Read frames
    frames_read = 0

    frames_to_save = 3

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frames_read += 1

        if frames_read <= frames_to_save:
            filename = f"frames/frame_{frames_read:03d}.png"
            cv2.imwrite(filename, frame)
            print(f"Saved: {filename}")

    print("Frames successfully read:", frames_read)


    cap.release()