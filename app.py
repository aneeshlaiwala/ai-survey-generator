import streamlit as st
import openai

# Title
st.title("AI Survey Questionnaire Generator with Auto Survey Generation")

# API Key Input
st.sidebar.header("API Settings")
api_key = st.sidebar.text_input("Enter your OpenAI API Key:", type="password")

# Survey Planning Inputs
st.header("Survey Planning Inputs")
survey_objective = st.text_area("Survey Objective (exploratory, predictive, segmentation, etc.)")
target_audience = st.text_input("Target Audience")
population_size = st.number_input("Population Size", min_value=0, value=1000)
survey_loi = st.number_input("Survey Length (LOI) in Minutes", min_value=1, value=10)
methodology = st.selectbox("Survey Methodology", ["Online", "Phone", "Face-to-Face", "Mobile App"])
device_context = st.selectbox("Device Context", ["Desktop", "Mobile", "Mixed"])
preferred_tone = st.selectbox("Preferred Tone", ["Formal", "Casual", "Technical"])

# Statistical Analysis Methods
statistical_methods = st.multiselect("Required Statistical Analysis Methods", [
    "Regression", "Conjoint", "Cluster Analysis", "MaxDiff", "Factor Analysis", "TURF Analysis",
    "Discriminant Analysis", "Correspondence Analysis", "Latent Class Analysis", "SEM",
    "CHAID", "Survival Analysis"
])

# Allowed Question Types
allowed_question_types = st.multiselect("Allowed Question Types", ["Likert", "Open-End", "Rating Scale", "Matrix/Grid", "Dichotomous", "Dropdown", "Ranking", "Image Choice", "Slider"])

# Compliance Requirements
compliance_requirements = st.multiselect("Compliance Requirements", ["GDPR", "CCPA", "Other"])

# Market/Country
market_country = st.text_input("Market (Country)")

# Generate Prompt Button
if st.button("Generate AI Survey Prompt and Questionnaire"):
    # Calculate Estimated Question Count based on LOI
    min_questions = int(survey_loi * 3)
    max_questions = int(survey_loi * 5)

    prompt = f"""
You are an expert AI survey designer. Your task is to create a high-quality, professional survey questionnaire, fully optimized for research validity, ethical compliance, and advanced analytics.

Survey Objective: {survey_objective}
Target Audience: {target_audience}
Population Size: {population_size}
Survey Length (LOI): {survey_loi} minutes
Survey Methodology: {methodology}
Device Context: {device_context}
Preferred Tone: {preferred_tone}
Required Statistical Analysis Methods: {', '.join(statistical_methods)}
Allowed Question Types: {', '.join(allowed_question_types)}
Compliance Requirements: {', '.join(compliance_requirements)}
Market/Country: {market_country}

**IMPORTANT:**
- For all brand-related or attribute-based questions, use only the latest, relevant brands and attributes for the specified market: {market_country}.
- Auto-research current brands or attributes; if uncertain, flag for manual validation.

**Estimated Question Count Guidance:**
Based on the target LOI of {survey_loi} minutes, recommend between {min_questions} and {max_questions} questions.
Distribute approximately:
- 5-10% for Screener questions
- 60-70% for Core Research questions
- 10-15% for Rating/Scale/Attitudinal questions
- 5-10% for Open-Ends and Demographics

Generate a section-by-section questionnaire with:
- Logic/Flow Notes (Skip Logic, Piping, Randomization)
- Fraud Checks
- Sampling Guidance
- Localization considerations for {market_country}
- Survey Launch Checklist

**For EACH Question Generated:**
Include:
1. Recommended Statistical Analysis Methods (basic and advanced).
2. Fraud Detection Flag (Yes/No) with specific post-survey review steps.
3. Analysis Tips (e.g., cross-tabulation, segmentation uses, driver analysis potential).

**Excel Toolkit Reference:**
Refer to the AI Survey Toolkit available at:
https://github.com/your-username/ai-survey-generator/blob/main/docs/AI_Survey_Generation_Template.xlsx

Reference the AI Survey Toolkit Excel document for additional details on question types, statistical methods, fraud checks, and launch guidelines.
"""

    st.subheader("Generated AI Survey Prompt")
    st.code(prompt, language='markdown')

    if api_key:
        openai.api_key = api_key
        with st.spinner("Generating full survey questionnaire from OpenAI..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert survey researcher."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5,
                    max_tokens=4096
                )
                questionnaire = response.choices[0].message.content
                st.subheader("Generated Survey Questionnaire")
                st.text_area("Survey Questionnaire", questionnaire, height=500)
                st.download_button("Download Questionnaire as Text File", questionnaire, file_name="survey_questionnaire.txt")
            except Exception as e:
                st.error(f"Error generating questionnaire: {str(e)}")
    else:
        st.warning("Please enter your OpenAI API key in the sidebar to auto-generate the questionnaire.")
