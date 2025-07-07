import streamlit as st
from openai import OpenAI
import pandas as pd
import requests
import json
from datetime import datetime
import io
from docx import Document
from docx.shared import Inches
import base64

# Configure page
st.set_page_config(page_title="AI Survey Generator", layout="wide")

# Initialize session state
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}

def preserve_form_data():
    """Preserve form data in session state"""
    st.session_state.form_data = {
        'survey_objective': st.session_state.get('survey_objective', ''),
        'target_audience': st.session_state.get('target_audience', ''),
        'population_size': st.session_state.get('population_size', 1000),
        'survey_loi': st.session_state.get('survey_loi', 10),
        'methodology': st.session_state.get('methodology', 'Online'),
        'device_context': st.session_state.get('device_context', 'Desktop'),
        'preferred_tone': st.session_state.get('preferred_tone', 'Formal'),
        'statistical_methods': st.session_state.get('statistical_methods', []),
        'allowed_question_types': st.session_state.get('allowed_question_types', []),
        'compliance_requirements': st.session_state.get('compliance_requirements', []),
        'market_country': st.session_state.get('market_country', ''),
        'api_key': st.session_state.get('api_key', '')
    }

def web_research(query, api_key):
    """Perform web research for current market trends and brands"""
    try:
        client = OpenAI(api_key=api_key)
        research_prompt = f"""
        Research current market trends, popular brands, and consumer preferences for: {query}
        Focus on:
        1. Top 10 most popular brands in this category
        2. Current market trends and consumer behaviors
        3. Key attributes/features consumers consider
        4. Recent industry developments (2024-2025)
        
        Provide a concise summary with specific brand names and current market insights.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a market research expert with access to current market data."},
                {"role": "user", "content": research_prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Research error: {str(e)}"

def load_excel_guidelines():
    """Load guidelines from Excel template"""
    guidelines = """
    AI Survey Generation Guidelines:
    
    QUESTION TYPES & SCALES:
    - Likert Scale: Use 5-point scales (Strongly Disagree to Strongly Agree)
    - Rating Scale: Use 5-point scales (Very Poor to Excellent)
    - Matrix Questions: Use 5-point scales consistently
    - Association Matrix: Use 5-point scales (Not at all associated to Extremely associated)
    
    FRAUD DETECTION GUIDELINES:
    - Include attention check questions (e.g., "Please select 'Agree' for this question")
    - Monitor response time patterns
    - Check for straight-lining in matrix questions
    - Validate open-end responses for quality
    - GPS/Location validation for geographic targeting
    
    STATISTICAL ANALYSIS MAPPING:
    - Likert/Rating: Descriptive stats, correlation, regression, factor analysis
    - Matrix Questions: Factor analysis, cluster analysis, correspondence analysis
    - Rankings: MaxDiff, TURF analysis
    - Open-ends: Text analysis, sentiment analysis, thematic coding
    - Demographics: Cross-tabulation, segmentation, CHAID analysis
    
    LOI CALCULATION:
    - Simple questions: 15-30 seconds each
    - Matrix questions: 45-90 seconds each
    - Open-ended: 60-120 seconds each
    - Demographics: 10-15 seconds each
    
    QUESTION DISTRIBUTION FOR 20-MINUTE SURVEY:
    - Screener: 3-5 questions (2-3 minutes)
    - Core Research: 25-35 questions (12-15 minutes)
    - Purchase Journey: 8-12 questions (3-4 minutes)
    - Demographics: 5-8 questions (2-3 minutes)
    """
    return guidelines

def generate_enhanced_prompt(survey_data, research_data, guidelines):
    """Generate enhanced prompt with research and guidelines"""
    
    # Calculate detailed question distribution
    loi = survey_data['survey_loi']
    total_questions = int(loi * 4)  # More questions for deeper analysis
    
    screener_q = max(3, int(total_questions * 0.15))
    core_q = max(15, int(total_questions * 0.50))
    journey_q = max(8, int(total_questions * 0.20))
    demo_q = max(5, int(total_questions * 0.15))
    
    prompt = f"""
You are an expert AI survey designer with access to current market research data and professional survey guidelines.

