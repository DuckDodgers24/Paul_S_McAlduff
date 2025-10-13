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
        phq9_responses (list): Response options for each question
        phq9_intvars (list): IntVar objects storing user responses
        UNANSWERED (int): Constant representing unanswered questions (-1)
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Health Questionnaire (PHQ-9)")
        self.root.geometry("800x710")

        self.phq9_instructions = ("Over the last 2 weeks, how often have you been bothered by any of the "
                                  "following problems? Type in the number beside the statement you picked.")

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

        self.phq9_responses = [
            "Not at all",
            "Several days",
            "More than half the days",
            "Nearly every day"
            ]

        self.phq9_about = ("The Personal Health Questionnaire (PHQ-9) was developed by Drs. Robert L. Spitzer, "
                           "Janet B.W. Williams, Kurt Kroenke and colleagues, with an educational grant from "
                           "Pfizer Inc.  No permission required to reproduce, translate, display or distribute.")
        
        self.phq9_disclaimer = ("Note: These results are for educational demonstration only and cannot diagnose "
                                "mental health conditions. If you have concerns about depression or anxiety, "
                                "please speak with a qualified healthcare professional.")

        self.phq9_intvars = []
        self.UNANSWERED = -1

        self.create_widgets()

    def create_widgets(self):
        """ Display questions and prompts users for responses. """
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        title_label = tk.Label(main_frame, text="Personal Health Questionnaire", font=("Arial", 16, "bold"))
        title_label.pack()

        # Displays instructions on how to use the PHQ-9
        instructions_label = tk.Label(main_frame, text=self.phq9_instructions, font=("Arial", 10), wraplength=640, justify="left")
        instructions_label.pack(pady=10)

        phq9_frame = ttk.LabelFrame(main_frame, text="PHQ-9 Depression Screening", padding=20)
        phq9_frame.pack()

        # Iterates through the questions stored in a list
        for question in self.phq9_questions:
            question_label = tk.Label(phq9_frame, text=question, font=("Arial", 10), wraplength=550, justify="left")
            question_label.pack(padx=10, anchor="w")

            var = tk.IntVar(value=self.UNANSWERED) # Initializes var and sets buttons to unselected
                    
            radio_frame = tk.Frame(phq9_frame)
            radio_frame.pack()

            # Iterates through the responses and indexes stored in a list
            for score_index, answer in enumerate(self.phq9_responses):
                # Creates radio buttons for question responses
                ttk.Radiobutton(radio_frame, text=answer, variable=var, value=score_index).pack(side=tk.LEFT, padx=10, pady=(0, 6))

            self.phq9_intvars.append(var) # Receives values from Radiobuttons

        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=20)  # Centers by default
        
        submit_button = ttk.Button(button_frame, text="Submit", command=self.calculate_scores)
        submit_button.pack(side=tk.LEFT, padx=10)

        reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_form)
        reset_button.pack(side=tk.LEFT, padx=10)

        exit_button = ttk.Button(button_frame, text="Exit", command=self.root.destroy) # Closes GUI and ends program
        exit_button.pack(side=tk.LEFT, padx=10)
            
        about_button = ttk.Button(button_frame, text="About", command=self.show_about)
        about_button.pack(side=tk.LEFT, padx=10)

    def calculate_scores(self):
        """
        Ensure all questions are answered and calculate the score.

        Display a warning if any questions are unanswered, otherwise
        calculate the total score and determine severity.
        """
        for value in self.phq9_intvars:
            if value.get() == self.UNANSWERED:
                messagebox.showwarning("Incomplete", "Please answer all questions")
                return

        # Calculates total score by summing all responses
        total_score = 0
        for value in self.phq9_intvars:
            total_score += value.get()

        self.calculate_severity(total_score)
            
    def calculate_severity(self, total_score):
        """
        Determine the severity of symptoms based on the score.

        Args:
            total_score (int): The sum of all question responses (0-27)
        """
        if total_score >= 20:
            severity_rating = "Severe depression"
        elif total_score >= 15:
            severity_rating = "Moderately severe depression"
        elif total_score >= 10:
            severity_rating = "Moderate depression"
        elif total_score >= 5:
            severity_rating = "Mild depression"
        else:
            severity_rating = "Minimal depression"

        self.show_results(total_score, severity_rating)
        
    def show_results(self, total_score, severity_rating):
        """
        Display the assessment results in a popup window.

        Args:
            total_score (int): The sum of all question responses (0-27)
            severity_rating (str): The depression severity classification
        """
        results_popup = tk.Toplevel(self.root)
        results_popup.title("Assessment Results")
        results_popup.geometry("450x250")
        results_popup.transient(self.root) # Makes it stay on top of parent
        results_popup.grab_set() # Makes it modal (blocks parent until closed)

        phq9_frame = ttk.LabelFrame(results_popup, text="Results", padding=20)
        phq9_frame.pack(fill="both", padx=20, pady=20)

        # Outputs the total score
        total_score_label = tk.Label(phq9_frame, text=f"Total Score: {total_score}/27", font=("Arial", 16, "bold"))
        total_score_label.pack()

        # Outputs the depression severity
        severity_score_label = tk.Label(phq9_frame, text=f"Severity: {severity_rating}", font=("Arial", 12))
        severity_score_label.pack()
        
        disclaimer_label = tk.Label(phq9_frame, text=self.phq9_disclaimer, font=("Arial", 10), wraplength=350, justify="left")
        disclaimer_label.pack(pady=10)
        
    def show_about(self):
        """
        Display information on the PHQ-9 in a popup window.
        Provide a disclaimer on the use of the PHQ-9.
        """
        about_popup = tk.Toplevel(self.root)
        about_popup.title("About PHQ-9")
        about_popup.geometry("450x300")
        about_popup.transient(self.root) # Makes it stay on top of parent
        about_popup.grab_set() # Makes it modal (blocks parent until closed)

        phq9_frame = ttk.LabelFrame(about_popup, text="About", padding=20)
        phq9_frame.pack(fill="both", padx=20, pady=20)

        # Provides users with information on the PHQ-9
        about_label = tk.Label(phq9_frame, text=self.phq9_about, font=("Arial", 10), wraplength=350, justify="left")
        about_label.pack(pady=10)

        # Provides a disclaimer on the use the PHQ-9
        disclaimer_label = tk.Label(phq9_frame, text=self.phq9_disclaimer, font=("Arial", 10), wraplength=350, justify="left")
        disclaimer_label.pack(pady=10)
        
    def reset_form(self):
        """ Allow users to reset the questionnaire to the unselected state. """
        for var in self.phq9_intvars: 
            var.set(self.UNANSWERED) # Resets buttons to unselected

if __name__ == "__main__":
    root = tk.Tk()
    app = PatientHealthQuestionnaire(root)
    root.mainloop()
