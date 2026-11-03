import cv2
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from merge import merge_notes

def main():
    pic_count = capture_images()
    if pic_count:
        merge_notes(delete_originals=True)
    else:
        print("No pictures captured; skipping PDF.")

    
def capture_images():
    pic_count = 0
    cap = cv2.VideoCapture(0) #Default

    if not cap.isOpened():
        print("Error: Could not open video stream from iPhone.")
        return 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Display the frame
        cv2.imshow('iPhone Camera', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

        elif key == ord('s'):
            filename = f'captured_image_{pic_count}.jpg'
            cv2.imwrite(filename, frame)
            print(f"Imgae saved as {filename}")
            pic_count += 1

    # Release the camera and close any OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
    return pic_count

if __name__ == "__main__":
    main()