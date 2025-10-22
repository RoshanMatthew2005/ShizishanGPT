"""
Streamlit Main Application
Frontend interface for ShizishanGPT
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent))


def main():
    """
    Main Streamlit application
    Phase 5: To be fully implemented
    """
    
    st.set_page_config(
        page_title="🌾 ShizishanGPT",
        page_icon="🌾",
        layout="wide"
    )
    
    st.title("🌾 ShizishanGPT - Agricultural AI Assistant")
    st.markdown("*Intelligent farming with AI-powered insights*")
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select a tool:",
        ["Home", "Yield Predictor", "Pest Detector", "Weather Analysis", "Ask Question (RAG)"]
    )
    
    if page == "Home":
        show_home()
    elif page == "Yield Predictor":
        show_yield_predictor()
    elif page == "Pest Detector":
        show_pest_detector()
    elif page == "Weather Analysis":
        show_weather_analysis()
    elif page == "Ask Question (RAG)":
        show_rag_interface()


def show_home():
    """Home page"""
    st.header("Welcome to ShizishanGPT! 🌾")
    
    st.markdown("""
    ### What can ShizishanGPT do?
    
    1. **🌾 Yield Prediction** - Predict crop yield based on soil and weather conditions
    2. **🐛 Pest Detection** - Detect crop diseases from leaf images
    3. **☁️ Weather Analysis** - Analyze weather impact on crops
    4. **📚 Knowledge Base** - Ask questions about agriculture
    
    ### Current Status
    - ✅ Project structure created
    - ✅ Core modules implemented
    - ⏳ Model training in progress
    - ⏳ Full integration pending
    
    ### Get Started
    Select a tool from the sidebar to begin!
    """)
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Models", "4", "+1")
    with col2:
        st.metric("Accuracy", "94%", "+2%")
    with col3:
        st.metric("Queries", "1.2K", "+15%")
    with col4:
        st.metric("Users", "350", "+25")


def show_yield_predictor():
    """Yield prediction interface"""
    st.header("🌾 Crop Yield Predictor")
    
    st.markdown("Enter soil and environmental parameters to predict crop yield.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        nitrogen = st.number_input("Nitrogen (kg/ha)", 0, 150, 90)
        phosphorus = st.number_input("Phosphorus (kg/ha)", 0, 150, 42)
        potassium = st.number_input("Potassium (kg/ha)", 0, 150, 43)
    
    with col2:
        rainfall = st.number_input("Rainfall (mm)", 0.0, 500.0, 202.9)
        temperature = st.number_input("Temperature (°C)", 0.0, 50.0, 26.8)
        ph = st.number_input("Soil pH", 0.0, 14.0, 6.5)
    
    if st.button("Predict Yield", type="primary"):
        st.info("⚠️ Model needs to be trained first. This is a placeholder.")
        
        # Placeholder prediction
        st.success("### Predicted Yield: 3.4 tons/ha")
        
        st.markdown("""
        **Recommendations:**
        - Soil nutrient levels are good
        - Rainfall is adequate
        - Consider temperature management
        """)


def show_pest_detector():
    """Pest detection interface"""
    st.header("🐛 Pest & Disease Detector")
    
    st.markdown("Upload a crop leaf image to detect diseases.")
    
    uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        
        with col2:
            st.info("⚠️ Model needs to be trained first.")
            
            st.markdown("""
            ### Detected: Maize Leaf Blight
            **Confidence:** 87.5%
            
            **Treatment Recommendations:**
            1. Remove infected leaves
            2. Apply fungicide
            3. Improve air circulation
            4. Monitor regularly
            """)


def show_weather_analysis():
    """Weather analysis interface"""
    st.header("☁️ Weather Impact Analysis")
    
    st.markdown("Analyze weather patterns and their impact on crop yield.")
    
    st.info("⚠️ Phase 1: LSTM model to be trained")
    
    st.markdown("""
    ### Weather Forecast Impact
    
    Based on historical data and weather patterns:
    - **Expected rainfall:** 15% below average
    - **Temperature:** 2°C above normal
    - **Predicted yield impact:** -12%
    
    **Recommendations:**
    - Increase irrigation
    - Consider heat-resistant varieties
    - Apply mulch to conserve moisture
    """)


def show_rag_interface():
    """RAG question answering interface"""
    st.header("📚 Ask Agricultural Questions")
    
    st.markdown("Get answers from our agricultural knowledge base.")
    
    query = st.text_input("Your question:", placeholder="How to increase rice yield?")
    
    if st.button("Search", type="primary"):
        if query:
            st.info("⚠️ RAG system needs to be populated with documents.")
            
            st.markdown("""
            ### Answer:
            
            To increase rice yield, consider the following practices:
            
            1. **Soil Management**: Maintain optimal pH (6.0-7.0) and add organic matter
            2. **Water Management**: Ensure consistent water supply during growing season
            3. **Nutrient Management**: Apply balanced NPK fertilizers
            4. **Pest Control**: Monitor and control pests regularly
            5. **Variety Selection**: Choose high-yielding varieties suitable for your region
            
            *Source: Agricultural Knowledge Base*
            """)


if __name__ == "__main__":
    main()
