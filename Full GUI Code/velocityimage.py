import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter.filedialog import askopenfilename
from skimage import measure, morphology
import pydicom as dicom
import pydicom.encoders.gdcm
import pydicom.encoders.pylibjpeg
import sys
import os
from os import path
import math
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import config

import logging
logging.getLogger('tensorflow').setLevel(logging.ERROR)


class VelocityImage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=config.bg_col)
        self.controller = controller

        def choose_file():
            """
            Uses askopenfilename() function from tkinter.filedialog to allow the user to browse their system files and
            choose which one to upload to the GUI. File expected in either .png or .dcm format.

            If image is .png, it is saved to global config.U_img. A copy is saved to config.U_original_img in case user
            chooses to undo changes.
            image_plot() is called to display .png image.

            If image is .dcm it is loaded using function dcmread() from pydicom. 80 pixels are immediately deleted from
            the top in case patient name is there.
            DICOM image saved to config.U_dicom_img, and a copy saved to U_dicom_original.
            process_dicom() is called to display .dcm frame.
            """
            # Ensure only DICOM or PNG files can be selected
            file_path = askopenfilename(filetypes=[("DICOM files", "*.dcm"), ("PNG files", "*.png")])
            config.U_image_path = file_path
            file_extension = os.path.splitext(config.U_image_path)[1].lower()  # Get file extension

            if file_extension == '.png':
                config.U_original_img = Image.open(config.U_image_path)
                config.U_img = config.U_original_img.copy()
                image_plot(config.U_img)

            elif file_extension == '.dcm':
                config.dicom_upload = True
                config.U_dcm_box_coords = []

                print('Extracting DICOM may take up to a minute.')
                ds = dicom.dcmread(config.U_image_path)
                dicom_img_array = ds.pixel_array[config.U_dicom_frame, :, :, 0]
                config.U_dicom_img = Image.fromarray(np.uint8(dicom_img_array))  # Convert pixel array to image

                width, height = config.U_dicom_img.size
                config.U_dicom_img = config.U_dicom_img.crop((0, 80, width, height))  # Crop off top of DICOM

                config.U_dicom_img = config.U_dicom_img.convert("RGB")  # Convert the grayscale image to RGB
                config.U_dicom_original = config.U_dicom_img.copy()  # Save a copy in case user wants to undo changes

                process_dicom()

            else:
                pass

        def process_dicom():
            """
            Displays DICOM frame in GUI. Allows user to click to draw a box around the area of interest, using functions
            on_click() and draw_box().
            Save coordinates where the user has clicked in global config.U_dcm_box_coords, and edits global DICOM image
            config.U_dicom_img.
            """
            fig, ax = plt.subplots(figsize=(10, 4.9))
            img_display = ax.imshow(config.U_dicom_img, cmap='gray')  # Keep a reference to the image plot for editing
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, self)
            canvas.get_tk_widget().grid(row=0, column=0, columnspan=11)

            # Stuff for detecting mouse clicks on plot
            def on_click(event):
                if event.inaxes is not None:  # Check if the click was inside the plot axes.
                    config.U_dcm_box_coords = np.append(config.U_dcm_box_coords, [event.xdata, event.ydata])

                    if len(config.U_dcm_box_coords) == 4:  # Once there are 4 coordinates a box is drawn on the image.
                        config.U_dicom_img = draw_box(config.U_dicom_img, config.U_dcm_box_coords)

                    img_display.set_data(config.U_dicom_img)  # Edit image in plot and redraw canvas.
                    canvas.draw()

            canvas.mpl_connect('button_press_event', on_click)  # Bind on_click function to mouse click events.

        def draw_box(original_img, box_coords):
            """
            Takes and image and array of coordinates in order to draw a box on the image and return the edited version.

            :param original_img: Image object to be edited by function. Box drawn on it at specified coordinates.
            :param box_coords:  Array containing coordinates of diagonally opposing corners of the box to be drawn.

            :return box_img: Image object which is the original image but with box drawn on.
            """
            box_img = original_img.copy()
            x1, y1 = round(box_coords[-4]), round(box_coords[-3])
            x2, y2 = round(box_coords[-2]), round(box_coords[-1])

            # Define the color of the rectangle (B, G, R) and the thickness.
            colour = (0, 255, 0)  # Green color in BGR

            # Draw rectangles on image by looping through pixels and editing using putpixel() from PIL.
            for x in range(box_img.size[0]):
                for y in range(box_img.size[1]):
                    if (((min(x1, x2) < x < max(x1, x2)) and (y == y1 or y == y2)) or
                            ((min(y1, y2) < y < max(y1, y2)) and (x == x1 or x == x2))):
                        box_img.putpixel((x, y), colour)

            return box_img

        def crop_dicom():
            """
            Takes global config.U_dcm_box_coords and crops the DICOM frame to the desired size and shape as drawn by the
            user.
            Activated by GUI button 'btn_crop_dicom'.
            Saves cropped image to global config.U_img. This is the same variable to which the image would have been
            saved immediately were it already a processed .png, rather than .dcm which requires loading in and cropping
            to include only the area of interest.
            Calls image_plot() to display the new cropped image and allow user to proceed with analysis.
            """
            x1, y1 = round(config.U_dcm_box_coords[0]), round(config.U_dcm_box_coords[1])
            x2, y2 = round(config.U_dcm_box_coords[2]), round(config.U_dcm_box_coords[3])
            left, right = min(x1, x2), max(x1, x2)
            top, bottom = min(y1, y2), max(y1, y2)
            config.U_img = config.U_dicom_img.crop((left, top, right, bottom))  # Crop DICOM based on box drawn by user.

            # Remove stray coloured pixels left from the box drawn on the image. In certain situations they are not
            # cropped out.
            for x in range(config.U_img.width):
                for y in range(config.U_img.height):
                    if config.U_img.getpixel((x, y)) == (0, 255, 0):
                        config.U_img.putpixel((x, y), (0, 0, 0))

            config.U_original_img = config.U_img.copy()
            image_plot(config.U_img)

        def image_plot(display_img):
            """
            Displays image in GUI. Allows user to click to draw a box around anomalies, using functions on_click() and
            draw_box().
            Save coordinates where the user has clicked in global config.U_box_coords, and edits global image
            config.U_img.
            Global config.anomaly_mode dictates which image is to be edited, depending on whether we are dealing with an
            original or already annotated image.

            :param display_img: Image object to be displayed in the plot and edited.
            """
            fig, ax = plt.subplots(figsize=(10, 4.9))
            img_display = ax.imshow(display_img, cmap='gray')  # Keep a reference to the image plot for editing
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, self)
            canvas.get_tk_widget().grid(row=0, column=0, columnspan=11)

            # Stuff for detecting mouse clicks on plot and removing anomalies
            def on_click(event):
                if event.inaxes is not None:  # Check if the click was inside the plot axes
                    config.U_box_coords = np.append(config.U_box_coords, [event.xdata, event.ydata])

                    # Each time len(config.U_box_coords) is a multiple of 4, the user has specified the corners of a box
                    # to be drawn.
                    if len(config.U_box_coords) % 4 == 0 and len(config.U_box_coords) >= 4:

                        # Different images are modified by draw_box() depending on whether the model has already been
                        # run and annotated the image, or we are dealing woth the original unannotated image.
                        # Edited image is dictated by global config.anomaly_mode.
                        if config.anomaly_mode == 1:
                            config.U_img = draw_box(config.U_img, config.U_box_coords)
                        elif config.anomaly_mode == 2:
                            config.U_img_annotated = draw_box(config.U_img_annotated, config.U_box_coords)

                    # Update plot with new images returned by draw_box() and redraw canvas.
                    if config.anomaly_mode == 1:
                        img_display.set_data(config.U_img)
                    elif config.anomaly_mode == 2:
                        img_display.set_data(config.U_img_annotated)
                    canvas.draw()

            canvas.mpl_connect('button_press_event', on_click)  # Bind on_click function to mouse click events.

        def remove_anomalies_1():
            """
            Removes anomalies from global config.U_img. Anomalies are identified as being within boxes drawn by user,
            coordinates of which are stored globally in config.U_box_coords.
            Any pixels within boxes are changed to black so they will be ignored by the image segmentation model.
            Replots config.U_img after anomaly removal using image_plot().
            """
            colour = (0, 0, 0)  # Black

            # U_box_coords should always be multiple of 4 to correctly produce boxes.
            # If it is not, spare coordinates are removed from the end
            if len(config.U_box_coords) % 4 != 0:
                config.U_box_coords = np.delete(config.U_box_coords, [-2, -1])

            # Fill in each user drawn anomaly box in black so the model doesn't detect them
            box = 0
            while box < len(config.U_box_coords):
                x = 0
                while x < config.U_img.size[0]:
                    y = 0
                    while y < config.U_img.size[1]:
                        # Check if the pixel lies within any of the boxes
                        if (min(config.U_box_coords[box], config.U_box_coords[box + 2]) <= x <=
                                max(config.U_box_coords[box], config.U_box_coords[box + 2])
                                and min(config.U_box_coords[box + 1], config.U_box_coords[box + 3]) <= y <=
                                max(config.U_box_coords[box + 1], config.U_box_coords[box + 3])):
                            config.U_img.putpixel((x, y), colour)

                        # Remove any remaining green pixels. Prevents some strange behaviour.
                        if (config.U_img.getpixel((x, y)) == (0, 255, 0, 255) or
                                config.U_img.getpixel((x, y)) == (0, 255, 0)):
                            config.U_img.putpixel((x, y), colour)
                        y += 1
                    x += 1
                box += 4

            # Replot image after anomaly removal, giving user option to continue identifying anomalies if they want.
            image_plot(config.U_img)

        def get_model_path(relative_path):
            """
            Get path to image segmentation model for use in run_model(). Model must be in same folder as GUI. This
            method is necessary when models are packaged by pyinstaller into single GUI .exe file.

            :param relative_path: Name of appropriate image segmentation model. Always '512_velocity_30.h5'. Name shows
                   model was trained on 512x512 velocity images for 30 epochs.

            :return path_to_model: Returns full path to model by joining current GUI folder path and model name.
            """
            bundle_dir = path.abspath(path.dirname(__file__))
            path_to_model = path.join(bundle_dir, relative_path)

            return path_to_model

        def split_image(u_img):
            """
            Takes u_img which is always global config.U_img. u_img typically has greater width than height. Image
            segmentation model requires square 512x512 images.
            u_img is resized to have height 512 pixels, then cropped into the necessary number of 512x512 square images.
            Final crop may overlap with the previous one if image width is not divisible by 512. This is accounted for
            when images are put back together in join_images().
            Also calculates conversion rate from pixels to relevant units globally as config.pix_scale, which is used
            when saving the extracted data in save_u_data().

            :param u_img: Image object to be cropped 512x512 squares.

            :return square_crops: List of cropped square images is returned to run_model().
            """
            if config.dicom_upload:
                #  Calculate pixel to unit conversion
                try:
                    float(ent_scale.get())
                    valid = True
                except ValueError:
                    valid = False
                if valid:
                    scale_len = float(ent_scale.get())
                else:
                    messagebox.showwarning("Warning", "Please input DICOM scale before proceeding.")

                config.u_pix_scale = scale_len / 460
                resize_ratio = u_img.height / 512
                config.u_pix_scale *= resize_ratio

            #  Resize img to have side length 512, in order to be compatible with model
            aspect_ratio = u_img.width / u_img.height
            new_width = round(512 * aspect_ratio)
            u_img = u_img.resize((new_width, 512), Image.LANCZOS)
            config.U_img = u_img.copy()  # Match global U_img for future use

            num_squares = math.ceil(u_img.width / 512)  # No. squares img must be cropped into. Always rounded up
            square_crops = []
            left_edge = 0
            for i in range(num_squares - 1):
                square_crop = u_img.crop((left_edge, 0, left_edge + 512, 512))
                square_crops.append(square_crop)
                left_edge += 512

            # Crop of the final square is taken backwards from the end of the image. Overlap with previous crops not an
            # issue.
            last_square = u_img.crop((u_img.width - 512, 0, u_img.width, 512))
            square_crops.append(last_square)

            return square_crops

        def clean_mask(binary_mask):
            """
            Removes isolated groups of pixels from the model output predicted mask. Any group of white pixels small
            enough to not be the main body of the mask is filled in black.
            Uses remove_small_objects() function from skimage.morphology. This requires conversion to array and
            conversion back to image using np.array() and Image.fromarray() respectively.

            :param binary_mask: Image object predicted mask produced by image segmentation model.

            :return binary_mask: Image object predicted mask is returned to process_predictions() with anomalous groups
                                 of white pixels removed.
            """
            min_size = 40000
            binary_array = np.array(binary_mask)
            labeled_image = measure.label(binary_array)
            filtered_image = morphology.remove_small_objects(labeled_image, min_size=min_size, connectivity=2)
            filtered_image = filtered_image > 0
            binary_mask = Image.fromarray(filtered_image.astype(np.uint8) * 255)

            return binary_mask

        def join_images(masks):
            """
            Takes square 512x512 model predicted output masks after cleaning using clean_mask() and joins them to form
            the full predicted mask for the original image dimensions.

            :param masks: List of square predicted masks passed by process_predictions().

            :return long_mask: Image object predicted mask for the full image passed back to process_predictions().
            """
            # Create blank image with same dimensions as config.U_img.
            long_mask = Image.new(masks[0].mode, (config.U_img.width, 512))

            # Loop through empty image and paste square masks at appropriate points.
            left_edge = 0
            for i in range(len(masks) - 1):
                long_mask.paste(masks[i], (left_edge, 0))
                left_edge += 512

            # Final mask position is taken backwards from end and may overlap with previously pasted masks. This aligns
            # with how the image was first split up in split_image().
            long_mask.paste(masks[-1], (long_mask.width - 512, 0))

            return long_mask

        def mask_to_annotation(long_mask):
            """
            Takes the predicted binary mask and converts it to an annotated image showing where the velocity waveform
            has been identified by image segmentation.
            Detects the outermost white pixels of the mask, and plots these in colour onto a copy of config.U_img.
            Saves global config.og_top_u_values and config.og_bottom_u_values in case the user wishes to undo later
            changes made to the annotated image.

            :param long_mask: Predicted mask for config.U_img from which velocity waveform can be found.

            :return annotated_image: Copy of config.U_img with velocity waveform outlined is returned to
                                     process_predictions().
            """
            img_array = np.array(long_mask)  # Convert mask to array
            top_y_values = []
            bottom_y_values = []
            for column in img_array.T:  # Move through pixel columns finding top and bottom white pixel.
                white_pixels = np.where(column == 255)[0]
                top_y_values.append(white_pixels[0])
                bottom_y_values.append(white_pixels[-1])

            annotated_image = config.U_img.copy()
            width, height = annotated_image.size
            annotation_colour = (255, 255, 0)

            for x in range(width):  # Move through copy of config.U_img adding annotation from mask outline.
                for y in range(height):
                    if y == top_y_values[x] or y == bottom_y_values[x]:
                        annotated_image.putpixel((x, y), annotation_colour)

            # Save copies of annotation outline values in case user wants to undo later changes.
            config.top_u_values = top_y_values.copy()
            config.bottom_u_values = bottom_y_values.copy()
            config.og_top_u_values = top_y_values.copy()
            config.og_bottom_u_values = bottom_y_values.copy()

            return annotated_image

        def run_model():
            """
            Called when user presses GUI button 'btn_run_model'.
            Gets full model path for '512_velocity_30.h5' from get_model_path(). Model must be in same folder as GUI if
            running source code. Works automatically if running through .exe file.
            Runs the image segmentation model on square crops created by split_image().
            Saves model prediction for each image in global list config.u_predictions.
            Calls process_predictions() to convert model predictions into a usable form.
            """
            # model_path = r'C:\Users\alexa\Documents\L4 Capstone\Trained Models\512_velocity_30.h5'
            model_path = get_model_path('512_velocity_30.h5')
            loaded_model = load_model(model_path)

            model_images = split_image(config.U_img)  # Split image into usable 512x512 squares.
            config.u_predictions = []

            print('Segmenting velocity image...')
            for i in range(len(model_images)):  # Get prediction for each image and save to config.u_predictions.
                input_image = model_images[i]
                grayscale_image = input_image.convert("L")
                input_image_array = img_to_array(grayscale_image) / 255.0
                input_image_array = input_image_array.reshape((1,) + input_image_array.shape)

                prediction = loaded_model.predict(input_image_array)
                config.u_predictions.append(prediction)

            process_predictions(config.u_predictions)

            config.anomaly_mode = 2  # Changes how anomaly removal works when image has already been annotated.

        def process_predictions(predictions):
            """
            Takes model predictions from config.u_predictions and converts to usable annotated image using clean_mask(),
            join_images(), mask_to_annotation().
            Creates list of masks which is filled with binary masks of the predictions above threshold value
            config.u_mask_threshold.
            Default threshold value can be adjusted in global configurator, and user can change it manually with entry
            box in GUI.
            Immediately displays annotated image using image_plot().
            Saves annotated image to global config.U_img_annotated for later use.

            :param predictions: List of model predictions passed by run_model. Always config.u_predictions.
            """
            masks = []
            for i in range(len(predictions)):  # Create masks of predictions above threshold value.
                binary_mask = (predictions[i] > config.u_mask_threshold).astype('int')
                binary_mask = binary_mask[0, :, :, 0]
                binary_mask = clean_mask(binary_mask)

                masks.append(binary_mask)

            long_mask = join_images(masks)
            annotated_image = mask_to_annotation(long_mask)
            image_plot(annotated_image)
            config.U_img_annotated = annotated_image

        def remove_anomalies_2():
            """
            Called if user chooses to draw anomaly boxes on config.U_img_annotated' then presses GUI button
            'btn_remove_anomalies'.
            config.anomaly_mode has now been set to 2, so this function is called instead of remove_anomalies_1().
            Deletes any parts of the image annotation within the boxes (config.U_box_coords), then linearly interpolates
            to replace the deleted values with a straight line joining the two nearest points.
            Displays new image with anomalies removed using image_plot().
            """
            # U_box_coords should always be multiple of 4 to correctly produce boxes.
            # If it is not, spare coordinates are removed from the end
            if len(config.U_box_coords) % 4 != 0:
                config.U_box_coords = np.delete(config.U_box_coords, [-2, -1])

            # Set anomalies in line to -1
            box = 0
            while box < len(config.U_box_coords):
                x = 0
                while x < len(config.bottom_u_values):
                    if (min(config.U_box_coords[box], config.U_box_coords[box + 2]) <= x <=
                            max(config.U_box_coords[box], config.U_box_coords[box + 2]) and
                            min(config.U_box_coords[box + 1], config.U_box_coords[box + 3]) <=
                            config.bottom_u_values[x] <= max(config.U_box_coords[box + 1],
                                                             config.U_box_coords[box + 3])):
                        config.bottom_u_values[x] = -1
                    x += 1
                box += 4

            # Straight Line Replaces Missing Values
            config.bottom_u_values = np.array(config.bottom_u_values)

            non_neg_indices = np.where(config.bottom_u_values >= 0)[0]
            # Create a copy of the array to work with
            interpolated_y_values = config.bottom_u_values.copy()
            # Iterate over the array and interpolate missing values
            for i in range(len(config.bottom_u_values)):
                if config.bottom_u_values[i] == -1:  # If current value is -1
                    # Find the nearest non-negative values at either side
                    left_index = max(non_neg_indices[non_neg_indices < i], default=None)
                    right_index = min(non_neg_indices[non_neg_indices > i], default=None)

                    if left_index is not None and right_index is not None:
                        # Linear interpolation
                        left_value = config.bottom_u_values[left_index]
                        right_value = config.bottom_u_values[right_index]
                        interpolated_y_values[i] = left_value + (right_value - left_value) * (i - left_index) / (
                                right_index - left_index)

            # Remove -1 values
            interpolated_y_values = interpolated_y_values[interpolated_y_values != -1]
            config.bottom_u_values = interpolated_y_values

            # Apply changes to lines drawn on image
            edited_image = config.U_img.copy()
            width, height = edited_image.size
            annotation_colour = (255, 255, 0)

            for x in range(width):
                for y in range(height):
                    if y == config.top_u_values[x] or y == config.bottom_u_values[x]:
                        edited_image.putpixel((x, y), annotation_colour)

            image_plot(edited_image)  # Plot the image again after removal of anomalies
            config.U_box_coords = []  # Reset box_coords in case user wants to identify more anomalies.
            config.U_img_annotated = edited_image

        def undo_changes():
            """
            Called when user presses GUI button 'btn_undo'. Function differs depending on the stage of the image
            analysis process.
            If DICOM has just been cropped, resets to original DICOM image and displays using process_dicom() so a new
            crop can be taken.
            If anomalies have just been removed before running the model, reverts to original image and displays with
            image_plot().
            If the model has already been run and anomalies have been removed, reverts image to state immediately after
            model annotation and displays with image_plot().
            """
            if config.dicom_upload:  # Reset DICOM image and display.
                config.U_dcm_box_coords = []
                config.U_dicom_img = config.U_dicom_original.copy()
                process_dicom()

            if config.anomaly_mode == 1 and config.U_img is not None:
                config.U_img = config.U_original_img.copy()
                image_plot(config.U_img)  # Plot the image again after resetting
                config.U_box_coords = []
            elif config.anomaly_mode == 2:
                config.U_box_coords = []
                config.top_u_values = config.og_top_u_values.copy()
                config.bottom_u_values = config.og_bottom_u_values.copy()
                remove_anomalies_2()

        def reset_image():
            """
            Completely resets global config.U_img to its original state config.U_img_original and displays using
            image_plot(), regardless of which stage of the image analysis process has been reached.
            """
            config.U_img = config.U_original_img.copy()
            image_plot(config.U_img)  # Plot the image again after resetting
            config.U_box_coords = []
            config.anomaly_mode = 1

        def save_u_data():
            """
            Makes data from image available as global numpy array config.u_data for use in the rest of the GUI.
            Also uses upsampling to ensure config.u_data has same length as config.d_data, provided config.d_data has
            already been assigned.
            """
            config.top_u_values = np.array(config.top_u_values)
            config.bottom_u_values = np.array(config.bottom_u_values)
            config.u_data = config.bottom_u_values - config.top_u_values
            if config.dicom_upload:
                config.u_data = config.u_data * config.u_pix_scale  # Convert pixels to relevant units
            else:
                config.u_data = config.u_data * 0.003

            # Upsample U array using linear interpolation to match length of diameter array, if diameter array already
            # exists.
            if config.D_img is not None:
                target_size = config.D_img.width
                original_indices = np.linspace(0, len(config.u_data) - 1, num=len(config.u_data))
                new_indices = np.linspace(0, len(config.u_data) - 1, num=target_size)
                config.u_data = np.interp(new_indices, original_indices, config.u_data)

        def change_mask_threshold():
            """
            Saves new value for global config.u_mask_threshold when user changes it in 'spinbox' widget.
            Runs process_predictions() to produce and display new annotated image based on mask threshold chosen by
            user.
            """
            try:
                # Attempt to convert the entry content to a float
                float_threshold = float(spinbox_value.get())
                # Check if the number is between 0 and 1
                if 0 <= float_threshold <= 1:
                    config.u_mask_threshold = float_threshold
                elif float_threshold > 1:
                    config.u_mask_threshold = 1
                else:
                    config.u_mask_threshold = 0

                process_predictions(config.u_predictions)

            except ValueError:
                # If the string in the entry box cannot convert to floating point, nothing happens.
                pass

        def remove_anomaly_press():
            """
            Called when user presses GUI button 'btn_remove_anomalies'.
            Button activates a different method of anomaly removal depending on which stage of the image analysis
            process has been reached when the button is pressed.
            """
            if config.anomaly_mode == 1:
                remove_anomalies_1()
            elif config.anomaly_mode == 2:
                remove_anomalies_2()

        def save_and_exit():
            """
            Called when user presses GUI button 'btn_save_exit'.
            Saves data extracted from image to be used globally throughout rest of GUI as config.u_data.
            Calls function controller.show_frame("InputPage") to return user to previous GUI page.
            """
            save_u_data()
            controller.show_frame("InputPage")

        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)                           # Configure rows to split evenly.
        self.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10), weight=1)  # Configure columns to split evenly.

        # Define frame to hold the buttons relating to anomaly removal
        button_frame = tk.Frame(self, bg=config.frame_col, relief='flat', highlightbackground=config.frame_border_col, highlightthickness=2)
        button_frame.place(x=140, y=495)

        # Labels for anomaly removal button frame
        lbl_anomaly_tools = tk.Label(button_frame, text="Anomaly Removal Tools", font=('Roboto', 13, 'bold'), bg=config.frame_col, fg=config.lbl_text_col)
        lbl_click_to = tk.Label(button_frame, text="Click image to draw boxes around anomalies", font=('Roboto', 11), bg=config.frame_col, fg=config.lbl_text_col)

        ent_scale = tk.Entry(self, font=('Roboto', 12), width=16, bg=config.frame_col)
        lbl_enter_scale = tk.Label(self, text="             Enter length of DICOM scale:", font=('Roboto', 12), bg=config.bg_col, fg=config.lbl_text_col)

        # Define buttons which call anomaly removal functions
        btn_remove_anomalies = tk.Button(
            button_frame,
            text="Remove anomalies",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=19,
            height=config.btn_height,
            command=lambda: remove_anomaly_press()
        )
        btn_undo = tk.Button(
            button_frame,
            text="Undo",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=14,
            height=config.btn_height,
            command=lambda: undo_changes()
        )
        btn_reset = tk.Button(
            button_frame,
            text="Reset",
            font=config.font,
            bg=config.red,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=14,
            height=config.btn_height,
            command=lambda: reset_image()
        )
        btn_crop_dicom = tk.Button(
            self,
            text="Crop DICOM",
            font=('Roboto', 13),
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=14,
            height=config.btn_height,
            command=lambda: crop_dicom()
        )

        # Define other buttons used in the GUI frame: Back, Select File, Run Model, and Save Data.
        btn_back = tk.Button(
            self,
            text="Back",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=config.btn_width,
            height=config.btn_height,
            command=lambda: controller.show_frame("InputPage")
        )
        btn_select_image = tk.Button(
            self,
            text="Select file",
            font=('Roboto', 13),
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=14,
            height=config.btn_height,
            command=lambda: choose_file()
        )
        btn_run_model = tk.Button(
            self,
            text="Run model",
            font=('Roboto', 13),
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=14,
            height=config.btn_height,
            command=lambda: run_model()
        )
        btn_save_exit = tk.Button(
            self,
            text="Save and exit",
            font=('Roboto', 13),
            bg=config.dark_green,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=14,
            height=config.btn_height,
            command=lambda: save_and_exit()
        )

        # Spinbox which adjusts mask threshold value. Defaults to 0.5
        spinbox_value = tk.StringVar(value=config.u_mask_threshold)
        spinbox = tk.Spinbox(
            button_frame,
            from_=0,
            to=1,
            width=9,
            increment=0.05,
            bg='#FFFFFF',
            fg=config.frame_border_col,
            font=('Roboto', 14),
            relief=tk.FLAT,
            textvariable=spinbox_value,
            command=lambda: change_mask_threshold()
        )
        lbl_spinbox = tk.Label(button_frame, text=" Mask threshold:", font=('Roboto', 13), bg=config.frame_col, fg=config.lbl_text_col)

        # Create a blank plot to save space for user input image
        fig, ax = plt.subplots(figsize=(10, 4.9))
        ax.axis('off')  # Hide the axes
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().grid(row=0, column=0, columnspan=11)

        # Arrange all widgets for this frame
        lbl_anomaly_tools.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        lbl_click_to.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        btn_remove_anomalies.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        btn_undo.grid(row=3, column=0, padx=5, pady=5)
        btn_reset.grid(row=3, column=1, padx=5, pady=5)

        lbl_spinbox.grid(row=4, column=0, padx=5, pady=5)
        spinbox.grid(row=4, column=1, padx=5, pady=5)

        btn_select_image.grid(row=2, column=8, padx=5, pady=10)
        btn_crop_dicom.grid(row=2, column=9, padx=5, pady=10)
        lbl_enter_scale.grid(row=1, column=8, padx=5, pady=10)
        ent_scale.grid(row=1, column=9, padx=5, pady=10)
        btn_run_model.grid(row=3, column=8, padx=5, pady=10)
        btn_save_exit.grid(row=3, column=9, padx=5, pady=10)

        btn_back.grid(row=4, column=0, padx=5, pady=5, sticky='w')
