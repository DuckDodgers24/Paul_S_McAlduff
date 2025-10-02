
# ==============================================
# PHQ-9 and GAD-7 Questionnaire Program
# ==============================================

# --- Constants ---
choice_list=["0", "1", "2", "3"]

# List of questions for the PHQ
phq_question_list = [
    "1. Little interest or pleasure in doing things.",
    "2. Feeling down, depressed, or hopeless.",
    "3. Trouble falling or staying asleep, or sleeping too much.",
    "4. Feeling tired or having little energy.",
    "5. Poor appetite or overeating.",
    "6. Feeling bad about yourself – or that you are a failure\nor have let yourself or your family down.",
    "7. Trouble concentrating on things, such as reading the\nnewspaper or watching television.",
    "8. Moving or speaking so slowly that other people could have\nnoticed. Or the opposite – being so fidgety or restless that\nyou have been moving around a lot more than usual.",
    "9. Thoughts that you would be better off dead, or of hurting\nyourself in some way."
]

# List of questions for the GAD questionnaire
gad_question_list = [
    "1. Feeling nervous, anxious, or on edge.",
    "2. Not being able to stop or control worrying.",
    "3. Worrying too much about different things.",
    "4. Trouble relaxing.",
    "5. Being so restless that it's hard to sit still.",
    "6. Becoming easily annoyed or irritable.",
    "7. Feeling afraid as if something awful might happen."
]

# --- Helper Functions ---
def print_disclaimer():
    print("""Disclaimer
This is a programming exercise implementing the PHQ-9 and GAD-7,
public domain screening tools developed by Drs. Spitzer, Kroenke,
Williams, and Löwe. This demo is for educational purposes only and
is not intended for clinical use or self-diagnosis. If you have
mental health concerns, please consult a qualified healthcare
professional.

Crisis Resources: If you're experiencing thoughts of self-harm,
call 988 (Suicide & Crisis Lifeline), 911 (Emergency) or go to
your nearest emergency room.""")

def print_phq_instructions():
    print("""Over the last 2 weeks, how often have you been bothered by any of
the following problems? Type in the number beside the statement
you picked.""")

def print_gad_instructions():
    print("""Over the last 2 weeks, how often have you been bothered by the
following problems? Type in the number beside the statement
you picked.""")

def display_header(title, char):
    print("\n" + char * 70)
    print(title)
    print(char * 70 + "\n")

def ask_questions(question_list):
    """Iterates through questions and returns total score."""
    user_score = 0
    for question in question_list:
        question_string = f"""
{question}
   0. Not at all
   1. Several days
   2. More than half the days
   3. Nearly every day 
     """
        print(question_string)

        user_choice = input("Enter the number for your choice: ")
        while user_choice not in choice_list:
            print("Your choice must be between 0 and 3.")
            print("")
            user_choice = input("Enter the number for your choice: ")

        # Calculates total score
        user_score = user_score + int(user_choice)    
    return user_score


def phq_results(user_score):
    """Displays PHQ-9 score and interprets severity level."""
    print("\n" + "-" * 70)
    print("Total PHQ-9 Score:", user_score)


    if user_score >= 20:
        print("Severe depression")
    elif user_score >= 15:
        print("Moderately severe depression")
    elif user_score >= 10:
        print("Moderate depression")
    elif user_score >= 5:
        print("Mild depression")
    else:
        print("Minimal depression")          
    print("")

def gad_results(user_score):
    """Displays GAD-7 score and interprets severity level."""
    print("Total GAD-7 Score:", user_score)

    if user_score >= 15:
        print("Severe anxiety")
    elif user_score >= 10:
        print("Moderate anxiety")
    elif user_score >= 5:
        print("Mild anxiety")
    else:
        print("Minimal anxiety")
    print("-" * 70 + "\n")

def print_final_note():
    print("""Note: These results are for educational demonstration only
and cannot diagnose mental health conditions. If you have
concerns about depression or anxiety, please speak with a
qualified healthcare professional.

Crisis Resources: 988 Suicide & Crisis Lifeline | Emergency: 911
""")

# --- Main Program ---
def main():
    display_header("Patient Health Questionnaire and Generalized Anxiety Disorder\n(PHQ-9 and GAD-7)", "=")

    print_disclaimer()

    display_header("Patient Health Questionnaire-9 (PHQ-9)", "-")

    print_phq_instructions()  

    user_score_phq = ask_questions(phq_question_list)

    display_header("Generalized Anxiety Disorder-7 (GAD-7)", "-")

    print_gad_instructions()

    user_score_gad = ask_questions(gad_question_list)

    phq_results(user_score_phq)

    gad_results(user_score_gad)

    print_final_note()


# --- Entry Point ---
if __name__ == "__main__":
    main()
