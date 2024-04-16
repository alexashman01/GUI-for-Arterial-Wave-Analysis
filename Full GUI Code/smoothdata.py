import tkinter as tk
import numpy as np
import scipy
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import ScalarFormatter
from scipy.signal import savgol_filter
import config


class SmoothData(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=config.bg_col)
        self.controller = controller

        def clean_data():
            """
            Clean data using Savitzky-Golay filter. Function savgol_filter() in scipy.signal. Only data currently
            selected out of P, U, and D is edited.
            Filter parameters polynomial order (config.poly_order) and window size (config.window_size) are taken from
            entry boxes in GUI.
            Saves filtered data to globals config.p_edit, config.u_edit, and config.d_edit. Original global data is not
            changed until user presses 'bit_save_exit'.
            Cleaned data is displayed using graph1().
            """
            config.poly_order = int(config.poly_order)  # Convert to int type to be usable by scipy
            config.window_size = int(config.window_size)
            if config.chosen_data == 'P':
                config.p_edit = scipy.signal.savgol_filter(config.p_edit, config.window_size, config.poly_order)
            elif config.chosen_data == 'U':
                config.u_edit = scipy.signal.savgol_filter(config.u_edit, config.window_size, config.poly_order)
            elif config.chosen_data == 'D':
                config.d_edit = scipy.signal.savgol_filter(config.d_edit, config.window_size, config.poly_order)

            self.graph1()  # Display cleaned data

        def cut_data():
            """
            Trims data down to only include section between lines drawn on graph in graph1(). Only data currently
            selected out of P, U, and D is edited.
            Saves filtered data to globals config.p_edit, config.u_edit, and config.d_edit. Original global data is not
            changed until user presses 'bit_save_exit'.
            Also edits temporary time data arrays config.t_p, config.t_u, and config.t_d to allow plotting of trimmed
            data.
            Trimmed data is displayed using graph1().
            """
            # Find indices closest to cutting lines
            index1 = (np.abs(config.t_data - config.x1)).argmin()
            index2 = (np.abs(config.t_data - config.x2)).argmin()
            index_low, index_high = min(index1, index2), max(index1, index2)

            # Trim selected data to within the desired indices.
            if config.chosen_data == 'P':
                config.p_edit = config.p_edit[index_low:index_high]
                config.t_p = config.t_p[index_low:index_high]
            if config.chosen_data == 'U':
                config.u_edit = config.u_edit[index_low:index_high]
                config.t_u = config.t_u[index_low:index_high]
            if config.chosen_data == 'D':
                config.d_edit = config.d_edit[index_low:index_high]
                config.t_d = config.t_d[index_low:index_high]

            config.x_cut_values = []
            self.graph1()  # Plot trimmed data

        def reset_data():
            """
            Called when user presses GUI button 'btn_reset_data'.
            Reverts edited data arrays config.p_edit, config.u_edit, and config.d_edit to their original states
            config.p_data, config.u_data, and config.d_data.
            Reverts temporary time array to original states in the same manner.
            All cleaning and trimming of the data is undone.
            Original data is displayed using graph1().
            """
            if config.chosen_data == 'P':
                config.p_edit = config.p_data.copy()
                config.t_p = config.t_data.copy()
            if config.chosen_data == 'U':
                config.u_edit = config.u_data.copy()
                config.t_u = config.t_data.copy()
            if config.chosen_data == 'D':
                config.d_edit = config.d_data.copy()
                config.t_d = config.t_data.copy()

            self.graph1()

        def p_toggle():
            """
            Ensure only one data set can be selected at a time.
            Make data choice available globally at config.chosen_data.
            Display chosen data using graph1().
            """
            if p_checked.get() == 1:
                u_checked.set(0)
                d_checked.set(0)
                config.chosen_data = 'P'  # Make data choice available globally

            config.x_cut_values = []
            self.graph1()

        def u_toggle():
            """
            Ensure only one data set can be selected at a time.
            Make data choice available globally at config.chosen_data.
            Display chosen data using graph1().
            """
            if u_checked.get() == 1:
                p_checked.set(0)
                d_checked.set(0)
                config.chosen_data = 'U'  # Make data choice available globally

            config.x_cut_values = []
            self.graph1()

        def d_toggle():
            """
            Ensure only one data set can be selected at a time.
            Make data choice available globally at config.chosen_data.
            Display chosen data using graph1().
            """
            if d_checked.get() == 1:
                p_checked.set(0)
                u_checked.set(0)
                config.chosen_data = 'D'  # Make data choice available globally

            config.x_cut_values = []
            self.graph1()

        def save_parameters(x):
            """
            Called on key release any time user edits entry box 'ent_poly_order' or 'ent_window_size'.
            Make chosen polynomial order and window size available globally at config.poly_order and config.window_size
            respectively.

            :param x: Arbitrary variable x which is not used. Required in this situation when binding the function to
                      entry boxes.
            """
            # Make chosen polynomial order and window size available globally.
            config.poly_order = poly_order_entry.get()
            config.window_size = window_size_entry.get()

        def fix_image_data():
            """
            Called when user presses GUI button 'btn_save_exit'.
            Required when data has been trimmed by user clicking on graph. Data arrays must all have same length beyond
            this page, so linear interpolation is used to increase the size of the smaller array to match the larger.
            Also generates a matching time data array with length dictated by config.u_data.
            """
            if config.method_choice == 1 or config.method_choice == 1:
                if len(config.p_data) > len(config.u_data):  # Check which data array is longer
                    target_size = len(config.p_data)
                    original_indices = np.linspace(0, len(config.u_data) - 1, num=len(config.u_data))
                    new_indices = np.linspace(0, len(config.u_data) - 1, num=target_size)
                    config.u_data = np.interp(new_indices, original_indices, config.u_data)
                elif len(config.p_data) < len(config.u_data):
                    target_size = len(config.u_data)
                    original_indices = np.linspace(0, len(config.p_data) - 1, num=len(config.p_data))
                    new_indices = np.linspace(0, len(config.p_data) - 1, num=target_size)
                    config.p_data = np.interp(new_indices, original_indices, config.p_data)

            if config.method_choice == 2:
                if len(config.d_data) > len(config.u_data):  # Check which data array is longer
                    target_size = len(config.d_data)
                    original_indices = np.linspace(0, len(config.u_data) - 1, num=len(config.u_data))
                    new_indices = np.linspace(0, len(config.u_data) - 1, num=target_size)
                    config.u_data = np.interp(new_indices, original_indices, config.u_data)
                elif len(config.d_data) < len(config.u_data):
                    target_size = len(config.u_data)
                    original_indices = np.linspace(0, len(config.d_data) - 1, num=len(config.d_data))
                    new_indices = np.linspace(0, len(config.d_data) - 1, num=target_size)
                    config.d_data = np.interp(new_indices, original_indices, config.d_data)

                # Generate time array with values and length based on config.u_data.
                config.t_data = np.linspace(0, config.t_u[-1], len(config.u_data))

        def save_and_exit():
            """
            Called when user presses GUI button 'btn_save_exit'.
            Saves all edits made to data in 'SmoothData' frame to be used globally throughout rest of GUI as
            config.p_data, config.u_data, and config.d_data.
            Calls fix_image_data() to ensure all finalised data arrays have equal length.
            Calls function controller.show_frame("PtNew") to return user to previous 'PtNew' GUI page.
            """
            config.p_data = config.p_edit.copy()
            config.u_data = config.u_edit.copy()
            config.d_data = config.d_edit.copy()
            fix_image_data()
            controller.show_frame("PtNew")

        # Configure row weights
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        # Configure column weights
        self.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11), weight=1)

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
            command=lambda: controller.show_frame("PtNew")
        )

        # Check boxes for user tp select the data they want to edit
        p_checked = tk.IntVar()
        p_checked.set(1)  # Set P as default option
        config.chosen_data = 'P'
        u_checked = tk.IntVar()
        d_checked = tk.IntVar()
        check_p = tk.Checkbutton(
            self,
            text='P',
            font=('Roboto', 12),
            bg=config.bg_col,
            fg=config.lbl_text_col,
            variable=p_checked,
            command=lambda: p_toggle()
        )
        check_u = tk.Checkbutton(
            self,
            text='U',
            font=('Roboto', 12),
            bg=config.bg_col,
            fg=config.lbl_text_col,
            variable=u_checked,
            command=lambda: u_toggle()
        )
        check_d = tk.Checkbutton(
            self,
            text='D',
            font=('Roboto', 12),
            bg=config.bg_col,
            fg=config.lbl_text_col,
            variable=d_checked,
            command=lambda: d_toggle()
        )

        # Entry boxes for Savitzky-Golay filter parameters
        poly_order_entry = tk.StringVar()
        window_size_entry = tk.StringVar()
        ent_poly_order = tk.Entry(self, font=('Roboto', 12), width=8, textvariable=poly_order_entry)
        ent_window_size = tk.Entry(self, font=('Roboto', 12), width=8, textvariable=window_size_entry)
        ent_poly_order.bind('<KeyRelease>', save_parameters)  # Call save_parameters as soon as entry box is edited
        ent_window_size.bind('<KeyRelease>', save_parameters)

        label1 = tk.Label(self, text="Select data to edit", font=('Roboto', 12), bg=config.bg_col, fg=config.lbl_text_col)
        label2 = tk.Label(self, text="Polynomial order:", font=('Roboto', 12), bg=config.bg_col, fg=config.lbl_text_col)
        label3 = tk.Label(self, text="Window size:", font=('Roboto', 12), bg=config.bg_col, fg=config.lbl_text_col)
        label4 = tk.Label(self, text="Click graph to trim data", font=('Roboto', 12), bg=config.bg_col, fg=config.lbl_text_col)

        btn_reset_data = tk.Button(
            self,
            text="Reset data",
            font=config.font,
            bg=config.red,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=12,
            height=3,
            command=lambda: reset_data()
        )
        btn_clean = tk.Button(
            self,
            text="Clean data",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=12,
            height=3,
            command=lambda: clean_data()
        )
        btn_save_exit = tk.Button(
            self,
            text="Save and exit",
            font=config.font,
            bg=config.dark_green,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=12,
            height=3,
            command=lambda: save_and_exit()
        )
        btn_cut = tk.Button(
            self,
            text="Cut data",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=12,
            height=3,
            command=lambda: cut_data()
        )

        # Arrange all widgets for this frame
        label1.grid(row=1, column=2, columnspan=3, padx=5, pady=5)
        check_p.grid(row=2, column=2, padx=5, pady=5)
        check_u.grid(row=2, column=3, padx=5, pady=5)
        check_d.grid(row=2, column=4, padx=5, pady=5)

        ent_poly_order.grid(row=3, column=4, padx=5, pady=5)
        ent_window_size.grid(row=4, column=4, padx=5, pady=5)
        label2.grid(row=3, column=2, columnspan=2,  padx=5, pady=5)
        label3.grid(row=4, column=2, columnspan=2, padx=5, pady=5)

        label4.grid(row=1, column=6, columnspan=4, padx=5, pady=5)
        btn_clean.grid(row=2, column=7, padx=5, pady=5)
        btn_reset_data.grid(row=2, column=8, padx=5, pady=5)
        btn_save_exit.grid(row=3, column=8, rowspan=2, padx=5, pady=5)
        btn_cut.grid(row=3, column=7, rowspan=2, padx=5, pady=5)

        btn_back.grid(row=5, column=1, padx=5, pady=5)

    def set_edit_data(self):
        """
        Called as soon as frame 'SmoothData' opens in GUI.
        Sets globals config.p_edit, config.u_edit, and config.d_edit to be copies of user input data config.p_data,
        config.u_data, and config.d_data.
        The edit variables are used instead of the original data throughout this frame, until the user chooses to save
        and exit.
        """
        config.p_edit = config.p_data.copy()
        config.u_edit = config.u_data.copy()
        config.d_edit = config.d_data.copy()
        config.t_p = config.t_data.copy()
        config.t_u = config.t_data.copy()
        config.t_d = config.t_data.copy()

    def graph1(self):
        """
        Called as soon as frame 'SmoothData' is opened in GUI, as well as by various functions within the frame.
        Displays whichever data has been chosen by the user using global config.chosen_data.
        In cases where config.chosen_data indicates a data type which is not available, empty_graph() is called to
        produce a placeholder plot until the user selects available data.
        Allows user to click on plot using on_click() and draw vertical lines. These lines mark the point at which the
        data will be cut off when 'btn_cut' is pressed by the user.
        Various aesthetic choices which remain consistent throughout GUI.
        """
        fig = None
        if config.chosen_data == 'P' and len(config.p_edit) != 0:
            if len(config.p_edit) > 200:
                pts_per_marker = round(len(config.p_edit) / 200)
            else:
                pts_per_marker = 1
            fig, ax = plt.subplots(figsize=(8, 4.5))
            fig.patch.set_facecolor(config.plot_bg_col)
            ax.set_facecolor(config.plot_bg_col)
            ax.plot(config.t_p, config.p_edit, c='#1638cc', linewidth=0.8, label='P')
            plt.plot(config.t_p[::pts_per_marker], config.p_edit[::pts_per_marker], linestyle='None', marker='.',
                     markeredgecolor='#030785',
                     markerfacecolor='None', markeredgewidth=0.5, markersize=2)
            plt.gca().yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
            plt.gca().ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
            ax.set_xlabel('t (s)')
            ax.set_ylabel(f'P ({config.p_unit})')
            ax.set_title('P/t graph')
            plt.minorticks_on()
            plt.tick_params(axis='both', which='major', labelsize=12)
            plt.grid(which='major', color='grey', linestyle='-', linewidth=0.5, alpha=0.5)
            plt.grid(which='minor', color='grey', linestyle='-', linewidth=0.2, alpha=0.5)
            fig.tight_layout()

        elif config.chosen_data == 'P' and len(config.p_data) == 0:  # Create a blank plot if there is no P data
            self.empty_graph()

        elif config.chosen_data == 'U':
            if len(config.u_edit) > 200:
                pts_per_marker = round(len(config.u_edit) / 200)
            else:
                pts_per_marker = 1
            fig, ax = plt.subplots(figsize=(8, 4.5))
            fig.patch.set_facecolor(config.plot_bg_col)
            ax.set_facecolor(config.plot_bg_col)
            ax.plot(config.t_u, config.u_edit, c='#e00202', linewidth=0.8, label='U')
            plt.plot(config.t_u[::pts_per_marker], config.u_edit[::pts_per_marker], linestyle='None', marker='.',
                     markeredgecolor='#8a0000',
                     markerfacecolor='None', markeredgewidth=0.5, markersize=2)
            plt.gca().yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
            plt.gca().ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
            ax.set_xlabel('t (s)')
            ax.set_ylabel(f'U ({config.u_unit})')
            ax.set_title('U/t graph')
            plt.minorticks_on()
            plt.tick_params(axis='both', which='major', labelsize=12)
            plt.grid(which='major', color='grey', linestyle='-', linewidth=0.5, alpha=0.5)
            plt.grid(which='minor', color='grey', linestyle='-', linewidth=0.2, alpha=0.5)
            fig.tight_layout()

        elif config.chosen_data == 'D' and len(config.d_edit) != 0:
            if len(config.d_edit) > 200:
                pts_per_marker = round(len(config.d_edit) / 200)
            else:
                pts_per_marker = 1
            fig, ax = plt.subplots(figsize=(8, 4.5))
            fig.patch.set_facecolor(config.plot_bg_col)
            ax.set_facecolor(config.plot_bg_col)
            ax.plot(config.t_d, config.d_edit, c='#1638cc', linewidth=0.8, label='P')
            plt.plot(config.t_d[::pts_per_marker], config.d_edit[::pts_per_marker], linestyle='None', marker='.',
                     markeredgecolor='#030785',
                     markerfacecolor='None', markeredgewidth=0.5, markersize=2)
            plt.gca().yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
            plt.gca().ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
            ax.set_xlabel('t (s)')
            ax.set_ylabel(f'D ({config.d_unit})')
            ax.set_title('D/t graph')
            plt.minorticks_on()
            plt.tick_params(axis='both', which='major', labelsize=12)
            plt.grid(which='major', color='grey', linestyle='-', linewidth=0.5, alpha=0.5)
            plt.grid(which='minor', color='grey', linestyle='-', linewidth=0.2, alpha=0.5)
            fig.tight_layout()

        elif config.chosen_data == 'D' and len(config.d_data) == 0:  # Create a blank plot if there is no P data
            self.empty_graph()

        if fig is not None:
            canvas = FigureCanvasTkAgg(fig, self)
            canvas.get_tk_widget().grid(row=0, column=1, columnspan=10, padx=5, pady=5)

        # Stuff for detecting mouse clicks on plot and removing anomalies
        def on_click(event, ax):
            # Section of code to move the lines when the user clicks on the graph.
            if event.inaxes is not None:  # Check if the click was inside the axes
                config.x_cut_values = np.append(config.x_cut_values, event.xdata)
                if len(config.x_cut_values) == 1:  # Plot first line
                    config.x1 = config.x_cut_values[-1]
                    config.x1_line = ax.axvline(x=config.x1, color=config.green, linestyle='--')
                elif len(config.x_cut_values) == 2:  # Plot second line
                    config.x2 = config.x_cut_values[-1]
                    config.x2_line = ax.axvline(x=config.x2, color=config.green, linestyle='--')
                elif len(config.x_cut_values) > 2:  # Moves line closest to latest user click. Other line unchanged.
                    x3 = config.x_cut_values[-1]
                    if abs(config.x1 - x3) < abs(config.x2 - x3):
                        config.x1_line.remove()
                        config.x1 = x3.copy()
                        config.x1_line = ax.axvline(x=config.x1, color=config.green, linestyle='--')
                    else:
                        config.x2_line.remove()
                        config.x2 = x3.copy()
                        config.x2_line = ax.axvline(x=config.x2, color=config.green, linestyle='--')

                canvas.draw()  # Redraw canvas with update lines

        # Connect the on_click function to mouse click events
        if fig is not None:
            canvas.mpl_connect('button_press_event', lambda event: on_click(event, ax))

    def empty_graph(self):
        """
        Plots an empty graph in cases when actual data is not available.
        """
        fig, ax = plt.subplots(figsize=(8, 4.5))
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().grid(row=0, column=1, columnspan=10, padx=5, pady=5)

    def tkraise(self):
        """
        Calls functions set_edit_data() and graph1() as soon as this frame is opened in GUI.
        """
        super().tkraise()
        self.set_edit_data()
        self.graph1()
