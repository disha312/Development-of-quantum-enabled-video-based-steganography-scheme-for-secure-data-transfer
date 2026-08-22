
import cv2

input_video = "input/MyTest_Video.mp4"
output_video = "output/reconstructed_video.mp4"

cap = cv2.VideoCapture(input_video)

if not cap.isOpened():
    print("Failed to open video.")
else:
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    writer = cv2.VideoWriter(
        output_video,
        fourcc,
        fps,
        (width, height)
    )

    frames_written = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        writer.write(frame)
        frames_written += 1

    cap.release()
    writer.release()

    print("Video reconstruction completed.")
    print("Frames written:", frames_written)
    print("Output:", output_video)