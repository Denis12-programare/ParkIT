import cv2
import easyocr
import re
import warnings
import time
# warnings.filterwarnings()

class OCR:
    def __init__(self, languages=None, allow_non_english=False):
        """
        :param languages: List of languages for OCR (default: ['en'])
        :param allow_non_english: If False, filters out non-English letters/digits
        """
        if languages is None:
            languages = ['en']
        self.reader = easyocr.Reader(languages)
        self.allow_non_english = allow_non_english

    def read_frame(self, frame, detail=0):
        """
        Read text from a single OpenCV frame.
        :param frame: Image frame (numpy array, BGR)
        :param detail: EasyOCR detail level (0 = text only)
        :return: List of recognized strings
        """
        # Convert frame to RGB for EasyOCR
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.reader.readtext(img_rgb, detail=detail)

        if not self.allow_non_english:
            # Keep only English letters, digits, and spaces
            result = [re.sub(r'[^A-Za-z0-9 ]+', '', text) for text in result]

        return result
    def run(self):
            cap = cv2.VideoCapture(0)  # 0 = default camera
            if not cap.isOpened():
                print("❌ Could not open camera")
                exit()

            print("📷 Press 'q' to quit")
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # OCR on the current frame
                start = time.time()
                text = ocr.read_frame(frame, detail=0)

                # Show result on the frame
                display_text = text[0] if text else ""
                # cv2.putText(frame, display_text, (30, 50),
                #             cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                # cv2.imshow("Camera OCR", frame)
                if display_text:
                    print(time.time() - start)
                    print(display_text)
                    break

                # Show camera feed

                # Exit on 'q'
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     break

            cap.release()
            return(display_text)


if __name__ == "__main__":
    ocr = OCR()
    ocr.run()


