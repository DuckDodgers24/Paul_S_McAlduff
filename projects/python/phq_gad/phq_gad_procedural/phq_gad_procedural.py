user_choice_PHQ = 0
user_score_PHQ = 0
user_choice_GAD = 0
user_score_GAD = 0

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

print("\n" + "=" * 70)
print("Patient Health Questionnaire and Generalized Anxiety Disorder")
print("(PHQ-9 and GAD-7)")
print("=" * 70 + "\n")

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

print("\n" + "-" * 70)
print("Patient Health Questionnaire-9 (PHQ-9)")
print("-" * 70 + "\n")

print("""Over the last 2 weeks, how often have you been bothered by any of
the following problems? Type in the number beside the statement
you picked.""")

# Iterates through the PHQ questions
for phq_question in phq_question_list:
    print("")
    print(f"{phq_question}")
    print("""   0. Not at all
   1. Several days
   2. More than half the days
   3. Nearly every day 
    """)

    user_choice_PHQ = input("Enter the number for your choice: ")
    while user_choice_PHQ not in choice_list:
        print("Your choice must be between 0 and 3.")
        print("")
        user_choice_PHQ = input("Enter the number for your choice: ")

    # Calculates total PHQ score
    user_score_PHQ = user_score_PHQ + int(user_choice_PHQ)

print("\n" + "-" * 70)
print("Generalized Anxiety Disorder-7 (GAD-7)")
print("-" * 70 + "\n")

print("""Over the last 2 weeks, how often have you been bothered by the
following problems? Type in the number beside the statement
you picked.""")

# Iterates through the GAD questions
for gad_question in gad_question_list:
    print("")
    print(f"{gad_question}")
    print("""   0. Not at all
   1. Several days
   2. Over half the days
   3. Nearly every day
    """)

    user_choice_GAD = input("Enter the number for your choice: ")
    while user_choice_GAD not in choice_list:
        print("Your choice must be between 0 and 3.")
        print("")
        user_choice_GAD = input("Enter the number for your choice: ")

    # Calculates total GAD score
    user_score_GAD = user_score_GAD + int(user_choice_GAD)

# Outputs and interprets the PHQ results
print("\n" + "-" * 70)
print("Total PHQ-9 Score:", user_score_PHQ)


if user_score_PHQ >= 20:
    print("Severe depression")
elif user_score_PHQ >= 15:
    print("Moderately severe depression")
elif user_score_PHQ >= 10:
    print("Moderate depression")
elif user_score_PHQ >= 5:
    print("Mild depression")
else:
    print("Minimal depression")          
print("")

# Outputs and interprets the results
print("Total GAD-7 Score:", user_score_GAD)

if user_score_GAD >= 15:
    print("Severe anxiety")
elif user_score_GAD >= 10:
    print("Moderate anxiety")
elif user_score_GAD >= 5:
    print("Mild anxiety")
else:
    print("Minimal anxiety")
print("-" * 70 + "\n")
    
print("""Note: These results are for educational demonstration only
and cannot diagnose mental health conditions. If you have
concerns about depression or anxiety, please speak with a
qualified healthcare professional.

Crisis Resources: 988 Suicide & Crisis Lifeline | Emergency: 911
""")

