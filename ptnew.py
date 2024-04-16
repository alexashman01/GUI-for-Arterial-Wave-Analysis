import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import config


class PtNew(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=config.bg_col)
        self.controller = controller

        self.grid_rowconfigure(0, weight=6)                                      # Configure row weights.
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10), weight=1)  # Configure column weights.

        # Define buttons to move out of this GUI frame.
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
            command=lambda: controller.show_frame("PUAdjust")
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
            command=lambda: controller.show_frame("InputPage")
        )
        btn_filter = tk.Button(
            self,
            text="Clean Data",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=config.btn_width,
            height=config.btn_height,
            command=lambda: controller.show_frame("SmoothData")
        )

        # Arrange all widgets for this frame
        btn_next.grid(row=1, column=9, padx=5, pady=5)
        btn_back.grid(row=1, column=0, padx=5, pady=5)
        btn_filter.grid(row=1, column=4, columnspan=2, padx=5, pady=5)

    def ptgraph(self):
        """
        Called as soon as frame 'PtNew' is opened in GUI.
        Plot config.p_data vs config.t_data.
        Various aesthetic choices which remain consistent throughout GUI.
        """
        if config.method_choice == 1 or config.method_choice == 3:
            if len(config.p_data) > 200:
                pts_per_marker = round(len(config.p_data) / 200)
            else:
                pts_per_marker = 1
            fig, ax = plt.subplots(figsize=(5, 3))
            fig.patch.set_facecolor(config.plot_bg_col)
            ax.set_facecolor(config.plot_bg_col)
            ax.plot(config.t_data, config.p_data, c='#1638cc', linewidth=0.8, label='P')
            plt.plot(config.t_data[::pts_per_marker], config.p_data[::pts_per_marker], linestyle='None', marker='.',
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
            canvas = FigureCanvasTkAgg(fig, self)
            canvas.get_tk_widget().grid(row=0, column=0, columnspan=5, padx=5, pady=5)

    def utgraph(self):
        """
        Called as soon as frame 'PtNew' is opened in GUI.
        Plot config.u_data vs config.t_data.
        Various aesthetic choices which remain consistent throughout GUI.
        """
        if len(config.u_data) > 200:
            pts_per_marker = round(len(config.u_data) / 200)
        else:
            pts_per_marker = 1
        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor(config.plot_bg_col)
        ax.set_facecolor(config.plot_bg_col)
        ax.plot(config.t_data, config.u_data, c='#e00202', linewidth=0.8, label='U')
        plt.plot(config.t_data[::pts_per_marker], config.u_data[::pts_per_marker], linestyle='None', marker='.',
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
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().grid(row=0, column=5, columnspan=5, padx=5, pady=5)

    def dtgraph(self):
        """
        Called as soon as frame 'PtNew' is opened in GUI.
        Plot config.d_data vs config.t_data.
        Various aesthetic choices which remain consistent throughout GUI.
        """
        if config.method_choice == 2:
            if len(config.d_data) > 200:
                pts_per_marker = round(len(config.d_data) / 200)
            else:
                pts_per_marker = 1
            fig, ax = plt.subplots(figsize=(5, 3))
            fig.patch.set_facecolor(config.plot_bg_col)
            ax.set_facecolor(config.plot_bg_col)
            ax.plot(config.t_data, config.d_data, c='#1638cc', linewidth=0.8, label='P')
            plt.plot(config.t_data[::pts_per_marker], config.d_data[::pts_per_marker], linestyle='None', marker='.',
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
            canvas = FigureCanvasTkAgg(fig, self)
            canvas.get_tk_widget().grid(row=0, column=0, columnspan=5, padx=5, pady=5)

    def tkraise(self):
        """
        Calls functions ptgraph(), utgraph, and dtgraph() as soon as this frame is opened in GUI.
        """
        super().tkraise()
        self.ptgraph()
        self.utgraph()
        self.dtgraph()
