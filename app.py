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

# Sidebar navigation
st.sidebar.image("https://via.placeholder.com/200x80/1f77b4/ffffff?text=Hospital+Logo", use_container_width=True)
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio(
    "Go to",
    ["🏠 Dashboard Overview", "👨‍⚕️ Clinicians", "🏥 Services", "💰 Pricing", "📈 Analytics"],
    label_visibility="collapsed"
)

# Check if data loaded successfully
if clinicians_df is None:
    st.stop()

# ===========================
# PAGE 1: DASHBOARD OVERVIEW
# ===========================
if page == "🏠 Dashboard Overview":
    st.title("🏥 Hospital Management Dashboard")
    st.markdown("### Welcome to the Hospital Analytics Portal")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_doctors = len(clinicians_df)
        st.metric("👨‍⚕️ Total Clinicians", total_doctors)
    
    with col2:
        total_services = len(services_df)
        st.metric("🏥 Total Services", total_services)
    
    with col3:
        mapped_doctors = len(mapping_df[mapping_df['Services Offered'] != 'No Match'])
        mapping_rate = f"{(mapped_doctors/total_doctors*100):.1f}%"
        st.metric("✅ Mapped Clinicians", f"{mapped_doctors} ({mapping_rate})")
    
    with col4:
        unique_specializations = clinicians_df['Specialization'].nunique()
        st.metric("🎯 Specializations", unique_specializations)
    
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
        st.subheader("🗺️ Service Mapping Coverage")
        mapping_status = mapping_df['Services Offered'].apply(lambda x: 'Mapped' if x != 'No Match' else 'Not Mapped').value_counts()
        fig2 = px.pie(
            values=mapping_status.values,
            names=mapping_status.index,
            color=mapping_status.index,
            color_discrete_map={'Mapped': '#2ecc71', 'Not Mapped': '#e74c3c'}
        )
        fig2.update_traces(textposition='inside', textinfo='percent+label')
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Service Distribution
    st.subheader("📈 Clinicians per Service")
    
    # Explode services for doctors with multiple services
    service_list = []
    for _, row in mapping_df.iterrows():
        if row['Services Offered'] != 'No Match':
            services = [s.strip() for s in row['Services Offered'].split(',')]
            service_list.extend(services)
    
    service_counts = pd.Series(service_list).value_counts()
    fig3 = px.bar(
        x=service_counts.index,
        y=service_counts.values,
        labels={'x': 'Service', 'y': 'Number of Clinicians'},
        color=service_counts.values,
        color_continuous_scale='Viridis'
    )
    fig3.update_layout(xaxis_tickangle=-45, height=450, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)
    
    # Data Quality Insights
    st.markdown("---")
    st.subheader("📋 Data Quality Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-box">
            <h4>👥 Clinicians Database</h4>
            <p>✅ Complete records: <b>{}</b></p>
            <p>📊 Unique specializations: <b>{}</b></p>
        </div>
        """.format(total_doctors, unique_specializations), unsafe_allow_html=True)
    
    with col2:
        unmapped = len(mapping_df[mapping_df['Services Offered'] == 'No Match'])
        st.markdown("""
        <div class="info-box">
            <h4>🔗 Service Mapping</h4>
            <p>✅ Mapped: <b>{}</b></p>
            <p>⚠️ Unmapped: <b>{}</b></p>
        </div>
        """.format(mapped_doctors, unmapped), unsafe_allow_html=True)
    
    with col3:
        # Count non-empty price rows (excluding headers and empty rows)
        price_services = prices_df[prices_df.iloc[:, 0].notna()].iloc[:, 0].nunique()
        st.markdown("""
        <div class="info-box">
            <h4>💰 Pricing Data</h4>
            <p>📋 Services with pricing: <b>{}</b></p>
            <p>🏢 Locations covered: <b>2</b></p>
        </div>
        """.format(price_services), unsafe_allow_html=True)

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
    
    # Service mapping filter
    mapping_filter = st.sidebar.radio(
        "Service Mapping Status",
        ["All", "Mapped Only", "Unmapped Only"]
    )
    
    # Search box
    search_term = st.sidebar.text_input("🔎 Search Clinician Name", "")
    
    # Apply filters
    filtered_df = mapping_df.copy()
    
    if selected_spec != 'All':
        filtered_df = filtered_df[filtered_df['Specialization'] == selected_spec]
    
    if mapping_filter == "Mapped Only":
        filtered_df = filtered_df[filtered_df['Services Offered'] != 'No Match']
    elif mapping_filter == "Unmapped Only":
        filtered_df = filtered_df[filtered_df['Services Offered'] == 'No Match']
    
    if search_term:
        filtered_df = filtered_df[filtered_df['Name'].str.contains(search_term, case=False, na=False)]
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Filtered Results", len(filtered_df))
    with col2:
        mapped = len(filtered_df[filtered_df['Services Offered'] != 'No Match'])
        st.metric("Mapped", mapped)
    with col3:
        unmapped = len(filtered_df[filtered_df['Services Offered'] == 'No Match'])
        st.metric("Unmapped", unmapped)
    
    st.markdown("---")
    
    # Display table with styling
    st.subheader(f"📋 Showing {len(filtered_df)} Clinician(s)")
    
    # Add styling to services column
    display_df = filtered_df.copy()
    display_df['Services Offered'] = display_df['Services Offered'].apply(
        lambda x: '❌ Not Mapped' if x == 'No Match' else f'✅ {x}'
    )
    
    st.dataframe(
        display_df,
        use_container_width=True,
        height=500,
        hide_index=True
    )
    
    # Export option
    st.markdown("---")
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name="clinicians_filtered.csv",
        mime="text/csv"
    )

# ===========================
# PAGE 3: SERVICES
# ===========================
elif page == "🏥 Services":
    st.title("🏥 Services Overview")
    
    # Create service analysis
    service_analysis = []
    all_services = services_df['Services'].tolist()
    
    for service in all_services:
        # Count doctors for this service
        doctor_count = mapping_df['Services Offered'].str.contains(service, case=False, na=False).sum()
        
        # Check if pricing exists
        has_pricing = service in prices_df.iloc[:, 0].values
        
        service_analysis.append({
            'Service': service,
            'Number of Clinicians': doctor_count,
            'Pricing Available': '✅ Yes' if has_pricing else '❌ No'
        })
    
    service_df = pd.DataFrame(service_analysis)
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        show_pricing = st.selectbox(
            "Filter by Pricing Availability",
            ["All Services", "With Pricing Only", "Without Pricing"]
        )
    
    with col2:
        min_doctors = st.slider("Minimum Clinicians", 0, service_df['Number of Clinicians'].max(), 0)
    
    # Apply filters
    filtered_services = service_df.copy()
    
    if show_pricing == "With Pricing Only":
        filtered_services = filtered_services[filtered_services['Pricing Available'] == '✅ Yes']
    elif show_pricing == "Without Pricing":
        filtered_services = filtered_services[filtered_services['Pricing Available'] == '❌ No']
    
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
        st.metric("Total Doctor Assignments", total_doctors)
    
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
            color_discrete_map={'✅ Yes': '#2ecc71', '❌ No': '#e74c3c'}
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
    
    # Get unique service categories from prices
    price_categories = prices_df.iloc[:, 0].dropna().unique()
    
    # Sidebar filters
    st.sidebar.markdown("### 🔍 Filters")
    selected_category = st.sidebar.selectbox(
        "Select Service Category",
        ['All'] + sorted([cat for cat in price_categories if pd.notna(cat) and cat.strip() != ''])
    )
    
    search_price = st.sidebar.text_input("🔎 Search Service", "")
    
    # Display pricing
    if selected_category == 'All':
        st.subheader("📋 All Services Pricing")
        
        # Display by category
        current_category = None
        for idx, row in prices_df.iterrows():
            service_name = row.iloc[0]
            
            if pd.isna(service_name) or service_name.strip() == '':
                continue
            
            # Check if this is a category header
            if pd.isna(row.iloc[1]) and pd.isna(row.iloc[2]):
                current_category = service_name
                st.markdown(f"### 🏷️ {current_category}")
                continue
            
            # Apply search filter
            if search_price and search_price.lower() not in str(service_name).lower():
                continue
            
            # Display service with prices
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{service_name}**")
            with col2:
                canary_price = row.iloc[1] if pd.notna(row.iloc[1]) else 'N/A'
                st.write(f"🏢 {canary_price}")
            with col3:
                orpington_price = row.iloc[2] if pd.notna(row.iloc[2]) else 'N/A'
                st.write(f"🏢 {orpington_price}")
            
            st.markdown("---")
    
    else:
        st.subheader(f"📋 {selected_category} Pricing")
        
        # Find the category and display its services
        in_category = False
        services_found = False
        
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown("**Service**")
        with col2:
            st.markdown("**Canary Wharf**")
        with col3:
            st.markdown("**Orpington**")
        
        st.markdown("---")
        
        for idx, row in prices_df.iterrows():
            service_name = row.iloc[0]
            
            if pd.isna(service_name) or service_name.strip() == '':
                continue
            
            # Check if this is our category
            if service_name == selected_category:
                in_category = True
                continue
            
            # Check if we hit a new category
            if in_category and pd.isna(row.iloc[1]) and pd.isna(row.iloc[2]):
                break
            
            # Display services in this category
            if in_category:
                # Apply search filter
                if search_price and search_price.lower() not in str(service_name).lower():
                    continue
                
                services_found = True
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{service_name}**")
                with col2:
                    canary_price = row.iloc[1] if pd.notna(row.iloc[1]) else 'N/A'
                    st.write(f"{canary_price}")
                with col3:
                    orpington_price = row.iloc[2] if pd.notna(row.iloc[2]) else 'N/A'
                    st.write(f"{orpington_price}")
                
                st.markdown("---")
        
        if not services_found:
            st.info("No services found in this category.")

# ===========================
# PAGE 5: ANALYTICS
# ===========================
elif page == "📈 Analytics":
    st.title("📈 Advanced Analytics")
    
    tab1, tab2, tab3 = st.tabs(["Specialization Analysis", "Service Coverage", "Department Insights"])
    
    with tab1:
        st.subheader("🎯 Specialization Distribution")
        
        # Top specializations
        spec_counts = clinicians_df['Specialization'].value_counts()
        
        fig1 = px.treemap(
            names=spec_counts.index,
            parents=[""] * len(spec_counts),
            values=spec_counts.values,
            title="Clinician Distribution by Specialization"
        )
        fig1.update_layout(height=500)
        st.plotly_chart(fig1, use_container_width=True)
        
        # Statistics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Most Common Specialization", spec_counts.index[0])
            st.write(f"**Count:** {spec_counts.values[0]} clinicians")
        
        with col2:
            single_spec = (spec_counts == 1).sum()
            st.metric("Unique Specializations", single_spec)
            st.write(f"**Specializations with only 1 clinician**")
    
    with tab2:
        st.subheader("🗺️ Service Coverage Matrix")
        
        # Create a heatmap-style view
        service_list = []
        for _, row in mapping_df.iterrows():
            if row['Services Offered'] != 'No Match':
                services = [s.strip() for s in row['Services Offered'].split(',')]
                service_list.extend(services)
        
        service_counts = pd.Series(service_list).value_counts()
        
        # Calculate coverage percentage
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
        
        # Group specializations into departments (simplified)
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
        <p>Data last updated: 2024</p>
    </div>
    """, unsafe_allow_html=True)