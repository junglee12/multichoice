import streamlit as st
import pandas as pd
import random
import os
import datetime
from typing import List, Dict, Any, Optional, Set

# --- Constants ---
# We will now use an uploaded file, so this is just a reference for expected structure
# QUIZ_FILE = "ROME-2.csv"
RESULTS_FILE = "quiz_results_uploaded_mc.csv" # Use a different results file name

# Column Indices (Expected structure for uploaded file based on position)
COL_IDX_QUESTION = 0
COL_IDX_OPTION_A = 1
COL_IDX_OPTION_B = 2
COL_IDX_OPTION_C = 3
COL_IDX_OPTION_D = 4
COL_IDX_CORRECT_ANSWER_LETTER = 5

# Session State Keys
SS_QUIZ_DATA = 'quiz_data_uploaded_mc'
SS_USER = 'user_uploaded_mc'
SS_CURRENT_INDEX = 'current_card_index_uploaded_mc'  # Store the index being displayed
SS_FLASHCARDS = 'flashcards_uploaded_mc' # Store the parsed quiz data
SS_LOADED_FILE_NAME = '_loaded_file_name_uploaded_mc' # Track the name of the loaded file

# Quiz Data Keys (within session_state[SS_QUIZ_DATA])
QK_STARTED = 'quiz_started'
QK_CORRECT_COUNT = 'correct_count'
QK_INCORRECT_COUNT = 'incorrect_count'
QK_CORRECT_QUESTIONS = 'correct_questions'  # List of {question, correct_text} dicts
# List of {q_text, correct_a_text, user_a_text} dicts
QK_INCORRECT_QUESTIONS = 'incorrect_questions'
QK_SHOW_ANSWER = 'show_answer'  # Boolean flag for current question display
QK_USER_SELECTED_OPTION = 'user_selected_option' # Stores the user's selected option letter (A, B, C, D) for the current question
QK_SUBMITTED = 'submitted'  # Boolean flag for current question submission
QK_SHOW_ANSWER_CLICKED = 'show_answer_clicked'  # Boolean flag for current q
QK_USED_QUESTIONS = 'used_questions'  # Set of original indices attempted
# Stores options for the currently displayed question (list of strings like 'A: Text')
QK_CURRENT_OPTIONS_DISPLAY = 'current_options_display'
QK_LAST_ANSWER_CORRECT = 'last_answer_correct' # Added: Store if the last submitted answer was correct


# --- Helper Functions ---

def _get_default_quiz_state() -> Dict[str, Any]:
    """Returns the default structure for the quiz state dictionary."""
    return {
        QK_STARTED: True,           # Flag indicating the quiz is active
        QK_CORRECT_COUNT: 0,        # Count of correctly answered questions
        QK_INCORRECT_COUNT: 0,      # Count of incorrectly answered questions
        QK_CORRECT_QUESTIONS: [],   # Stores details of correctly answered questions
        QK_INCORRECT_QUESTIONS: [],  # Stores details of incorrectly answered questions
        QK_SHOW_ANSWER: False,      # Flag to display the answer for the current question
        QK_USER_SELECTED_OPTION: None, # Stores the user's selected option letter (A, B, C, D)
        QK_SUBMITTED: False,        # Flag indicating if the current question's answer was submitted
        # Flag indicating if 'Show Answer' was clicked for the current question
        QK_SHOW_ANSWER_CLICKED: False,
        QK_USED_QUESTIONS: set(),   # Set of original flashcard indices already presented
        QK_CURRENT_OPTIONS_DISPLAY: None, # Options generated for the current question (for display)
        QK_LAST_ANSWER_CORRECT: None, # Added: Initialize correctness state
    }

# --- Core Logic Functions ---