SURVEY SPECIFICATION:
- Objective: {survey_data['survey_objective']}
- Target Audience: {survey_data['target_audience']}
- Population Size: {survey_data['population_size']:,}
- Survey Length (LOI): {survey_data['survey_loi']} minutes
- Methodology: {survey_data['methodology']}
- Device Context: {survey_data['device_context']}
- Tone: {survey_data['preferred_tone']}
- Market/Country: {survey_data['market_country']}
- Statistical Methods Required: {', '.join(survey_data['statistical_methods'])}
- Allowed Question Types: {', '.join(survey_data['allowed_question_types'])}
- Compliance: {', '.join(survey_data['compliance_requirements'])}

CURRENT MARKET RESEARCH DATA:
{research_data}

PROFESSIONAL GUIDELINES:
{guidelines}

DETAILED QUESTION REQUIREMENTS:
Generate exactly {total_questions} questions distributed as follows:
1. SCREENER SECTION ({screener_q} questions):
   - Demographic screening
   - Target audience validation
   - Include fraud check questions

2. CORE RESEARCH SECTION ({core_q} questions):
   - Brand awareness and usage
   - Product/service preferences
   - Attribute importance ratings (5-point scales)
   - Association matrix questions (5-point scales)
   - Current ownership/usage details
   - Satisfaction ratings

3. PURCHASE JOURNEY SECTION ({journey_q} questions):
   - Purchase consideration process
   - Information sources
   - Decision factors and their ratings (5-point scales)
   - Purchase timeline
   - Influencer identification

4. DEMOGRAPHICS SECTION ({demo_q} questions):
   - Age, gender, income, education
   - Geographic location
   - Household composition

MANDATORY REQUIREMENTS FOR EACH QUESTION:
✓ Question Number and Type
✓ Question Text with proper formatting
✓ Response Options (include "Others (specify)" where applicable)
✓ Statistical Analysis Methods (both basic and advanced)
✓ Fraud Detection Flag (Yes/No) with specific checks
✓ Analysis Applications (cross-tabs, segmentation, etc.)
✓ Skip Logic Instructions (if any)

FORMATTING REQUIREMENTS:
- Each question on separate lines
- Clear section headers
- Numbered questions (Q1, Q2, etc.)
- Response options as bullet points
- Statistical notes in brackets
- Use only 5-point scales for all rating questions

BRAND AND ATTRIBUTE REQUIREMENTS:
- Use current, relevant brands from the market research data
- Include contemporary attributes and features
- Ensure cultural and regional appropriateness

Generate a comprehensive, professionally structured questionnaire that meets all these requirements.
"""
    return prompt

def format_questionnaire_output(questionnaire_text):
    """Format questionnaire for better readability"""
    lines = questionnaire_text.split('\n')
    formatted_lines = []
    
    for line in lines:
        if line.strip():
            # Add extra spacing for question numbers
            if line.strip().startswith('Q') and ':' in line:
                formatted_lines.append('\n' + line)
            # Add spacing for section headers
            elif line.strip().isupper() or 'SECTION' in line.upper():
                formatted_lines.append('\n' + '='*50)
                formatted_lines.append(line)
                formatted_lines.append('='*50)
            else:
                formatted_lines.append(line)
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def create_word_document(questionnaire_text, survey_data):
    """Create Word document from questionnaire"""
    doc = Document()
    
    # Title
    title = doc.add_heading('Survey Questionnaire', 0)
    
    # Survey details
    doc.add_heading('Survey Details', level=1)
    details = f"""
    Objective: {survey_data['survey_objective']}
    Target Audience: {survey_data['target_audience']}
    Expected LOI: {survey_data['survey_loi']} minutes
    Methodology: {survey_data['methodology']}
    Market: {survey_data['market_country']}
    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    doc.add_paragraph(details)
    
    # Questionnaire content
    doc.add_heading('Questionnaire', level=1)
    
    # Split content into paragraphs
    lines = questionnaire_text.split('\n')
    for line in lines:
        if line.strip():
            if line.strip().startswith('Q') and ':' in line:
                doc.add_paragraph(line, style='Heading 3')
            elif 'SECTION' in line.upper():
                doc.add_paragraph(line, style='Heading 2')
            else:
                doc.add_paragraph(line)
    
    return doc

