import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Hospital Management Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 {
        color: #1f77b4;
        padding-bottom: 10px;
        border-bottom: 3px solid #1f77b4;
    }
    h2 {
        color: #2c3e50;
    }
    .info-box {
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
    }
    .price-category {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0 10px 0;
        font-size: 20px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Load data function
@st.cache_data
def load_data():
    try:
        clinicians = pd.read_csv('clinicians.csv')
        services = pd.read_csv('services.csv')
        mapping = pd.read_csv('doctor_services_mapping.csv')
        prices = pd.read_csv('Lyca_prices.csv')
        return clinicians, services, mapping, prices
    except FileNotFoundError as e:
        st.error(f"Error loading files: {e}")
        st.info("Please ensure all CSV files are in the same directory as this script.")
        return None, None, None, None

# Load the data
clinicians_df, services_df, mapping_df, prices_df = load_data()

# Check if data loaded successfully
if clinicians_df is None:
    st.stop()

# Pricing category mapping to services
PRICING_SERVICE_MAP = {
    'MRI': 'MRI',
    'CT': 'CT Scan',
    'Ultrasound': 'Ultrasound',
    'X-Ray': 'X-Ray',
    'Cardiology': 'Cardiology',
    'Physiotherapy': 'Physiotherapy and sports health',
    'Audiology': 'Audiology',
    'One Stop Breast Clinic': 'Breast care services'
}

# Sidebar navigation
# st.sidebar.image("https://via.placeholder.com/200x80/1f77b4/ffffff?text=Hospital+Logo", use_container_width=True)
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio(
    "Go to",
    ["🏠 Dashboard Overview", "👨‍⚕️ Clinicians", "🏥 Services", "💰 Pricing", "📈 Analytics"],
    label_visibility="collapsed"
)

# Filter out unmapped entries for display
mapped_df = mapping_df[mapping_df['Services Offered'] != 'No Match'].copy()

# ===========================
# PAGE 1: DASHBOARD OVERVIEW
# ===========================
if page == "🏠 Dashboard Overview":
    st.title("🏥 Hospital Management Dashboard")
    st.markdown("### Welcome to the Hospital Analytics Portal")
    
    # Key Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_doctors = len(clinicians_df)
        st.metric("👨‍⚕️ Total Clinicians", total_doctors)
    
    with col2:
        total_services = len(services_df)
        st.metric("🏥 Total Services", total_services)
    
    with col3:
        mapped_doctors = len(mapped_df)
        # st.metric("✅ Active Service Providers", mapped_doctors)
        unique_specializations = clinicians_df['Specialization'].nunique()
        st.metric("🎯 Specializations", unique_specializations)
    
    # with col4:
    #     unique_specializations = clinicians_df['Specialization'].nunique()
    #     st.metric("🎯 Specializations", unique_specializations)
    
    st.markdown("---")
    
    # Two column layout for visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Top 10 Specializations")
        spec_counts = clinicians_df['Specialization'].value_counts().head(10)
        fig1 = px.bar(
            x=spec_counts.values,
            y=spec_counts.index,
            orientation='h',
            labels={'x': 'Number of Clinicians', 'y': 'Specialization'},
            color=spec_counts.values,
            color_continuous_scale='Blues'
        )
        fig1.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("🏥 Most Popular Services")
        service_list = []
        for _, row in mapped_df.iterrows():
            services = [s.strip() for s in row['Services Offered'].split(',')]
            service_list.extend(services)
        
        service_counts = pd.Series(service_list).value_counts().head(10)
        fig2 = px.bar(
            x=service_counts.values,
            y=service_counts.index,
            orientation='h',
            labels={'x': 'Number of Clinicians', 'y': 'Service'},
            color=service_counts.values,
            color_continuous_scale='Viridis'
        )
        fig2.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Service Distribution
    st.subheader("📈 Service Coverage Across Hospital")
    
    service_list_all = []
    for _, row in mapped_df.iterrows():
        services = [s.strip() for s in row['Services Offered'].split(',')]
        service_list_all.extend(services)
    
    service_counts_all = pd.Series(service_list_all).value_counts()
    fig3 = px.bar(
        x=service_counts_all.index,
        y=service_counts_all.values,
        labels={'x': 'Service', 'y': 'Number of Clinicians'},
        color=service_counts_all.values,
        color_continuous_scale='Teal'
    )
    fig3.update_layout(xaxis_tickangle=-45, height=450, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)
    
    # Data Quality Insights
    st.markdown("---")
    st.subheader("📋 Hospital Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-box">
            <h4>👥 Clinicians Database</h4>
            <p>✅ Total clinicians: <b>{}</b></p>
            <p>📊 Unique specializations: <b>{}</b></p>
        </div>
        """.format(total_doctors, unique_specializations), unsafe_allow_html=True)
    
    with col2:
        unique_services = len(service_counts_all)
        st.markdown("""
        <div class="info-box">
            <h4>🔗 Services Offered</h4>
            <p>✅ Active services: <b>{}</b></p>
            <p>👨‍⚕️ Service providers: <b>{}</b></p>
        </div>
        """.format(unique_services, mapped_doctors), unsafe_allow_html=True)
    
    with col3:
        services_with_pricing = len(PRICING_SERVICE_MAP)
        st.markdown("""
        <div class="info-box">
            <h4>💰 Pricing Information</h4>
            <p>📋 Services with pricing: <b>{}</b></p>
            <p>🏢 Locations covered: <b>2</b></p>
        </div>
        """.format(services_with_pricing), unsafe_allow_html=True)

# ===========================
# PAGE 2: CLINICIANS
# ===========================
elif page == "👨‍⚕️ Clinicians":
    st.title("👨‍⚕️ Clinicians Directory")
    
    # Filters in sidebar
    st.sidebar.markdown("### 🔍 Filters")
    
    # Specialization filter
    all_specializations = ['All'] + sorted(clinicians_df['Specialization'].unique().tolist())
    selected_spec = st.sidebar.selectbox("Filter by Specialization", all_specializations)
    
    # Search box
    search_term = st.sidebar.text_input("🔎 Search Clinician Name", "")
    
    # Option to show all or only those with services
    show_option = st.sidebar.radio(
        "Display Options",
        ["Show All Clinicians", "Show Service Providers Only"]
    )
    
    # Apply filters
    if show_option == "Show Service Providers Only":
        filtered_df = mapped_df.copy()
    else:
        filtered_df = mapping_df.copy()
        filtered_df['Services Offered'] = filtered_df['Services Offered'].replace('No Match', '-')
    
    if selected_spec != 'All':
        filtered_df = filtered_df[filtered_df['Specialization'] == selected_spec]
    
    if search_term:
        filtered_df = filtered_df[filtered_df['Name'].str.contains(search_term, case=False, na=False)]
    
    # Key Metrics Row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Showing Results", len(filtered_df))
    with col2:
        unique_specs = filtered_df['Specialization'].nunique()
        st.metric("Specializations", unique_specs)
    with col3:
        service_list = []
        for _, row in filtered_df.iterrows():
            if row['Services Offered'] not in ['No Match', '-', '']:
                services = [s.strip() for s in row['Services Offered'].split(',')]
                service_list.extend(services)
        unique_services = len(set(service_list))
        st.metric("Services Covered", unique_services)
    
    st.markdown("---")
    
    # Visual Analytics Section
    st.subheader("📊 Visual Analytics")
    
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        # Top 10 Specializations in filtered data
        st.markdown("**🎯 Top Specializations**")
        spec_distribution = filtered_df['Specialization'].value_counts().head(10)
        
        fig_spec = px.bar(
            x=spec_distribution.values,
            y=spec_distribution.index,
            orientation='h',
            labels={'x': 'Number of Clinicians', 'y': 'Specialization'},
            color=spec_distribution.values,
            color_continuous_scale='Blues',
            height=400
        )
        fig_spec.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_spec, use_container_width=True)
    
    with viz_col2:
        # Service Provider vs Non-Provider
        st.markdown("**✅ Service Provider Status**")
        provider_status = filtered_df['Services Offered'].apply(
            lambda x: 'Has Services' if x not in ['No Match', '-', ''] else 'No Services'
        ).value_counts()
        
        fig_provider = px.pie(
            values=provider_status.values,
            names=provider_status.index,
            color=provider_status.index,
            color_discrete_map={'Has Services': '#2ecc71', 'No Services': '#95a5a6'},
            height=400
        )
        fig_provider.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_provider, use_container_width=True)
    
    # Services Breakdown
    if len(service_list) > 0:
        st.markdown("---")
        st.markdown("**🏥 Services Distribution**")
        
        service_counts = pd.Series(service_list).value_counts().head(15)
        
        fig_services = px.bar(
            x=service_counts.values,
            y=service_counts.index,
            orientation='h',
            labels={'x': 'Number of Clinicians', 'y': 'Service'},
            color=service_counts.values,
            color_continuous_scale='Viridis',
            height=500
        )
        fig_services.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_services, use_container_width=True)
    
    st.markdown("---")
    
    # Clinician Cards Grid (Visual Display)
    st.subheader("👥 Clinician Cards")
    
    # Additional filters for card view
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        # Get all unique specializations from filtered data
        card_specializations = ['All'] + sorted(filtered_df['Specialization'].unique().tolist())
        selected_card_spec = st.selectbox(
            "🎯 Filter by Specialization:",
            options=card_specializations,
            key='card_spec_filter'
        )
    
    with filter_col2:
        # Get all unique services from filtered data
        all_services_list = []
        for _, row in filtered_df.iterrows():
            if row['Services Offered'] not in ['No Match', '-', '']:
                services = [s.strip() for s in row['Services Offered'].split(',')]
                all_services_list.extend(services)
        unique_services_for_filter = ['All'] + sorted(list(set(all_services_list)))
        
        selected_card_service = st.selectbox(
            "🏥 Filter by Service:",
            options=unique_services_for_filter,
            key='card_service_filter'
        )
    
    with filter_col3:
        # Name starting letter filter
        letters = ['All'] + list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        selected_letter = st.selectbox(
            "🔤 Name starts with:",
            options=letters,
            key='card_letter_filter'
        )
    
    # Apply card-specific filters
    card_filtered_df = filtered_df.copy()
    
    if selected_card_spec != 'All':
        card_filtered_df = card_filtered_df[card_filtered_df['Specialization'] == selected_card_spec]
    
    if selected_card_service != 'All':
        card_filtered_df = card_filtered_df[
            card_filtered_df['Services Offered'].str.contains(selected_card_service, case=False, na=False)
        ]
    
    if selected_letter != 'All':
        card_filtered_df = card_filtered_df[
            card_filtered_df['Name'].str.upper().str.startswith(selected_letter)
        ]
    
    # Show count of filtered results
    st.info(f"📋 Showing {len(card_filtered_df)} clinician(s) based on filters")
    
    # Display clinicians in card format
    if len(card_filtered_df) > 0:
        num_cols = 3
        clinician_rows = [card_filtered_df.iloc[i:i+num_cols] for i in range(0, min(len(card_filtered_df), 12), num_cols)]
        
        for row_data in clinician_rows:
            cols = st.columns(num_cols)
            for idx, (_, clinician) in enumerate(row_data.iterrows()):
                with cols[idx]:
                    services = clinician['Services Offered']
                    has_services = services not in ['No Match', '-', '']
                    
                    # Create card
                    card_color = "#e8f5e9" if has_services else "#fafafa"
                    st.markdown(f"""
                    <div style="
                        background-color: {card_color};
                        padding: 20px;
                        border-radius: 10px;
                        border-left: 5px solid {'#2ecc71' if has_services else '#95a5a6'};
                        margin-bottom: 15px;
                        min-height: 180px;
                    ">
                        <h4 style="margin: 0; color: #2c3e50;">⚕️{clinician['Name'][:30]}{'...' if len(clinician['Name']) > 30 else ''}</h4>
                                            </h4>
                        <p style="color: #7f8c8d; margin: 5px 0;"><strong>Specialization:</strong></p>
                                            </p>
                        <p style="color: #34495e; margin: 0; font-size: 14px;">{clinician['Specialization']} </p>
                        <p style="color: #7f8c8d; margin-top: 10px; margin-bottom: 5px;"><strong>Services:</strong></p>
                        <p style="color: #27ae60; margin: 0; font-size: 13px;">{services if has_services else 'No services listed'}</p>
                    </div>
                        """, unsafe_allow_html=True)
        
        # Show more button for remaining clinicians
        if len(card_filtered_df) > 12:
            with st.expander(f"📋 View All {len(card_filtered_df)} Clinicians (Table View)"):
                st.dataframe(
                    card_filtered_df,
                    use_container_width=True,
                    height=500,
                    hide_index=True
                )
        
        # Show complete table if 12 or less
        if len(card_filtered_df) <= 12:
            st.markdown("---")
            st.subheader("📋 Complete List")
            st.dataframe(
                card_filtered_df,
                use_container_width=True,
                height=400,
                hide_index=True
            )
    else:
        st.warning("No clinicians found matching the selected filters. Please adjust your filter criteria.")
    
    # Export option (export the card-filtered data)
    st.markdown("---")
    csv = card_filtered_df.to_csv(index=False) if len(card_filtered_df) > 0 else filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name="clinicians_filtered.csv",
        mime="text/csv"
    )# ===========================
# PAGE 3: SERVICES
# ===========================
elif page == "🏥 Services":
    st.title("🏥 Services Overview")
    
    # Create service analysis for ALL services from services.csv
    service_analysis = []
    all_services = services_df['Services'].tolist()
    
    for service in all_services:
        # Count doctors for this service from mapped data
        doctor_count = 0
        for _, row in mapped_df.iterrows():
            if service in row['Services Offered']:
                doctor_count += 1
        
        # Check if pricing exists using the mapping
        has_pricing = service in PRICING_SERVICE_MAP.values()
        
        service_analysis.append({
            'Service': service,
            'Number of Clinicians': doctor_count,
            'Pricing Available': '✅ Yes' if has_pricing else '📋 No price mentioned'
        })
    
    service_df = pd.DataFrame(service_analysis)
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        show_pricing = st.selectbox(
            "Filter by Pricing Availability",
            ["All Services", "With Pricing", "Contact for Pricing"]
        )
    
    with col2:
        max_doctors = service_df['Number of Clinicians'].max()
        min_doctors = st.slider("Minimum Clinicians", 0, int(max_doctors), 0)
    
    # Apply filters
    filtered_services = service_df.copy()
    
    if show_pricing == "With Pricing":
        filtered_services = filtered_services[filtered_services['Pricing Available'] == '✅ Yes']
    elif show_pricing == "Contact for Pricing":
        filtered_services = filtered_services[filtered_services['Pricing Available'] == '📋 No price mentioned']
    
    filtered_services = filtered_services[filtered_services['Number of Clinicians'] >= min_doctors]
    
    # Sort by number of clinicians
    filtered_services = filtered_services.sort_values('Number of Clinicians', ascending=False)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Services", len(filtered_services))
    with col2:
        with_pricing = len(filtered_services[filtered_services['Pricing Available'] == '✅ Yes'])
        st.metric("With Pricing", with_pricing)
    with col3:
        total_doctors = filtered_services['Number of Clinicians'].sum()
        st.metric("Total Assignments", total_doctors)
    
    st.markdown("---")
    
    # Display table
    st.subheader("📊 Services Details")
    st.dataframe(
        filtered_services,
        use_container_width=True,
        height=400,
        hide_index=True
    )
    
    # Visualization
    st.markdown("---")
    st.subheader("📈 Service Visualization")
    
    tab1, tab2 = st.tabs(["Clinician Distribution", "Pricing Coverage"])
    
    
    with tab1:
        fig = px.bar(
            filtered_services.sort_values('Number of Clinicians'),
            x='Number of Clinicians',
            y='Service',
            orientation='h',
            color='Number of Clinicians',
            color_continuous_scale='Blues',
            labels={'Number of Clinicians': 'Number of Clinicians'}
        )
        fig.update_layout(height=max(400, len(filtered_services) * 25), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        pricing_counts = filtered_services['Pricing Available'].value_counts()
        fig2 = px.pie(
            values=pricing_counts.values,
            names=pricing_counts.index,
            color=pricing_counts.index,
            color_discrete_map={'✅ Yes': '#2ecc71', '📋 Contact Us': '#3498db'}
        )
        fig2.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig2, use_container_width=True)

# ===========================
# PAGE 4: PRICING
# ===========================
elif page == "💰 Pricing":
    st.title("💰 Service Pricing")
    
    st.markdown("""
    <div class="info-box">
        ℹ️ Prices are shown for two locations: <b>Canary Wharf</b> and <b>Orpington</b>
    </div>
    """, unsafe_allow_html=True)
    
    # Load pricing data from individual CSV files
    @st.cache_data
    def load_pricing_csvs():
        pricing_data = {}
        csv_files = {
            'Audiology': 'prices/audiology.csv',
            'One Stop Breast Clinic': 'prices/breast_clinic.csv',
            'Cardiology': 'prices/cardiology.csv',
            'CT': 'prices/ct.csv',
            'Minor Operations': 'prices/minor_operations.csv',
            'MRI': 'prices/mri.csv',
            'Physiotherapy': 'prices/physiotherapy.csv',
            'Ultrasound': 'prices/ultrasound.csv',
            'X-Ray': 'prices/x-ray.csv'
        }
        
        for category, filepath in csv_files.items():
            try:
                # Try multiple encodings to handle special characters like £
                df = None
                for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        df = pd.read_csv(filepath, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                
                if df is not None:
                    # Skip the header row (first row contains category name and location headers)
                    df = df.iloc[1:].reset_index(drop=True)
                    df.columns = ['Service', 'Canary Wharf', 'Orpington']
                    pricing_data[category] = df
                else:
                    st.error(f"Error loading {category}: Unable to decode file with any encoding")
            except Exception as e:
                st.error(f"Error loading {category}: {e}")
        
        return pricing_data
    
    pricing_data = load_pricing_csvs()
    
    # Create tabs for each pricing category
    tabs = st.tabs([
        "🦻 Audiology",
        "🎗️ Breast Clinic", 
        "❤️ Cardiology",
        "🔬 CT",
        "⚕️ Minor Operations",
        "🧲 MRI",
        "🏃 Physiotherapy",
        "📡 Ultrasound",
        "� X-Ray"
    ])
    
    category_names = list(pricing_data.keys())
    
    for idx, tab in enumerate(tabs):
        with tab:
            category = category_names[idx]
            df = pricing_data[category]
            
            # Remove any rows with NaN values
            df = df.dropna(subset=['Service'])
            
            # Display category header
            st.subheader(f"📋 {category} Services")
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Services", len(df))
            
            with col2:
                # Calculate average price for Canary Wharf
                try:
                    canary_prices = []
                    for price in df['Canary Wharf']:
                        price_str = str(price).replace('£', '').replace(',', '').strip()
                        if price_str and price_str != '' and 'From' not in price_str and price_str.replace('.', '').isdigit():
                            canary_prices.append(float(price_str))
                    
                    if canary_prices:
                        avg_canary = sum(canary_prices) / len(canary_prices)
                        st.metric("Avg Price (Canary Wharf)", f"£{avg_canary:,.0f}")
                    else:
                        st.metric("Avg Price (Canary Wharf)", "Varies")
                except:
                    st.metric("Avg Price (Canary Wharf)", "Varies")
            
            with col3:
                # Calculate average price for Orpington
                try:
                    orp_prices = []
                    for price in df['Orpington']:
                        price_str = str(price).replace('£', '').replace(',', '').strip()
                        if price_str and price_str != '' and 'From' not in price_str and price_str.replace('.', '').isdigit():
                            orp_prices.append(float(price_str))
                    
                    if orp_prices:
                        avg_orp = sum(orp_prices) / len(orp_prices)
                        st.metric("Avg Price (Orpington)", f"£{avg_orp:,.0f}")
                    else:
                        st.metric("Avg Price (Orpington)", "Varies")
                except:
                    st.metric("Avg Price (Orpington)", "Varies")
            
            with col4:
                # Price range
                try:
                    all_prices = []
                    for price in list(df['Canary Wharf']) + list(df['Orpington']):
                        price_str = str(price).replace('£', '').replace(',', '').strip()
                        if price_str and price_str != '' and 'From' not in price_str and price_str.replace('.', '').isdigit():
                            all_prices.append(float(price_str))
                    
                    if all_prices:
                        price_range = f"£{min(all_prices):,.0f} - £{max(all_prices):,.0f}"
                        st.metric("Price Range", price_range)
                    else:
                        st.metric("Price Range", "Varies")
                except:
                    st.metric("Price Range", "Varies")
            
            st.markdown("---")
            
            # Display data table
            st.subheader("📊 Price List")
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            st.markdown("---")
            
            # Graphical Analysis
            st.subheader("📈 Graphical Analysis")
            
            # Create two columns for charts
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                # Price comparison bar chart (top 10 services)
                try:
                    chart_data = []
                    for idx_row, row in df.head(10).iterrows():
                        service_name = str(row['Service'])[:30] + '...' if len(str(row['Service'])) > 30 else str(row['Service'])
                        
                        canary_str = str(row['Canary Wharf']).replace('£', '').replace(',', '').strip()
                        if canary_str and canary_str != '' and 'From' not in canary_str and canary_str.replace('.', '').isdigit():
                            chart_data.append({
                                'Service': service_name,
                                'Location': 'Canary Wharf',
                                'Price': float(canary_str)
                            })
                        
                        orp_str = str(row['Orpington']).replace('£', '').replace(',', '').strip()
                        if orp_str and orp_str != '' and 'From' not in orp_str and orp_str.replace('.', '').isdigit():
                            chart_data.append({
                                'Service': service_name,
                                'Location': 'Orpington',
                                'Price': float(orp_str)
                            })
                    
                    if chart_data:
                        chart_df = pd.DataFrame(chart_data)
                        fig1 = px.bar(
                            chart_df,
                            x='Service',
                            y='Price',
                            color='Location',
                            barmode='group',
                            title="Price Comparison (Top 10 Services)",
                            labels={'Price': 'Price (£)'},
                            color_discrete_map={'Canary Wharf': '#3498db', 'Orpington': '#2ecc71'}
                        )
                        fig1.update_layout(xaxis_tickangle=-45, height=450)
                        st.plotly_chart(fig1, use_container_width=True)
                    else:
                        st.info("No numerical price data available for comparison chart.")
                except Exception as e:
                    st.info("Price comparison chart not available.")
            
            with chart_col2:
                # Price distribution pie chart
                try:
                    location_totals = []
                    
                    canary_total = 0
                    for price in df['Canary Wharf']:
                        price_str = str(price).replace('£', '').replace(',', '').strip()
                        if price_str and price_str != '' and 'From' not in price_str and price_str.replace('.', '').isdigit():
                            canary_total += float(price_str)
                    
                    orp_total = 0
                    for price in df['Orpington']:
                        price_str = str(price).replace('£', '').replace(',', '').strip()
                        if price_str and price_str != '' and 'From' not in price_str and price_str.replace('.', '').isdigit():
                            orp_total += float(price_str)
                    
                    if canary_total > 0 or orp_total > 0:
                        fig2 = px.pie(
                            values=[canary_total, orp_total],
                            names=['Canary Wharf', 'Orpington'],
                            title="Total Revenue Potential by Location",
                            color_discrete_map={'Canary Wharf': '#3498db', 'Orpington': '#2ecc71'}
                        )
                        fig2.update_traces(textposition='inside', textinfo='percent+label')
                        fig2.update_layout(height=450)
                        st.plotly_chart(fig2, use_container_width=True)
                    else:
                        st.info("No data available for location distribution.")
                except Exception as e:
                    st.info("Location distribution chart not available.")
            
            # Additional analysis - Price difference heatmap
            st.markdown("---")
            st.subheader("💡 Price Insights")
            
            try:
                price_diff_data = []
                for idx_row, row in df.iterrows():
                    canary_str = str(row['Canary Wharf']).replace('£', '').replace(',', '').strip()
                    orp_str = str(row['Orpington']).replace('£', '').replace(',', '').strip()
                    
                    if (canary_str and canary_str != '' and 'From' not in canary_str and canary_str.replace('.', '').isdigit() and
                        orp_str and orp_str != '' and 'From' not in orp_str and orp_str.replace('.', '').isdigit()):
                        canary_price = float(canary_str)
                        orp_price = float(orp_str)
                        diff = canary_price - orp_price
                        diff_pct = (diff / orp_price * 100) if orp_price > 0 else 0
                        
                        price_diff_data.append({
                            'Service': row['Service'],
                            'Canary Wharf': canary_price,
                            'Orpington': orp_price,
                            'Difference (£)': diff,
                            'Difference (%)': round(diff_pct, 1)
                        })
                
                if price_diff_data:
                    diff_df = pd.DataFrame(price_diff_data)
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        # Top 5 most expensive services
                        st.markdown("**🔺 Top 5 Most Expensive Services (Canary Wharf)**")
                        top_expensive = diff_df.nlargest(5, 'Canary Wharf')[['Service', 'Canary Wharf']]
                        st.dataframe(top_expensive, hide_index=True, use_container_width=True)
                    
                    with col_b:
                        # Top 5 biggest price differences
                        st.markdown("**📊 Top 5 Biggest Price Differences**")
                        top_diff = diff_df.nlargest(5, 'Difference (£)')[['Service', 'Difference (£)', 'Difference (%)']]
                        st.dataframe(top_diff, hide_index=True, use_container_width=True)
                else:
                    st.info("Price comparison data not available.")
            except Exception as e:
                st.info("Price insights not available.")

# ===========================
# PAGE 5: ANALYTICS
# ===========================
elif page == "📈 Analytics":
    st.title("📈 Advanced Analytics")
    
    tab1, tab2, tab3 = st.tabs(["Specialization Analysis", "Service Coverage", "Department Insights"])
    
    with tab1:
        st.subheader("🎯 Specialization Distribution")
        
        spec_counts = clinicians_df['Specialization'].value_counts()
        
        # Create the treemap
        fig1 = px.treemap(
            names=spec_counts.index,
            parents=[""] * len(spec_counts),
            values=spec_counts.values,
            title="Clinician Distribution by Specialization"
        )
        fig1.update_layout(height=500)
        st.plotly_chart(fig1, use_container_width=True)
        
        st.markdown("---")
        
        # Dropdown to select specialization
        st.markdown("### 🔍 View Specialization Details")
        selected_spec = st.selectbox(
            "Select a specialization to view detailed information:",
            options=['-- Select a Specialization --'] + sorted(spec_counts.index.tolist()),
            key='spec_dropdown'
        )
        
        if selected_spec != '-- Select a Specialization --':
            # Filter data for clicked specialization
            spec_clinicians = clinicians_df[clinicians_df['Specialization'] == selected_spec]
            spec_mapped = mapped_df[mapped_df['Specialization'] == selected_spec]
            
            # Create detailed view
            st.markdown(f"""
            <div class="info-box">
                <h3>📋 {selected_spec}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Metrics row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("👨‍⚕️ Total Clinicians", len(spec_clinicians))
            
            with col2:
                active_providers = len(spec_mapped)
                st.metric("✅ Service Providers", active_providers)
            
            with col3:
                # Get unique services for this specialization
                services_offered = []
                for _, row in spec_mapped.iterrows():
                    services = [s.strip() for s in row['Services Offered'].split(',')]
                    services_offered.extend(services)
                unique_services = len(set(services_offered))
                st.metric("🏥 Services Offered", unique_services)
            
            with col4:
                # Calculate percentage of total clinicians
                percentage = (len(spec_clinicians) / len(clinicians_df) * 100)
                st.metric("📊 % of Total", f"{percentage:.1f}%")
            
            # Display clinicians in expandable section
            with st.expander("� View All Clinicians", expanded=True):
                if len(spec_mapped) > 0:
                    display_data = spec_mapped[['Name', 'Services Offered']].copy()
                    st.dataframe(display_data, use_container_width=True, hide_index=True)
                else:
                    st.info("No clinicians with mapped services in this specialization.")
            
            # Services breakdown
            if len(services_offered) > 0:
                st.markdown("---")
                st.markdown("#### 🏥 Service Distribution")
                
                service_counts_spec = pd.Series(services_offered).value_counts()
                
                col_a, col_b = st.columns([2, 1])
                
                with col_a:
                    # Bar chart of services
                    fig_services = px.bar(
                        x=service_counts_spec.values,
                        y=service_counts_spec.index,
                        orientation='h',
                        labels={'x': 'Number of Clinicians', 'y': 'Service'},
                        title=f"Services Offered by {selected_spec}",
                        color=service_counts_spec.values,
                        color_continuous_scale='Blues'
                    )
                    fig_services.update_layout(showlegend=False, height=300)
                    st.plotly_chart(fig_services, use_container_width=True)
                
                with col_b:
                    st.markdown("**📋 Service Breakdown:**")
                    for service, count in service_counts_spec.items():
                        st.write(f"• **{service}**: {count} clinician(s)")
        else:
            # Show summary when nothing is clicked
            st.info("👆 Click on any box in the treemap above to see detailed information about that specialization")
            
            # Show quick stats
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Specializations", len(spec_counts))
            
            with col2:
                st.metric("Most Common", spec_counts.index[0])
                st.caption(f"{spec_counts.values[0]} clinicians")
            
            with col3:
                avg_clinicians = spec_counts.mean()
                st.metric("Average per Specialty", f"{avg_clinicians:.1f}")
    
    with tab2:
        st.subheader("🗺️ Service Coverage Matrix")
        
        service_list = []
        for _, row in mapped_df.iterrows():
            services = [s.strip() for s in row['Services Offered'].split(',')]
            service_list.extend(services)
        
        service_counts = pd.Series(service_list).value_counts()
        
        total_clinicians = len(clinicians_df)
        service_coverage = pd.DataFrame({
            'Service': service_counts.index,
            'Clinicians': service_counts.values,
            'Coverage %': (service_counts.values / total_clinicians * 100).round(1)
        })
        
        fig2 = px.bar(
            service_coverage.sort_values('Coverage %', ascending=True),
            x='Coverage %',
            y='Service',
            orientation='h',
            text='Clinicians',
            color='Coverage %',
            color_continuous_scale='RdYlGn',
            labels={'Coverage %': 'Coverage Percentage'}
        )
        fig2.update_traces(textposition='outside')
        fig2.update_layout(height=max(400, len(service_coverage) * 30))
        st.plotly_chart(fig2, use_container_width=True)
        
        st.dataframe(service_coverage.sort_values('Clinicians', ascending=False), use_container_width=True, hide_index=True)
    
    with tab3:
        st.subheader("🏥 Department Insights")
        
        def categorize_specialization(spec):
            spec_lower = spec.lower()
            if any(word in spec_lower for word in ['cardio', 'heart']):
                return 'Cardiology'
            elif any(word in spec_lower for word in ['ortho', 'bone', 'joint', 'knee', 'hip', 'spine']):
                return 'Orthopaedics'
            elif any(word in spec_lower for word in ['gastro', 'hepato', 'bowel']):
                return 'Gastroenterology'
            elif any(word in spec_lower for word in ['breast', 'oncoplastic']):
                return 'Breast Care'
            elif any(word in spec_lower for word in ['dermat', 'skin']):
                return 'Dermatology'
            elif any(word in spec_lower for word in ['ent', 'ear', 'nose', 'throat']):
                return 'ENT'
            elif any(word in spec_lower for word in ['neuro', 'brain']):
                return 'Neurology/Neurosurgery'
            elif any(word in spec_lower for word in ['gynae', 'obstet', 'women']):
                return 'Women\'s Health'
            elif any(word in spec_lower for word in ['physio', 'therapy']):
                return 'Physiotherapy'
            elif any(word in spec_lower for word in ['gp', 'general practice', 'practitioner']):
                return 'General Practice'
            elif any(word in spec_lower for word in ['urol', 'kidney', 'renal']):
                return 'Urology/Renal'
            elif any(word in spec_lower for word in ['plastic', 'aesthetic', 'cosmetic']):
                return 'Plastic Surgery'
            else:
                return 'Other Specialties'
        
        clinicians_df['Department'] = clinicians_df['Specialization'].apply(categorize_specialization)
        dept_counts = clinicians_df['Department'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig3 = px.pie(
                values=dept_counts.values,
                names=dept_counts.index,
                title="Clinicians by Department"
            )
            fig3.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Department Summary")
            for dept, count in dept_counts.items():
                percentage = (count / len(clinicians_df) * 100)
                st.write(f"**{dept}:** {count} clinicians ({percentage:.1f}%)")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #7f8c8d; padding: 20px;'>
        <p>🏥 Hospital Management Dashboard | Built with Streamlit</p>
    </div>
    """, unsafe_allow_html=True)
