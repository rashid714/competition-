import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
import datetime
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_metrics_dashboard(metrics: Dict[str, Any]):
    """
    Create metrics dashboard with error handling.
    Handles missing or invalid metrics gracefully.
    """
    try:
        # Get metrics with defaults
        total_weight = metrics.get('total_weight', 0.0)
        total_meals = metrics.get('total_meals', 0.0)
        store_count = metrics.get('store_count', 0)
        donation_count = metrics.get('donation_count', 0)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🍎 Total Weight", f"{total_weight:.1f} lbs")
        
        with col2:
            st.metric("🍽️ Meals Provided", f"{total_meals:.0f}")
        
        with col3:
            st.metric("🏪 Stores", store_count)
        
        with col4:
            st.metric("📦 Items", donation_count)
            
    except Exception as e:
        logger.error(f"Metrics dashboard creation failed: {str(e)}")
        st.warning("Could not display metrics dashboard")

def create_weight_distribution_chart(metrics: Dict[str, Any]):
    """
    Create weight distribution chart with error handling.
    Gracefully handles missing or invalid data.
    """
    try:
        # Get donations data
        from agent import FoodRescueAgent
        agent = FoodRescueAgent()
        session_id = st.session_state.get('current_session', f"daily_{datetime.date.today().strftime('%Y%m%d')}")
        dashboard = agent.get_dashboard(session_id)
        donations = dashboard.get('donations', [])
        
        if not donations:
            st.info("🌱 No donations yet. Start by logging your first surplus!")
            return
        
        # Calculate weight by store
        store_weights = {}
        for donation in donations:
            store = donation.get('store', 'Unknown Store')
            weight = donation.get('weight', 0)
            store_weights[store] = store_weights.get(store, 0) + weight
        
        if not store_weights:
            st.info("No valid store data available for chart")
            return
        
        # Determine theme
        theme = st.session_state.get('theme', 'Light')

        # Create DataFrame
        df = pd.DataFrame({
            'Store': list(store_weights.keys()),
            'Weight': list(store_weights.values())
        })
        
        # Sort by weight descending
        df = df.sort_values('Weight', ascending=True)
        
        # Create horizontal bar chart
        # Choose template and color scale based on theme
        if theme == 'Dark':
            template = 'plotly_dark'
            color_scale = 'Viridis'
            bg_color = 'rgba(0,0,0,0)'
        else:
            template = 'simple_white'
            color_scale = 'Blues'
            bg_color = 'rgba(0,0,0,0)'

        fig = px.bar(
            df,
            x='Weight',
            y='Store',
            orientation='h',
            title='Weight Distribution by Store',
            color='Weight',
            color_continuous_scale=color_scale,
            text='Weight',
            height=400,
            template=template
        )

        # Update layout to be transparent so CSS panel shows through
        fig.update_layout(
            plot_bgcolor=bg_color,
            paper_bgcolor=bg_color,
            xaxis_title='Weight (lbs)',
            yaxis_title=None,
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        # Update traces
        fig.update_traces(
            texttemplate='%{text:.1f} lbs',
            textposition='outside',
            marker_line_width=0
        )

        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        logger.error(f"Weight distribution chart creation failed: {str(e)}")
        st.warning("Could not display weight distribution chart")

def create_donation_timeline(donations: List[Dict[str, Any]]):
    """
    Create donation timeline with error handling.
    Handles missing or invalid donation data gracefully.
    """
    if not donations:
        return
    
    try:
        # Extract hours and create data
        hours = []
        weights = []
        stores = []
        
        for donation in donations:
            try:
                timestamp = donation.get('timestamp', '')
                hour = int(timestamp.split('T')[1][:2]) if 'T' in timestamp else 0
                weight = donation.get('weight', 0)
                store = donation.get('store', 'Unknown')
                
                hours.append(hour)
                weights.append(weight)
                stores.append(store)
            except Exception as e:
                logger.warning(f"Error processing donation for timeline: {str(e)}")
                continue
        
        if not hours:
            return
        
        # Create DataFrame
        df = pd.DataFrame({
            'Hour': hours,
            'Weight': weights,
            'Store': stores
        })
        
        # Determine theme
        theme = st.session_state.get('theme', 'Light')

        if theme == 'Dark':
            template = 'plotly_dark'
            color = '#60A5FA'
            bg_color = 'rgba(0,0,0,0)'
        else:
            template = 'simple_white'
            color = '#16A34A'
            bg_color = 'rgba(0,0,0,0)'

        # Create histogram
        fig = px.histogram(
            df,
            x='Hour',
            y='Weight',
            nbins=24,
            title='Donation Activity by Hour',
            labels={'Hour': 'Hour of Day', 'Weight': 'Weight (lbs)'},
            color_discrete_sequence=[color],
            template=template
        )

        # Update layout
        fig.update_layout(
            plot_bgcolor=bg_color,
            paper_bgcolor=bg_color,
            xaxis_range=[0, 23],
            xaxis_dtick=1,
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        logger.error(f"Donation timeline creation failed: {str(e)}")
        st.warning("Could not display donation timeline")

def create_impact_card(report: str):
    """
    Create impact report card with error handling.
    Always displays something meaningful.
    """
    try:
        st.markdown("""
        <style>
        .impact-card {
            background: linear-gradient(135deg, #4285F4 0%, #34A853 100%);
            border-radius: 16px;
            padding: 25px;
            color: white;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
        }
        .impact-text {
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="impact-card">
            <h2>🌍 Community Impact</h2>
            <div class="impact-text">{report}</div>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        logger.error(f"Impact card creation failed: {str(e)}")
        st.warning(f"Could not display impact report: {report}")