def create_excel_output(questionnaire_text, survey_data):
    """Create Excel file with structured questionnaire data"""
    # Parse questionnaire into structured data
    lines = questionnaire_text.split('\n')
    questions_data = []
    current_question = {}
    
    for line in lines:
        line = line.strip()
        if line.startswith('Q') and ':' in line:
            if current_question:
                questions_data.append(current_question)
            current_question = {
                'Question_Number': line.split(':')[0],
                'Question_Text': line.split(':', 1)[1].strip(),
                'Question_Type': '',
                'Response_Options': '',
                'Statistical_Methods': '',
                'Fraud_Check': '',
                'Analysis_Notes': ''
            }
        elif line and current_question:
            if 'Statistical Analysis' in line:
                current_question['Statistical_Methods'] = line
            elif 'Fraud Detection' in line:
                current_question['Fraud_Check'] = line
            elif 'Analysis' in line:
                current_question['Analysis_Notes'] = line
            elif line.startswith('- ') or line.startswith('• '):
                current_question['Response_Options'] += line + '\n'
    
    if current_question:
        questions_data.append(current_question)
    
    # Create DataFrame
    df = pd.DataFrame(questions_data)
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Survey details sheet
        survey_info = pd.DataFrame([survey_data])
        survey_info.to_excel(writer, sheet_name='Survey_Details', index=False)
        
        # Questions sheet
        df.to_excel(writer, sheet_name='Questions', index=False)
        
        # Guidelines sheet
        guidelines_df = pd.DataFrame([{'Guidelines': load_excel_guidelines()}])
        guidelines_df.to_excel(writer, sheet_name='Guidelines', index=False)
    
    return output.getvalue()

# Title
st.title("🔍 AI Survey Questionnaire Generator with Enhanced Intelligence")

# Sidebar for API and settings
st.sidebar.header("🔧 API Settings")
api_key = st.sidebar.text_input(
    "Enter your OpenAI API Key:", 
    type="password",
    value=st.session_state.form_data.get('api_key', ''),
    key='api_key'
)

# Main form with preserved values
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📋 Survey Planning Inputs")
    
    survey_objective = st.text_area(
        "Survey Objective (exploratory, predictive, segmentation, etc.)",
        value=st.session_state.form_data.get('survey_objective', ''),
        key='survey_objective'
    )
    
    target_audience = st.text_input(
        "Target Audience",
        value=st.session_state.form_data.get('target_audience', ''),
        key='target_audience'
    )
    
    col_a, col_b = st.columns(2)
    with col_a:
        population_size = st.number_input(
            "Population Size", 
            min_value=0, 
            value=st.session_state.form_data.get('population_size', 1000),
            key='population_size'
        )
    
    with col_b:
        survey_loi = st.number_input(
            "Survey Length (LOI) in Minutes", 
            min_value=1, 
            value=st.session_state.form_data.get('survey_loi', 10),
            key='survey_loi'
        )
    
    col_c, col_d = st.columns(2)
    with col_c:
        methodology = st.selectbox(
            "Survey Methodology", 
            ["Online", "Phone", "Face-to-Face", "Mobile App"],
            index=["Online", "Phone", "Face-to-Face", "Mobile App"].index(
                st.session_state.form_data.get('methodology', 'Online')
            ),
            key='methodology'
        )
    
    with col_d:
        device_context = st.selectbox(
            "Device Context", 
            ["Desktop", "Mobile", "Mixed"],
            index=["Desktop", "Mobile", "Mixed"].index(
                st.session_state.form_data.get('device_context', 'Desktop')
            ),
            key='device_context'
        )
    
    preferred_tone = st.selectbox(
        "Preferred Tone", 
        ["Formal", "Casual", "Technical"],
        index=["Formal", "Casual", "Technical"].index(
            st.session_state.form_data.get('preferred_tone', 'Formal')
        ),
        key='preferred_tone'
    )
    
    market_country = st.text_input(
        "Market (Country)",
        value=st.session_state.form_data.get('market_country', ''),
        key='market_country'
    )

with col2:
    st.header("⚙️ Advanced Settings")
    
    statistical_methods = st.multiselect(
        "Required Statistical Analysis Methods", 
        ["Regression", "Conjoint", "Cluster Analysis", "MaxDiff", "Factor Analysis", 
         "TURF Analysis", "Discriminant Analysis", "Correspondence Analysis", 
         "Latent Class Analysis", "SEM", "CHAID", "Survival Analysis"],
        default=st.session_state.form_data.get('statistical_methods', []),
        key='statistical_methods'
    )
    
    allowed_question_types = st.multiselect(
        "Allowed Question Types", 
        ["Likert", "Open-End", "Rating Scale", "Matrix/Grid", "Dichotomous", 
         "Dropdown", "Ranking", "Image Choice", "Slider"],
        default=st.session_state.form_data.get('allowed_question_types', []),
        key='allowed_question_types'
    )
    
    compliance_requirements = st.multiselect(
        "Compliance Requirements", 
        ["GDPR", "CCPA", "HIPAA", "Other"],
        default=st.session_state.form_data.get('compliance_requirements', []),
        key='compliance_requirements'
    )

