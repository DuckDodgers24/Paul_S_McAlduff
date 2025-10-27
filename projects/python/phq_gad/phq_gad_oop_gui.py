import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class PatientHealthQuestionnaire:
    """
    Create a computer version of the Personal Health Questionnaire (PHQ-9),
    which is a 9-item depression screening tool that scores each item from
    0-3, producing a total score ranging from 0-27. Higher scores indicate
    more severe depression symptoms.
    
    Attributes:
        root: The Tkinter root window
        phq9_questions (list): The 9 PHQ-9 questionnaire items
        gad7_questions (list): The 7 GAD-7 questionnaire items
        phq_gad_responses (list): Response options for each question
        phq9_intvars (list): IntVar objects storing user responses
        UNANSWERED (int): Constant representing unanswered questions (-1)
    """
    def __init__(self, root):
        self.root = root
        self.root.title("PHQ-9 and GAD-7 Questionnaires")
        self.root.geometry("800x600")

        # PHQ-9 Severity Thresholds
        self.PHQ9_SEVERE = 20
        self.PHQ9_MODERATELY_SEVERE = 15
        self.PHQ9_MODERATE = 10
        self.PHQ9_MILD = 5
        
        # GAD-7 Severity Thresholds
        self.GAD7_SEVERE = 15
        self.GAD7_MODERATE = 10
        self.GAD7_MILD = 5

        # Constant for unanswered questionnaire items
        self.UNANSWERED = -1


        self.phq9_instructions = ("Over the last 2 weeks, how often have you been bothered by any of the "
                                  "following problems? Please select one response for each statement.")

        self.gad7_instructions = ("Over the last 2 weeks, how often have you been bothered by the "
                                  "following problems? Please select one response for each statement.")

        # List of questions for the PHQ-9 questionnaire
        self.phq9_questions = [
            "1. Little interest or pleasure in doing things.",
            "2. Feeling down, depressed, or hopeless.",
            "3. Trouble falling or staying asleep, or sleeping too much.",
            "4. Feeling tired or having little energy.",
            "5. Poor appetite or overeating.",
            "6. Feeling bad about yourself – or that you are a failure or have let yourself or your family down.",
            "7. Trouble concentrating on things, such as reading the newspaper or watching television.",
            ("8. Moving or speaking so slowly that other people could have noticed. Or the opposite – being so fidgety "
             "or restless that you have been moving around a lot more than usual."),
            "9. Thoughts that you would be better off dead, or of hurting yourself in some way."
            ]

        # List of questions for the GAD-7 questionnaire
        self.gad7_questions = [
            "1. Feeling nervous, anxious, or on edge.",
            "2. Not being able to stop or control worrying.",
            "3. Worrying too much about different things.",
            "4. Trouble relaxing.",
            "5. Being so restless that it's hard to sit still.",
            "6. Becoming easily annoyed or irritable.",
            "7. Feeling afraid as if something awful might happen."
            ]

        self.phq_gad_responses = [
            "Not at all",
            "Several days",
            "More than half the days",
            "Nearly every day"
            ]

        self.phq9_about = ("Both the Personal Health Questionnaire (PHQ-9) and Generalized Anxiety Disorder (GAD-7) "
                           "questionnaire were developed by Drs. Robert L. Spitzer, Janet B.W. Williams, Kurt "
                           "Kroenke and colleagues, with an educational grant from Pfizer Inc. No permission "
                           "required to reproduce, translate, display or distribute.")
        
        self.phq9_disclaimer = ("Note: These results are for educational demonstration only and cannot diagnose "
                                "mental health conditions. If you have concerns about depression or anxiety, "
                                "please speak with a qualified healthcare professional.")

        self.phq9_intvars = []
        self.gad7_intvars = []

        self.create_widgets()

    def create_widgets(self):
        """ Display questions and prompts users for responses. """
        # Creates canvas for scrollbar
        main_canvas = tk.Canvas(self.root, highlightthickness=0)
        
        # Creates scrollbar
        vert_scrollbar = ttk.Scrollbar(self.root, orient='vertical', command=main_canvas.yview)
        main_canvas.config(yscrollcommand=vert_scrollbar.set)
        
        scrollable_frame = ttk.Frame(main_canvas, padding=20)
        
        main_canvas.create_window((400, 0), window=scrollable_frame, anchor='n')
        
        # Updates scrollable area whenever content is added or resized
        def on_frame_configure(event):
            main_canvas.configure(scrollregion=main_canvas.bbox('all'))

        scrollable_frame.bind('<Configure>', on_frame_configure)

        # Mouse wheel scrolling
        def on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        main_canvas.bind_all("<MouseWheel>", on_mousewheel)

        # Packs canvas and scrollbar
        main_canvas.pack(side='left', fill='both', expand=True)
        vert_scrollbar.pack(side='right', fill='y')

        title_label = ttk.Label(scrollable_frame, text="PHQ-9 and GAD-7 Questionnaires", font=("Arial", 16, "bold"))
        title_label.pack()

        # Displays instructions on how to use the PHQ-9
        instructions_label = ttk.Label(scrollable_frame, text=self.phq9_instructions, font=("Arial", 10), wraplength=640, justify="left")
        instructions_label.pack(pady=10)

        # ****** PHQ-9 Section ******
        
        # Creates PHQ-9 frame
        phq9_frame = ttk.LabelFrame(scrollable_frame, text="PHQ-9 Depression Screening", padding=20)
        phq9_frame.pack(pady=(5, 5), fill="x")

        # Iterates through the questions stored in a list
        for phq_question in self.phq9_questions:
            question_label_phq = ttk.Label(phq9_frame, text=phq_question, font=("Arial", 10, "bold"), wraplength=520, justify="left")
            question_label_phq.pack(padx=50, anchor="w")

            var_phq = tk.IntVar(value=self.UNANSWERED) # Initializes var and sets buttons to unselected
                    
            radio_frame_phq = ttk.Frame(phq9_frame)
            radio_frame_phq.pack()

            # Iterates through the responses and indexes stored in a list
            for phq_score_index, phq_response in enumerate(self.phq_gad_responses):
                # Creates radio buttons for question responses
                ttk.Radiobutton(radio_frame_phq, text=phq_response, variable=var_phq, value=phq_score_index).pack(side=tk.LEFT, padx=10, pady=(0, 6))

            separator = ttk.Separator(phq9_frame, orient='horizontal')
            separator.pack(fill='x', padx=70, pady=(0, 6))

            self.phq9_intvars.append(var_phq) # Receives values from Radiobuttons

        # ****** GAD-7 Section ******
        
        # Creates GAD-7 frame
        gad7_frame = ttk.LabelFrame(scrollable_frame, text="GAD-7 Anxiety Screening", padding=20)
        gad7_frame.pack(pady=(10, 0), fill="x")

        # Iterates through the questions stored in a list
        for gad_question in self.gad7_questions:
            question_label_gad = ttk.Label(gad7_frame, text=gad_question, font=("Arial", 10, "bold"), wraplength=550, justify="left")
            question_label_gad.pack(padx=50, anchor="w")

            var_gad = tk.IntVar(value=self.UNANSWERED) # Initializes var and sets buttons to unselected
                    
            radio_frame_gad = ttk.Frame(gad7_frame)
            radio_frame_gad.pack()

            # Iterates through the responses and indexes stored in a list
            for gad_score_index, gad_response in enumerate(self.phq_gad_responses):
                # Creates radio buttons for question responses
                ttk.Radiobutton(radio_frame_gad, text=gad_response, variable=var_gad, value=gad_score_index).pack(side=tk.LEFT, padx=10, pady=(0, 6))

            separator = ttk.Separator(gad7_frame, orient='horizontal')
            separator.pack(fill='x', padx=70, pady=(0, 6))

            self.gad7_intvars.append(var_gad) # Receives values from Radiobuttons
            
        # Creates buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(pady=20)  # Centers by default
        
        submit_button = ttk.Button(button_frame, text="Submit", command=self.calculate_scores)
        submit_button.pack(side=tk.LEFT, padx=10)

        reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_form)
        reset_button.pack(side=tk.LEFT, padx=10)
           
        about_button = ttk.Button(button_frame, text="About", command=self.show_about)
        about_button.pack(side=tk.LEFT, padx=10)

        exit_button = ttk.Button(button_frame, text="Exit", command=self.confirm_exit) # Closes GUI and ends program
        exit_button.pack(side=tk.LEFT, padx=10)

    def calculate_scores(self):
        """
        Ensure all questions are answered and calculate the score.

        Display a warning if any questions are unanswered, otherwise
        calculate the total score and determine severity.
        """
        for value in self.phq9_intvars + self.gad7_intvars:
            if value.get() == self.UNANSWERED:
                messagebox.showwarning("Incomplete", "Please answer all questions")
                return

        # Calculates total PHQ score by summing all responses
        total_phq_score = 0
        for phq_value in self.phq9_intvars:
            total_phq_score += phq_value.get()

        # Calculates total GAD score by summing all responses
        total_gad_score = 0
        for gad_value in self.gad7_intvars:
            total_gad_score += gad_value.get()

        self.calculate_severity(total_phq_score, total_gad_score)
            
    def calculate_severity(self, total_phq_score, total_gad_score):
        """
        Determine the severity of phq and gad symptoms based on the score.

        Args:
            total_phq_score (int): The sum of all question responses (0-27)
            total_gad_score (int): The sum of all question responses (0-21)
        """

        # ****** PHQ-9 Section ******
        
        if total_phq_score >= self.PHQ9_SEVERE:
            phq_severity_rating = "Severe depression"
        elif total_phq_score >= self.PHQ9_MODERATELY_SEVERE:
            phq_severity_rating = "Moderately severe depression"
        elif total_phq_score >= self.PHQ9_MODERATE:
            phq_severity_rating = "Moderate depression"
        elif total_phq_score >= self.PHQ9_MILD:
            phq_severity_rating = "Mild depression"
        else:
            phq_severity_rating = "Minimal depression"

        # ****** GAD-7 Section ******

        if total_gad_score >= self.GAD7_SEVERE:
            gad_severity_rating = "Severe anxiety"
        elif total_gad_score >= self.GAD7_MODERATE:
            gad_severity_rating = "Moderate anxiety"
        elif total_gad_score >= self.GAD7_MILD:
            gad_severity_rating = "Mild anxiety"
        else:
            gad_severity_rating = "Minimal anxiety"

        self.show_results(total_phq_score, phq_severity_rating, total_gad_score, gad_severity_rating)

    def show_results(self, total_phq_score, phq_severity_rating, total_gad_score, gad_severity_rating):
        """
        Display the assessment results in a popup window.

        Args:
            total_phq_score (int): The sum of all phq question responses (0-27)
            phq_severity_rating (str): The depression severity classification
            total_gad_score (int): The sum of all gad question responses (0-21)
            gad_severity_rating (str): The anxiety severity classification
        """
        results_popup = tk.Toplevel(self.root)
        results_popup.title("PHQ-9 and GAD-7 Results")
        results_popup.geometry("450x350")
        results_popup.transient(self.root) # Makes it stay on top of parent
        results_popup.grab_set() # Makes it modal (blocks parent until closed)

        # Makes popup modal
        results_popup.transient(self.root)
        results_popup.grab_set()
        results_popup.focus_set()

        results_frame = ttk.LabelFrame(results_popup, text="Results", padding=20)
        results_frame.pack(fill="both", padx=20, pady=20)

        # Outputs the total phq score
        total_phq_score_label = tk.Label(results_frame, text=f"PHQ-9 Score: {total_phq_score}/27", font=("Arial", 16, "bold"))
        total_phq_score_label.pack()

        # Outputs the depression severity
        phq_severity_score_label = tk.Label(results_frame, text=f"Severity: {phq_severity_rating}", font=("Arial", 12))
        phq_severity_score_label.pack()

        separator = ttk.Separator(results_frame, orient='horizontal')
        separator.pack(fill='x', padx=70, pady=(10, 10))

        # Outputs the total gad score
        total_gad_score_label = tk.Label(results_frame, text=f"GAD-7 Score: {total_gad_score}/21", font=("Arial", 16, "bold"))
        total_gad_score_label.pack()

        # Outputs the anxiety severity
        gad_severity_score_label = tk.Label(results_frame, text=f"Severity: {gad_severity_rating}", font=("Arial", 12))
        gad_severity_score_label.pack()
        
        disclaimer_label = tk.Label(results_frame, text=self.phq9_disclaimer, font=("Arial", 10), wraplength=350, justify="left")
        disclaimer_label.pack(pady=10)

        exit_results_button = ttk.Button(results_frame, text="Exit", command=results_popup.destroy) # Closes results popup
        exit_results_button.pack(padx=10)
    
    def show_about(self):
        """
        Display information on the PHQ-9 in a popup window.
        Provide a disclaimer on the use of the PHQ-9 and GAD-7.
        """
        about_popup = tk.Toplevel(self.root)
        about_popup.title("About PHQ-9 and GAD-7")
        about_popup.geometry("450x350")
        about_popup.transient(self.root) # Makes it stay on top of parent
        about_popup.grab_set() # Makes it modal (blocks parent until closed)

        # Makes popup modal
        about_popup.transient(self.root)
        about_popup.grab_set()
        about_popup.focus_set()      

        about_frame = ttk.LabelFrame(about_popup, text="About", padding=20)
        about_frame.pack(fill="both", padx=20, pady=20)

        # Provides users with information on the PHQ-9
        about_label = tk.Label(about_frame, text=self.phq9_about, font=("Arial", 10), wraplength=350, justify="left")
        about_label.pack(pady=10)

        # Provides a disclaimer on the use the PHQ-9
        disclaimer_label = tk.Label(about_frame, text=self.phq9_disclaimer, font=("Arial", 10), wraplength=350, justify="left")
        disclaimer_label.pack(pady=10)

        exit_about_button = ttk.Button(about_frame, text="Exit", command=about_popup.destroy) # Closes results popup
        exit_about_button.pack(padx=10)
        
    def reset_form(self):
        """ Allow users to reset the questionnaire to the unselected state. """
        if messagebox.askokcancel("Reset", "Proceed with reset?"):
            for var_phq in self.phq9_intvars: 
                var_phq.set(self.UNANSWERED) # Resets buttons to unselected
            for var_gad in self.gad7_intvars: 
                var_gad.set(self.UNANSWERED) # Resets buttons to unselected

    def confirm_exit(self):
        """Show confirmation dialog before closing the application"""
        if messagebox.askokcancel("Exit", "Do you want to exit?"):
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PatientHealthQuestionnaire(root)
    root.mainloop()
