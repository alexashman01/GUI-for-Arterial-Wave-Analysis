
# Dictates chosen type of analysis
# Value of 1/2/3 for invasive, non-invasive and windkessel respectively
method_choice = int

# Units of measurement for data
p_unit = str
u_unit = str
d_unit = str

# File column containing each data type
t_column = int
p_column = int
u_column = int
d_column = int

# Original data inputs
all_data = None
t_data = []
p_data = []
u_data = []
d_data = []

# Sampling frequency
sampling_frequency = 1000

# Dictate how certain functions behave when carrying out image analysis
image_analysis = False
dicom_upload = False
anomaly_mode = 1

# File paths chosen by user for U and D ultrasounds
U_image_path = None
D_image_path = None

# Copy of unedited image uploaded by the user
U_original_img = None
D_original_img = None

# Images variables used in first parts of image analysis
U_img = None
D_img = None

# Images variables used in image analysis after model has run
U_img_annotated = None
D_img_annotated = None

# Frame of DICOM file to be displayed an analysed
U_dicom_frame = 0
D_dicom_frame = 0

# Copy of full unedited DICOM frame
U_dicom_original = None
D_dicom_original = None

# DICOM image to be worked with until it becomes config.U_img after cropping
U_dicom_img = None
D_dicom_img = None

# List of square images cropped out of larger image by split_image() in image analysis frames
square_crops = []

# List of segmentation predictions made by model on square images in image analysis frames
u_predictions = []
d_predictions = []

# Threshold values determining which parts of the prediction become part of the predicted mask
u_mask_threshold = 0.5
d_mask_threshold = 0.3

# Pixel coordinates of image segmentation output. Change with anomaly removal
top_u_values = []
bottom_u_values = []
top_d_values = []
bottom_d_values = []

# Saved copy of initial pixel coordinates of image segmentation output
og_top_u_values = []
og_bottom_u_values = []
og_top_d_values = []
og_bottom_d_values = []

# Coordinates of boxes drawn on image to highlight anomalies
U_box_coords = []
D_box_coords = []

# Coordinates of boxes drawn on DICOM frame to choose which area to crop out and treat as config.U_img
U_dcm_box_coords = []
D_dcm_box_coords = []

u_pix_scale = float
d_pix_scale = float

# Dictates which data is to be cleaned or shortened in smoothdata.py
chosen_data = str

# Savitzky–Golay filter parameters
poly_order = int
window_size = int

# Coordinates which determine which bits of data to cut off after use draws vertical lines on graph
x_cut_values = []
x1 = None
x2 = None
x1_line = None
x2_line = None

# Temporary copy of each data type which is edited in smoothdata.py
p_edit = []
u_edit = []
d_edit = []

# Temporary time arrays corresponding to each data type in smoothdata.py
t_p = []
t_u = []
t_d = []

# Temporary shifted time data for PUAdjust page
p_t_adjusted = []
u_t_adjusted = []
d_t_adjusted = []

# Saved shifted data
p_data_adjusted = []
u_data_adjusted = []
d_data_adjusted = []
lnd_data_adjusted = []

# Saved to allow updates to plot data without redrawing whole plots in puadjust.py and puloop.py
p_line = None
p_markers = None
u_line = None
u_markers = None
d_line = None
d_markers = None
loop_line = None
loop_markers = None

# Data points for linear section of loop detected by automatic gradient function
lin_x = []
lin_y = []

# Blood density
rho = 1050

# Wave speed
c = 0

# First derivatives of data
dP = []
dU = []
dD = []
dlnD = []
dI = []

# First derivatives of data in forward direction
dP_f = []
dU_f = []
dD_f = []
dlnD_f = []
dI_f = []

# First derivatives of data in backward direction
dP_b = []
dU_b = []
dD_b = []
dlnD_b = []
dI_b = []

# Data in forward direction
P_f = []
U_f = []
D_f = []

# Data in backward direction
P_b = []
U_b = []
D_b = []

# Dictates which plot is displayed in outputpage.py
current_plot = str

# Output data from windkessel analysis
windkessel_t = []
windkessel_p = []
windkessel_pr = []
windkessel_pex = []
prd = []

# Aesthetic choices
bg_col = '#FFFFFF'       # GUI background colour
plot_bg_col = '#FFFFFF'  # Plot background colour
frame_col = '#E8EDEE'    # Frame background colour
frame_border_col = '#231f20'

btn_col = '#0c5dab'      # Button colour
btn_text = '#FFFFFF'     # Button text colour
btn_col_a = '#003087'    # Button active colour
btn_text_a = '#FFFFFF'   # Button active text colour

drop_col = '#0c5dab'     # Dropdown menu colour
drop_text = '#FFFFFF'    # Dropdown menu text colour
drop_col_a = '#0c5dab'   # Dropdown menu active colour
drop_text_a = '#FFFFFF'  # Dropdown menu active text colour

lbl_text_col = '#231f20'   # Label text colour

font = ('Roboto', 11)    # Default button font
btn_width = 10           # Default button width
btn_height = 1           # Default button height

dark_green = '#006747'
green = '#009639'
red = '#8A1538'
warm_yellow = '#FFB81C'
yellow = '#FAE100'