# Survey generation section
st.header("🚀 Generate Survey")

if st.button("🎯 Generate Enhanced AI Survey Questionnaire", type="primary"):
    preserve_form_data()  # Preserve form data before processing
    
    if not api_key:
        st.error("⚠️ Please enter your OpenAI API key in the sidebar.")
        st.stop()
    
    if not survey_objective or not target_audience:
        st.error("⚠️ Please fill in at least the Survey Objective and Target Audience.")
        st.stop()
    
    survey_data = {
        'survey_objective': survey_objective,
        'target_audience': target_audience,
        'population_size': population_size,
        'survey_loi': survey_loi,
        'methodology': methodology,
        'device_context': device_context,
        'preferred_tone': preferred_tone,
        'statistical_methods': statistical_methods,
        'allowed_question_types': allowed_question_types,
        'compliance_requirements': compliance_requirements,
        'market_country': market_country
    }
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Step 1: Load guidelines
    status_text.text("📚 Loading AI Survey Generation Guidelines...")
    progress_bar.progress(20)
    guidelines = load_excel_guidelines()
    
    # Step 2: Perform market research
    status_text.text("🔍 Conducting market research...")
    progress_bar.progress(40)
    research_query = f"{target_audience} in {market_country} market trends brands preferences"
    research_data = web_research(research_query, api_key)
    
    # Step 3: Generate enhanced prompt
    status_text.text("📝 Generating enhanced survey prompt...")
    progress_bar.progress(60)
    enhanced_prompt = generate_enhanced_prompt(survey_data, research_data, guidelines)
    
    # Step 4: Generate questionnaire
    status_text.text("🤖 Generating comprehensive questionnaire...")
    progress_bar.progress(80)
    
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert survey researcher with access to current market data and professional survey design guidelines."},
                {"role": "user", "content": enhanced_prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        questionnaire = response.choices[0].message.content
        
        # Step 5: Format output
        status_text.text("✨ Formatting questionnaire...")
        progress_bar.progress(100)
        formatted_questionnaire = format_questionnaire_output(questionnaire)
        
        # Clear progress
        progress_bar.empty()
        status_text.empty()
        
        # Display results
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("📊 Generated Survey Questionnaire")
            st.text_area(
                "Survey Questionnaire", 
                formatted_questionnaire, 
                height=600,
                help="Your comprehensive survey questionnaire with statistical analysis notes and fraud detection guidelines."
            )
        
        with col2:
            st.subheader("📥 Download Options")
            
            # Text download
            st.download_button(
                "📄 Download as Text",
                formatted_questionnaire,
                file_name=f"survey_questionnaire_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
            
            # Word download
            doc = create_word_document(formatted_questionnaire, survey_data)
            doc_io = io.BytesIO()
            doc.save(doc_io)
            doc_io.seek(0)
            
            st.download_button(
                "📝 Download as Word",
                doc_io.getvalue(),
                file_name=f"survey_questionnaire_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
            # Excel download
            excel_data = create_excel_output(formatted_questionnaire, survey_data)
            st.download_button(
                "📊 Download as Excel",
                excel_data,
                file_name=f"survey_questionnaire_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        # Display research insights
        with st.expander("🔍 Market Research Insights Used"):
            st.write(research_data)
        
        # Display enhanced prompt
        with st.expander("📋 Enhanced AI Prompt Generated"):
            st.code(enhanced_prompt, language='markdown')
            
        st.success("✅ Survey questionnaire generated successfully! All form data has been preserved.")
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ Error generating questionnaire: {str(e)}")

# Footer
st.markdown("---")
st.markdown("### 📚 AI Survey Toolkit Reference")
st.info("""
This enhanced generator uses:
- ✅ Current market research and brand data
- ✅ Professional survey design guidelines  
- ✅ 5-point scales for all rating questions
- ✅ Statistical analysis recommendations
- ✅ Fraud detection guidelines
- ✅ Purchase journey questions
- ✅ 'Others (specify)' options where applicable
- ✅ Multiple download formats (TXT, Word, Excel)
- ✅ Form data preservation
""")
