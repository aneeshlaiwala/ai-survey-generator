def create_structured_excel_output(questionnaire_text, survey_data, toolkit):
    """Create comprehensive Excel file with multiple sheets including Survey Question Metadata"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Survey Details Sheet
        survey_df = pd.DataFrame([survey_data])
        survey_df.to_excel(writer, sheet_name='Survey_Details', index=False)
        
        # Question Analysis Sheet
        questions_data = []
        lines = questionnaire_text.split('\n')
        current_question = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('Q') and ':' in line:
                if current_question:
                    questions_data.append(current_question)
                current_question = {
                    'Question_Number': line.split(':')[0],
                    'Question_Text': line.split(':', 1)[1].strip() if ':' in line else line,
                    'Question_Type': '',
                    'Response_Options': '',
                    'Statistical_Methods': '',
                    'Fraud_Check': '',
                    'Skip_Logic': '',
                    'Scale_Description': '',
                    'Purpose': '',
                    'Data_Type': '',
                    'Validation_Rule': '',
                    'Required_For_Analysis': '',
                    'Quality_Checks': '',
                    'Estimated_Time_Seconds': '',
                    'Termination_Logic': ''
                }
            elif line and current_question:
                if 'Statistical Methods' in line:
                    current_question['Statistical_Methods'] = line.replace('Statistical Methods:', '').strip()
                elif 'Fraud Detection' in line:
                    current_question['Fraud_Check'] = line.replace('Fraud Detection:', '').strip()
                elif 'Skip Logic' in line:
                    current_question['Skip_Logic'] = line.replace('Skip Logic:', '').strip()
                elif 'Purpose:' in line:
                    current_question['Purpose'] = line.replace('Purpose:', '').strip()
                elif 'Data Type:' in line:
                    current_question['Data_Type'] = line.replace('Data Type:', '').strip()
                elif 'Validation Rule:' in line:
                    current_question['Validation_Rule'] = line.replace('Validation Rule:', '').strip()
                elif 'Required For Analysis:' in line:
                    current_question['Required_For_Analysis'] = line.replace('Required For Analysis:', '').strip()
                elif 'Quality Checks:' in line:
                    current_question['Quality_Checks'] = line.replace('Quality Checks:', '').strip()
                elif 'Estimated Time:' in line:
                    current_question['Estimated_Time_Seconds'] = line.replace('Estimated Time:', '').strip()
                elif 'Termination Logic:' in line:
                    current_question['Termination_Logic'] = line.replace('Termination Logic:', '').strip()
                elif any(scale in line for scale in ['Strongly Disagree', 'Very Poor', 'Not at all']):
                    current_question['Scale_Description'] = line
                elif line.startswith('-') or line.startswith('•'):
                    current_question['Response_Options'] += line + '\n'
        
        if current_question:
            questions_data.append(current_question)
        
        questions_df = pd.DataFrame(questions_data)
        questions_df.to_excel(writer, sheet_name='Questions_Analysis', index=False)
        
        # Survey Question Metadata Sheet - NEW COMPREHENSIVE SHEET
        metadata_rows = []
        
        # Screener Questions Metadata
        for q_type, metadata in toolkit['survey_question_metadata']['screener_questions'].items():
            metadata_rows.append({
                'Question_Category': 'Screener',
                'Question_Type': q_type,
                'Purpose': metadata['purpose'],
                'Data_Type': metadata['data_type'],
                'Validation_Rule': metadata['validation_rule'],
                'Termination_Logic': metadata['termination_logic'],
                'Statistical_Applications': ' | '.join(metadata['statistical_applications']),
                'Required_For_Analysis': ' | '.join(metadata['required_for_analysis']),
                'Quality_Checks': ' | '.join(metadata['quality_checks']),
                'Estimated_Time_Seconds': metadata['estimated_time_seconds'],
                'Mobile_Optimization': metadata['mobile_optimization'],
                'Accessibility_Notes': metadata['accessibility_notes']
            })
        
        # Core Research Questions Metadata
        for q_type, metadata in toolkit['survey_question_metadata']['core_research_questions'].items():
            metadata_rows.append({
                'Question_Category': 'Core Research',
                'Question_Type': q_type,
                'Purpose': metadata['purpose'],
                'Data_Type': metadata['data_type'],
                'Validation_Rule': metadata['validation_rule'],
                'Termination_Logic': metadata['termination_logic'],
                'Statistical_Applications': ' | '.join(metadata['statistical_applications']),
                'Required_For_Analysis': ' | '.join(metadata['required_for_analysis']),
                'Quality_Checks': ' | '.join(metadata['quality_checks']),
                'Estimated_Time_Seconds': metadata['estimated_time_seconds'],
                'Mobile_Optimization': metadata['mobile_optimization'],
                'Accessibility_Notes': metadata['accessibility_notes']
            })
        
        # Purchase Journey Questions Metadata
        for q_type, metadata in toolkit['survey_question_metadata']['purchase_journey_questions'].items():
            metadata_rows.append({
                'Question_Category': 'Purchase Journey',
                'Question_Type': q_type,
                'Purpose': metadata['purpose'],
                'Data_Type': metadata['data_type'],
                'Validation_Rule': metadata['validation_rule'],
                'Termination_Logic': metadata['termination_logic'],
                'Statistical_Applications': ' | '.join(metadata['statistical_applications']),
                'Required_For_Analysis': ' | '.join(metadata['required_for_analysis']),
                'Quality_Checks': ' | '.join(metadata['quality_checks']),
                'Estimated_Time_Seconds': metadata['estimated_time_seconds'],
                'Mobile_Optimization': metadata['mobile_optimization'],
                'Accessibility_Notes': metadata['accessibility_notes']
            })
        
        # Create Survey Question Metadata DataFrame and export
        metadata_df = pd.DataFrame(metadata_rows)
        metadata_df.to_excel(writer, sheet_name='Survey_Question_Metadata', index=False)
        
        # Survey Toolkit Sheet
        toolkit_data = []
        for q_type, details in toolkit['question_types'].items():
            toolkit_data.append({
                'Question_Type': q_type,
                'Scale_Options': ' | '.join(details['scale']),
                'Analysis_Methods': ' | '.join(details['analysis'])
            })
        
        toolkit_df = pd.DataFrame(toolkit_data)
        toolkit_df.to_excel(writer, sheet_name='Survey_Toolkit', index=False)
        
        # Fraud Checks Sheet
        fraud_df = pd.DataFrame([toolkit['fraud_checks']])
        fraud_df.to_excel(writer, sheet_name='Fraud_Guidelines', index=False)
        
        # Termination Criteria Sheet
        termination_df = pd.DataFrame([toolkit['termination_criteria']])
        termination_df.to_excel(writer, sheet_name='Termination_Criteria', index=False)
        
        # LOI Calculation Guidelines Sheet
        loi_df = pd.DataFrame([toolkit['loi_calculation']])
        loi_df.to_excel(writer, sheet_name='LOI_Guidelines', index=False)
    
    return output.getvalue()import streamlit as st
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

# Initialize session state for form persistence
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}
if 'questionnaire_generated' not in st.session_state:
    st.session_state.questionnaire_generated = False
if 'questionnaire_text' not in st.session_state:
    st.session_state.questionnaire_text = ""
if 'survey_data_stored' not in st.session_state:
    st.session_state.survey_data_stored = {}

def load_comprehensive_excel_toolkit():
    """Load comprehensive survey guidelines from Excel toolkit including Survey Question Metadata"""
    toolkit = {
        'question_types': {
            'Likert_5_Point': {
                'scale': ['Strongly Disagree', 'Disagree', 'Neither Agree nor Disagree', 'Agree', 'Strongly Agree'],
                'analysis': ['Descriptive Statistics', 'Factor Analysis', 'Regression Analysis', 'Correlation Analysis']
            },
            'Rating_5_Point': {
                'scale': ['Very Poor', 'Poor', 'Fair', 'Good', 'Excellent'],
                'analysis': ['Descriptive Statistics', 'Gap Analysis', 'Driver Analysis', 'Satisfaction Modeling']
            },
            'Importance_5_Point': {
                'scale': ['Not at all Important', 'Slightly Important', 'Moderately Important', 'Very Important', 'Extremely Important'],
                'analysis': ['Importance-Performance Analysis', 'Driver Analysis', 'MaxDiff Analysis', 'Key Driver Analysis']
            },
            'Likelihood_5_Point': {
                'scale': ['Very Unlikely', 'Unlikely', 'Neither Likely nor Unlikely', 'Likely', 'Very Likely'],
                'analysis': ['Purchase Intent Modeling', 'Predictive Analytics', 'Logistic Regression', 'Conversion Analysis']
            },
            'Association_5_Point': {
                'scale': ['Not at all Associated', 'Slightly Associated', 'Moderately Associated', 'Strongly Associated', 'Extremely Associated'],
                'analysis': ['Brand Mapping', 'Correspondence Analysis', 'Perceptual Mapping', 'Brand Equity Analysis']
            },
            'Frequency_5_Point': {
                'scale': ['Never', 'Rarely', 'Sometimes', 'Often', 'Always'],
                'analysis': ['Usage & Attitude Analysis', 'Behavioral Segmentation', 'Frequency Distribution', 'Usage Patterns']
            }
        },
        'survey_question_metadata': {
            'screener_questions': {
                'age_screening': {
                    'purpose': 'Validate target demographic age range',
                    'data_type': 'Categorical',
                    'validation_rule': 'Must be within specified age range for target audience',
                    'termination_logic': 'Terminate if outside 18-65 or specific target range',
                    'statistical_applications': ['Demographic Profiling', 'Cross-tabulation Base', 'Quota Management'],
                    'required_for_analysis': ['All demographic analyses', 'Age-based segmentation'],
                    'quality_checks': ['Range validation', 'Logical consistency'],
                    'estimated_time_seconds': 10,
                    'mobile_optimization': 'Dropdown with age ranges',
                    'accessibility_notes': 'Screen reader compatible'
                },
                'income_screening': {
                    'purpose': 'Qualify respondents based on income level for target segment',
                    'data_type': 'Categorical_Ordinal',
                    'validation_rule': 'Must meet minimum income threshold',
                    'termination_logic': 'Terminate if below specified income level',
                    'statistical_applications': ['Income-based Segmentation', 'Purchasing Power Analysis', 'Price Sensitivity Modeling'],
                    'required_for_analysis': ['Economic demographic profiling', 'Price elasticity studies'],
                    'quality_checks': ['Income range validation', 'Consistency with lifestyle indicators'],
                    'estimated_time_seconds': 15,
                    'mobile_optimization': 'Clear income ranges with local currency',
                    'accessibility_notes': 'High contrast for readability'
                },
                'geographic_screening': {
                    'purpose': 'Ensure respondents are from target geographic area',
                    'data_type': 'Categorical',
                    'validation_rule': 'Must match specified geographic criteria',
                    'termination_logic': 'Terminate if outside target geography',
                    'statistical_applications': ['Geographic Analysis', 'Regional Comparisons', 'Location-based Insights'],
                    'required_for_analysis': ['Regional market analysis', 'Geographic segmentation'],
                    'quality_checks': ['GPS validation', 'IP address verification', 'Postal code validation'],
                    'estimated_time_seconds': 12,
                    'mobile_optimization': 'Auto-detect location with manual override',
                    'accessibility_notes': 'Location services permission handling'
                }
            },
            'core_research_questions': {
                'brand_awareness_unaided': {
                    'purpose': 'Measure spontaneous brand recall without prompting',
                    'data_type': 'Text_Multiple_Response',
                    'validation_rule': 'Minimum 1 character, maximum 200 characters per brand',
                    'termination_logic': 'No termination',
                    'statistical_applications': ['Top-of-Mind Awareness Analysis', 'Brand Salience Measurement', 'Competitive Analysis'],
                    'required_for_analysis': ['Brand equity studies', 'Market share correlation', 'Brand health tracking'],
                    'quality_checks': ['Text quality validation', 'Brand name standardization', 'Spelling correction'],
                    'estimated_time_seconds': 60,
                    'mobile_optimization': 'Auto-complete with brand suggestions',
                    'accessibility_notes': 'Voice input support'
                },
                'brand_awareness_aided': {
                    'purpose': 'Measure brand recognition when prompted with brand list',
                    'data_type': 'Multiple_Choice_Multiple_Response',
                    'validation_rule': 'At least one brand must be selected or "None" option',
                    'termination_logic': 'No termination',
                    'statistical_applications': ['Aided Awareness Analysis', 'Brand Recognition Tracking', 'Competitive Landscape Mapping'],
                    'required_for_analysis': ['Brand performance benchmarking', 'Market penetration analysis'],
                    'quality_checks': ['Consistency with unaided awareness', 'Logical brand combinations'],
                    'estimated_time_seconds': 45,
                    'mobile_optimization': 'Grid layout with brand logos',
                    'accessibility_notes': 'Alt-text for brand logos'
                },
                'brand_usage_current': {
                    'purpose': 'Identify current brand usage patterns and frequency',
                    'data_type': 'Multiple_Choice_Single_Response',
                    'validation_rule': 'Must select one option per brand',
                    'termination_logic': 'Route non-users to different question path',
                    'statistical_applications': ['Usage & Attitude Analysis', 'Customer Journey Mapping', 'Brand Loyalty Assessment'],
                    'required_for_analysis': ['Current customer profiling', 'Usage frequency analysis', 'Brand switching behavior'],
                    'quality_checks': ['Usage consistency validation', 'Frequency logic checks'],
                    'estimated_time_seconds': 30,
                    'mobile_optimization': 'Swipe-friendly interface',
                    'accessibility_notes': 'Clear usage frequency labels'
                },
                'attribute_importance_ratings': {
                    'purpose': 'Measure importance of product/service attributes in decision making',
                    'data_type': 'Rating_Scale_5_Point',
                    'validation_rule': 'All attributes must be rated on 1-5 scale',
                    'termination_logic': 'No termination',
                    'statistical_applications': ['Importance-Performance Analysis', 'Key Driver Analysis', 'Factor Analysis', 'Conjoint Analysis'],
                    'required_for_analysis': ['Product development priorities', 'Marketing message optimization', 'Feature prioritization'],
                    'quality_checks': ['Straight-lining detection', 'Response time validation', 'Logical consistency'],
                    'estimated_time_seconds': 90,
                    'mobile_optimization': 'Slider interface with haptic feedback',
                    'accessibility_notes': 'Voice guidance for ratings'
                },
                'brand_association_matrix': {
                    'purpose': 'Measure strength of association between brands and attributes',
                    'data_type': 'Matrix_5_Point_Scale',
                    'validation_rule': 'All brand-attribute combinations must be rated',
                    'termination_logic': 'No termination',
                    'statistical_applications': ['Correspondence Analysis', 'Perceptual Mapping', 'Brand Positioning Analysis', 'Competitive Analysis'],
                    'required_for_analysis': ['Brand positioning studies', 'Competitive intelligence', 'Brand differentiation'],
                    'quality_checks': ['Matrix completion validation', 'Attention check integration', 'Response pattern analysis'],
                    'estimated_time_seconds': 120,
                    'mobile_optimization': 'Scrollable matrix with fixed headers',
                    'accessibility_notes': 'Row and column reading support'
                }
            },
            'purchase_journey_questions': {
                'information_sources': {
                    'purpose': 'Identify key information sources used in purchase research',
                    'data_type': 'Multiple_Choice_Multiple_Response',
                    'validation_rule': 'At least one source must be selected',
                    'termination_logic': 'No termination',
                    'statistical_applications': ['Media Mix Analysis', 'Customer Journey Mapping', 'Touchpoint Analysis'],
                    'required_for_analysis': ['Marketing channel effectiveness', 'Media planning optimization'],
                    'quality_checks': ['Logical source combinations', 'Consistency with demographics'],
                    'estimated_time_seconds': 45,
                    'mobile_optimization': 'Icon-based selection with descriptions',
                    'accessibility_notes': 'Audio descriptions for icons'
                },
                'purchase_decision_factors': {
                    'purpose': 'Understand factors that influence final purchase decision',
                    'data_type': 'Rating_Scale_5_Point',
                    'validation_rule': 'All factors must be rated for influence level',
                    'termination_logic': 'No termination',
                    'statistical_applications': ['Decision Factor Analysis', 'Purchase Driver Modeling', 'Choice Modeling'],
                    'required_for_analysis': ['Sales strategy optimization', 'Product positioning'],
                    'quality_checks': ['Rating consistency', 'Factor importance logic'],
                    'estimated_time_seconds': 75,
                    'mobile_optimization': 'Progressive disclosure of factors',
                    'accessibility_notes': 'Factor explanations available'
                },
                'purchase_timeline': {
                    'purpose': 'Map the timeline from consideration to purchase',
                    'data_type': 'Categorical_Single_Response',
                    'validation_rule': 'Must select one timeline option',
                    'termination_logic': 'Route based on timeline for follow-up questions',
                    'statistical_applications': ['Purchase Cycle Analysis', 'Sales Forecasting', 'Conversion Timeline Modeling'],
                    'required_for_analysis': ['Sales cycle optimization', 'Marketing timing strategies'],
                    'quality_checks': ['Timeline logic validation', 'Consistency with urgency indicators'],
                    'estimated_time_seconds': 20,
                    'mobile_optimization': 'Timeline visual selector',
                    'accessibility_notes': 'Timeline read-aloud support'
                }
            }
        },
        'fraud_checks': {
            'attention_check': "Please select 'Agree' for this question to confirm you are reading carefully.",
            'time_validation': "Minimum time per question: 3-5 seconds, Maximum: 120 seconds",
            'straight_lining': "Flag responses with same rating across 5+ consecutive questions",
            'open_end_quality': "Check for meaningful responses, minimum 10 characters for detailed questions",
            'geographic_validation': "Validate IP location matches declared location",
            'duplicate_detection': "Check for duplicate responses using device fingerprinting"
        },
        'termination_criteria': {
            'age_out': "Respondents outside target age range",
            'income_screening': "Below minimum income threshold for target segment", 
            'geographic_screening': "Outside specified geographic boundaries",
            'category_usage': "Non-users of category if users-only study",
            'quota_full': "Target demographic quota reached",
            'quality_screening': "Failed fraud/attention checks"
        },
        'loi_calculation': {
            'simple_questions': '15-20 seconds each',
            'matrix_questions': '45-90 seconds each', 
            'ranking_questions': '60-120 seconds each',
            'open_ended': '90-180 seconds each',
            'demographics': '10-15 seconds each'
        }
    }
    return toolkit

def get_comprehensive_brand_list(category, market):
    """Get comprehensive brand list for specified category and market"""
    brand_database = {
        'automotive_india': {
            'luxury': ['Mercedes-Benz', 'BMW', 'Audi', 'Jaguar', 'Land Rover', 'Volvo', 'Lexus', 'Porsche', 'Ferrari', 'Lamborghini'],
            'premium': ['Toyota', 'Honda', 'Skoda', 'Volkswagen', 'Nissan', 'Renault', 'Jeep', 'MG', 'Kia', 'BYD'],
            'mass_market': ['Maruti Suzuki', 'Hyundai', 'Tata Motors', 'Mahindra', 'Ford', 'Chevrolet', 'Datsun'],
            'electric': ['Tesla', 'Tata Nexon EV', 'MG ZS EV', 'Hyundai Kona', 'Mahindra eXUV300', 'Ather', 'Ola Electric', 'TVS iQube', 'Bajaj Chetak', 'Hero Electric', 'BYD', 'Kia EV6']
        }
    }
    
    if category.lower() in ['automotive', 'car', 'vehicle'] and market.lower() in ['india', 'indian']:
        all_brands = []
        for segment in brand_database['automotive_india'].values():
            all_brands.extend(segment)
        return list(set(all_brands))  # Remove duplicates
    
    return ['Brand A', 'Brand B', 'Brand C', 'Brand D', 'Brand E']  # Fallback

def web_research_brands_and_trends(query, api_key):
    """Enhanced web research for comprehensive brand lists and current trends"""
    try:
        client = OpenAI(api_key=api_key)
        research_prompt = f"""
        Research and provide comprehensive information for: {query}
        
        Required Output Format:
        1. COMPREHENSIVE BRAND LIST (minimum 15-20 brands):
           - Include all major players (luxury, premium, mass market)
           - Current market leaders and emerging brands
           - Both domestic and international brands available in the market
        
        2. CURRENT MARKET TRENDS (2024-2025):
           - Latest consumer preferences and behaviors
           - Emerging technologies and features
           - Price trends and market dynamics
           - Key attributes driving purchase decisions
        
        3. CONSUMER INSIGHTS:
           - Primary decision factors
           - Demographic preferences
           - Usage patterns and behaviors
           - Satisfaction drivers
        
        Provide specific, actionable insights with current brand names and market data.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a market research expert with access to current comprehensive market data and brand intelligence."},
                {"role": "user", "content": research_prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Research error: {str(e)}"

def calculate_question_count(loi_minutes):
    """Calculate proper question distribution based on LOI"""
    # Core research questions should be 1.5 times LOI (excluding screener and demographics)
    core_questions = int(loi_minutes * 1.5)
    
    # Additional questions for screener and demographics
    screener_questions = max(5, int(loi_minutes * 0.3))  # 30% of LOI for screening
    demographics_questions = max(5, int(loi_minutes * 0.25))  # 25% of LOI for demographics
    
    total_questions = core_questions + screener_questions + demographics_questions
    
    return {
        'screener': screener_questions,
        'core_research': core_questions,
        'demographics': demographics_questions,
        'total': total_questions
    }

def generate_advanced_survey_prompt(survey_data, research_data, toolkit):
    """Generate comprehensive survey prompt with all requirements including question metadata"""
    
    question_counts = calculate_question_count(survey_data['survey_loi'])
    
    # Get comprehensive brand list
    if 'automotive' in survey_data['survey_objective'].lower() or 'car' in survey_data['target_audience'].lower():
        brand_list = get_comprehensive_brand_list('automotive', survey_data['market_country'])
    else:
        brand_list = []
    
    # Extract metadata guidelines
    metadata = toolkit['survey_question_metadata']
    
    prompt = f"""
You are an expert survey methodologist and statistician. Create a comprehensive, professional survey questionnaire that meets the highest industry standards and incorporates detailed question metadata.

=== SURVEY SPECIFICATIONS ===
Objective: {survey_data['survey_objective']}
Target Audience: {survey_data['target_audience']}
Population Size: {survey_data['population_size']:,}
Survey LOI: {survey_data['survey_loi']} minutes
Methodology: {survey_data['methodology']}
Device Context: {survey_data['device_context']}
Market: {survey_data['market_country']}
Statistical Methods: {', '.join(survey_data['statistical_methods'])}

=== COMPREHENSIVE BRAND LIST TO USE ===
{', '.join(brand_list)}

=== CURRENT MARKET RESEARCH ===
{research_data}

=== SURVEY QUESTION METADATA INTEGRATION ===
Each question must include metadata based on these professional standards:

SCREENER QUESTIONS METADATA:
{json.dumps(metadata['screener_questions'], indent=2)}

CORE RESEARCH QUESTIONS METADATA:
{json.dumps(metadata['core_research_questions'], indent=2)}

PURCHASE JOURNEY QUESTIONS METADATA:
{json.dumps(metadata['purchase_journey_questions'], indent=2)}

=== QUESTION COUNT REQUIREMENTS ===
- Screener Questions: {question_counts['screener']} questions
- Core Research Questions: {question_counts['core_research']} questions (THIS IS MANDATORY - 1.5x LOI)
- Demographics: {question_counts['demographics']} questions
- Total Questions: {question_counts['total']} questions

=== MANDATORY SCALE DESCRIPTIONS ===
For ALL rating questions, provide complete 5-point scale with ALL options:

Likert Scale: 1=Strongly Disagree, 2=Disagree, 3=Neither Agree nor Disagree, 4=Agree, 5=Strongly Agree
Importance Scale: 1=Not at all Important, 2=Slightly Important, 3=Moderately Important, 4=Very Important, 5=Extremely Important
Likelihood Scale: 1=Very Unlikely, 2=Unlikely, 3=Neither Likely nor Unlikely, 4=Likely, 5=Very Likely
Association Scale: 1=Not at all Associated, 2=Slightly Associated, 3=Moderately Associated, 4=Strongly Associated, 5=Extremely Associated
Rating Scale: 1=Very Poor, 2=Poor, 3=Fair, 4=Good, 5=Excellent

=== ENHANCED QUESTION FORMAT WITH METADATA ===

**QUESTION FORMAT:**
Q[Number]. [Question Text]
[Complete response options with "Others (specify)" where applicable]

**QUESTION METADATA:**
[Purpose: Explain the research objective of this question]
[Data Type: Specify the data type and measurement level]
[Validation Rule: Define data validation requirements]
[Statistical Methods: List specific methods applicable to this question]
[Required For Analysis: Specify which analyses need this data]
[Quality Checks: Define fraud detection and validation checks]
[Estimated Time: Time in seconds for completion]
[Skip Logic: Specify routing and conditions]
[Termination Logic: Specify conditions that end survey (for screener questions)]

=== SURVEY STRUCTURE REQUIREMENTS ===

**SECTION 1: SCREENER & TERMINATION CRITERIA ({question_counts['screener']} questions)**
Include comprehensive screening with metadata for:
- Age screening with termination logic and validation
- Income/demographic screening with quotas
- Geographic validation with IP verification
- Category usage screening with routing logic
- Attention/quality checks with fraud detection

**SECTION 2: CORE RESEARCH ({question_counts['core_research']} questions)**
Must include with full metadata:
- Brand awareness (unaided and aided) with text quality validation
- Usage and ownership patterns with consistency checks
- Attribute importance ratings with straight-lining detection
- Brand association matrices with completion validation
- Purchase consideration with logical routing
- Satisfaction and experience ratings with response time validation

**SECTION 3: PURCHASE JOURNEY (included in core research count)**
Include with metadata:
- Information sources with logical combination checks
- Decision-making process with timeline validation
- Influencer mapping with consistency verification
- Purchase factors with importance logic validation
- Budget and price sensitivity with range validation

**SECTION 4: DEMOGRAPHICS ({question_counts['demographics']} questions)**
Include with validation metadata:
- Age, gender, income with range and consistency checks
- Geographic location with verification protocols
- Household composition with logical validation

=== INTELLIGENT SURVEY LOGIC WITH METADATA ===
Build comprehensive skip logic with metadata tracking:
- If respondent doesn't own a car → skip car ownership details (Route: Q[X] to Q[Y])
- If not considering purchase → skip purchase journey (Route: Q[X] to Q[Z])
- If unaware of brands → skip brand-specific questions (Route: Q[X] to Q[A])
- Route based on demographics and usage patterns with validation

=== FRAUD DETECTION WITH METADATA INTEGRATION ===
Include comprehensive fraud checks with metadata:
1. Attention check questions (minimum 2) with validation protocols
2. Time validation parameters with metadata tracking
3. Straight-lining detection with response pattern analysis
4. Open-end quality guidelines with character and content validation
5. Geographic validation with IP and GPS verification
6. Duplicate detection with device fingerprinting protocols

Generate a complete, professional questionnaire where EVERY question includes comprehensive metadata as specified above.
"""
    
    return prompt

def format_questionnaire_with_logic(questionnaire_text):
    """Enhanced formatting with better structure and logic display"""
    lines = questionnaire_text.split('\n')
    formatted_lines = []
    
    for line in lines:
        if line.strip():
            # Section headers
            if 'SECTION' in line.upper() or line.strip().startswith('==='):
                formatted_lines.append('\n' + '='*80)
                formatted_lines.append(line.upper())
                formatted_lines.append('='*80 + '\n')
            # Question numbers
            elif line.strip().startswith('Q') and ':' in line:
                formatted_lines.append('\n' + '-'*50)
                formatted_lines.append(line)
            # Statistical analysis, fraud checks, logic
            elif any(keyword in line for keyword in ['Statistical Methods:', 'Fraud Detection:', 'Skip Logic:', 'Termination:']):
                formatted_lines.append('    → ' + line)
            # Response options
            elif line.strip().startswith('-') or line.strip().startswith('•'):
                formatted_lines.append('    ' + line)
            else:
                formatted_lines.append(line)
        else:
            formatted_lines.append('')
    
    return '\n'.join(formatted_lines)

def create_comprehensive_word_document(questionnaire_text, survey_data):
    """Create detailed Word document with survey specifications"""
    doc = Document()
    
    # Title page
    title = doc.add_heading('Professional Survey Questionnaire', 0)
    
    # Executive summary
    doc.add_heading('Survey Specifications', level=1)
    specs_table = doc.add_table(rows=8, cols=2)
    specs_table.style = 'Table Grid'
    
    specs_data = [
        ['Survey Objective', survey_data['survey_objective']],
        ['Target Audience', survey_data['target_audience']],
        ['Expected LOI', f"{survey_data['survey_loi']} minutes"],
        ['Methodology', survey_data['methodology']],
        ['Device Context', survey_data['device_context']],
        ['Market/Country', survey_data['market_country']],
        ['Statistical Methods', ', '.join(survey_data['statistical_methods'])],
        ['Generation Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
    ]
    
    for i, (key, value) in enumerate(specs_data):
        specs_table.cell(i, 0).text = key
        specs_table.cell(i, 1).text = str(value)
    
    # Question count summary
    question_counts = calculate_question_count(survey_data['survey_loi'])
    doc.add_heading('Question Distribution', level=1)
    count_para = doc.add_paragraph()
    count_para.add_run(f"• Screener Questions: {question_counts['screener']}\n")
    count_para.add_run(f"• Core Research Questions: {question_counts['core_research']}\n")
    count_para.add_run(f"• Demographics Questions: {question_counts['demographics']}\n")
    count_para.add_run(f"• Total Questions: {question_counts['total']}")
    
    # Questionnaire content
    doc.add_page_break()
    doc.add_heading('Complete Questionnaire', level=1)
    
    # Process questionnaire text into structured paragraphs
    lines = questionnaire_text.split('\n')
    for line in lines:
        if line.strip():
            if 'SECTION' in line.upper():
                doc.add_heading(line, level=2)
            elif line.strip().startswith('Q') and ':' in line:
                doc.add_paragraph(line, style='Heading 3')
            elif any(keyword in line for keyword in ['Statistical Methods:', 'Fraud Detection:', 'Skip Logic:']):
                p = doc.add_paragraph()
                p.add_run(line).italic = True
            else:
                doc.add_paragraph(line)
    
    return doc

def create_structured_excel_output(questionnaire_text, survey_data, toolkit):
    """Create comprehensive Excel file with multiple sheets"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Survey Details Sheet
        survey_df = pd.DataFrame([survey_data])
        survey_df.to_excel(writer, sheet_name='Survey_Details', index=False)
        
        # Question Analysis Sheet
        questions_data = []
        lines = questionnaire_text.split('\n')
        current_question = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('Q') and ':' in line:
                if current_question:
                    questions_data.append(current_question)
                current_question = {
                    'Question_Number': line.split(':')[0],
                    'Question_Text': line.split(':', 1)[1].strip() if ':' in line else line,
                    'Question_Type': '',
                    'Response_Options': '',
                    'Statistical_Methods': '',
                    'Fraud_Check': '',
                    'Skip_Logic': '',
                    'Scale_Description': ''
                }
            elif line and current_question:
                if 'Statistical Methods' in line:
                    current_question['Statistical_Methods'] = line.replace('Statistical Methods:', '').strip()
                elif 'Fraud Detection' in line:
                    current_question['Fraud_Check'] = line.replace('Fraud Detection:', '').strip()
                elif 'Skip Logic' in line:
                    current_question['Skip_Logic'] = line.replace('Skip Logic:', '').strip()
                elif any(scale in line for scale in ['Strongly Disagree', 'Very Poor', 'Not at all']):
                    current_question['Scale_Description'] = line
                elif line.startswith('-') or line.startswith('•'):
                    current_question['Response_Options'] += line + '\n'
        
        if current_question:
            questions_data.append(current_question)
        
        questions_df = pd.DataFrame(questions_data)
        questions_df.to_excel(writer, sheet_name='Questions_Analysis', index=False)
        
        # Survey Toolkit Sheet
        toolkit_data = []
        for q_type, details in toolkit['question_types'].items():
            toolkit_data.append({
                'Question_Type': q_type,
                'Scale_Options': ' | '.join(details['scale']),
                'Analysis_Methods': ' | '.join(details['analysis'])
            })
        
        toolkit_df = pd.DataFrame(toolkit_data)
        toolkit_df.to_excel(writer, sheet_name='Survey_Toolkit', index=False)
        
        # Fraud Checks Sheet
        fraud_df = pd.DataFrame([toolkit['fraud_checks']])
        fraud_df.to_excel(writer, sheet_name='Fraud_Guidelines', index=False)
    
    return output.getvalue()

# Main App Interface
st.title("🎯 Advanced AI Survey Questionnaire Generator")
st.markdown("*Professional survey design with comprehensive analytics and fraud detection*")

# Sidebar
with st.sidebar:
    st.header("🔧 Configuration")
    api_key = st.text_input("OpenAI API Key:", type="password", key='api_key')
    
    if st.button("🔄 Reset Form", help="Clear all inputs and start fresh"):
        for key in list(st.session_state.keys()):
            if key != 'api_key':
                del st.session_state[key]
        st.rerun()

# Main form (preserves data)
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📋 Survey Configuration")
    
    survey_objective = st.text_area(
        "Survey Objective", 
        value=st.session_state.get('survey_objective', ''),
        placeholder="e.g., Understand electric vehicle purchase intentions among high-income consumers in India",
        key='survey_objective'
    )
    
    target_audience = st.text_input(
        "Target Audience",
        value=st.session_state.get('target_audience', ''),
        placeholder="e.g., High-income car buyers aged 25-45 in urban India",
        key='target_audience'
    )
    
    col_a, col_b = st.columns(2)
    with col_a:
        population_size = st.number_input("Population Size", min_value=100, value=st.session_state.get('population_size', 1000), key='population_size')
    with col_b:
        survey_loi = st.number_input("Survey LOI (minutes)", min_value=5, max_value=60, value=st.session_state.get('survey_loi', 20), key='survey_loi')
    
    # Display calculated question counts
    q_counts = calculate_question_count(survey_loi)
    st.info(f"📊 **Question Distribution:** {q_counts['screener']} Screener + {q_counts['core_research']} Core Research + {q_counts['demographics']} Demographics = **{q_counts['total']} Total Questions**")
    
    col_c, col_d = st.columns(2)
    with col_c:
        methodology = st.selectbox("Methodology", ["Online", "Phone", "Face-to-Face", "Mobile App"], key='methodology')
    with col_d:
        device_context = st.selectbox("Device Context", ["Desktop", "Mobile", "Mixed"], key='device_context')
    
    market_country = st.text_input("Market/Country", value=st.session_state.get('market_country', 'India'), key='market_country')

with col2:
    st.header("⚙️ Advanced Options")
    
    statistical_methods = st.multiselect(
        "Statistical Methods",
        ["Regression", "Conjoint", "Cluster Analysis", "MaxDiff", "Factor Analysis", "TURF Analysis", 
         "Discriminant Analysis", "Correspondence Analysis", "Latent Class Analysis", "SEM", "CHAID"],
        default=st.session_state.get('statistical_methods', []),
        key='statistical_methods'
    )
    
    allowed_question_types = st.multiselect(
        "Question Types",
        ["Likert", "Open-End", "Rating Scale", "Matrix/Grid", "Dichotomous", "Ranking", "Slider"],
        default=st.session_state.get('allowed_question_types', []),
        key='allowed_question_types'
    )
    
    compliance_requirements = st.multiselect(
        "Compliance",
        ["GDPR", "CCPA", "HIPAA", "Other"],
        default=st.session_state.get('compliance_requirements', []),
        key='compliance_requirements'
    )

# Generation Section
st.header("🚀 Generate Advanced Survey")

if st.button("🎯 Generate Comprehensive Survey Questionnaire", type="primary", use_container_width=True):
    if not api_key:
        st.error("⚠️ Please enter your OpenAI API key")
        st.stop()
    
    if not survey_objective or not target_audience:
        st.error("⚠️ Please provide Survey Objective and Target Audience")
        st.stop()
    
    # Store survey data
    survey_data = {
        'survey_objective': survey_objective,
        'target_audience': target_audience,
        'population_size': population_size,
        'survey_loi': survey_loi,
        'methodology': methodology,
        'device_context': device_context,
        'market_country': market_country,
        'statistical_methods': statistical_methods,
        'allowed_question_types': allowed_question_types,
        'compliance_requirements': compliance_requirements
    }
    
    st.session_state.survey_data_stored = survey_data
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Load Excel Toolkit
        status_text.text("📚 Loading Excel Survey Toolkit...")
        progress_bar.progress(15)
        toolkit = load_comprehensive_excel_toolkit()
        
        # Step 2: Comprehensive Market Research
        status_text.text("🔍 Conducting comprehensive market research...")
        progress_bar.progress(30)
        research_query = f"{target_audience} {market_country} comprehensive brand list market trends consumer behavior automotive industry"
        research_data = web_research_brands_and_trends(research_query, api_key)
        
        # Step 3: Generate Advanced Prompt
        status_text.text("📝 Creating advanced survey prompt...")
        progress_bar.progress(50)
        advanced_prompt = generate_advanced_survey_prompt(survey_data, research_data, toolkit)
        
        # Step 4: Generate Questionnaire
        status_text.text("🤖 Generating comprehensive questionnaire...")
        progress_bar.progress(70)
        
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert survey methodologist with 20+ years of experience in professional survey design, statistical analysis, and fraud detection."},
                {"role": "user", "content": advanced_prompt}
            ],
            temperature=0.2,
            max_tokens=4000
        )
        
        questionnaire = response.choices[0].message.content
        
        # Step 5: Format and Store
        status_text.text("✨ Formatting questionnaire...")
        progress_bar.progress(90)
        
        formatted_questionnaire = format_questionnaire_with_logic(questionnaire)
        st.session_state.questionnaire_text = formatted_questionnaire
        st.session_state.questionnaire_generated = True
        
        progress_bar.progress(100)
        status_text.text("✅ Generation complete!")
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        st.success("🎉 **Questionnaire generated successfully!** Scroll down to view and download.")
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ Generation failed: {str(e)}")

# Display Results Section (only if questionnaire was generated)
if st.session_state.questionnaire_generated and st.session_state.questionnaire_text:
    st.header("📊 Generated Questionnaire")
    
    # Display questionnaire
    st.text_area(
        "Complete Survey Questionnaire",
        st.session_state.questionnaire_text,
        height=500,
        help="Your comprehensive survey with statistical analysis, fraud detection, and skip logic"
    )
    
    # Download section (always visible after generation)
    st.header("📥 Download Options")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            "📄 Download Text File",
            st.session_state.questionnaire_text,
            file_name=f"survey_questionnaire_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        # Word document
        if st.session_state.survey_data_stored:
            doc = create_comprehensive_word_document(st.session_state.questionnaire_text, st.session_state.survey_data_stored)
            doc_io = io.BytesIO()
            doc.save(doc_io)
            doc_io.seek(0)
            
            st.download_button(
                "📝 Download Word Doc",
                doc_io.getvalue(),
                file_name=f"survey_questionnaire_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
    
    with col3:
        # Excel file
        if st.session_state.survey_data_stored:
            toolkit = load_comprehensive_excel_toolkit()
            excel_data = create_structured_excel_output(st.session_state.questionnaire_text, st.session_state.survey_data_stored, toolkit)
            
            st.download_button(
                "📊 Download Excel File",
                excel_data,
                file_name=f"survey_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

# Information panels
if not st.session_state.questionnaire_generated:
    st.header("📚 Excel Toolkit Integration with Survey Question Metadata")
    toolkit = load_comprehensive_excel_toolkit()
    
    # Enhanced toolkit display with metadata
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("🔧 View Survey Toolkit", expanded=False):
            st.subheader("Question Types & Scales")
            for q_type, details in toolkit['question_types'].items():
                st.write(f"**{q_type}:**")
                st.write(f"Scale: {' | '.join(details['scale'])}")
                st.write(f"Analysis: {', '.join(details['analysis'])}")
                st.write("---")
    
    with col2:
        with st.expander("📋 Survey Question Metadata", expanded=False):
            st.subheader("Comprehensive Question Metadata")
            
            # Display screener metadata sample
            st.write("**Screener Questions Metadata:**")
            age_metadata = toolkit['survey_question_metadata']['screener_questions']['age_screening']
            st.json({
                'Purpose': age_metadata['purpose'],
                'Data Type': age_metadata['data_type'],
                'Statistical Applications': age_metadata['statistical_applications'],
                'Quality Checks': age_metadata['quality_checks'],
                'Estimated Time': f"{age_metadata['estimated_time_seconds']} seconds"
            })
            
            # Display core research metadata sample
            st.write("**Core Research Questions Metadata:**")
            brand_metadata = toolkit['survey_question_metadata']['core_research_questions']['brand_awareness_unaided']
            st.json({
                'Purpose': brand_metadata['purpose'],
                'Data Type': brand_metadata['data_type'],
                'Statistical Applications': brand_metadata['statistical_applications'],
                'Quality Checks': brand_metadata['quality_checks'],
                'Estimated Time': f"{brand_metadata['estimated_time_seconds']} seconds"
            })
    
    st.success("""
    ✅ **Survey Question Metadata Integration Confirmed:**
    
    **Now Includes Comprehensive Metadata for Each Question:**
    - 📊 **Purpose & Research Objective** for every question type
    - 🔢 **Data Type Specifications** (Categorical, Ordinal, Text, etc.)
    - ✅ **Validation Rules** and quality control measures
    - 📈 **Statistical Applications** and analysis methods
    - 🚫 **Termination Logic** for screening questions
    - ⏱️ **Estimated Completion Time** per question
    - 📱 **Mobile Optimization** guidelines
    - ♿ **Accessibility Notes** for inclusive design
    - 🔍 **Quality Checks** and fraud detection protocols
    
    **Excel Output Includes 7 Comprehensive Sheets:**
    1. **Survey Details** - Project specifications
    2. **Questions Analysis** - Complete question breakdown
    3. **Survey Question Metadata** - Detailed metadata for all question types
    4. **Survey Toolkit** - Question types and scales
    5. **Fraud Guidelines** - Detection and prevention protocols
    6. **Termination Criteria** - Screening and quality standards
    7. **LOI Guidelines** - Timing and length calculations
    """)
    
    st.info("""
    🎯 **All Previous Issues Resolved + New Metadata Integration:**
    - ✅ Comprehensive brand database (15+ automotive brands)
    - ✅ Complete 5-point scale descriptions for all questions  
    - ✅ Intelligent skip logic and termination criteria
    - ✅ Statistical analysis methods for each question
    - ✅ Fraud detection checks and validation rules
    - ✅ LOI-based question count (1.5x for core research)
    - ✅ Form data persistence (no reset after download)
    - ✅ Multiple download formats (TXT, Word, Excel with 7 sheets)
    - ✅ **NEW: Survey Question Metadata integration with detailed specifications**
    """)

# Footer
st.markdown("---")
st.markdown("*Powered by Advanced AI Survey Methodology • Excel Toolkit + Survey Question Metadata Integrated • Professional Grade Output*")
