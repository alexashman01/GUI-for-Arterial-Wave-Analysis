import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import ScalarFormatter
from scipy import integrate
from tkinter.filedialog import asksaveasfilename
import config


class OutputPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=config.bg_col)
        self.controller = controller

        def convert_units():
            """
            Called if user goes back to previous frame 'PULoop' by pressing GUI button 'btn_back'.
            Units must flip back and forth between pages to avoid units being 'converted' many times repeatedly as the
            user navigates back and forth through the GUI.
            """
            if config.p_unit == 'kPa':
                config.p_data_adjusted *= 1000
            if config.p_unit == 'mmHg':
                config.p_data_adjusted *= 133
            if config.u_unit == 'cm/s':
                config.u_data_adjusted /= 100
            if config.u_unit == 'mm/s':
                config.u_data_adjusted /= 1000
            if config.d_unit == 'cm':
                config.d_data_adjusted /= 100
            if config.d_unit == 'mm':
                config.d_data_adjusted /= 1000

        def save_p_separation_plot():  # saves d separation instead of p if running non-invasive analysis
            """
            Called when user presses GUI button 'btn_save_plot' while the pressure separation is being displayed.
            Asks user to choose save file path using asksaveasfilename() from tkinter.filedialog.
            PLot saves at 150 DPI to balance clarity and file size.
            """
            fig = self.create_p_separation_plot()
            file_path = asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            fig.savefig(file_path, dpi=150)

        def save_u_separation_plot():
            """
            Called when user presses GUI button 'btn_save_plot' while the velocity separation is being displayed.
            Asks user to choose save file path using asksaveasfilename() from tkinter.filedialog.
            PLot saves at 150 DPI to balance clarity and file size.
            """
            fig = self.create_u_separation_plot()
            file_path = asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            fig.savefig(file_path, dpi=150)

        def save_wia_plot():
            """
            Called when user presses GUI button 'btn_save_plot' while the wave intensity analysis is being displayed.
            Asks user to choose save file path using asksaveasfilename() from tkinter.filedialog.
            PLot saves at 150 DPI to balance clarity and file size.
            """
            fig = self.create_wia_plot()
            file_path = asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            fig.savefig(file_path, dpi=150)

        def save_wia_separation_plot():
            """
            Called when user presses GUI button 'btn_save_plot' while the WIA separation is being displayed.
            Asks user to choose save file path using asksaveasfilename() from tkinter.filedialog.
            PLot saves at 150 DPI to balance clarity and file size.
            """
            fig = self.create_wia_separation_plot()
            file_path = asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            fig.savefig(file_path, dpi=150)

        def save_p_separation_data():
            """
            Called when user presses GUI button 'btn_save_data' while the pressure separation is being displayed.
            Asks user to choose save file path using asksaveasfilename() from tkinter.filedialog.
            Saves raw data for the displayed plot as .txt file.
            """
            file_path = asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if config.method_choice == 1:
                data = np.column_stack((config.t_data, config.p_data_adjusted, config.P_f, config.P_b))
            elif config.method_choice == 2:
                data = np.column_stack((config.t_data, config.d_data_adjusted, config.D_f, config.D_b))
            np.savetxt(file_path, data, fmt='%.6f', delimiter='\t', comments='')

        def save_u_separation_data():
            """
            Called when user presses GUI button 'btn_save_data' while the velocity separation is being displayed.
            Asks user to choose save file path using asksaveasfilename() from tkinter.filedialog.
            Saves raw data for the displayed plot as .txt file.
            """
            file_path = asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            data = np.column_stack((config.t_data, config.u_data_adjusted, config.U_f, config.U_b))
            np.savetxt(file_path, data, fmt='%.6f', delimiter='\t', comments='')

        def save_wia_data():
            """
            Called when user presses GUI button 'btn_save_data' while the wave intensity analysis is being displayed.
            Asks user to choose save file path using asksaveasfilename() from tkinter.filedialog.
            Saves raw data for the displayed plot as .txt file.
            """
            file_path = asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            data = np.column_stack((config.t_data, config.dI))
            np.savetxt(file_path, data, fmt='%.6f', delimiter='\t', comments='')

        def save_wia_separation_data():
            """
            Called when user presses GUI button 'btn_save_data' while the WIA separation is being displayed.
            Asks user to choose save file path using asksaveasfilename() from tkinter.filedialog.
            Saves raw data for the displayed plot as .txt file.
            """
            file_path = asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            data = np.column_stack((config.t_data, config.dI, config.dI_f, config.dI_b))
            np.savetxt(file_path, data, fmt='%.6f', delimiter='\t', comments='')

        def save_plot_pressed():
            """
            Ensures the plot being displayed matches the plot being saved when user presses GUI button 'btn_save_plot'.
            """
            if config.current_plot == 'P sep':
                save_p_separation_plot()
            elif config.current_plot == 'U sep':
                save_u_separation_plot()
            elif config.current_plot == 'WIA':
                save_wia_plot()
            elif config.current_plot == 'WIA sep':
                save_wia_separation_plot()

        def save_data_pressed():
            """
            Ensures the plot being displayed matches the data being saved when user presses GUI button 'btn_save_data'.
            """
            if config.current_plot == 'P sep':
                save_p_separation_data()
            elif config.current_plot == 'U sep':
                save_u_separation_data()
            elif config.current_plot == 'WIA':
                save_wia_data()
            elif config.current_plot == 'WIA sep':
                save_wia_separation_data()

        def close_program():
            """
            Called when user presses GUI button 'btn_exit'.
            Closes the program.
            """
            self.controller.destroy()

        self.grid_rowconfigure((0, 1, 2), weight=1)        # Configure row weights
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)  # Configure column weights

        # Define widgets
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
            command=lambda: [convert_units(), controller.show_frame("PULoop")]
        )
        # Button to save plots as .png images
        btn_save_plot = tk.Button(
            self,
            text="Save plot",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=16,
            height=config.btn_height,
            command=lambda: save_plot_pressed()
        )
        # Button to save the raw data from each plot as .txt file
        btn_save_data = tk.Button(
            self,
            text="Save data",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=16,
            height=config.btn_height,
            command=lambda: save_data_pressed()
        )
        btn_display_p_sep = tk.Button(
            self,
            text="P separation",
            font=config.font,
            bg='#768692',
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=25,
            height=config.btn_height,
            command=lambda: self.display_p_separation_plot()
        )
        btn_display_u_sep = tk.Button(
            self,
            text="U separation",
            font=config.font,
            bg='#768692',
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=25,
            height=config.btn_height,
            command=lambda: self.display_u_separation_plot()
        )
        btn_display_wia = tk.Button(
            self,
            text="WIA",
            font=config.font,
            bg='#768692',
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=25,
            height=config.btn_height,
            command=lambda: self.display_wia_plot()
        )
        btn_display_wia_sep = tk.Button(
            self,
            text="WIA separation",
            font=config.font,
            bg='#768692',
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=25,
            height=config.btn_height,
            command=lambda: self.display_wia_separation_plot()
        )

        btn_exit = tk.Button(
            self,
            text="Close Program",
            font=config.font,
            bg=config.red,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=14,
            height=config.btn_height,
            command=lambda: close_program()
        )

        # Arrange all widgets for this frame
        btn_back.grid(row=2, column=0, padx=5, pady=5)

        btn_display_p_sep.grid(row=0, column=0, padx=5, pady=5)
        btn_display_u_sep.grid(row=0, column=1, padx=5, pady=5)
        btn_display_wia.grid(row=0, column=2, padx=5, pady=5)
        btn_display_wia_sep.grid(row=0, column=3, padx=5, pady=5)

        btn_save_plot.grid(row=2, column=1, padx=5, pady=5)
        btn_save_data.grid(row=2, column=2, padx=5, pady=5)
        btn_exit.grid(row=2, column=3, padx=5, pady=5)

    def run_analysis(self):
        """
        Runs as soon as this frame opens in GUI.
        Perform calculations for waveform separations and wave intensity analysis using wave speed value config.c
        calculated in previous page 'PULoop'
        """
        if config.method_choice == 1:
            config.dP = np.gradient(config.p_data_adjusted, config.t_data)
            config.dU = np.gradient(config.u_data_adjusted, config.t_data)
            config.dI = config.dP * config.dU

            # Calculating wave separation derivatives
            config.dP_f = (config.dP + (config.rho * config.c * config.dU)) / 2
            config.dU_f = (config.dU + (config.dP / (config.rho * config.c))) / 2
            config.dI_f = config.dP_f * config.dU_f
            config.dP_b = (config.dP - (config.rho * config.c * config.dU)) / 2
            config.dU_b = (config.dU - (config.dP / (config.rho * config.c))) / 2
            config.dI_b = config.dP_b * config.dU_b

            # Calculating wave separations
            # np.insert is necessary after each cumtrapz in order for dimensions to align.
            # cumtrapz returns an array 1 element shorter than its inputs.
            config.P_f = min(config.p_data_adjusted) + integrate.cumtrapz(config.dP_f, config.t_data)
            config.P_f = np.insert(config.P_f, 0, config.P_f[0])
            config.U_f = integrate.cumtrapz(config.dU_f, config.t_data)
            config.U_f = np.insert(config.U_f, 0, config.U_f[0])
            config.P_b = integrate.cumtrapz(config.dP_b, config.t_data)
            config.P_b = np.insert(config.P_b, 0, config.P_b[0])
            config.U_b = integrate.cumtrapz(config.dU_b, config.t_data)
            config.U_b = np.insert(config.U_b, 0, config.U_b[0])

        elif config.method_choice == 2:
            config.dD = np.gradient(config.d_data_adjusted, config.t_data)
            config.dlnD = np.gradient(config.lnd_data_adjusted, config.t_data)
            config.dU = np.gradient(config.u_data_adjusted, config.t_data)
            config.dI = config.dD * config.dU

            # Calculating wave separation derivatives
            config.dD_f = (config.d_data_adjusted / 2) * (config.dlnD + (config.dU / (2 * config.c)))
            config.dD_b = (-config.d_data_adjusted / 2) * (config.dlnD - (config.dU / (2 * config.c)))
            config.dU_f = 0.5 * (config.dU + (2 * config.c * config.dlnD))
            config.dU_b = 0.5 * (config.dU - (2 * config.c * config.dlnD))
            config.dI_f = config.dD_f * config.dU_f
            config.dI_b = config.dD_b * config.dU_b

            # Calculating wave separations
            # np.insert is necessary after each cumtrapz in order for dimensions to align.
            # cumtrapz returns an array 1 element shorter than its inputs.
            config.D_f = config.d_data_adjusted[0] + integrate.cumtrapz(config.dD_f, config.t_data)
            config.D_f = np.insert(config.D_f, 0, config.D_f[0])
            config.U_f = integrate.cumtrapz(config.dU_f, config.t_data)
            config.U_f = np.insert(config.U_f, 0, config.U_f[0])
            config.D_b = config.d_data_adjusted[0] - integrate.cumtrapz(config.dD_b, config.t_data)
            config.D_b = np.insert(config.D_b, 0, config.D_b[0])
            config.U_b = integrate.cumtrapz(config.dU_b, config.t_data)
            config.U_b = np.insert(config.U_b, 0, config.U_b[0])
    def convert_units_back(self):
        """
        Called as soon as this frame opens in GUI.
        Converts all units back to those originally input by the user so they can see the displayed output plots in
        their preferred units.
        """
        if config.p_unit == 'kPa':
            config.p_data_adjusted /= 1000
            config.P_f /= 1000
            config.P_b /= 1000
        if config.p_unit == 'mmHg':
            config.p_data_adjusted /= 133
            config.P_f /= 133
            config.P_b /= 133
        if config.u_unit == 'cm/s':
            config.u_data_adjusted *= 100
            config.U_f *= 100
            config.U_b *= 100
        if config.u_unit == 'mm/s':
            config.u_data_adjusted *= 1000
            config.U_f *= 1000
            config.U_b *= 1000
        if config.d_unit == 'cm':
            config.d_data_adjusted *= 100
            config.D_f *= 100
            config.D_b *= 100
        if config.d_unit == 'mm':
            config.d_data_adjusted *= 1000
            config.D_f *= 1000
            config.D_b *= 1000

    def create_p_separation_plot(self):
        """
        Called as soon as this frame opens in GUI.
        Creates either P separation or D separation plot depending on whether analysis is invasive or non-invasive.
        Plot is not displayed in this function.
        Various aesthetic choices which remain consistent throughout GUI.
        """
        if config.method_choice == 1:
            # Plot separation of P, P+ and P-.
            if len(config.p_data_adjusted) > 200:
                pts_per_marker = round(len(config.p_data_adjusted) / 200)
            else:
                pts_per_marker = 1
            fig, ax = plt.subplots(figsize=(8, 5))
            fig.patch.set_facecolor(config.plot_bg_col)
            ax.set_facecolor(config.plot_bg_col)
            ax.plot(config.t_data, config.p_data_adjusted, c='#e00202', linewidth=0.8, label='P')
            plt.plot(config.t_data[::pts_per_marker], config.p_data_adjusted[::pts_per_marker], linestyle='None',
                     marker='.', markeredgecolor='#8a0000',
                     markerfacecolor='None', markeredgewidth=0.5, markersize=2)
            ax.plot(config.t_data, config.P_f, c='#1638cc', linewidth=0.8, label=r'$\mathregular{P_{+}}$')
            plt.plot(config.t_data[::pts_per_marker], config.P_f[::pts_per_marker], linestyle='None', marker='.',
                     markeredgecolor='#030785',
                     markerfacecolor='None', markeredgewidth=0.5, markersize=2)
            ax.plot(config.t_data, config.P_b, c='#05d8f0', linewidth=0.8, label=r'$\mathregular{P_{-}}$')
            plt.plot(config.t_data[::pts_per_marker], config.P_b[::pts_per_marker], linestyle='None', marker='.',
                     markeredgecolor='#1638cc',
                     markerfacecolor='None', markeredgewidth=0.5, markersize=2)
            plt.gca().yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
            plt.gca().ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
            ax.set_xlabel('t (s)')
            ax.set_ylabel(f'P ({config.p_unit})')
            ax.set_title('P separation')
            ax.legend(loc='upper right')
            plt.minorticks_on()
            plt.tick_params(axis='both', which='major', labelsize=12)
            plt.grid(which='major', color='grey', linestyle='-', linewidth=0.5, alpha=0.5)
            plt.grid(which='minor', color='grey', linestyle='-', linewidth=0.2, alpha=0.5)
            fig.tight_layout()

        elif config.method_choice == 2:
            # Plot separation of D, D+ and D-.
            if len(config.d_data_adjusted) > 200:
                pts_per_marker = round(len(config.d_data_adjusted) / 200)
            else:
                pts_per_marker = 1
            fig, ax = plt.subplots(figsize=(8, 5))
            fig.patch.set_facecolor(config.plot_bg_col)
            ax.set_facecolor(config.plot_bg_col)
            ax.plot(config.t_data, config.d_data_adjusted, c='#e00202', linewidth=0.8, label='P')
            plt.plot(config.t_data[::pts_per_marker], config.d_data_adjusted[::pts_per_marker], linestyle='None',
                     marker='.', markeredgecolor='#8a0000',
                     markerfacecolor='None', markeredgewidth=0.5, markersize=2)
            ax.plot(config.t_data, config.D_f, c='#1638cc', linewidth=0.8, label=r'$\mathregular{P_{+}}$')
            plt.plot(config.t_data[::pts_per_marker], config.D_f[::pts_per_marker], linestyle='None', marker='.',
                     markeredgecolor='#030785',
                     markerfacecolor='None', markeredgewidth=0.5, markersize=2)
            ax.plot(config.t_data, config.D_b, c='#05d8f0', linewidth=0.8, label=r'$\mathregular{P_{-}}$')
            plt.plot(config.t_data[::pts_per_marker], config.D_b[::pts_per_marker], linestyle='None', marker='.',
                     markeredgecolor='#1638cc',
                     markerfacecolor='None', markeredgewidth=0.5, markersize=2)
            plt.gca().yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
            plt.gca().ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
            ax.set_xlabel('t (s)')
            ax.set_ylabel(f'D ({config.d_unit})')
            ax.set_title('D separation')
            ax.legend(loc='upper right')
            plt.minorticks_on()
            plt.tick_params(axis='both', which='major', labelsize=12)
            plt.grid(which='major', color='grey', linestyle='-', linewidth=0.5, alpha=0.5)
            plt.grid(which='minor', color='grey', linestyle='-', linewidth=0.2, alpha=0.5)
            fig.tight_layout()

        return fig

    def create_u_separation_plot(self):
        """
        Called as soon as this frame opens in GUI.
        Creates U separation plot but does not display.
        Various aesthetic choices which remain consistent throughout GUI.
        """
        # Plot separation of U, U+ and U-.
        if len(config.u_data_adjusted) > 200:
            pts_per_marker = round(len(config.u_data_adjusted) / 200)
        else:
            pts_per_marker = 1
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor(config.plot_bg_col)
        ax.set_facecolor(config.plot_bg_col)
        ax.plot(config.t_data, config.u_data_adjusted, c='#e00202', linewidth=0.8, label='U')
        plt.plot(config.t_data[::pts_per_marker], config.u_data_adjusted[::pts_per_marker], linestyle='None',
                 marker='.', markeredgecolor='#8a0000',
                 markerfacecolor='None', markeredgewidth=0.5, markersize=2)
        ax.plot(config.t_data, config.U_f, c='#1638cc', linewidth=0.8, label=r'$\mathregular{U_{+}}$')
        plt.plot(config.t_data[::pts_per_marker], config.U_f[::pts_per_marker], linestyle='None', marker='.',
                 markeredgecolor='#030785',
                 markerfacecolor='None', markeredgewidth=0.5, markersize=2)
        ax.plot(config.t_data, config.U_b, c='#05d8f0', linewidth=0.8, label=r'$\mathregular{U_{-}}$')
        plt.plot(config.t_data[::pts_per_marker], config.U_b[::pts_per_marker], linestyle='None', marker='.',
                 markeredgecolor='#1638cc',
                 markerfacecolor='None', markeredgewidth=0.5, markersize=2)
        plt.gca().yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        plt.gca().ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
        ax.set_xlabel('t (s)')
        ax.set_ylabel(f'U ({config.u_unit})')
        ax.set_title('U separation')
        ax.legend(loc='upper right')
        plt.minorticks_on()
        plt.tick_params(axis='both', which='major', labelsize=12)
        plt.grid(which='major', color='grey', linestyle='-', linewidth=0.5, alpha=0.5)
        plt.grid(which='minor', color='grey', linestyle='-', linewidth=0.2, alpha=0.5)
        fig.tight_layout()

        return fig

    def create_wia_plot(self):
        """
        Called as soon as this frame opens in GUI.
        Creates wave intensity analysis plot but does not display.
        Various aesthetic choices which remain consistent throughout GUI.
        """
        # Plot wave intensity analysis.
        if len(config.dI) > 200:
            pts_per_marker = round(len(config.dI) / 200)
        else:
            pts_per_marker = 1
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor(config.plot_bg_col)
        ax.set_facecolor(config.plot_bg_col)
        ax.plot(config.t_data, config.dI, c='#e00202', linewidth=0.8, label='dI')
        plt.plot(config.t_data[::pts_per_marker], config.dI[::pts_per_marker], linestyle='None', marker='.',
                 markeredgecolor='#8a0000',
                 markerfacecolor='None', markeredgewidth=0.5, markersize=2)
        plt.gca().yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        plt.gca().ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
        ax.set_xlabel('t (s)')
        ax.set_ylabel(r'dI $\mathregular{(Wm^{-2})}$')
        ax.set_title('Wave Intensity Analysis')
        plt.minorticks_on()
        plt.tick_params(axis='both', which='major', labelsize=12)
        plt.grid(which='major', color='grey', linestyle='-', linewidth=0.5, alpha=0.5)
        plt.grid(which='minor', color='grey', linestyle='-', linewidth=0.2, alpha=0.5)
        fig.tight_layout()

        return fig

    def create_wia_separation_plot(self):
        """
        Called as soon as this frame opens in GUI.
        Creates WIA separation plot but does not display.
        Various aesthetic choices which remain consistent throughout GUI.
        """
        # Plot separation of dI, dI+ and dI-.
        if len(config.dI) > 200:
            pts_per_marker = round(len(config.dI) / 200)
        else:
            pts_per_marker = 1
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor(config.plot_bg_col)
        ax.set_facecolor(config.plot_bg_col)
        ax.plot(config.t_data, config.dI, c='#e00202', linewidth=0.8, label='dI')
        plt.plot(config.t_data[::pts_per_marker], config.dI[::pts_per_marker], linestyle='None', marker='.',
                 markeredgecolor='#8a0000',
                 markerfacecolor='None', markeredgewidth=0.5, markersize=2)
        ax.plot(config.t_data, config.dI_f, c='#1638cc', linewidth=0.8, label=r'$\mathregular{dI_{+}}$')
        plt.plot(config.t_data[::pts_per_marker], config.dI_f[::pts_per_marker], linestyle='None', marker='.',
                 markeredgecolor='#030785',
                 markerfacecolor='None', markeredgewidth=0.5, markersize=2)
        ax.plot(config.t_data, config.dI_b, c='#05d8f0', linewidth=0.8, label=r'$\mathregular{dI_{-}}$')
        plt.plot(config.t_data[::pts_per_marker], config.dI_b[::pts_per_marker], linestyle='None', marker='.',
                 markeredgecolor='#1638cc',
                 markerfacecolor='None', markeredgewidth=0.5, markersize=2)
        plt.gca().yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        plt.gca().ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
        ax.set_xlabel('t (s)')
        ax.set_ylabel(r'dI $\mathregular{(Wm^{-2})}$')
        ax.set_title('WIA separation')
        ax.legend(loc='upper right')
        plt.minorticks_on()
        plt.tick_params(axis='both', which='major', labelsize=12)
        plt.grid(which='major', color='grey', linestyle='-', linewidth=0.5, alpha=0.5)
        plt.grid(which='minor', color='grey', linestyle='-', linewidth=0.2, alpha=0.5)
        fig.tight_layout()

        return fig

    def display_p_separation_plot(self):
        """
        Called as soon as this frame opens in GUI.
        Calls create_p_separation_plot() to create the plot, then displays in GUI frame.
        Sets config.current_plot to relevant graph for use when saving plots and data.
        """
        fig = self.create_p_separation_plot()
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().grid(row=1, column=0, columnspan=4, padx=5, pady=5)
        config.current_plot = 'P sep'

    def display_u_separation_plot(self):
        """
        Called as soon as this frame opens in GUI.
        Calls create_u_separation_plot() to create the plot, then displays in GUI frame.
        Sets config.current_plot to relevant graph for use when saving plots and data.
        """
        fig = self.create_u_separation_plot()
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().grid(row=1, column=0, columnspan=4, padx=5, pady=5)
        config.current_plot = 'U sep'

    def display_wia_plot(self):
        """
        Called as soon as this frame opens in GUI.
        Calls create_wia_plot() to create the plot, then displays in GUI frame.
        Sets config.current_plot to relevant graph for use when saving plots and data.
        """
        fig = self.create_wia_plot()
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().grid(row=1, column=0, columnspan=4, padx=5, pady=5)
        config.current_plot = 'WIA'

    def display_wia_separation_plot(self):
        """
        Called as soon as this frame opens in GUI.
        Calls create_wia_separation_plot() to create the plot, then displays in GUI frame.
        Sets config.current_plot to relevant graph for use when saving plots and data.
        """
        fig = self.create_wia_separation_plot()
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().grid(row=1, column=0, columnspan=4, padx=5, pady=5)
        config.current_plot = 'WIA sep'

    def tkraise(self):
        """
        Calls functions run_analysis(), convert_units_back(), and display_p_separation_plot() as soon as this frame is
        opened in GUI.
        """
        super().tkraise()
        self.run_analysis()
        self.convert_units_back()
        self.display_p_separation_plot()