def load_quiz_data_from_file(uploaded_file) -> Optional[List[Dict[str, Any]]]:
    """
    Loads quiz data from an uploaded CSV or XLSX file based on column position.

    Assumes the file has at least 6 columns in the following order:
    1st: Question text
    2nd: Option A text
    3rd: Option B text
    4th: Option C text
    5th: Option D text
    6th: Correct Answer Letter (A, B, C, or D)

    Args:
        uploaded_file: The file object uploaded via st.file_uploader.

    Returns:
        A list of dictionaries (quiz questions) or None if loading fails or format is incorrect.
    """
    try:
        fname = uploaded_file.name
        if fname.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif fname.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload a CSV or XLSX file.")
            return None

        if df.empty:
            st.error(f"The file '{fname}' is empty.")
            return None

        # Check if there are enough columns based on position
        if df.shape[1] < 6:
            st.error(
                f"Uploaded file must contain at least 6 columns. "
                f"Detected {df.shape[1]} columns."
            )
            st.info("Expected column structure (by position): Question (1st), Option A (2nd), Option B (3rd), Option C (4th), Option D (5th), Correct Answer Letter (6th).")
            return None

        quiz_data = []
        # Iterate through rows, using iloc to access columns by position
        for index, row in df.iterrows():
            options = {
                'A': str(row.iloc[COL_IDX_OPTION_A]),
                'B': str(row.iloc[COL_IDX_OPTION_B]),
                'C': str(row.iloc[COL_IDX_OPTION_C]),
                'D': str(row.iloc[COL_IDX_OPTION_D]),
            }
            # --- Modified logic to handle quotation marks ---
            correct_letter_raw = str(row.iloc[COL_IDX_CORRECT_ANSWER_LETTER]).strip()
            # Remove leading/trailing single or double quotes
            correct_letter = correct_letter_raw.lstrip('"\'').rstrip('"\'').upper()
            # --- End modified logic ---

            question_text = str(row.iloc[COL_IDX_QUESTION])

            if correct_letter not in options:
                 st.warning(f"Row {index + 2}: Invalid correct answer letter '{correct_letter_raw}' (parsed as '{correct_letter}'). Skipping question.")
                 continue

            # Basic check for empty question text
            if not question_text.strip():
                 st.warning(f"Row {index + 2}: Empty question text. Skipping question.")
                 continue

            quiz_data.append({
                'original_index': index, # Keep track of the original row index
                'question': question_text,
                'options': options,
                'correct_option_letter': correct_letter,
                'correct_answer_text': options[correct_letter], # Store the text of the correct answer
            })

        if not quiz_data:
             st.error("No valid questions found in the uploaded file.")
             return None

        return quiz_data

    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")
        return None


def start_quiz(quiz_data: List[Dict[str, Any]]):
    """Initializes or restarts the quiz state in session_state."""
    st.session_state[SS_FLASHCARDS] = quiz_data  # Store the loaded quiz data
    st.session_state[SS_QUIZ_DATA] = _get_default_quiz_state()
    # Clear any lingering current index from a previous run
    if SS_CURRENT_INDEX in st.session_state:
        del st.session_state[SS_CURRENT_INDEX]
    st.rerun()  # Rerun to reflect the start of the quiz immediately


def display_question(question_data: Dict[str, Any], question_key_suffix: str):
    """
    Displays the question and multiple-choice options using st.radio.

    Args:
        question_data: Dictionary containing the question data.
        question_key_suffix: A unique suffix for the st.radio key.

    Returns:
        The option letter (A, B, C, D) selected by the user, or None.
    """
    st.write(f"**Question:** {question_data['question']}")

    # Ensure options are in a consistent order (A, B, C, D) for display
    options_display = [
        f"A: {question_data['options']['A']}",
        f"B: {question_data['options']['B']}",
        f"C: {question_data['options']['C']}",
        f"D: {question_data['options']['D']}",
    ]

    # Store options display for later use (e.g., check_answer)
    st.session_state[SS_QUIZ_DATA][QK_CURRENT_OPTIONS_DISPLAY] = options_display

    # Use a unique key based on the question index/suffix to maintain state correctly
    selected_option_display = st.radio(
        "Choose your answer:",
        options_display,
        key=f"radio_{question_key_suffix}",
        index=None  # Default to no selection
    )

    # Extract the option letter (A, B, C, D) from the selected string
    if selected_option_display:
        return selected_option_display.split(':')[0].strip()
    return None


