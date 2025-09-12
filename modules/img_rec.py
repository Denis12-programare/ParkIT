import easyocr
import re

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

    def read(self, image_path, detail=0):
        """
        Read text from an image.
        :param image_path: Path to the image file
        :param detail: EasyOCR detail level (0 = text only)
        :return: List of recognized strings
        """
        result = self.reader.readtext(image_path, detail=detail)

        if not self.allow_non_english:
            # Keep only English letters, digits, and spaces
            result = [re.sub(r'[^A-Za-z0-9 ]+', '', text) for text in result]

        return result


# Example usage
if __name__ == "__main__":
    ocr = OCR()  # English only, filter enabled
    text = ocr.read("img.jpg", detail=0)
    if text:
        print("First detected:", text[0])
    else:
        print("No text detected.")
