import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askopenfile
import numpy as np
import config


class InputPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=config.bg_col)
        self.controller = controller

        def save_columns(x):
            """
            Save which column of the user input data corresponds to P/U/D/t to global configuration.
            Called on key release every time any of the column entry boxes are edited.
            Edits variables config.p_column/config.u_column/config.d_column/config.t_column.

            :param x: Arbitrary variable x which is not used. Required in this situation when binding the function to
                      entry boxes.
            """
            if ent_column_p.get().isdigit():
                config.p_column = int(ent_column_p.get())
            if ent_column_u.get().isdigit():
                config.u_column = int(ent_column_u.get())
            if ent_column_d.get().isdigit():
                config.d_column = int(ent_column_d.get())
            if ent_column_t.get().isdigit():
                config.t_column = int(ent_column_t.get())

        def save_units(x):
            """
            Save the unit of measurement for P/U/D to global configuration.
            Called whenever any unit of measurement dropdown is changed in GUI.
            Edits variables config.p_unit/config.u_unit/config.d_unit.

            :param x: Arbitrary variable x which is not used. Required in this situation when binding the function to
                      dropdown boxes.
            """
            config.p_unit = p_unit.get()
            config.u_unit = u_unit.get()
            config.d_unit = d_unit.get()

        def choose_file():
            """
            Uses askopenfile() function from tkinter.filedialog to allow the user to browse their system files and
            choose which one to upload to the GUI. File expected in .txt format.
            Data is saved to global configuration through variable config.all_data as a numpy array.
            Immediately calls process_data() once data file has been selected.
            """
            config.all_data = askopenfile(filetypes=[("Text files", "*.txt")])
            config.all_data = np.loadtxt(config.all_data)
            process_data()

        def single_file_button():
            """
            Called when user ticks GUI box saying their data is all in a single file.
            Removes buttons for multiple file upload and replaces them with single file upload button.
            """
            self.btn_p_file.grid_forget()
            self.btn_u_file.grid_forget()
            self.btn_d_file.grid_forget()
            self.btn_t_file.grid_forget()

            btn_select_single.grid(row=3, column=0, padx=5, pady=5)

        def multi_file_buttons():
            """
            Called when user ticks GUI box saying their data is in multiple files.
            Removes button for single file upload and replaces it with multiple file upload buttons.
            """
            btn_select_single.grid_forget()  # Hide button for selecting single data file

            self.btn_p_file = tk.Button(
                self,
                text="Select P file",
                font=config.font,
                bg=config.btn_col,
                fg=config.btn_text,
                activebackground=config.btn_col_a,
                activeforeground=config.btn_text_a,
                relief=tk.FLAT,
                width=config.btn_width,
                height=config.btn_height,
                command=lambda: assign_p_data()
            )
            self.btn_u_file = tk.Button(
                self,
                text="Select U file",
                font=config.font,
                bg=config.btn_col,
                fg=config.btn_text,
                activebackground=config.btn_col_a,
                activeforeground=config.btn_text_a,
                relief=tk.FLAT,
                width=config.btn_width,
                height=config.btn_height,
                command=lambda: assign_u_data()
            )
            self.btn_d_file = tk.Button(
                self,
                text="Select D file",
                font=config.font,
                bg=config.btn_col,
                fg=config.btn_text,
                activebackground=config.btn_col_a,
                activeforeground=config.btn_text_a,
                relief=tk.FLAT,
                width=config.btn_width,
                height=config.btn_height,
                command=lambda: assign_d_data()
            )
            self.btn_t_file = tk.Button(
                self,
                text="Select t file",
                font=config.font,
                bg=config.btn_col,
                fg=config.btn_text,
                activebackground=config.btn_col_a,
                activeforeground=config.btn_text_a,
                relief=tk.FLAT,
                width=config.btn_width,
                height=config.btn_height,
                command=lambda: assign_t_data()
            )

            self.btn_p_file.grid(row=2, column=0, padx=5, pady=5)
            self.btn_u_file.grid(row=3, column=0, padx=5, pady=5)
            self.btn_d_file.grid(row=4, column=0, padx=5, pady=5)
            self.btn_t_file.grid(row=5, column=0, padx=5, pady=5)

        def assign_p_data():
            """
            Assigns data from user chosen file to config.p_data in cases when data is contained in multiple files.
            """
            config.p_data = askopenfile(filetypes=[("Text files", "*.txt")])
            config.p_data = np.loadtxt(config.p_data)
            process_data()

        def assign_u_data():
            """
            Assigns data from user chosen file to config.u_data in cases when data is contained in multiple files.
            """
            config.u_data = askopenfile(filetypes=[("Text files", "*.txt")])
            config.u_data = np.loadtxt(config.u_data)
            process_data()

        def assign_d_data():
            """
            Assigns data from user chosen file to config.d_data in cases when data is contained in multiple files.
            """
            config.d_data = askopenfile(filetypes=[("Text files", "*.txt")])
            config.d_data = np.loadtxt(config.d_data)
            process_data()

        def assign_t_data():
            """
            Assigns data from user chosen file to config.t_data in cases when data is contained in multiple files.
            """
            config.t_data = askopenfile(filetypes=[("Text files", "*.txt")])
            config.t_data = np.loadtxt(config.t_data)
            process_data()

        def process_data():
            """
            Splits data assigned by user to config.all_data into separate numpy arrays for P/U/D/t/
            Also generates time data for the user if one is not specified in their data. Sampling frequency is assigned
            to config.sampling_frequency. Default value is 1000, but can be changed in entry box in GUI.
            """
            if single_file.get() == 1:  # Skip assigning columns if data has been upload multiple files
                if isinstance(config.t_column, int):
                    config.t_data = np.array(config.all_data[:, config.t_column - 1])
                if isinstance(config.p_column, int):
                    config.p_data = np.array(config.all_data[:, config.p_column - 1])
                if isinstance(config.u_column, int):
                    config.u_data = np.array(config.all_data[:, config.u_column - 1])
                if isinstance(config.d_column, int):
                    config.d_data = np.array(config.all_data[:, config.d_column - 1])

            # Detect sampling frequency if user provided time data.
            if len(config.t_data) > 0:
                config.sampling_frequency = 1 / (config.t_data[1] - config.t_data[0])

            # Create time data array if one was not included in uploaded file. Default sampling frequency is 1000,
            # although user should specify the actual value in the entry box.
            if len(config.t_data) == 0:
                step = 1 / config.sampling_frequency
                length = len(config.u_data)
                config.t_data = np.arange(0, step * length, step)

        def u_image_press():
            """
            Uses function controller.show_frame() to move to the 'VelocityImage' page of the GUI, used for analysing
            velocity ultrasound images.
            Sets global variable config.image_analysis to True to signify image analysis methods are required.
            Sets global config.anomaly_mode to 1 to reset it after potential use in 'DiameterImage' frame.
            """
            controller.show_frame("VelocityImage")
            config.image_analysis = True
            config.anomaly_mode = 1

        def d_image_press():
            """
            Uses function controller.show_frame() to move to the 'DiameterImage' page of the GUI, used for analysing
            diameter ultrasound images.
            Sets global variable config.image_analysis to True to signify image analysis methods are required.
            Sets global config.anomaly_mode to 1 to reset it after potential use in 'VelocityImage' frame.
            """
            controller.show_frame("DiameterImage")
            config.image_analysis = True
            config.anomaly_mode = 1

        def col_key_release(x):
            """
            Runs function process_data() if any edits are made by user to column entry boxes after initial data upload.
            Ensures the correct data is assigned before moving on from this frame.

            :param x: Arbitrary variable x which is not used. Required in this situation when binding the function to
                      entry boxes.
            """
            save_columns(1)
            if config.all_data is not None:  # Only execute process_data() if user has already selected data.
                process_data()

        def single_file_toggle():
            """
            Ensure that both the single and multiple file options cannot be selected simultaneously, by switching
            the one which has not been selected.
            """
            if multiple_file.get() == 1:
                multiple_file.set(0)
            else:
                multiple_file.set(1)

        def multiple_file_toggle():
            """
            Ensure that both the single and multiple file options cannot be selected simultaneously, by switching
            the one which has not been selected.
            """
            if single_file.get() == 1:
                single_file.set(0)
            else:
                single_file.set(1)

        def next_button_press():
            """
            Stops progress through the GUI if the user has not selected data.
            """
            if len(config.u_data) != 0:
                controller.show_frame("PtNew")
            else:
                messagebox.showwarning("Warning", "Please upload data before proceeding.")



        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10), weight=1)  # Configure rows to split evenly.
        self.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)               # Configure columns to split evenly.

        # Define next and back buttons for GUI frame
        btn_next = tk.Button(
            self,
            text="Next",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=config.btn_width,
            height=config.btn_height,
            command=lambda: next_button_press()
        )
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
            command=lambda: controller.show_frame("Homepage")
        )

        # Define button for user to upload a single data file containing all data
        btn_select_single = tk.Button(
            self,
            text="Select file",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=config.btn_width,
            height=config.btn_height,
            command=lambda: choose_file()
        )

        lbl_p = tk.Label(self, text="Pressure (P)", font=('Roboto', 12), bg=config.bg_col, fg=config.lbl_text_col)
        lbl_u = tk.Label(self, text="Velocity (U)", font=('Roboto', 12), bg=config.bg_col, fg=config.lbl_text_col)
        lbl_d = tk.Label(self, text="Diameter (D)", font=('Roboto', 12), bg=config.bg_col, fg=config.lbl_text_col)
        lbl_t = tk.Label(self, text="Time (t)", font=('Roboto', 12), bg=config.bg_col, fg=config.lbl_text_col)

        # Allows the user to specify which column of their file contains data for which parameter.
        ent_column_p = tk.Entry(self, font=('Roboto', 12), width=5)
        ent_column_p.bind("<KeyRelease>", col_key_release)
        ent_column_u = tk.Entry(self, font=('Roboto', 12), width=5)
        ent_column_u.bind("<KeyRelease>", col_key_release)
        ent_column_d = tk.Entry(self, font=('Roboto', 12), width=5)
        ent_column_d.bind("<KeyRelease>", col_key_release)
        ent_column_t = tk.Entry(self, font=('Roboto', 12), width=5)
        ent_column_t.bind("<KeyRelease>", col_key_release)

        # Series of dropdowns allows the user to specify the units that their data is in.
        p_unit = tk.StringVar()
        p_unit.set("-")
        drop_p_unit = tk.OptionMenu(self, p_unit, "-", "mmHg", "Pa", "kPa")
        drop_p_unit.bind("<Configure>", save_units)
        drop_p_unit.config(font=('Roboto', 11))
        drop_p_unit.config(
            bg=config.drop_col,
            fg=config.drop_text,
            activebackground=config.drop_col_a,
            activeforeground=config.drop_text_a,
            relief=tk.FLAT,
        )
        u_unit = tk.StringVar()
        u_unit.set("-")
        drop_u_unit = tk.OptionMenu(self, u_unit, "-", "m/s", "cm/s", "mm/s")
        drop_u_unit.bind("<Configure>", save_units)
        drop_u_unit.config(font=('Roboto', 11))
        drop_u_unit.config(
            bg=config.drop_col,
            fg=config.drop_text,
            activebackground=config.drop_col_a,
            activeforeground=config.drop_text_a,
            relief=tk.FLAT,
        )
        d_unit = tk.StringVar()
        d_unit.set("-")
        drop_d_unit = tk.OptionMenu(self, d_unit, "-", "mm", "cm")
        drop_d_unit.bind("<Configure>", save_units)
        drop_d_unit.config(font=('Roboto', 11))
        drop_d_unit.config(
            bg=config.drop_col,
            fg=config.drop_text,
            activebackground=config.drop_col_a,
            activeforeground=config.drop_text_a,
            relief=tk.FLAT,
        )

        lbl_fileup = tk.Label(self, text="File Upload", font=('Roboto', 16), bg=config.bg_col, fg=config.lbl_text_col)
        lbl_column = tk.Label(self, text="Column", font=('Roboto', 12), bg=config.bg_col, fg=config.lbl_text_col)
        lbl_units = tk.Label(self, text="Units", font=('Roboto', 12), bg=config.bg_col, fg=config.lbl_text_col)
        lbl_samplingf = tk.Label(self, text="Sampling frequency", font=('Roboto', 12), bg=config.bg_col, fg=config.lbl_text_col)

        # Define buttons for the user to navigate to image analysis pages of GUI
        btn_u_image = tk.Button(
            self,
            text="Analyse U Ultrasound",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=20,
            height=config.btn_height,
            command=lambda: u_image_press()
        )
        btn_d_image = tk.Button(
            self,
            text="Analyse D Ultrasound",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=20,
            height=config.btn_height,
            command=lambda: d_image_press()
        )

        # Variables single_file and multiple_file save whether the user's data is in one or multiple files.
        # The toggle functions defined above ensure both options cannot be selected simultaneously.
        single_file = tk.IntVar()
        single_file.set(1)  # Set single file as the default option
        multiple_file = tk.IntVar()
        check_yes = tk.Checkbutton(
            self,
            text='Yes',
            font=('Roboto', 12),
            variable=single_file,
            bg=config.bg_col,
            fg=config.lbl_text_col,
            command=lambda: [single_file_toggle(),single_file_button()]
        )
        check_no = tk.Checkbutton(
            self,
            text='No',
            font=('Roboto', 12),
            variable=multiple_file,
            bg=config.bg_col,
            fg=config.lbl_text_col,
            command=lambda: [multiple_file_toggle(), multi_file_buttons()]
        )
        lbl_num_files = tk.Label(
            self,
            text="Is the data all in one file?",
            font=('Roboto', 12),
            bg=config.bg_col,
            fg=config.lbl_text_col
        )

        ent_sampling = tk.Entry(self)
        ent_sampling.insert(0, "Sampling frequency")

        # Arrange all widgets for this frame
        lbl_fileup.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
        lbl_column.grid(row=1, column=2, padx=5, pady=5)
        lbl_units.grid(row=1, column=3, padx=5, pady=5)

        # if single_file.get() == 1:
        #     btn_select_p.grid(row=2, column=0, padx=5, pady=5)
        #     btn_select_u.grid(row=3, column=0, padx=5, pady=5)
        #     btn_select_d.grid(row=4, column=0, padx=5, pady=5)
        #     btn_select_q.grid(row=5, column=0, padx=5, pady=5)
        #     btn_select_a.grid(row=6, column=0, padx=5, pady=5)
        #     btn_select_ecg.grid(row=7, column=0, padx=5, pady=5)
        #     btn_select_t.grid(row=8, column=0, padx=5, pady=5)

        btn_select_single.grid(row=3, column=0, padx=5, pady=5)

        lbl_p.grid(row=2, column=1, padx=5, pady=5)
        lbl_u.grid(row=3, column=1, padx=5, pady=5)
        lbl_d.grid(row=4, column=1, padx=5, pady=5)
        lbl_t.grid(row=5, column=1, padx=5, pady=5)

        ent_column_p.grid(row=2, column=2, padx=5, pady=5)
        ent_column_u.grid(row=3, column=2, padx=5, pady=5)
        ent_column_d.grid(row=4, column=2, padx=5, pady=5)
        ent_column_t.grid(row=5, column=2, padx=5, pady=5)

        drop_p_unit.grid(row=2, column=3, padx=5, pady=5)
        drop_u_unit.grid(row=3, column=3, padx=5, pady=5)
        drop_d_unit.grid(row=4, column=3, padx=5, pady=5)

        btn_u_image.grid(row=7, column=2, columnspan=3, padx=5, pady=5)
        btn_d_image.grid(row=8, column=2, columnspan=3, padx=5, pady=5)

        # ent_sampling.grid(row=10, column=3, columnspan=2, padx=5, pady=5)

        check_yes.grid(row=7, column=1, padx=5, pady=5)
        check_no.grid(row=8, column=1, padx=5, pady=5)
        lbl_num_files.grid(row=7, column=0, rowspan=2, padx=5, pady=5)

        btn_next.grid(row=10, column=4, padx=5, pady=5)
        btn_back.grid(row=10, column=0, padx=5, pady=5)