def check_answer(user_selected_option_letter: Optional[str], correct_option_letter: str) -> bool:
    """Checks if the user's selected option letter is correct (case-insensitive comparison)."""
    if user_selected_option_letter is None:
        return False  # No answer selected is incorrect
    return user_selected_option_letter.strip().upper() == correct_option_letter.strip().upper()


def handle_incorrect_answer(current_card: Dict[str, Any], user_selected_option_letter: Optional[str]):
    """Handles the logic when an answer is marked incorrect."""
    quiz_data = st.session_state[SS_QUIZ_DATA]
    # Avoid double counting if somehow submitted again (e.g., clicking show answer after submitting)
    if current_card['original_index'] not in quiz_data[QK_USED_QUESTIONS]:
        quiz_data[QK_INCORRECT_COUNT] += 1
        user_answer_text = "No answer"
        if user_selected_option_letter and user_selected_option_letter in current_card['options']:
             user_answer_text = current_card['options'][user_selected_option_letter]

        quiz_data[QK_INCORRECT_QUESTIONS].append({
            'Question': current_card['question'],
            'Correct Answer': current_card['correct_answer_text'],
            'Your Answer': user_answer_text
        })


def handle_submit(current_card_index: int):
    """Handles the answer submission logic."""
    quiz_data = st.session_state[SS_QUIZ_DATA]
    flashcards = st.session_state[SS_FLASHCARDS]
    current_card = flashcards[current_card_index]

    user_selected_option_letter = quiz_data[QK_USER_SELECTED_OPTION]

    is_correct = check_answer(user_selected_option_letter, current_card['correct_option_letter'])

    # --- Store correctness state ---
    quiz_data[QK_LAST_ANSWER_CORRECT] = is_correct
    # --- End store correctness state ---

    if is_correct:
        # Avoid double counting if somehow submitted again
        if current_card['original_index'] not in quiz_data[QK_USED_QUESTIONS]:
            quiz_data[QK_CORRECT_COUNT] += 1
            quiz_data[QK_CORRECT_QUESTIONS].append({
                'Question': current_card['question'],
                'Correct Answer': current_card['correct_answer_text']
            })
    else:
        # Record incorrect only if not already recorded via "Show Answer"
        if current_card['original_index'] not in quiz_data[QK_USED_QUESTIONS]:
            handle_incorrect_answer(current_card, user_selected_option_letter)

    quiz_data[QK_SUBMITTED] = True
    quiz_data[QK_SHOW_ANSWER] = True  # Show answer after submitting
    quiz_data[QK_USED_QUESTIONS].add(current_card['original_index'])  # Mark as used
    st.rerun()  # Update UI to show feedback and potentially Next button


def handle_show_answer(current_card_index: int):
    """Handles the logic when 'Show Answer' is clicked."""
    quiz_data = st.session_state[SS_QUIZ_DATA]
    flashcards = st.session_state[SS_FLASHCARDS]
    current_card = flashcards[current_card_index]

    # --- Set correctness state to False if showing answer before submitting ---
    if current_card['original_index'] not in quiz_data[QK_USED_QUESTIONS]:
         quiz_data[QK_LAST_ANSWER_CORRECT] = False # Showing answer before submitting means it's incorrect
    # --- End set correctness state ---

    st.info(f"**Correct Answer:** {current_card['correct_answer_text']}")
    quiz_data[QK_SHOW_ANSWER] = True
    quiz_data[QK_SHOW_ANSWER_CLICKED] = True

    # If the answer wasn't already submitted/used, mark it as incorrect
    if current_card['original_index'] not in quiz_data[QK_USED_QUESTIONS]:
        user_selected_option_letter = quiz_data[QK_USER_SELECTED_OPTION]
        handle_incorrect_answer(current_card, user_selected_option_letter)
        quiz_data[QK_USED_QUESTIONS].add(current_card['original_index'])  # Mark as used

    # Treat showing answer as a form of submission
    quiz_data[QK_SUBMITTED] = True
    st.rerun()  # Update UI


