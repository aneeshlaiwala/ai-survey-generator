
# AI Survey Questionnaire Generator (Streamlit App)

This is a Streamlit-based AI agent that generates survey questionnaire prompts using advanced guidelines for survey design, fraud detection, response logic, statistical analysis, sample size estimation, and localization.

## Features:
- Auto-generates detailed survey design prompts.
- Calculates estimated number of questions based on LOI (Length of Interview).
- Includes market/country-specific brand and attribute localization.
- Suggests statistical analysis methods and fraud checks for each question.
- Downloads prompts as text files for AI tools like ChatGPT, Claude, etc.

## Inputs:
- Survey Objective
- Target Audience
- Population Size
- Survey Length (LOI)
- Methodology
- Device Context
- Preferred Tone
- Statistical Analysis Methods
- Allowed Question Types
- Compliance Requirements
- Market (Country)

## How to Run Locally:
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   streamlit run app.py
   ```

## Deployment on Streamlit Cloud:
1. Push this repo to GitHub.
2. Connect your GitHub repo in [Streamlit Cloud](https://streamlit.io/cloud).
3. Deploy the app (Streamlit Cloud auto-installs dependencies from `requirements.txt`).

## Excel Toolkit Usage:
- Your survey design references an external Excel Toolkit for detailed guidance on question types, fraud checks, statistical methods, etc.
- You can store your Excel file in a `/docs/` folder or any internal documentation system.
- Researchers should refer to this toolkit manually when building surveys.

Enjoy creating powerful AI-powered survey questionnaires!
