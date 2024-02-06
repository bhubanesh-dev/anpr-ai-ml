import os

import cv2
from imutils import paths
import anpr_YOLOv8 as ANPR
from essentials import mk_title

# This is for mass input
IMG_PATH = 'bike_samples/'
file_paths = sorted(list(paths.list_images(IMG_PATH)), reverse=False)
# print(file_paths)


# Get the license plates using Y0L0v8 Model in the Predefined Resolution
for file_path in file_paths:
    # Path Preprocessing to save image
    path = str(file_path)
    remove = ".jpg"
    bare = path.replace(remove, '')
    op_path = "results/" + bare + '/'
    org_title = bare.replace(IMG_PATH, '')

    if not os.path.exists(op_path):
        os.makedirs(op_path)

    org_img = cv2.imread(file_path)
    img_cvt = cv2.resize(org_img, (1280, 720))

    title = "0_" + "Original Image"
    # ANPR.show_img(title, img_cvt)/home/avisek
    output_txt = mk_title(org_title, title)
    ANPR.save_img(op_path, output_txt, img_cvt)

    # Run the YOLOv8 Model and Check if number plate is detected in input
    check = ANPR.get_license_plate(img_cvt)
    if not check:
        print("License plate not detected for: " + file_path)
        continue
    else:
        print("License plate detected for: " + file_path)

        # Assign the YOLOv8 Model detection results
        results, detected_box = check

        # Crop & Plot the License plate if detection was successful
        license_plate = ANPR.crop_plate(img_cvt, results, detected_box, op_path, org_title)

        # Resize the cropped plate for standardized size
        height, width, channels = license_plate.shape
        normal_format = cv2.resize(license_plate, (500, 250), interpolation=cv2.INTER_CUBIC)

        # Preprocess license plate
        preprocessed_image, grayscale = ANPR.preprocess_lPlate(normal_format, op_path, org_title)

        # Clean the license plate to remove White blobs(Connected Component analysis)
        clean_img = ANPR.clean_license_plate(preprocessed_image, grayscale.shape, op_path, org_title)

        # Character Segmentation
        lPlate, segments, bounding_boxes = ANPR.segment_lic_plate(clean_img, op_path, org_title)

        # Optical Character Recognition
        result_img, license_number = ANPR.apply_ocr(lPlate, bounding_boxes, op_path, org_title)

