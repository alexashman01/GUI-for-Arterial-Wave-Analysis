import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.ticker import ScalarFormatter
from scipy import integrate
from scipy.optimize import minimize
from tkinter.filedialog import asksaveasfilename
import config


class Windkessel(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=config.bg_col)
        self.controller = controller

        def save_windkessel_plot():
            """
            Called when user presses GUI button 'btn_save_windkessel_plot'.
            Asks user to choose save file path using asksaveasfilename() from tkinter.filedialog.
            PLot saves at 150 DPI to balance clarity and file size.
            """
            fig = self.windkessel_plot()
            file_path = asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            fig.savefig(file_path, dpi=150)

        def save_windkessel_data():
            """
            Called when user presses GUI button 'btn_save_windkessel_data'.
            Asks user to choose save file path using asksaveasfilename() from tkinter.filedialog.
            Saves raw data for the displayed plot as .txt file.
            """
            file_path = asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            data = np.column_stack((config.windkessel_t, config.windkessel_p,
                                    config.windkessel_pr, config.windkessel_pex))
            np.savetxt(file_path, data, fmt='%.6f', delimiter='\t', comments='')

        self.grid_rowconfigure((0, 1, 2), weight=1)              # Configure row weights
        self.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)  # Configure column weights

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
            command=lambda: controller.show_frame("PUAdjust")
        )
        btn_save_windkessel_plot = tk.Button(
            self,
            text="Save windkessel plot",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=18,
            height=config.btn_height,
            command=lambda: save_windkessel_plot()
        )
        btn_windkessel_data = tk.Button(
            self,
            text="Save windkessel data",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=18,
            height=config.btn_height,
            command=lambda: save_windkessel_data()
        )

        # Arrange all widgets for this frame
        btn_back.grid(row=2, column=0, padx=5, pady=5)
        btn_save_windkessel_plot.grid(row=2, column=4, padx=5, pady=5)
        btn_windkessel_data.grid(row=2, column=5, padx=5, pady=5)

    def calculate_windkessel(self):
        """
        Runs as soon as this frame opens in GUI.
        This function has been translated from MATLAB script 'Windkessel.mlapp' to Python.
        Complete windkessel analysis, outputting pressure, reservoir pressure and excess pressure as
        config.windkessel_p, config.windkessel_pr, and config.windkessel_pex respectively.
        """
        def kexpint(Y, T, A):
            N = len(Y) - 1
            t1 = np.linspace(0, T, N + 1)
            dt = t1[2] - t1[1]
            Y0 = Y[1]
            y = Y - Y0
            ye = y * np.exp(A * t1)
            z = (integrate.cumtrapz(ye)) * dt
            z = np.insert(z, 0, z[0])
            Z = z + Y0 * (np.exp(A * t1) - 1) / A
            return Z

        def dias_int(Ps, Ts, a, b, Pinf, nn):
            dt = Ts[2] - Ts[1]
            pse = integrate.cumtrapz(Ps * np.exp((a + b) * Ts)) * dt
            pse = np.insert(pse, 0, pse[0])
            prb = np.exp(-(a + b) * Ts) * (a * pse + Ps[1] - (b * Pinf / (a + b))) + b * Pinf / (a + b)
            Prd = prb[nn:]
            return Prd

        def beat_int(Ps, Ts, a, b, Pinf):
            dt = Ts[2] - Ts[1]
            pse = integrate.cumtrapz(Ps * np.exp((a + b) * Ts)) * dt
            pse = np.insert(pse, 0, pse[0])
            prb = np.exp(-(a + b) * Ts) * (a * pse + Ps[1] - (b * Pinf / (a + b))) + b * Pinf / (a + b)
            Pr = prb
            return Pr

        def afind(aa):
            return np.sum((p[nn:] - dias_int(p, t, aa, b, pinf, nn)) ** 2)

        # Find the index of the minimum value
        min_index = np.argmin(config.p_data)
        # Extract elements from the minimum index onwards
        P = config.p_data[min_index:]
        p = P

        # Creates t array of the right length for new shortened p_data
        step = 1 / config.sampling_frequency
        length = len(P) - 1
        t = np.arange(0, step * length, step)

        # Duration of beat, Tb
        Tb = t[-1]
        # Time of start of diastole, Tn
        tn = 0
        # index at start of diastole
        nn = 0

        # calculate moments of pressure during diastole using model d=a*exp(-bt)+c
        pd = p[:-1]
        td = t[:-1] - tn
        Td = Tb - tn
        E0 = np.mean(pd)
        E1 = kexpint(pd - E0, Td, 1 / Td)
        E2 = kexpint(pd - E0, Td, 2 / Td)
        r = E2[-1] / E1[-1]

        # Coefficients obtained by polyfit in MATLAB
        polyB = [198.7882, -427.3471, 350.9809, -148.1055, 28.1913]
        # Polynomial evaluation
        BTd = np.polyval(polyB, r - 3)
        # Check condition
        if BTd > 10:
            warning_str = f"BTd = {BTd:.3f} diastolic time constant is out of expected bounds"
            print(warning_str)

        e1 = np.exp(1)
        if BTd == 1:
            denom = (3 - e1 - 1 / e1)
        else:
            denom = (1 - e1 * np.exp(-BTd)) / (BTd - 1) - (e1 - 1) * (1 - np.exp(-BTd)) / BTd
        a = E1[-1] / (Td * denom)
        c = E0 - a * (1 - np.exp(-BTd)) / BTd
        b = BTd / Td
        pinf = c
        prd = a * np.exp(-b * td) + c  # Exponential fit

        # Set options for optimization
        options = {'ftol': 1e-6}

        # Perform the optimization
        result = minimize(afind, 0, method='L-BFGS-B', options=options)
        # Extract the optimized parameter
        aa = result.x
        # Use the optimized parameter in the beat_int function
        pr = beat_int(p, t, aa, b, pinf)

        pex = p - pr  # Calculate excess pressure

        p = np.delete(p, 0)  # p = pressure waveform
        p = np.insert(p, 0, p[0])
        pr = np.delete(pr, 0)  # pr = reservoir pressure
        pr = np.insert(pr, 0, pr[0])
        pex = np.delete(pex, 0)  # pex = excess pressure
        pex = np.insert(pex, 0, pex[0])

        # Save results to config.py with clear naming convention, in line with rest of program.
        config.windkessel_p = p
        config.windkessel_pr = pr
        config.windkessel_pex = pex
        config.windkessel_t = t
        config.prd = prd

    def windkessel_plot(self):
        """
        Called as soon as this frame opens in GUI.
        Plot windkessel analysis: pressure, reservoir pressure and excess pressure.
        Various aesthetic choices which remain consistent throughout GUI.
        """
        if len(config.windkessel_p) > 200:
            pts_per_marker = round(len(config.windkessel_p) / 200)
        else:
            pts_per_marker = 1
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor(config.plot_bg_col)
        ax.set_facecolor(config.plot_bg_col)
        ax.plot(config.windkessel_t, config.windkessel_p, c='#e00202', linewidth=0.8, label='P')
        plt.plot(config.windkessel_t[::pts_per_marker], config.windkessel_p[::pts_per_marker], linestyle='None',
                 marker='.', markeredgecolor='#8a0000',
                 markerfacecolor='None', markeredgewidth=0.5, markersize=2)
        ax.plot(config.windkessel_t, config.windkessel_pr, c='#1638cc', linewidth=0.8, label=r'$\mathregular{P_{+}}$')
        plt.plot(config.windkessel_t[::pts_per_marker], config.windkessel_pr[::pts_per_marker], linestyle='None', marker='.',
                 markeredgecolor='#030785',
                 markerfacecolor='None', markeredgewidth=0.5, markersize=2)
        ax.plot(config.windkessel_t, config.windkessel_pex, c='#05d8f0', linewidth=0.8, label=r'$\mathregular{P_{-}}$')
        plt.plot(config.windkessel_t[::pts_per_marker], config.windkessel_pex[::pts_per_marker], linestyle='None', marker='.',
                 markeredgecolor='#1638cc',
                 markerfacecolor='None', markeredgewidth=0.5, markersize=2)
        plt.gca().yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        plt.gca().ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
        ax.set_xlabel('t (s)')
        ax.set_ylabel(f'P ({config.p_unit})')
        ax.set_title('Windkessel Analysis')
        ax.legend(loc='upper right')
        plt.minorticks_on()
        plt.tick_params(axis='both', which='major', labelsize=12)
        plt.grid(which='major', color='grey', linestyle='-', linewidth=0.5, alpha=0.5)
        plt.grid(which='minor', color='grey', linestyle='-', linewidth=0.2, alpha=0.5)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().grid(row=0, column=0, columnspan=10, padx=5, pady=5)

        return fig

    def tkraise(self):
        """
        Calls functions calculate_windkessel() and windkessel_plot() as soon as this frame is opened in GUI.
        """
        super().tkraise()
        self.calculate_windkessel()
        self.windkessel_plot()
