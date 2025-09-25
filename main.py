import streamlit as st
from bson.objectid import ObjectId
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import random

# Your existing imports and MongoDB connection
from admin import admin_dashboard
from user import user_page
from bert_model import predict_drug
from mongodb_utils import get_db_collection
from pymongo import MongoClient

# Your existing MongoDB collections
users_col = get_db_collection()  # returns the "users" collection
client = MongoClient("mongodb+srv://url")
db = client["drug_recommender_db"]
admins_col = db["admins"]
recommendations_col = db["recommendations"]  # Add this line to define recommendations_col

# Set page configuration
st.set_page_config(
    page_title="Drug Recommendation System",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #4a6fa5;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #6b8cbc;
        border-bottom: 2px solid #6b8cbc;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .feature-card {
        background-color: black;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #4a6fa5;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s;
    }
    .feature-card:hover {
        transform: translateY(-5px);
    }
    .stat-card {
        background: linear-gradient(135deg, #4a6fa5 0%, #6b8cbc 100%);
        color: white;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .model-card {
        background-color: #fff;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        border: 1px solid #4a6fa5;
        background-color: #4a6fa5;
        color: white;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #6b8cbc;
        border: 1px solid #6b8cbc;
        transform: scale(1.05);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #4a6fa5 0%, #6b8cbc 100%);
    }
    .sidebar .sidebar-content .block-container {
        color: white;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    .user-welcome {
        background: linear-gradient(135deg, #4a6fa5 0%, #6b8cbc 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def get_user_count():
    # Replace mock with actual count from your database
    return users_col.count_documents({})

def get_recommendation_count():
    # Replace with actual count from your recommendations collection
    return recommendations_col.count_documents({})

def get_accuracy_rate():
    # Replace with actual calculation from your data
    # This is a placeholder - implement your actual accuracy calculation
    return 92.5  # Example static value

# Initialize session state
def init_session_state():
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"
    if "user_logged_in" not in st.session_state:
        st.session_state.user_logged_in = False
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = ""
    if "symptoms" not in st.session_state:
        st.session_state.symptoms = ""
    if "recommendations" not in st.session_state:
        st.session_state.recommendations = []

# Navigation sidebar
def render_sidebar():
    with st.sidebar:
        st.markdown('<div style="text-align: center; margin-bottom: 2rem;">', unsafe_allow_html=True)
        st.markdown('<h1 style="color: white; font-size: 1.8rem;">💊 Drug-Recommendation System</h1>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Navigation options
        pages = ["Home", "User Portal", "Admin Portal", "About", "Contact"]
        icons = ["🏠", "👤", "🛠️", "ℹ️", "📞"]
        
        for i, page in enumerate(pages):
            if st.button(f"{icons[i]} {page}", key=f"nav_{page}_{i}", use_container_width=True):
                st.session_state.current_page = page
                st.rerun()
                
        st.markdown("---")
        
        # Display login status
        if st.session_state.user_logged_in:
            st.success(f"Logged in as: {st.session_state.user_email}")
            if st.button("🚪 Logout", key="sidebar_logout_user", use_container_width=True):
                st.session_state.user_logged_in = False
                st.session_state.user_email = ""
                st.rerun()
        elif st.session_state.admin_logged_in:
            st.success("Logged in as Admin")
            if st.button("🚪 Logout", key="sidebar_logout_admin", use_container_width=True):
                st.session_state.admin_logged_in = False
                st.rerun()
        else:
            st.info("Please log in to access all features")
            
        st.markdown("---")
        st.markdown('<div style="text-align: center; color: white; font-size: 0.8rem;">© 2023 Medi-AI. All rights reserved.</div>', unsafe_allow_html=True)

# Home Page
def render_home_page():
    st.markdown('<h1 class="main-header">💊 Drug Recommendation System</h1>', unsafe_allow_html=True)
    
    # Introduction
    st.markdown("""
    <div style="text-align: center; font-size: 1.2rem; margin-bottom: 2rem;">
        Welcome to advanced drug recommendation system that combines multiple AI models 
        to provide accurate and personalized medication suggestions based on symptoms, medical history, and user feedback.
    </div>
    """, unsafe_allow_html=True)
    
    # Stats Section
    st.markdown('<h2 class="sub-header">📊 System Statistics</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <h3>👥 Users</h3>
            <h2>{get_user_count():,}</h2>
            <p>Registered users</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <h3>💊 Recommendations</h3>
            <h2>{250}</h2>
            <p>Drug recommendations provided</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <h3>🎯 Accuracy</h3>
            <h2>{get_accuracy_rate()}%</h2>
            <p>System accuracy rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Interactive Chart
    st.markdown('<h2 class="sub-header">📈 Recommendation Trends</h2>', unsafe_allow_html=True)
    
    # Generate sample data for the chart
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    recommendations = [random.randint(300, 800) for _ in range(12)]
    users = [random.randint(50, 200) for _ in range(12)]
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=months, y=recommendations, name="Recommendations", line=dict(color="#4a6fa5", width=3)),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(x=months, y=users, name="New Users", marker_color="#6b8cbc", opacity=0.7),
        secondary_y=True,
    )
    fig.update_layout(
        title="Monthly Recommendations and User Growth",
        xaxis_title="Month",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    fig.update_yaxes(title_text="Recommendations", secondary_y=False)
    fig.update_yaxes(title_text="New Users", secondary_y=True)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Features Section
    st.markdown('<h2 class="sub-header">🚀 Advanced AI Features</h2>', unsafe_allow_html=True)
    
    features = [
        {
            "title": "BERT for Text Understanding",
            "icon": "🤖",
            "description": "Advanced natural language processing to understand symptoms and medical reviews with high accuracy."
        },
        {
            "title": "ResNet50 for Pill Recognition",
            "icon": "🔍",
            "description": "Computer vision model that identifies medications from pill images for verification and safety."
        },
        {
            "title": "LSTM for Time-Series Analysis",
            "icon": "📈",
            "description": "Analyzes patient history and feedback patterns to improve long-term recommendation quality."
        },
        {
            "title": "Reinforcement Learning",
            "icon": "⚡",
            "description": "Adaptive system that learns from user feedback to continuously enhance recommendation accuracy."
        }
    ]
    
    cols = st.columns(2)
    for i, feature in enumerate(features):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="feature-card">
                <h3>{feature['icon']} {feature['title']}</h3>
                <p>{feature['description']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # How It Works Section
    st.markdown('<h2 class="sub-header">🔍 How Drug-Recommendation System Works</h2>', unsafe_allow_html=True)

    steps = [
        {"step": "1", "title": "Symptom Input", "description": "Users describe their symptoms in natural language."},
        {"step": "2", "title": "AI Analysis", "description": "Multiple AI models analyze the input for comprehensive understanding."},
        {"step": "3", "title": "Drug Matching", "description": "System matches symptoms with appropriate medications from database."},
        {"step": "4", "title": "Personalization", "description": "Recommendations are tailored based on user history and preferences."},
        {"step": "5", "title": "Feedback Loop", "description": "User feedback improves future recommendations through reinforcement learning."}
    ]

    step_html = '<div style="display:flex; justify-content:space-between; align-items:center; margin:2rem 0;">'
    for i, step in enumerate(steps):
        step_html += f"""
        <div style="text-align:center; flex:1; position:relative;">
            <div style="background:#4a6fa5; color:white; width:40px; height:40px; border-radius:50%; display:flex; align-items:center; justify-content:center; margin:0 auto 10px; font-weight:bold;">{step['step']}</div>
            <div style="font-weight:bold; margin-bottom:5px;">{step['title']}</div>
            <div style="font-size:0.8rem;">{step['description']}</div>
        </div>
        """
        if i < len(steps) - 1:
            step_html += '<div style="flex:1; border-top:2px dashed #4a6fa5; margin:20px auto 0; min-width:50px;"></div>'
    step_html += '</div>'

    st.markdown(step_html, unsafe_allow_html=True)
def render_user_portal():
    # Instead of rendering the dashboard here, call your existing user_page function
    user_page()  # This will use your existing user_page implementation

def render_admin_portal():
    # Instead of rendering the dashboard here, call your existing admin_dashboard function
    admin_dashboard()  # This will use your existing admin_dashboard implementation

# About Page
def render_about_page():
    st.markdown('<h1 class="main-header">ℹ️ About Drug-Recommendation System</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="font-size: 1.1rem; line-height: 1.6;">
        <p>Drug recommendation system is a cutting-edge artificial intelligence recommender system designed
        to provide accurate and personalized medication suggestions. Our system combines multiple AI models 
        to ensure the highest level of accuracy and safety in drug recommendations.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<h2 class="sub-header">🤖 Our AI Technology</h2>', unsafe_allow_html=True)
    
    technologies = [
        {
            "name": "BERT (Bidirectional Encoder Representations from Transformers)",
            "description": "We use BERT to understand and process natural language descriptions of symptoms, medical history, and user reviews. This allows our system to comprehend complex medical descriptions with high accuracy.",
            "application": "Symptom analysis, review understanding, medical text processing"
        },
        {
            "name": "ResNet50 (Residual Neural Network)",
            "description": "Our computer vision model based on ResNet50 architecture can identify medications from pill images, helping to verify medications and prevent errors.",
            "application": "Pill recognition, medication verification, safety checks"
        },
        {
            "name": "LSTM (Long Short-Term Memory)",
            "description": "We utilize LSTM networks to analyze time-series data such as patient history, medication schedules, and longitudinal feedback to improve long-term recommendation quality.",
            "application": "Patient history analysis, trend detection, longitudinal studies"
        },
        {
            "name": "Reinforcement Learning",
            "description": "Our system employs reinforcement learning algorithms that continuously learn from user feedback to adapt and improve recommendation accuracy over time.",
            "application": "Adaptive learning, personalized recommendations, continuous improvement"
        }
    ]
    
    for tech in technologies:
        with st.expander(tech["name"], expanded=True):
            st.write(tech["description"])
            st.info(f"**Application:** {tech['application']}")
    
    st.markdown('<h2 class="sub-header">🎯 Our Mission</h2>', unsafe_allow_html=True)
    st.markdown("""
    Our mission is to make healthcare more accessible and accurate through the power of artificial intelligence.  
    We believe that everyone deserves access to reliable medical information and personalized treatment suggestions.

    By combining multiple AI approaches, we aim to create a system that not only recommends medications  
    but also learns from each interaction to become smarter and more helpful over time.
    """)


def render_contact_page():
    st.markdown('<h1>📞 Contact Us</h1>', unsafe_allow_html=True)
    
    # Two columns for layout
    col1, col2 = st.columns([1, 1])

    # ---- Left Column: Contact Info ----
    with col1:
        st.markdown("""
        ### 📍 Address
        123 Healthcare Avenue  
        Medical Innovation District  
        San Francisco, CA 94107

        ### 📞 Phone
        +1 (555) 123-4567

        ### ✉️ Email
        support@medi-ai.com""")


    # ---- Right Column: Contact Form ----
    with col2:
        st.markdown("""
        <div style="background-color: black; padding: 1.5rem; border-radius: 10px;">
            <h3>Send us a Message</h3>
        </div>
        """, unsafe_allow_html=True)

        # Use a proper form context
        with st.form(key="contact_form"):
            name = st.text_input("Your Name", key="contact_name")
            email = st.text_input("Your Email", key="contact_email")
            subject = st.selectbox("Subject", [
                "General Inquiry", 
                "Technical Support", 
                "Partnership Opportunity",
                "Feature Request",
                "Bug Report"
            ], key="contact_subject")
            message = st.text_area("Your Message", height=150, key="contact_message")
            
            submit = st.form_submit_button("Send Message")
            
            if submit:
                if name.strip() and email.strip() and message.strip():
                    st.success("✅ Thank you for your message! We'll get back to you within 24 hours.")
                else:
                    st.error("❌ Please fill in all required fields.")
# Main app logic
def main():
    init_session_state()
    render_sidebar()
    
    # Render the current page based on session state
    if st.session_state.current_page == "Home":
        render_home_page()
    elif st.session_state.current_page == "User Portal":
        render_user_portal()
    elif st.session_state.current_page == "Admin Portal":
        render_admin_portal()
    elif st.session_state.current_page == "About":
        render_about_page()
    elif st.session_state.current_page == "Contact":
        render_contact_page()

if __name__ == "__main__":
    main()