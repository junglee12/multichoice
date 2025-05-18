# 🏛️ Multiple Choice Quiz App

A Streamlit web application that allows users to take multiple-choice quizzes by uploading their own quiz data from CSV or Excel files. It provides immediate feedback, tracks scores, and saves quiz attempt history.

## Features

*   **Upload Quiz Data:** Load quiz questions from user-provided CSV or XLSX files.
*   **Interactive Quiz Interface:** Presents questions one by one with multiple-choice options.
*   **Immediate Feedback:** Shows whether the submitted answer is correct or incorrect.
*   **"Show Answer" Option:** Allows users to see the correct answer (counts as incorrect if used before submitting).
*   **Progress Tracking:** Displays the number of remaining questions, correct answers, and incorrect answers.
*   **Results Summary:** At the end of the quiz, shows the final score, a summary of performance, and a review of incorrectly answered questions.
*   **Persistent Results:** Saves quiz attempts (timestamp, user, score, incorrect details) to a local CSV file (`quiz_results_uploaded_mc.csv`).
*   **User Identification:** Allows users to enter their name for personalized result tracking.
*   **History Viewing:** Users can view a history of all past quiz attempts.
*   **Restart Functionality:** Option to restart the current quiz or start over after completion.
*   **In-App Instructions:** Provides guidance on how to use the application and the required file format.

## Requirements

*   Python 3.7+
*   Streamlit
*   Pandas
*   openpyxl (for reading `.xlsx` files)

## Setup and Running

1.  **Clone the repository or save `app.py`:**
    Ensure you have the `app.py` file in a directory on your local machine, for example, `/home/j/Downloads/dev/multipleChoiceQuiz/`.

2.  **Install dependencies:**
    It's recommended to use a virtual environment.
    ```bash
    pip install streamlit pandas openpyxl
    ```
    Alternatively, you can create a `requirements.txt` file with the following content:
    ```
    streamlit
    pandas
    openpyxl
    ```
    And then install using:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    Navigate to the directory containing `app.py` in your terminal and run:
    ```bash
    streamlit run /home/j/Downloads/dev/multipleChoiceQuiz/app.py
    ```
    The application will open in your web browser.

## Usage Instructions

1.  **Prepare Your Quiz File:**
    *   Create a CSV (`.csv`) or Excel (`.xlsx`, `.xls`) file.
    *   The file must adhere to the "Quiz File Format" detailed below.

2.  **Launch the App:**
    *   Run `streamlit run /home/j/Downloads/dev/multipleChoiceQuiz/app.py` in your terminal.

3.  **Enter Your Name (Recommended):**
    *   In the sidebar under "User", enter your name. This is used to save and identify your quiz results.

4.  **Upload Quiz File:**
    *   In the sidebar under "Load Quiz File," click "Browse files."
    *   Select your prepared quiz file.
    *   The app will confirm if the file is loaded successfully and show the number of questions found.

5.  **Start the Quiz:**
    *   Once the file is loaded, a "🚀 Start Quiz" button will appear in the main area. Click it to begin.

6.  **Answer Questions:**
    *   The current question and its multiple-choice options (A, B, C, D) will be displayed.
    *   Select your answer by clicking on the radio button next to your choice.
    *   Click the "✅ Submit Answer" button.
    *   You will receive immediate feedback (Correct/Incorrect). The correct answer will also be shown.
    *   If you are unsure, you can click "💡 Show Answer." This will reveal the correct answer but will mark the question as incorrect if you haven't submitted an answer yet.

7.  **Navigate:**
    *   After submitting or showing the answer, click the "➡️ Next Question" button to proceed.

8.  **View Results:**
    *   When all questions have been answered, the quiz ends.
    *   Your final score, total correct/incorrect answers, and a table reviewing any questions you answered incorrectly will be displayed.
    *   If you entered your name, your quiz attempt will be automatically recorded.

9.  **Restarting the Quiz:**
    *   **During the quiz:** Click "🔁 Restart Quiz Now" in the "Quiz Controls" section of the sidebar to start over with the same set of questions.
    *   **After completing the quiz:** A "Restart Quiz" button will appear below your results in the main area.

10. **View Past Results:**
    *   In the sidebar under "History," click "Show All Past Results" to see a table of all previously recorded quiz attempts.

## Quiz File Format

The application expects your quiz data in a CSV or Excel file with a specific structure based on column position. The **first row is assumed to be headers and is ignored**; data parsing begins from the second row.

*   **Column 1 (Index 0):** Question Text
*   **Column 2 (Index 1):** Option A Text
*   **Column 3 (Index 2):** Option B Text
*   **Column 4 (Index 3):** Option C Text
*   **Column 5 (Index 4):** Option D Text
*   **Column 6 (Index 5):** Correct Answer Letter (e.g., 'A', 'B', 'C', or 'D').
    *   The letter should correspond to one of the options.
    *   Leading/trailing single or double quotation marks around the letter (e.g., `"A"` or `'B'`) are automatically removed.

*Any columns beyond the 6th will be ignored.*

**Example (CSV format):**
```csv
Question,OptionA,OptionB,OptionC,OptionD,CorrectAnswerLetter
What is the capital of France?,"Rome","Paris","Berlin","Madrid",B
Which number is largest?,10,100,1,1000,D
"What is H2O?","Oxygen","Water","Hydrogen","Air","B"
```

## Results File

Quiz attempts are saved to a CSV file named `quiz_results_uploaded_mc.csv`. This file is created in the same directory where `app.py` is located. It stores:
*   `Timestamp`: Date and time of the quiz attempt.
*   `User`: Name of the user who took the quiz.
*   `Correct Count`: Number of correctly answered questions.
*   `Incorrect Count`: Number of incorrectly answered questions.
*   `Total Questions`: Total number of questions in the quiz.
*   `Incorrect Details`: A summary of the questions answered incorrectly, including the question, correct answer, and the user's answer.