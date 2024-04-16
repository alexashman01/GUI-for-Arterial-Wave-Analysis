import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import config


class PUAdjust(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=config.bg_col)
        self.controller = controller

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

        def convert_units():
            """
            Called when user presses GUI button 'btn_next' to move to 'PULoop frame'.
            Convert all units into SI so that correct values can be obtained from loop analysis.
            Reads config.p_unit, config.u_unit, and config.d_unit which were assigned by user in 'InputPage' frame.
            Also generates lnD data array as config.lnd_data_adjusted if non-invasive analysis is being carried out.
            """
            if config.p_unit == 'kPa':
                config.p_data *= 1000
                config.p_data_adjusted *= 1000
            if config.p_unit == 'mmHg':
                config.p_data *= 133
                config.p_data_adjusted *= 133
            if config.u_unit == 'cm/s':
                config.u_data /= 100
                config.u_data_adjusted /= 100
            if config.u_unit == 'mm/s':
                config.u_data /= 1000
                config.u_data_adjusted /= 1000
            if config.d_unit == 'cm':
                config.d_data /= 100
                config.d_data_adjusted /= 100
            if config.d_unit == 'mm':
                config.d_data /= 1000
                config.d_data_adjusted /= 1000

            config.lnd_data_adjusted = np.log(config.d_data_adjusted)

        def shift_p_left():
            """
            Called when user presses GUI button 'btn_p_left' to shift the pressure waveform left in plot graph1().
            Subtract one time step (1/sampling frequency) from every element of the time data against which P is
            plotted, shifting the P waveform left by one time step.
            Updates plot dynamically without redrawing the whole thing.
            """
            if config.method_choice == 1 or config.method_choice == 3:
                config.p_t_adjusted -= 1 / config.sampling_frequency  # Adjust time array by 1 time step
                config.p_line.set_xdata(config.p_t_adjusted)          # Update plot line

                if len(config.p_data) > 200:
                    pts_per_marker = round(len(config.p_data) / 200)  # Get number of markers required
                else:
                    pts_per_marker = 1
                config.p_markers[0].set_xdata(config.p_t_adjusted[::pts_per_marker])  # Update plot markers

                self.canvas.draw()  # Redraw the canvas on which the plot is placed

        def shift_p_right():
            """
            Called when user presses GUI button 'btn_p_right' to shift the pressure waveform right in plot graph1().
            Add one time step (1/sampling frequency) to every element of the time data against which P is
            plotted, shifting the P waveform right by one time step.
            Updates plot dynamically without redrawing the whole thing.
            """
            if config.method_choice == 1 or config.method_choice == 3:
                config.p_t_adjusted += 1 / config.sampling_frequency  # Adjust time array by 1 time step
                config.p_line.set_xdata(config.p_t_adjusted)          # Update plot line

                if len(config.p_data) > 200:
                    pts_per_marker = round(len(config.p_data) / 200)  # Get number of markers required
                else:
                    pts_per_marker = 1
                config.p_markers[0].set_xdata(config.p_t_adjusted[::pts_per_marker])  # Update plot markers

                self.canvas.draw()  # Redraw the canvas on which the plot is placed

        def shift_u_left():
            """
            Called when user presses GUI button 'btn_u_left' to shift the velocity waveform left in plot graph1().
            Subtract one time step (1/sampling frequency) from every element of the time data against which U is
            plotted, shifting the U waveform left by one time step.
            Updates plot dynamically without redrawing the whole thing.
            """
            config.u_t_adjusted -= 1 / config.sampling_frequency  # Adjust time array by 1 time step
            config.u_line.set_xdata(config.u_t_adjusted)          # Update plot line

            if len(config.u_data) > 200:
                pts_per_marker = round(len(config.u_data) / 200)  # Get number of markers required
            else:
                pts_per_marker = 1
            config.u_markers[0].set_xdata(config.u_t_adjusted[::pts_per_marker])  # Update plot markers

            self.canvas.draw()  # Redraw the canvas on which the plot is placed

        def shift_u_right():
            """
            Called when user presses GUI button 'btn_u_right' to shift the velocity waveform right in plot graph1().
            Add one time step (1/sampling frequency) to every element of the time data against which U is
            plotted, shifting the U waveform right by one time step.
            Updates plot dynamically without redrawing the whole thing.
            """
            config.u_t_adjusted += 1 / config.sampling_frequency  # Adjust time array by 1 time step
            config.u_line.set_xdata(config.u_t_adjusted)          # Update plot line

            if len(config.u_data) > 200:
                pts_per_marker = round(len(config.u_data) / 200)  # Get number of markers required
            else:
                pts_per_marker = 1
            config.u_markers[0].set_xdata(config.u_t_adjusted[::pts_per_marker])  # Update plot markers

            self.canvas.draw()  # Redraw the canvas on which the plot is placed

        def shift_d_left():
            """
            Called when user presses GUI button 'btn_p_left' to shift the diameter waveform left in plot graph1().
            Subtract one time step (1/sampling frequency) from every element of the time data against which D is
            plotted, shifting the D waveform left by one time step.
            Updates plot dynamically without redrawing the whole thing.
            """
            if config.method_choice == 2:
                config.d_t_adjusted -= 1 / config.sampling_frequency  # Adjust time array by 1 time step
                config.d_line.set_xdata(config.d_t_adjusted)          # Update plot line

                if len(config.d_data) > 200:
                    pts_per_marker = round(len(config.d_data) / 200)  # Get number of markers required
                else:
                    pts_per_marker = 1
                config.d_markers[0].set_xdata(config.d_t_adjusted[::pts_per_marker])  # Update plot markers

                self.canvas.draw()  # Redraw the canvas on which the plot is placed

        def shift_d_right():
            """
            Called when user presses GUI button 'btn_p_right' to shift the diameter waveform right in plot graph1().
            Add one time step (1/sampling frequency) to every element of the time data against which D is
            plotted, shifting the D waveform right by one time step.
            Updates plot dynamically without redrawing the whole thing.
            """
            if config.method_choice == 2:
                config.d_t_adjusted += 1 / config.sampling_frequency  # Adjust time array by 1 time step
                config.d_line.set_xdata(config.d_t_adjusted)          # Update plot line

                if len(config.d_data) > 200:
                    pts_per_marker = round(len(config.d_data) / 200)  # Get number of markers required
                else:
                    pts_per_marker = 1
                config.d_markers[0].set_xdata(config.d_t_adjusted[::pts_per_marker])  # Update plot markers

                self.canvas.draw()  # Redraw the canvas on which the plot is placed

        def next_button_press():
            """
            Called when user presses GUI button 'btn_next'.
            Calls save_adjusted() to convert temporary adjustments to the time arrays into actual change in the P, U,
            and D arrays.
            If user selected invasive or non-invasive analysis, controller.show_frame() moves GUI to 'PULoop' page for
            either PU-loop or lnDU-loop analysis.
            If user selected windkessel analysis, controller.show_frame() moves GUI to 'Windkessel' frame which plots
            windkessel technique output.
            """
            # When the button is pressed for next page, user is taken to a different screen depending on whether they
            # are performing windkessel or loop analysis.
            save_adjusted()
            if config.method_choice == 1 or config.method_choice == 2:
                convert_units()
                controller.show_frame("PULoop")
            elif config.method_choice == 3:
                controller.show_frame("Windkessel")

        # Configure row weights
        self.grid_rowconfigure((0, 1, 2), weight=1)
        # Configure column weights
        self.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15), weight=1)

        # Define buttons to navigate between GUI screens and to shift waveforms left and right.
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
            command=lambda: controller.show_frame("PtNew")
        )
        btn_p_left = tk.Button(
            self,
            text="P left",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=5,
            height=config.btn_height,
            command=lambda: [shift_p_left(), shift_d_left()]
        )
        btn_p_right = tk.Button(
            self,
            text="P right",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=5,
            height=config.btn_height,
            command=lambda: [shift_p_right(), shift_d_right()]
        )
        btn_u_left = tk.Button(
            self,
            text="U left",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=5,
            height=config.btn_height,
            command=lambda: shift_u_left()
        )
        btn_u_right = tk.Button(
            self,
            text="U right",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=5,
            height=config.btn_height,
            command=lambda: shift_u_right()
        )

        lbl_p = tk.Label(self, text="P", font=('Roboto', 14), bg=config.bg_col, fg=config.lbl_text_col)
        lbl_u = tk.Label(self, text="U", font=('Roboto', 14), bg=config.bg_col, fg=config.lbl_text_col)

        # Arrange all widgets for this frame
        btn_p_left.grid(row=2, column=4, padx=5, pady=5)
        lbl_p.grid(row=2, column=5, padx=5, pady=5)
        btn_p_right.grid(row=2, column=6, padx=5, pady=5)

        btn_u_left.grid(row=2, column=9, padx=5, pady=5)
        lbl_u.grid(row=2, column=10, padx=5, pady=5)
        btn_u_right.grid(row=2, column=11, padx=5, pady=5)

        btn_next.grid(row=2, column=15, padx=5, pady=5)
        btn_back.grid(row=2, column=0, padx=5, pady=5)

    def update_adjusted(self):
        """
        Called as soon as this frame opens in GUI.
        Creates temporary time arrays to be adjusted by the user without editing config.t_data.
        This allows for convenient shifting of the various waveforms left and right, without making permanent changes to
        config.p_data, config.p_data, or config.p_data until the presses 'btn_next'.
        """
        config.p_t_adjusted = config.t_data.copy()
        config.u_t_adjusted = config.t_data.copy()
        config.d_t_adjusted = config.t_data.copy()

    def graph1(self):
        """
        Called as soon as this frame opens in GUI. Also called each time a waveform is shifted left or right by user
        button presses in the GUI.
        If user chose invasive analysis, plots P vs t and U vs t on the same axes, so they can be aligned by user.
        If user chose non-invasive analysis, plots D vs t and U vs t on the same axes, so they can be aligned by user.
        """
        if config.method_choice == 1 or config.method_choice == 3:
            # For invasive or windkessel analysis, plot P and U on same axes against time,
            # allowing the user to manually align them.
            if len(config.p_data) > 200:
                pts_per_marker = round(len(config.p_data) / 200)
            else:
                pts_per_marker = 1
            fig, ax1 = plt.subplots(figsize=(8, 5))
            fig.patch.set_facecolor(config.plot_bg_col)
            ax1.set_facecolor(config.plot_bg_col)
            config.p_line, = ax1.plot(config.p_t_adjusted, config.p_data, c='#1638cc', linewidth=0.8, label='P')
            config.p_markers = ax1.plot(config.p_t_adjusted[::pts_per_marker], config.p_data[::pts_per_marker],
                                        linestyle='None',
                                        marker='.', markeredgecolor='#030785', markerfacecolor='None',
                                        markeredgewidth=0.5, markersize=2)
            ax1.set_xlabel('t (s)')
            ax1.set_ylabel(f'P ({config.p_unit})')

            ax2 = ax1.twinx()
            config.u_line, = ax2.plot(config.u_t_adjusted, config.u_data, c='#e00202', linewidth=0.8, label='U')
            config.u_markers = ax2.plot(config.u_t_adjusted[::pts_per_marker], config.u_data[::pts_per_marker], linestyle='None',
                     marker='.',
                     markeredgecolor='#8a0000', markerfacecolor='None', markeredgewidth=0.5, markersize=2)
            ax2.set_ylabel(f'U ({config.u_unit})')

            lines = [config.p_line, config.u_line]
            labels = [line.get_label() for line in lines]
            ax1.legend(lines, labels, loc='upper right')
            ax1.minorticks_on()
            ax1.grid(which='major', color='grey', linestyle='-', linewidth=0.5, alpha=0.5)
            ax1.grid(which='minor', color='grey', linestyle='-', linewidth=0.2, alpha=0.5)
            ax1.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
            ax1.tick_params(axis='both', which='major', labelsize=12)
            fig.tight_layout()

        elif config.method_choice == 2:
            # For non-invasive analysis, plot P and D on same axes against time,
            # allowing the user to manually align them.
            if len(config.d_data) > 200:
                pts_per_marker = round(len(config.d_data) / 200)
            else:
                pts_per_marker = 1
            fig, ax1 = plt.subplots(figsize=(8, 5))
            fig.patch.set_facecolor(config.plot_bg_col)
            ax1.set_facecolor(config.plot_bg_col)
            config.d_line, = ax1.plot(config.d_t_adjusted, config.d_data, c='#1638cc', linewidth=0.8, label='P')
            config.d_markers = ax1.plot(config.d_t_adjusted[::pts_per_marker], config.d_data[::pts_per_marker], linestyle='None',
                     marker='.',
                     markeredgecolor='#030785', markerfacecolor='None', markeredgewidth=0.5, markersize=2)
            ax1.set_xlabel('t (s)')
            ax1.set_ylabel(f'D ({config.d_unit})')

            ax2 = ax1.twinx()
            config.u_line, = ax2.plot(config.u_t_adjusted, config.u_data, c='#e00202', linewidth=0.8, label='U')
            config.u_markers = ax2.plot(config.u_t_adjusted[::pts_per_marker], config.u_data[::pts_per_marker], linestyle='None',
                     marker='.',
                     markeredgecolor='#8a0000', markerfacecolor='None', markeredgewidth=0.5, markersize=2)
            ax2.set_ylabel(f'U ({config.u_unit})')

            lines = [config.d_line, config.u_line]
            labels = [line.get_label() for line in lines]
            ax1.legend(lines, labels, loc='upper right')
            ax1.minorticks_on()
            ax1.grid(which='major', color='grey', linestyle='-', linewidth=0.5, alpha=0.5)
            ax1.grid(which='minor', color='grey', linestyle='-', linewidth=0.2, alpha=0.5)
            ax1.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
            ax1.tick_params(axis='both', which='major', labelsize=12)
            fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=16, padx=5, pady=5)

    def tkraise(self):
        """
        Calls functions update_adjusted() and graph1() as soon as this frame is opened in GUI.
        """
        super().tkraise()
        self.update_adjusted()
        self.graph1()
