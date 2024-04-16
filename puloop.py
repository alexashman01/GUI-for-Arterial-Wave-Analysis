import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from tkinter import messagebox
from sklearn.linear_model import LinearRegression
from matplotlib.ticker import ScalarFormatter
from tkinter.filedialog import asksaveasfilename
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import config


class PULoop(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=config.bg_col)
        self.controller = controller

        """
        The functions save_adjusted(), shift_u_left(), and shift_u_right() are copied directly from 'puadjust.py'
        Adjustment of only the U waveform is required in this page. Because only the loop plot indicates the alignment
        of the waveforms now, moving U right has the exact same effect as moving P or D left, and vice versa. Therefore
        a single set of buttons allowing the shifting left and right of the U waveform is sufficient.
        """

        def save_adjusted():
            """
            Called when user moves to the next frame 'PULoop'.
            Saves adjusted data globally to config.p_data_adjusted, config.u_data_adjusted, and config.d_data_adjusted.

            Convert the temporary adjusted time data into actual change in the data arrays. This is achieved by
            removing the necessary number of elements from one end of the array, and extending the opposite end
            with duplicates of the end value.
            For example: [1, 2, 3, 4, 5, 6] shifted left by 1 time step would become [2, 3, 4, 5, 6, 6].
            """
            if config.method_choice == 1:
                config.p_data_adjusted = config.p_data.copy()
                p_delta_t = config.p_t_adjusted[0]  # Amount of time adjusted by the user
                p_index = int(p_delta_t * config.sampling_frequency)  # No. of array indices corresponding to delta_t

                # Change in index is used to shift data left or right the correct amount, in the manner described above.
                # config.p_data_adjusted[0] * np.ones(p_index) creates array of duplicates of the required length.
                # config.p_data_adjusted[:-p_index] excludes from concatenation elements which are pushed off the end.
                if p_index > 0:
                    config.p_data_adjusted = np.concatenate(
                        (config.p_data_adjusted[0] * np.ones(p_index), config.p_data_adjusted[:-p_index]))
                elif p_index < 0:
                    config.p_data_adjusted = np.concatenate(
                        (config.p_data_adjusted[-p_index:], config.p_data_adjusted[-1] * np.ones(-p_index)))

            if config.method_choice == 1 or config.method_choice == 2:
                config.u_data_adjusted = config.u_data.copy()
                u_delta_t = config.u_t_adjusted[0]  # Amount of time adjusted by the user
                u_index = int(u_delta_t * config.sampling_frequency)  # No. of array indices corresponding to delta_t

                # Change in index is used to shift data left or right the correct amount, in the manner described above.
                # config.p_data_adjusted[0] * np.ones(p_index) creates array of duplicates of the required length.
                # config.p_data_adjusted[:-p_index] excludes from concatenation elements which are pushed off the end.
                if u_index > 0:
                    config.u_data_adjusted = np.concatenate(
                        (config.u_data_adjusted[0] * np.ones(u_index), config.u_data_adjusted[:-u_index]))
                elif u_index < 0:
                    config.u_data_adjusted = np.concatenate(
                        (config.u_data_adjusted[-u_index:], config.u_data_adjusted[-1] * np.ones(-u_index)))

            if config.method_choice == 2:
                config.d_data_adjusted = config.d_data.copy()
                d_delta_t = config.d_t_adjusted[0]  # Amount of time adjusted by the user
                d_index = int(d_delta_t * config.sampling_frequency)  # No. of array indices corresponding to delta_t

                # Change in index is used to shift data left or right the correct amount, in the manner described above.
                # config.p_data_adjusted[0] * np.ones(p_index) creates array of duplicates of the required length.
                # config.p_data_adjusted[:-p_index] excludes from concatenation elements which are pushed off the end.
                if d_index > 0:
                    config.d_data_adjusted = np.concatenate(
                        (config.d_data_adjusted[0] * np.ones(d_index), config.d_data_adjusted[:-d_index]))
                elif d_index < 0:
                    config.d_data_adjusted = np.concatenate(
                        (config.d_data_adjusted[-d_index:], config.d_data_adjusted[-1] * np.ones(-d_index)))

        def shift_u_left():
            """
            Called when user presses GUI button 'btn_u_left' to shift the velocity waveform left in plot graph1().
            Subtract one time step (1/sampling frequency) from every element of the time data against which U is
            plotted, shifting the U waveform left by one time step.
            """
            config.u_t_adjusted = config.u_t_adjusted - 1 / config.sampling_frequency

        def shift_u_right():
            """
            Called when user presses GUI button 'btn_u_right' to shift the velocity waveform right in plot graph1().
            Add one time step (1/sampling frequency) to every element of the time data against which U is
            plotted, shifting the U waveform right by one time step.
            """
            config.u_t_adjusted = config.u_t_adjusted + 1 / config.sampling_frequency

        def update_plot():
            """
            Called whenever user adjusts loop alignment using GUI buttons 'btn_u_left' or 'btn_u_right'.
            Updates data in loop graph without redrawing the whole thing.
            """
            if len(config.u_data) > 200:
                pts_per_marker = round(len(config.u_data) / 200)  # Get number of markers required
            else:
                pts_per_marker = 1

            config.loop_line.set_xdata(config.u_data_adjusted)
            config.loop_markers[0].set_xdata(config.u_data_adjusted[::pts_per_marker])
            self.canvas.draw()

        def manual_gradient():
            """
            Called when user presses GUI button 'btn_enter_gradient' after inputting the loop gradient in entry box
            'ent_gradient'.
            Allow the user to manually read and enter the gradient of the loop linear section.
            Calculates wave speed, c, by either PU-loop or lnDU-loop, and saves globally to config.c.
            """
            # Allow the user to manually read and enter the gradient of the loop linear section.
            if config.method_choice == 1:
                loop_gradient = float(ent_gradient.get())  # Read user input gradient and convert to float
                config.c = (1 / config.rho) * loop_gradient  # Calculate wave speed, c, using PU-loop

            elif config.method_choice == 2:
                loop_gradient = float(ent_gradient.get())  # Read user input gradient and convert to float
                config.c = 0.5 * (1 / loop_gradient)  # Calculate wave speed, c, using ln(D)U-loop

            ent_wave_speed.delete(0, tk.END)  # Clear wave speed display box
            ent_wave_speed.insert(0, config.c)  # Display calculated wave speed in GUI

        def automatic_gradient():
            """
            Called when user pressed GUI button 'btn_auto_gradient'.
            Automatically detects gradient of the linear portion of the loop plot. This is done by moving through
            'frames' and performing linear regression. The frame with the highest R2 score is taken as most linear.
            Once gradient of either PU-loop or lnDU-loop has been determined, calculates wave speed, c, and assigns to
            global config.c.
            Displays loopgraph() with the linear section highlighted in a different colour.
            """
            if config.method_choice == 1:
                pu_frame_fraction = 0.04  # Determines size of linear frames which are checked for linearity

                u_reg = config.u_data_adjusted
                p_reg = config.p_data_adjusted

                r2_values = np.array([])
                slopes = np.array([])
                intercepts = np.array([])
                window_starts = np.array([])

                frame_size = round(len(u_reg) * pu_frame_fraction)
                jump = round(frame_size / 5)
                start = np.argmin(p_reg)  # Start search for linear section at lowest point of loop
                if (start + frame_size) > len(u_reg):
                    start = 0
                start_og = start

                check_r2 = 1  # Checks the linear window has not moved around the corner of the loop.
                while (start + frame_size) < len(u_reg) and check_r2 > 0.9:
                    end = start + frame_size

                    # Select 'frame' within loop to be tested for linearity
                    x_segment = u_reg[start:end].reshape(-1, 1)
                    y_segment = p_reg[start:end]

                    reg = LinearRegression().fit(x_segment, y_segment)  # Perform linear regression
                    r2 = reg.score(x_segment, y_segment)
                    slope = reg.coef_
                    intercept = reg.intercept_

                    r2_values = np.append(r2_values, r2)
                    slopes = np.append(slopes, slope)
                    intercepts = np.append(intercepts, intercept)
                    window_starts = np.append(window_starts, start)

                    x_check = u_reg[start_og:end].reshape(-1, 1)
                    y_check = p_reg[start_og:end]
                    check_reg = LinearRegression().fit(x_check, y_check)
                    check_r2 = check_reg.score(x_check, y_check)

                    start += jump

                lin_index = np.argmax(r2_values)  # Find highest R2 values for most linear section
                lin_slope = slopes[lin_index]  # Find gradient for this section
                lin_intercept = intercepts[lin_index]  # Find y-intercept for this section
                lin_window = int(window_starts[lin_index])  # Find starting index of linear section within the loop

                # Assign x and y values of linear section of loop to config.x_lin and config.y_lin respectively.
                config.lin_x = u_reg[lin_window:lin_window + frame_size].copy()
                config.lin_y = lin_slope * config.lin_x + lin_intercept

                config.c = (1 / config.rho) * lin_slope  # Calculate wave speed, c, using PU-loop

            elif config.method_choice == 2:
                lndu_frame_fraction = 0.02  # Determines size of linear frames which are checked for linearity

                u_reg = config.u_data_adjusted
                lnd_reg = config.lnd_data_adjusted

                r2_values = np.array([])
                slopes = np.array([])
                intercepts = np.array([])
                window_starts = np.array([])

                frame_size = round(len(u_reg) * lndu_frame_fraction)
                jump = round(frame_size / 5)
                start = np.argmin(lnd_reg)  # Start search for linear section at lowest point of loop
                if (start + frame_size) > len(u_reg):
                    start = 0
                start_og = start

                check_r2 = 1  # Checks the linear window has not moved around the corner of the loop.
                while (start + frame_size) < len(u_reg) and check_r2 > 0.9:
                    end = start + frame_size
                    # Select 'frame' within loop to be tested for linearity
                    x_segment = u_reg[start:end].reshape(-1, 1)
                    y_segment = lnd_reg[start:end]

                    reg = LinearRegression().fit(x_segment, y_segment)  # Perform linear regression
                    r2 = reg.score(x_segment, y_segment)
                    slope = reg.coef_
                    intercept = reg.intercept_

                    r2_values = np.append(r2_values, r2)
                    slopes = np.append(slopes, slope)
                    intercepts = np.append(intercepts, intercept)
                    window_starts = np.append(window_starts, start)

                    x_check = u_reg[start_og:end].reshape(-1, 1)
                    y_check = lnd_reg[start_og:end]
                    check_reg = LinearRegression().fit(x_check, y_check)
                    check_r2 = check_reg.score(x_check, y_check)

                    start += jump

                lin_index = np.argmax(r2_values)  # Find highest R2 values for most linear section
                lin_slope = slopes[lin_index]  # Find gradient for this section
                lin_intercept = intercepts[lin_index]  # Find y-intercept for this section
                lin_window = int(window_starts[lin_index])  # Find starting index of linear section within the loop

                # Assign x and y values of linear section of loop to config.x_lin and config.y_lin respectively.
                config.lin_x = u_reg[lin_window:lin_window + frame_size].copy()
                config.lin_y = lin_slope * config.lin_x + lin_intercept

                config.c = 0.5 * (1 / lin_slope)  # Calculate wave speed using lndDU-loop

            ent_gradient.delete(0, tk.END)  # Clear gradient display box
            ent_gradient.insert(0, lin_slope)  # Display calculated gradient in GUI
            ent_wave_speed.delete(0, tk.END)  # Clear wave speed display box
            ent_wave_speed.insert(0, config.c)  # Display calculated wave speed in GUI
            self.loopgraph()  # Display loop graph with linear section added

        def convert_units_back():
            """
            Called if user goes back to previous frame 'PUAdjust' by pressing GUI button 'btn_back'.
            Units must flip back and forth between pages to avoid units being 'converted' many times repeatedly as the
            user navigates back and forth through the GUI.
            """
            # Convert back to original units if user goes back to previous page.
            if config.p_unit == 'kPa':
                config.p_data /= 1000
                config.p_data_adjusted /= 1000
            if config.p_unit == 'mmHg':
                config.p_data /= 133
                config.p_data_adjusted /= 133
            if config.u_unit == 'cm/s':
                config.u_data *= 100
                config.u_data_adjusted *= 100
            if config.u_unit == 'mm/s':
                config.u_data *= 1000
                config.u_data_adjusted *= 1000
            if config.d_unit == 'cm':
                config.d_data *= 100
                config.d_data_adjusted *= 100
            if config.d_unit == 'mm':
                config.d_data *= 1000
                config.d_data_adjusted *= 1000

        def save_data():
            """
            Called when user presses GUI button 'btn_save_data'.
            Asks the user to select a file path to save to using asksaveasfilename() from tkinter.filedialog.
            Saves config.t_data,  config.p_data_adjusted,  config.u_data_adjusted, and/or  config.d_data_adjusted into a
            single raw data .txt file.
            """
            file_path = asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if config.method_choice == 1:
                data = np.column_stack((config.t_data, config.p_data_adjusted, config.u_data_adjusted))
            elif config.method_choice == 2:
                data = np.column_stack((config.t_data, config.d_data_adjusted, config.u_data_adjusted))
            np.savetxt(file_path, data, fmt='%.6f', delimiter='\t', comments='')

        def next_button_press():
            """
            Stops progress through the GUI if the user has not selected data.
            """
            if config.c != 0:
                controller.show_frame("OutputPage")
            else:
                messagebox.showwarning("Warning", "Please calculate loop gradient before proceeding.")

        # Configure row weights
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        # Configure column weights
        self.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10), weight=1)

        button_frame = tk.Frame(self, bg=config.frame_col, relief='flat', highlightbackground=config.frame_border_col, highlightthickness=2)
        button_frame.place(x=100, y=360)

        # Define widgets
        ent_gradient = tk.Entry(button_frame, font=('Roboto', 12), width=8)

        btn_enter_gradient = tk.Button(
            button_frame,
            text="Enter",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=config.btn_width,
            height=config.btn_height,
            command=lambda: manual_gradient()
        )

        lbl_gradient = tk.Label(button_frame, text="Manual gradient:", font=('Roboto', 12), bg=config.frame_col,
                                fg=config.lbl_text_col)

        btn_auto_gradient = tk.Button(
            button_frame,
            text="Detect gradient",
            font=config.font,
            bg=config.dark_green,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=14,
            height=config.btn_height,
            command=lambda: automatic_gradient()
        )

        lbl_c = tk.Label(button_frame, text="c =       ", font=('Roboto', 14), bg=config.frame_col, fg=config.lbl_text_col)

        ent_wave_speed = tk.Entry(button_frame, font=('Roboto', 12), width=8)

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
            command=lambda: [convert_units_back(), controller.show_frame("PUAdjust")]
        )
        btn_u_left = tk.Button(
            button_frame,
            text="U left",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=config.btn_width,
            height=config.btn_height,
            command=lambda: [shift_u_left(), save_adjusted(), update_plot()]
        )
        btn_u_right = tk.Button(
            button_frame,
            text="U right",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=config.btn_width,
            height=config.btn_height,
            command=lambda: [shift_u_right(), save_adjusted(), update_plot()]
        )
        btn_save_data = tk.Button(
            self,
            text="Save aligned data",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=15,
            height=config.btn_height,
            command=lambda: save_data()
        )

        # lbl_p = tk.Label(self, text="P", font=14)
        lbl_u = tk.Label(button_frame, text="U", font=('Roboto', 14), bg=config.frame_col, fg=config.lbl_text_col)

        # Arrange all widgets for this frame
        lbl_gradient.grid(row=1, column=0, padx=5, pady=20)
        ent_gradient.grid(row=1, column=1, padx=5, pady=20)
        btn_enter_gradient.grid(row=1, column=2, padx=20, pady=20)

        btn_auto_gradient.grid(row=2, column=0, padx=5, pady=20)
        lbl_c.grid(row=2, column=1, columnspan=2, padx=5, pady=20)
        ent_wave_speed.grid(row=2, column=2, padx=5, pady=20)

        btn_next.grid(row=6, column=10, padx=5, pady=5)
        btn_back.grid(row=6, column=0, padx=5, pady=5)

        btn_u_left.grid(row=0, column=0, padx=5, pady=20)
        lbl_u.grid(row=0, column=1, padx=5, pady=20)
        btn_u_right.grid(row=0, column=2, padx=5, pady=20)

        btn_save_data.grid(row=6, column=4, columnspan=4, padx=5, pady=5)

    def ptgraph(self):
        """
        Called as soon as frame 'PULoop' is opened in GUI.
        Plot either config.p_data_adjusted vs config.t_data or config.d_data_adjusted vs config.t_data depending on
        whether invasive or non-invasive analysis is being carried out.
        Various aesthetic choices which remain consistent throughout GUI.
        """
        if config.method_choice == 1:
            if len(config.p_data_adjusted) > 200:
                pts_per_marker = round(len(config.p_data_adjusted) / 200)
            else:
                pts_per_marker = 1
            fig, ax = plt.subplots(figsize=(5, 3))
            fig.patch.set_facecolor(config.plot_bg_col)
            ax.set_facecolor(config.plot_bg_col)
            ax.plot(config.t_data, config.p_data_adjusted, c='#1638cc', linewidth=0.8, label='P')
            plt.plot(config.t_data[::pts_per_marker], config.p_data_adjusted[::pts_per_marker], linestyle='None',
                     marker='.', markeredgecolor='#030785', markerfacecolor='None', markeredgewidth=0.5, markersize=2)
            plt.gca().yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
            plt.gca().ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
            ax.set_xlabel('t (s)')
            ax.set_ylabel(f'P (Pa)')
            plt.minorticks_on()
            plt.tick_params(axis='both', which='major', labelsize=12)
            plt.grid(which='major', color='grey', linestyle='-', linewidth=0.5, alpha=0.5)
            plt.grid(which='minor', color='grey', linestyle='-', linewidth=0.2, alpha=0.5)
            fig.tight_layout()

        elif config.method_choice == 2:
            # Plot graph of D against t.
            if len(config.d_data_adjusted) > 200:
                pts_per_marker = round(len(config.d_data_adjusted) / 200)
            else:
                pts_per_marker = 1
            fig, ax = plt.subplots(figsize=(5, 3))
            fig.patch.set_facecolor(config.plot_bg_col)
            ax.set_facecolor(config.plot_bg_col)
            ax.plot(config.t_data, config.d_data_adjusted, c='#1638cc', linewidth=0.8, label='P')
            plt.plot(config.t_data[::pts_per_marker], config.d_data_adjusted[::pts_per_marker], linestyle='None',
                     marker='.', markeredgecolor='#030785', markerfacecolor='None', markeredgewidth=0.5, markersize=2)
            plt.gca().yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
            plt.gca().ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
            ax.set_xlabel('t (s)')
            ax.set_ylabel(f'D (m)')
            plt.minorticks_on()
            plt.tick_params(axis='both', which='major', labelsize=12)
            plt.grid(which='major', color='grey', linestyle='-', linewidth=0.5, alpha=0.5)
            plt.grid(which='minor', color='grey', linestyle='-', linewidth=0.2, alpha=0.5)
            fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().grid(row=0, column=0, columnspan=6, padx=5, pady=5)

    def tugraph(self):
        """
        Called as soon as frame 'PULoop' is opened in GUI.
        Plot config.t_data vs config.u_data_adjusted.
        Various aesthetic choices which remain consistent throughout GUI.
        """
        if len(config.u_data_adjusted) > 200:
            pts_per_marker = round(len(config.u_data_adjusted) / 200)
        else:
            pts_per_marker = 1
        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor(config.plot_bg_col)
        ax.set_facecolor(config.plot_bg_col)
        ax.plot(config.u_data_adjusted, config.t_data, c='#e00202', linewidth=0.8, label='U')
        plt.plot(config.u_data_adjusted[::pts_per_marker], config.t_data[::pts_per_marker], linestyle='None',
                 marker='.', markeredgecolor='#8a0000',
                 markerfacecolor='None', markeredgewidth=0.5, markersize=2)
        plt.gca().yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        plt.gca().ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
        ax.set_xlabel(f'U (m/s)')
        ax.set_ylabel('t (s)')
        plt.minorticks_on()
        plt.tick_params(axis='both', which='major', labelsize=12)
        plt.grid(which='major', color='grey', linestyle='-', linewidth=0.5, alpha=0.5)
        plt.grid(which='minor', color='grey', linestyle='-', linewidth=0.2, alpha=0.5)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().grid(row=1, column=6, columnspan=5, rowspan=5, padx=5, pady=5)

    def loopgraph(self):
        """
        Called as soon as frame 'PULoop' is opened in GUI.
        Plot either PU-loop or lnDU-loop depending on analysis type.
        If gradient is calculated automatically via linear regression, plot updates to highlight linear section of the
        loop in a different colour.
        Various aesthetic choices which remain consistent throughout GUI.
        """
        if config.method_choice == 1:
            # Plot graph of P against U.
            if len(config.p_data_adjusted) > 200:
                pts_per_marker = round(len(config.p_data_adjusted) / 200)
            else:
                pts_per_marker = 1
            fig, ax = plt.subplots(figsize=(5, 3))
            fig.patch.set_facecolor(config.plot_bg_col)
            ax.set_facecolor(config.plot_bg_col)
            config.loop_line, = ax.plot(config.u_data_adjusted, config.p_data_adjusted, c='#aa00ff', linewidth=0.8)
            config.loop_markers = plt.plot(config.u_data_adjusted[::pts_per_marker],
                                           config.p_data_adjusted[::pts_per_marker],
                                           linestyle='None', marker='.', markeredgecolor='#682860',
                                           markerfacecolor='None', markeredgewidth=0.5, markersize=2)

            # Plot line from which gradient is calculated
            if len(config.lin_x) != 0:
                ax.plot(config.lin_x, config.lin_y, color=config.green)

            plt.gca().yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
            plt.gca().ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
            ax.set_xlabel('U (m/s)')
            ax.set_ylabel('P (Pa)')
            plt.minorticks_on()
            plt.tick_params(axis='both', which='major', labelsize=12)
            plt.grid(which='major', color='grey', linestyle='-', linewidth=0.5, alpha=0.5)
            plt.grid(which='minor', color='grey', linestyle='-', linewidth=0.2, alpha=0.5)
            fig.tight_layout()

        elif config.method_choice == 2:
            # Plot graph of lnD against U.
            if len(config.lnd_data_adjusted) > 200:
                pts_per_marker = round(len(config.lnd_data_adjusted) / 200)
            else:
                pts_per_marker = 1
            fig, ax = plt.subplots(figsize=(5, 3))
            fig.patch.set_facecolor(config.plot_bg_col)
            ax.set_facecolor(config.plot_bg_col)
            config.loop_line, = ax.plot(config.u_data_adjusted, config.lnd_data_adjusted, c='#aa00ff', linewidth=0.8)
            config.loop_markers = plt.plot(config.u_data_adjusted[::pts_per_marker],
                                           config.lnd_data_adjusted[::pts_per_marker],
                                           linestyle='None', marker='.', markeredgecolor='#682860',
                                           markerfacecolor='None', markeredgewidth=0.5, markersize=2)

            # Plot line from which gradient is calculated
            if len(config.lin_x) != 0:
                ax.plot(config.lin_x, config.lin_y, color=config.green)

            plt.gca().yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
            plt.gca().ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
            ax.set_xlabel('U (m/s)')
            ax.set_ylabel('ln(D) (m)')
            plt.minorticks_on()
            plt.tick_params(axis='both', which='major', labelsize=12)
            plt.grid(which='major', color='grey', linestyle='-', linewidth=0.5, alpha=0.5)
            plt.grid(which='minor', color='grey', linestyle='-', linewidth=0.2, alpha=0.5)
            fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.get_tk_widget().grid(row=0, column=6, columnspan=5, padx=5, pady=5)

    def tkraise(self):
        """
        Calls functions ptgraph(), tugraph(), and loopgraph() as soon as this frame is opened in GUI.
        """
        super().tkraise()
        self.ptgraph()
        self.tugraph()
        self.loopgraph()