def handle_next_question():
    """Resets flags to prepare for the next question draw."""
    quiz_data = st.session_state[SS_QUIZ_DATA]
    quiz_data[QK_SHOW_ANSWER] = False
    quiz_data[QK_SUBMITTED] = False
    quiz_data[QK_SHOW_ANSWER_CLICKED] = False
    quiz_data[QK_USER_SELECTED_OPTION] = None # Clear user selection
    quiz_data[QK_CURRENT_OPTIONS_DISPLAY] = None # Clear options display for next question
    quiz_data[QK_LAST_ANSWER_CORRECT] = None # Added: Clear correctness state for next question
    # Remove the stored current index so a new one is picked
    if SS_CURRENT_INDEX in st.session_state:
        del st.session_state[SS_CURRENT_INDEX]
    st.rerun()  # Rerun to draw and display the next question


def display_quiz_results():
    """Displays the final quiz results and review sections."""
    quiz_data = st.session_state[SS_QUIZ_DATA]
    flashcards = st.session_state[SS_FLASHCARDS]
    total_questions = len(flashcards)

    st.subheader("Quiz Completed!")
    st.metric("Total Questions", total_questions)
    st.metric("Correct Answers",
              f"{quiz_data[QK_CORRECT_COUNT]} / {total_questions}")
    st.metric("Incorrect Answers",
              f"{quiz_data[QK_INCORRECT_COUNT]} / {total_questions}")

    # Calculate score
    score = (quiz_data[QK_CORRECT_COUNT] / total_questions) * \
        100 if total_questions > 0 else 0
    st.progress(int(score) / 100.0) # Progress expects value between 0.0 and 1.0
    st.write(f"**Score: {score:.2f}%**")

    if quiz_data[QK_INCORRECT_QUESTIONS]:
        st.subheader("Review Incorrect Questions:")
        incorrect_df = pd.DataFrame(quiz_data[QK_INCORRECT_QUESTIONS])
        st.dataframe(incorrect_df, use_container_width=True)

    if st.button("Restart Quiz"):
        # Pass flashcards from session state to start_quiz
        start_quiz(st.session_state[SS_FLASHCARDS])
        # No need for rerun here, start_quiz handles it

# --- Results Persistence ---


def load_quiz_results() -> List[Dict[str, Any]]:
    """Loads all past quiz results from the CSV file."""
    if os.path.exists(RESULTS_FILE):
        try:
            return pd.read_csv(RESULTS_FILE).to_dict('records')
        except pd.errors.EmptyDataError:
            return []  # File exists but is empty
        except Exception as e:
            st.error(f"Error loading results file: {e}")
            return []
    return []


def save_quiz_results(results: List[Dict[str, Any]]):
    """Saves quiz results to the CSV file."""
    try:
        df = pd.DataFrame(results)
        df.to_csv(RESULTS_FILE, index=False)
    except Exception as e:
        st.error(f"Error saving results file: {e}")


def record_quiz_attempt():
    """Records the just-completed quiz attempt to the results file."""
    quiz_data = st.session_state[SS_QUIZ_DATA]
    flashcards = st.session_state[SS_FLASHCARDS]
    # Get user, default if not set
    user = st.session_state.get(SS_USER, "Unknown")

    if not user or user == "Unknown":
        st.warning("User name not set. Results cannot be saved.")
        return

    results = load_quiz_results()
    timestamp = datetime.datetime.now().isoformat()

    # Format incorrect questions slightly more compactly for the CSV
    incorrect_details = []
    for item in quiz_data[QK_INCORRECT_QUESTIONS]:
        incorrect_details.append(
            f"Q: {item['Question']} | A: {item['Correct Answer']} | Your: {item['Your Answer']}"
        )
    incorrect_questions_str = "; ".join(incorrect_details)

    results.append({
        "Timestamp": timestamp,
        "User": user,
        "Correct Count": quiz_data[QK_CORRECT_COUNT],
        "Incorrect Count": quiz_data[QK_INCORRECT_COUNT],
        "Total Questions": len(flashcards),
        "Incorrect Details": incorrect_questions_str,
    })
    save_quiz_results(results)
    st.success("Quiz results recorded.")


