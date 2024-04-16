import tkinter as tk
import config


class Homepage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=config.bg_col)
        self.controller = controller

        def choose_method(x):
            """
            Saves which type of analysis the user wants to run to global configuration.
            Methods 1/2/3 correspond to invasive/non-invasive/windkessel respectively.
            Edits variable config.method_choice.

            :param x: Method choice based on which button the user pressed
            """
            config.method_choice = x

        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9), weight=1)  # Configure rows to split evenl.
        self.grid_columnconfigure(0, weight=1)                            # Configure columns to split evenly.

        label1 = tk.Label(
            self,
            text="What type of measurements do you have?",
            font=('Roboto', 14),
            fg='black',
            bg=config.bg_col,
            width=40,
            height=5
        )

        # Define 3 buttons for user to choose invasive/non-invasive/windkessel.
        btn_invasive = tk.Button(
            self,
            text="Invasive",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=config.btn_width,
            height=2,
            command=lambda: [choose_method(1), controller.show_frame("InputPage")]
        )
        btn_non_invasive = tk.Button(
            self,
            text="Non-Invasive",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=config.btn_width,
            height=2,
            command=lambda: [choose_method(2), controller.show_frame("InputPage")]
        )
        btn_windkessel = tk.Button(
            self,
            text="Windkessel",
            font=config.font,
            bg=config.btn_col,
            fg=config.btn_text,
            activebackground=config.btn_col_a,
            activeforeground=config.btn_text_a,
            relief=tk.FLAT,
            width=config.btn_width,
            height=2,
            command=lambda: [choose_method(3), controller.show_frame("InputPage")]
        )

        # Arrange widgets within GUI frame
        label1.grid(row=0, column=0, padx=5, pady=5)
        btn_invasive.grid(row=1, column=0, padx=5, pady=5)
        btn_non_invasive.grid(row=2, column=0, padx=5, pady=5)
        btn_windkessel.grid(row=3, column=0, padx=5, pady=5)
