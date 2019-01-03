import numpy as np
import cv2
import pytesseract
from datetime import datetime, date
import os


def apply_threshold(img, argument):
    switcher = {
        1: cv2.threshold(cv2.GaussianBlur(img, (9, 9), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        2: cv2.threshold(cv2.GaussianBlur(img, (7, 7), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        3: cv2.threshold(cv2.GaussianBlur(img, (5, 5), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        4: cv2.threshold(cv2.medianBlur(img, 5), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        5: cv2.threshold(cv2.medianBlur(img, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        6: cv2.adaptiveThreshold(cv2.GaussianBlur(img, (5, 5), 0), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 31, 2),
        7: cv2.adaptiveThreshold(cv2.medianBlur(img, 3), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2),
    }
    return switcher.get(argument, "Invalid method")


def get_birthdate_string(img):
    # Get image height and width channels
    height, width, channels = img.shape

    # Crop the lower part of the NID image
    img = img[int(height/2):height, 0:width]

    # Convert to gray
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply dilation and erosion to remove some noise
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)

    i = 1;
    while i < 8:
        #  Apply threshold to get image with only black and white
        img1 = apply_threshold(img, i)
        i += 1

        # Recognize text with tesseract for python
        prediction = pytesseract.image_to_string(img1, lang="eng")

        # sending value to find_match function to get the date of birth as string (removing extra spaces and converting
        # all character to small)
        full_date = find_match(prediction.strip().lower())

        # # verifying if OCR is reading it correctly or not
        months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
        for idx, m in enumerate(months):
            if m in full_date:
                return full_date

    return 'no'


def find_match(result):
    keywords = ["date", "birth", "of","jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]

    for key in keywords:
        if key in result and key == "birth":
            index = result.index(key)
            return result[index + 6: index + 17]
        elif key in result and key == "of":
            index = result.index(key)
            return result[index + 9:index + 20]
        elif key in result and key == "date":
            index = result.index(key)
            return result[index + 14:index + 25]
        else:
            index = result.index(key)
            return result[index - 3: index + 8]


def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def is21plus(age):
    if age >= 21:
        print('Yes, age is 21+')
    else:
        print('No, age is under 21')


if __name__ == '__main__':

    image = ''

    option = int(input("Input 1 to capture image \nInput 2 to get image from the local folder\n"))

    if option == 1:
        # Open camera using OpenCV
        camera = cv2.VideoCapture(0)

        # Check if camera opened successfully
        if not camera.isOpened():
            print("Error opening video stream or file")
        else:
            # Read until video is completed
            print("Press Q to capture a photo of NID card")
            while camera.isOpened():
                # Capture frame-by-frame
                ret, image = camera.read()

                if ret:

                    # Display the resulting frame
                    cv2.imshow('Frame', image)

                    # Press Q on keyboard to  exit
                    if cv2.waitKey(25) & 0xFF == ord('q'):
                        break

                # Break the loop
                else:
                    break

            # When everything done, release the video capture object
            camera.release()

            # Closes all the frames
            cv2.destroyAllWindows()
    else:
        # Read image using opencv
        if os.path.isfile('image1.jpg'):
            image = cv2.imread('image1.jpg')

    if image is not '':
        # Read image text and get date of birth as string
        dob = get_birthdate_string(image)

        if dob != 'no':

            # Calculating age
            age = calculate_age(datetime.strptime(dob, "%d %b %Y"))

            print("User's age is ", age)
            
            # Checking if age is 21+ or not
            is21plus(age)
        else:
            print("OCR could not read the image properly, please try again")
    else:
        print("No image found")