def display_all_quiz_results():
    """Displays all recorded quiz results in a table."""
    results = load_quiz_results()
    if results:
        st.subheader("All Past Quiz Results")
        df = pd.DataFrame(results)
        if "Timestamp" in df.columns:
            try:
                df["Timestamp"] = pd.to_datetime(
                    df["Timestamp"]).dt.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                pass  # Ignore formatting errors
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No past quiz results found.")

# --- Main Application ---

def main():
    st.set_page_config(layout="wide")
    st.title("🏛️ Multiple Choice Quiz App") # Updated title

    # --- User Identification ---
    st.sidebar.header("User")
    if SS_USER not in st.session_state:
        st.session_state[SS_USER] = ""  # Initialize user state

    user_name = st.sidebar.text_input(
        "Enter your name to save results:", value=st.session_state[SS_USER], key="user_name_input")
    if user_name:
        st.session_state[SS_USER] = user_name
        st.sidebar.success(f"Current User: {st.session_state[SS_USER]}")
    else:
        st.sidebar.warning("Enter your name to track results.")

    # --- Instructions Expander (Moved to Sidebar) ---
    with st.sidebar.expander("ℹ️ How to Use This App", expanded=False):  # Start collapsed
        st.markdown(
            f"""
            **Welcome to the Multiple Choice Quiz App!**

            1.  **Enter Your Name:** Enter your name under "User" above. This is needed to save your quiz results.
            2.  **Upload Your Quiz File:**
                *   Under "Load Quiz File" below, click "Browse files".
                *   Select a **CSV** or **XLSX** (Excel) file.
                *   **File Structure (by column position):**
                    *   Your file **must** contain at least 6 columns.
                    *   The **1st column** should contain the **Question** text.
                    *   The **2nd, 3rd, 4th, and 5th columns** should contain the text for **Option A, B, C, and D** respectively.
                    *   The **6th column** should contain the **Correct Answer Letter** ('A', 'B', 'C', or 'D'). Quotation marks around the letter are ignored.
                    *   The **very first row** of your file should contain **headers** (these are ignored, only the position matters).
                    *   Any columns beyond the 6th will be ignored.
            3.  **Start the Quiz:** Once the quiz file is loaded, click the "**🚀 Start Quiz**" button in the main area (right side).
            4.  **Answer Questions:**
                *   Read the question displayed in the main area.
                *   Select your answer from the multiple-choice options.
                *   Click "**✅ Submit Answer**". You'll get immediate feedback (Correct/Incorrect).
                *   *(Optional)*: Click "**💡 Show Answer**" if you're stuck (this will mark the question as incorrect if you haven't submitted yet).
            5.  **Continue:** After submitting or showing the answer, the main button changes to "**➡️ Next Question**". Click it to proceed.
            6.  **Restarting:**
                *   **During Quiz:** Use the "**🔁 Restart Quiz Now**" button under "Quiz Controls" below to start over with the same quiz questions at any time.
                *   **After Quiz:** Once finished, a "**Restart Quiz**" button appears below the results in the main area.
            7.  **View Results:**
                *   Your final score and a review of incorrect/correct answers appear automatically when the quiz ends in the main area.
                *   To see a history of all past attempts, click "**Show All Past Results**" under "History" below.

            **Good luck!** ✨
            """
        )

    # --- File Upload ---
    st.sidebar.header("Load Quiz File")
    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV or XLSX file",
        type=["csv", "xlsx", "xls"],
        help="Select a CSV or Excel file with at least 6 columns: Question (1st), Options A-D (2nd-5th), Correct Answer Letter (6th). Headers are ignored."
    )

    # --- Handle File Upload/Removal ---
    if uploaded_file is not None:
        current_file_name = uploaded_file.name
        previous_file_name = st.session_state.get(SS_LOADED_FILE_NAME, None)

        # Check if a new file is uploaded or if flashcards are not loaded yet
        if SS_FLASHCARDS not in st.session_state or current_file_name != previous_file_name:
            st.sidebar.info(f"Loading {current_file_name}...")
            quiz_data_loaded = load_quiz_data_from_file(uploaded_file)

            if quiz_data_loaded:
                st.session_state[SS_FLASHCARDS] = quiz_data_loaded
                st.session_state[SS_LOADED_FILE_NAME] = current_file_name
                st.sidebar.success(f"Loaded {len(quiz_data_loaded)} quiz questions from {current_file_name}.")
                # Reset quiz state when a new file is loaded successfully
                st.session_state[SS_QUIZ_DATA] = _get_default_quiz_state()
                st.session_state[SS_QUIZ_DATA][QK_STARTED] = False
                if SS_CURRENT_INDEX in st.session_state:
                    del st.session_state[SS_CURRENT_INDEX]
                st.rerun() # Rerun to update the UI after loading
            else:
                # Clear state if loading failed
                if SS_FLASHCARDS in st.session_state:
                    del st.session_state[SS_FLASHCARDS]
                if SS_LOADED_FILE_NAME in st.session_state:
                    del st.session_state[SS_LOADED_FILE_NAME]
                if SS_QUIZ_DATA in st.session_state:
                    del st.session_state[SS_QUIZ_DATA]
                if SS_CURRENT_INDEX in st.session_state:
                    del st.session_state[SS_CURRENT_INDEX]
                # Error message is shown inside load_quiz_data_from_file
                # st.rerun() # Rerun to clear UI if needed, but error message might be enough

    # Handle case where file is removed
    elif SS_FLASHCARDS in st.session_state:
        st.sidebar.info("File removed. Clearing quiz data.")
        del st.session_state[SS_FLASHCARDS]
        if SS_LOADED_FILE_NAME in st.session_state:
            del st.session_state[SS_LOADED_FILE_NAME]
        if SS_QUIZ_DATA in st.session_state:
            del st.session_state[SS_QUIZ_DATA]
        if SS_CURRENT_INDEX in st.session_state:
            del st.session_state[SS_CURRENT_INDEX]
        st.rerun()


    # --- Process Quiz State ---
    if SS_FLASHCARDS in st.session_state:
        flashcards = st.session_state[SS_FLASHCARDS]

        # Ensure quiz_data is initialized if flashcards are present but quiz_data is not
        if SS_QUIZ_DATA not in st.session_state:
            st.session_state[SS_QUIZ_DATA] = _get_default_quiz_state()
            st.session_state[SS_QUIZ_DATA][QK_STARTED] = False

        quiz_data = st.session_state[SS_QUIZ_DATA]

        # --- Sidebar Controls (Restart Button) ---
        st.sidebar.header("Quiz Controls")
        if quiz_data.get(QK_STARTED, False):
            all_indices_set = set(range(len(flashcards)))
            used_indices_set: Set[int] = quiz_data.get(
                QK_USED_QUESTIONS, set())
            is_finished = not (all_indices_set - used_indices_set)
            if not is_finished:
                if st.sidebar.button("🔁 Restart Quiz Now",
                                     key="restart_quiz_sidebar",
                                     help="Stop the current quiz and start over with the same quiz questions."):
                    start_quiz(st.session_state[SS_FLASHCARDS])
            else:
                st.sidebar.info("Quiz finished. See results in the main area.")


        # --- Main Area: Start Button or Quiz Display ---
        if not quiz_data.get(QK_STARTED, False):
            # Display file name if loaded
            if SS_LOADED_FILE_NAME in st.session_state:
                 st.info(f"Quiz data loaded from **{st.session_state[SS_LOADED_FILE_NAME]}**. Press 'Start Quiz' to begin.")
                 if st.button("🚀 Start Quiz", type="primary"):
                    start_quiz(st.session_state[SS_FLASHCARDS])
            else:
                 st.info("Please upload a quiz file (CSV or XLSX) using the sidebar to begin.")


        elif quiz_data.get(QK_STARTED, False):
            # --- Active Quiz Logic ---
            all_indices = set(range(len(flashcards)))
            used_indices: Set[int] = quiz_data[QK_USED_QUESTIONS]
            available_indices = list(all_indices - used_indices)

            if not available_indices:
                # --- Quiz Completion Display ---
                display_quiz_results()
                if 'results_recorded' not in quiz_data:
                    record_quiz_attempt()
                    quiz_data['results_recorded'] = True
            else:
                # --- Get or Select Current Question Index ---
                if SS_CURRENT_INDEX not in st.session_state:
                    st.session_state[SS_CURRENT_INDEX] = random.choice(
                        available_indices)
                    # Clear state for the new question
                    quiz_data[QK_CURRENT_OPTIONS_DISPLAY] = None
                    quiz_data[QK_USER_SELECTED_OPTION] = None
                    quiz_data[QK_LAST_ANSWER_CORRECT] = None # Added: Clear correctness state for new question


                current_card_index = st.session_state[SS_CURRENT_INDEX]
                current_card = flashcards[current_card_index]

                # --- Display Question UI ---
                # Display question and get user selection (letter A, B, C, D or None)
                user_selected_option_letter = display_question(
                    current_card, f"q_{current_card_index}")

                # Update session state with the user's selection
                quiz_data[QK_USER_SELECTED_OPTION] = user_selected_option_letter

                st.write("---")  # Separator

                # --- Action Buttons (Toggle Logic) ---
                submitted = quiz_data[QK_SUBMITTED]
                show_answer_clicked = quiz_data[QK_SHOW_ANSWER_CLICKED]
                action_button_key = f"action_button_{current_card_index}"

                if submitted or show_answer_clicked:
                    # --- Display Feedback Persistently ---
                    # Display Correct/Incorrect feedback
                    if quiz_data.get(QK_LAST_ANSWER_CORRECT) is True:
                        st.success("Correct!")
                    elif quiz_data.get(QK_LAST_ANSWER_CORRECT) is False:
                        st.error("Incorrect.")

                    # Ensure the answer text is shown
                    if quiz_data[QK_SHOW_ANSWER]:
                        correct_answer_text = current_card['correct_answer_text']
                        st.info(f"**Correct Answer:** {correct_answer_text}")

                    # Display Next Question button
                    if st.button("➡️ Next Question", key=action_button_key):
                        handle_next_question()
                else:
                    # Display Submit and Show Answer buttons
                    col_submit, col_show = st.columns(2)
                    with col_submit:
                        submit_disabled = user_selected_option_letter is None
                        if st.button("✅ Submit Answer", key=action_button_key, disabled=submit_disabled, type="primary"):
                            handle_submit(current_card_index)
                    with col_show:
                        show_answer_key = f"show_answer_{current_card_index}"
                        if st.button("💡 Show Answer",
                                     key=show_answer_key,
                                     help="Reveal the correct answer. Counts as incorrect if used before submitting."):
                            handle_show_answer(current_card_index)

                st.write("---")
                # --- Progress Indicators ---
                remaining_count = len(available_indices)
                st.write(f"**Remaining Questions:** {remaining_count}")
                st.write(
                    f"**Correct:** {quiz_data[QK_CORRECT_COUNT]} | **Incorrect:** {quiz_data[QK_INCORRECT_COUNT]}")

    else:
        # No flashcards loaded state (initial state or after file removal)
        st.info("Please upload a quiz file (CSV or XLSX) using the sidebar to begin.")


    # --- Display All Results Area ---
    st.sidebar.header("History")
    if st.sidebar.button("Show All Past Results"):
        display_all_quiz_results()


if __name__ == "__main__":
    main()