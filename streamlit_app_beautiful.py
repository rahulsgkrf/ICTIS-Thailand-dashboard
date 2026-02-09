"""
SmartCom 2026 - Beautiful Feature-Complete Dashboard
Streamlit version with ALL HTML features + Live Editing
"""

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# ============================================
# CONFIGURATION
# ============================================
VERSION = "v1.0"
CONFERENCE_NAME = "SmartCom"
CONFERENCE_YEAR = "2026"

# Custom CSS for beautiful styling (matches your HTML)
st.set_page_config(
    page_title=f"{CONFERENCE_NAME} {CONFERENCE_YEAR}",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject custom CSS to match your HTML design
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }
    
    .block-container {
        padding: 2rem;
        max-width: 1600px;
    }
    
    /* Header styling */
    .header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    /* Stats cards */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Decision badges */
    .badge-accept {
        background: #d4edda;
        color: #155724;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    
    .badge-reject {
        background: #f8d7da;
        color: #721c24;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    
    .badge-hold {
        background: #fff3cd;
        color: #856404;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    
    .badge-revision {
        background: #ffe5cc;
        color: #8b4513;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    
    .badge-pending {
        background: #e9ecef;
        color: #495057;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    
    /* Paper ID styling */
    .paper-id {
        color: #667eea;
        font-weight: 700;
        font-size: 1.1rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: white;
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        font-weight: 600;
    }
    
    /* Search boxes */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #dee2e6;
        padding: 0.75rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 12px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 12px;
        font-weight: 600;
        border: 1px solid #e9ecef;
    }
    
    .streamlit-expanderHeader:hover {
        background: #f8f9fa;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Author/Institution cards */
    .info-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin: 0.5rem 0;
        transition: all 0.3s;
    }
    
    .info-card:hover {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transform: scale(1.01);
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# GOOGLE SHEETS CONNECTION (Same as before)
# ============================================
@st.cache_resource
def get_google_sheets_connection():
    """Connect to Google Sheets"""
    try:
        credentials_dict = st.secrets["gcp_service_account"]
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return None

@st.cache_data(ttl=10)
def load_data_from_sheets():
    """Load data from Google Sheets"""
    try:
        client = get_google_sheets_connection()
        if client is None:
            return None, None
        
        sheet_url = st.secrets.get("sheet_url", "")
        spreadsheet = client.open_by_url(sheet_url)
        
        submissions_sheet = spreadsheet.worksheet("Submissions")
        authors_sheet = spreadsheet.worksheet("Author Master")
        
        submissions_df = pd.DataFrame(submissions_sheet.get_all_records())
        authors_df = pd.DataFrame(authors_sheet.get_all_records())
        
        submissions_df.columns = submissions_df.columns.str.strip()
        authors_df.columns = authors_df.columns.str.strip()
        
        return submissions_df, authors_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

def update_decision_in_sheet(paper_id, new_decision):
    """Update decision in Google Sheet"""
    try:
        client = get_google_sheets_connection()
        sheet_url = st.secrets.get("sheet_url", "")
        spreadsheet = client.open_by_url(sheet_url)
        submissions_sheet = spreadsheet.worksheet("Submissions")
        
        cell = submissions_sheet.find(str(paper_id))
        if cell:
            decision_col = 4
            submissions_sheet.update_cell(cell.row, decision_col, new_decision)
            st.cache_data.clear()
            return True
        return False
    except Exception as e:
        st.error(f"Error updating: {e}")
        return False

# ============================================
# DATA PROCESSING
# ============================================
def process_data(submissions_df, authors_df):
    """Process data same as HTML version"""
    authors_grouped = authors_df.groupby('Paper id').apply(
        lambda x: x[['Author', 'Email id', 'Country', 'City', 'Affiliation']].to_dict('records')
    ).to_dict()
    
    papers_data = []
    for paper_id in submissions_df['Paper id'].unique():
        paper_info = submissions_df[submissions_df['Paper id'] == paper_id].iloc[0]
        
        date_str = str(paper_info.get('Date', ''))
        try:
            if pd.notna(paper_info.get('Date')):
                dt = pd.to_datetime(paper_info['Date'], errors='coerce')
                formatted_date = dt.strftime('%d-%b') if pd.notna(dt) else date_str
            else:
                formatted_date = "N/A"
        except:
            formatted_date = date_str
        
        decision_raw = str(paper_info.get('Decision', '')) if pd.notna(paper_info.get('Decision')) else ""
        decision = "" if decision_raw.strip().lower() in ['accept?', 'nan', ''] else decision_raw.strip()
        
        papers_data.append({
            'paper_id': int(paper_id),
            'title': str(paper_info.get('Paper Title', '')),
            'decision': decision,
            'date': formatted_date,
            'keywords': str(paper_info.get('Keywords', '')) if pd.notna(paper_info.get('Keywords')) else '',
            'abstract': str(paper_info.get('Abstract', '')) if pd.notna(paper_info.get('Abstract')) else '',
            'authors': authors_grouped.get(paper_id, [])
        })
    
    return sorted(papers_data, key=lambda x: x['paper_id'])

def get_decision_badge(decision):
    """Return HTML badge for decision"""
    if not decision:
        return '<span class="badge-pending">Pending</span>'
    
    decision_upper = decision.upper()
    if decision_upper == 'ACCEPT':
        return '<span class="badge-accept">ACCEPT</span>'
    elif decision_upper == 'REJECT':
        return '<span class="badge-reject">REJECT</span>'
    elif decision_upper == 'HOLD':
        return '<span class="badge-hold">HOLD</span>'
    elif decision_upper == 'REVISION':
        return '<span class="badge-revision">REVISION</span>'
    else:
        return f'<span class="badge-pending">{decision}</span>'

# ============================================
# AUTHENTICATION
# ============================================
def check_authentication():
    """Authentication check"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown('<div class="header"><h1>🔐 SmartCom 2026 Login</h1></div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("👤 Username", key="login_user")
            password = st.text_input("🔑 Password", type="password", key="login_pass")
            
            if st.button("🚀 Login", use_container_width=True):
                users = st.secrets.get("users", {})
                if username in users and users[username]["password"] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.role = users[username]["role"]
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        st.stop()

# ============================================
# MAIN APP
# ============================================
def main():
    check_authentication()
    
    # Beautiful Header
    st.markdown(f'''
    <div class="header">
        <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">{CONFERENCE_NAME} {CONFERENCE_YEAR}</h1>
        <p style="font-size: 1.2rem; opacity: 0.95;">Conference Paper Submissions Dashboard</p>
        <p style="font-size: 0.9rem; opacity: 0.8; margin-top: 0.5rem;">Version: {VERSION} | User: {st.session_state.username} | Role: {st.session_state.role.upper()}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("🔄 Loading data..."):
        submissions_df, authors_df = load_data_from_sheets()
    
    if submissions_df is None or authors_df is None:
        st.error("Failed to load data. Please check configuration.")
        return
    
    papers_data = process_data(submissions_df, authors_df)
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stat-card"><h2 style="margin:0;">{len(papers_data)}</h2><p style="margin:0;">Total Papers</p></div>', unsafe_allow_html=True)
    with col2:
        accepted = sum(1 for p in papers_data if p['decision'] == 'ACCEPT')
        st.markdown(f'<div class="stat-card" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);"><h2 style="margin:0;">{accepted}</h2><p style="margin:0;">Accepted</p></div>', unsafe_allow_html=True)
    with col3:
        rejected = sum(1 for p in papers_data if p['decision'] == 'REJECT')
        st.markdown(f'<div class="stat-card" style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);"><h2 style="margin:0;">{rejected}</h2><p style="margin:0;">Rejected</p></div>', unsafe_allow_html=True)
    with col4:
        pending = sum(1 for p in papers_data if not p['decision'])
        st.markdown(f'<div class="stat-card" style="background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);"><h2 style="margin:0;">{pending}</h2><p style="margin:0;">Pending</p></div>', unsafe_allow_html=True)
    
    st.write("")
    
    # Tabs matching HTML design
    tab1, tab2, tab3, tab4 = st.tabs(["📄 Papers", "👥 Authors (Repeated)", "🏛️ Institutions (Repeated)", "🌍 Countries"])
    
    with tab1:
        show_papers_tab(papers_data)
    
    with tab2:
        show_authors_tab(papers_data)
    
    with tab3:
        show_institutions_tab(papers_data)
    
    with tab4:
        show_countries_tab(papers_data)
    
    # Logout button at bottom
    if st.button("🚪 Logout", key="logout_btn"):
        st.session_state.authenticated = False
        st.rerun()

# ============================================
# PAPERS TAB
# ============================================
def show_papers_tab(papers_data):
    """Papers tab with all HTML features"""
    
    # Search filters (3 columns like HTML)
    col1, col2, col3 = st.columns(3)
    with col1:
        search_id = st.text_input("🔍 Search by Paper ID (e.g., 6 or 6,15)", key="search_paper_id")
    with col2:
        search_title = st.text_input("📄 Search by Title", key="search_title")
    with col3:
        search_author = st.text_input("👤 Search by Author", key="search_author")
    
    # Filter papers
    filtered_papers = papers_data
    
    if search_id:
        if ',' in search_id:
            ids = [int(x.strip()) for x in search_id.split(',') if x.strip().isdigit()]
            filtered_papers = [p for p in filtered_papers if p['paper_id'] in ids]
        else:
            filtered_papers = [p for p in filtered_papers if str(search_id) in str(p['paper_id'])]
    
    if search_title:
        filtered_papers = [p for p in filtered_papers if search_title.lower() in p['title'].lower()]
    
    if search_author:
        filtered_papers = [p for p in filtered_papers 
                          if any(search_author.lower() in author['Author'].lower() 
                                for author in p['authors'])]
    
    st.caption(f"📊 Showing {len(filtered_papers)} of {len(papers_data)} papers")
    
    # Create beautiful table with Paper ID, Title, Decision, Date
    if filtered_papers:
        # Build table data
        table_data = []
        for paper in filtered_papers:
            table_data.append({
                'Paper ID': paper['paper_id'],
                'Title': paper['title'][:80] + '...' if len(paper['title']) > 80 else paper['title'],
                'Decision': paper['decision'] if paper['decision'] else 'Pending',
                'Date': paper['date']
            })
        
        # Display as dataframe with clickable rows
        df_display = pd.DataFrame(table_data)
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Paper ID": st.column_config.NumberColumn("Paper ID", format="%d"),
                "Title": st.column_config.TextColumn("Title"),
                "Decision": st.column_config.TextColumn("Decision"),
                "Date": st.column_config.TextColumn("Date")
            }
        )
        
        st.write("")
        st.write("👇 **Click on a paper below to view details:**")
        st.write("")
        
        # Show detailed expandable view for each paper
        for paper in filtered_papers:
            with st.expander(f"**Paper {paper['paper_id']}**: {paper['title']}", expanded=False):
                show_paper_details(paper)
    else:
        st.info("📭 No papers found matching your search criteria")

def show_paper_details(paper):
    """Show detailed paper information"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"**📅 Date:** {paper['date']}")
        st.markdown(f"**📊 Decision:** {get_decision_badge(paper['decision'])}", unsafe_allow_html=True)
        
        # Edit decision if user is editor
        if st.session_state.role == 'editor':
            st.write("")
            new_decision = st.selectbox(
                "Change Decision Status",
                ['', 'ACCEPT', 'REJECT', 'HOLD', 'REVISION'],
                index=0 if not paper['decision'] else ['', 'ACCEPT', 'REJECT', 'HOLD', 'REVISION'].index(paper['decision']) if paper['decision'] in ['ACCEPT', 'REJECT', 'HOLD', 'REVISION'] else 0,
                key=f"decision_{paper['paper_id']}"
            )
            
            if st.button(f"💾 Save Decision", key=f"save_{paper['paper_id']}"):
                if update_decision_in_sheet(paper['paper_id'], new_decision):
                    st.success("✅ Decision updated successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Failed to update decision")
    
    with col2:
        st.markdown(f'<p class="paper-id">Paper ID: {paper["paper_id"]}</p>', unsafe_allow_html=True)
    
    st.divider()
    
    # Abstract with show more/less
    st.markdown("**📝 Abstract:**")
    if len(paper['abstract']) > 300:
        if f"show_full_{paper['paper_id']}" not in st.session_state:
            st.session_state[f"show_full_{paper['paper_id']}"] = False
        
        if st.session_state[f"show_full_{paper['paper_id']}"]:
            st.write(paper['abstract'])
            if st.button("👆 Show less", key=f"less_{paper['paper_id']}"):
                st.session_state[f"show_full_{paper['paper_id']}"] = False
                st.rerun()
        else:
            st.write(paper['abstract'][:300] + "...")
            if st.button("👇 Show more", key=f"more_{paper['paper_id']}"):
                st.session_state[f"show_full_{paper['paper_id']}"] = True
                st.rerun()
    else:
        st.write(paper['abstract'])
    
    # Keywords
    if paper['keywords']:
        st.markdown("**🏷️ Keywords:**")
        keywords = [k.strip() for k in paper['keywords'].split('\n') if k.strip()]
        st.write(" • ".join(keywords))
    
    # Authors table
    st.markdown("**👥 Authors:**")
    if paper['authors']:
        authors_df = pd.DataFrame(paper['authors'])
        st.dataframe(
            authors_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Author": st.column_config.TextColumn("Author"),
                "Email id": st.column_config.TextColumn("Email"),
                "City": st.column_config.TextColumn("City"),
                "Country": st.column_config.TextColumn("Country"),
                "Affiliation": st.column_config.TextColumn("Affiliation")
            }
        )

# ============================================
# AUTHORS TAB
# ============================================
def show_authors_tab(papers_data):
    """Authors tab matching HTML design"""
    
    # Search
    col1, col2 = st.columns(2)
    with col1:
        search_name = st.text_input("👤 Search by Author Name", key="search_author_name")
    with col2:
        search_paper_id = st.text_input("🔢 Search by Paper ID (e.g., 6 or 6,15)", key="search_author_paper")
    
    # Calculate statistics
    author_stats = {}
    for paper in papers_data:
        for author in paper['authors']:
            name = author['Author']
            if name not in author_stats:
                author_stats[name] = {
                    'papers': [],
                    'info': author
                }
            author_stats[name]['papers'].append({
                'id': paper['paper_id'],
                'title': paper['title'],
                'decision': paper['decision']
            })
    
    # Filter by name
    if search_name:
        author_stats = {k: v for k, v in author_stats.items() 
                       if search_name.lower() in k.lower()}
    
    # Filter by paper ID
    if search_paper_id:
        if ',' in search_paper_id:
            paper_ids = [int(x.strip()) for x in search_paper_id.split(',') if x.strip().isdigit()]
            author_stats = {k: v for k, v in author_stats.items() 
                           if any(p['id'] in paper_ids for p in v['papers'])}
        else:
            search_id = int(search_paper_id) if search_paper_id.isdigit() else None
            if search_id:
                author_stats = {k: v for k, v in author_stats.items() 
                               if any(p['id'] == search_id for p in v['papers'])}
    
    # Sort by paper count
    sorted_authors = sorted(author_stats.items(), 
                           key=lambda x: len(x[1]['papers']), 
                           reverse=True)
    
    st.caption(f"📊 Showing {len(sorted_authors)} authors")
    
    # Display authors with paper badges
    for name, data in sorted_authors:
        info = data['info']
        papers = data['papers']
        
        # Filter papers if paper ID search is active
        if search_paper_id:
            if ',' in search_paper_id:
                paper_ids = [int(x.strip()) for x in search_paper_id.split(',') if x.strip().isdigit()]
                papers = [p for p in papers if p['id'] in paper_ids]
            else:
                search_id = int(search_paper_id) if search_paper_id.isdigit() else None
                if search_id:
                    papers = [p for p in papers if p['id'] == search_id]
        
        # Create header with paper count and badges
        badge_html = ""
        for p in papers:
            decision_class = f"badge-{p['decision'].lower()}" if p['decision'] else "badge-pending"
            badge_html += f'<span class="{decision_class}" style="margin-right: 0.5rem; cursor: pointer;">{p["id"]}</span>'
        
        with st.expander(f"**{name}** — {len(papers)} paper(s)", expanded=False):
            st.markdown(badge_html, unsafe_allow_html=True)
            st.write("")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**📧 Email:** {info.get('Email id', 'N/A')}")
                st.write(f"**🏙️ City:** {info.get('City', 'N/A')}")
            with col2:
                st.write(f"**🌍 Country:** {info.get('Country', 'N/A')}")
                st.write(f"**🏛️ Affiliation:** {info.get('Affiliation', 'N/A')}")
            
            st.write("")
            st.write("**📄 Papers:**")
            for p in papers:
                decision_badge = get_decision_badge(p['decision'])
                st.markdown(f"• Paper **{p['id']}**: {p['title']} {decision_badge}", unsafe_allow_html=True)

# ============================================
# INSTITUTIONS TAB
# ============================================
def show_institutions_tab(papers_data):
    """Institutions tab matching HTML design"""
    
    # Search
    col1, col2 = st.columns(2)
    with col1:
        search_name = st.text_input("🏛️ Search by Institution Name", key="search_inst_name")
    with col2:
        search_paper_id = st.text_input("🔢 Search by Paper ID (e.g., 6 or 6,15)", key="search_inst_paper")
    
    # Calculate statistics
    inst_stats = {}
    for paper in papers_data:
        for author in paper['authors']:
            inst = author.get('Affiliation', 'Unknown')
            if inst not in inst_stats:
                inst_stats[inst] = {'papers': {}}
            
            if paper['paper_id'] not in inst_stats[inst]['papers']:
                inst_stats[inst]['papers'][paper['paper_id']] = {
                    'title': paper['title'],
                    'decision': paper['decision']
                }
    
    # Filter by name
    if search_name:
        inst_stats = {k: v for k, v in inst_stats.items() 
                     if search_name.lower() in k.lower()}
    
    # Filter by paper ID
    if search_paper_id:
        if ',' in search_paper_id:
            paper_ids = [int(x.strip()) for x in search_paper_id.split(',') if x.strip().isdigit()]
            inst_stats = {k: v for k, v in inst_stats.items() 
                         if any(pid in paper_ids for pid in v['papers'].keys())}
        else:
            search_id = int(search_paper_id) if search_paper_id.isdigit() else None
            if search_id:
                inst_stats = {k: v for k, v in inst_stats.items() 
                             if search_id in v['papers'].keys()}
    
    # Sort by paper count
    sorted_insts = sorted(inst_stats.items(), 
                         key=lambda x: len(x[1]['papers']), 
                         reverse=True)
    
    st.caption(f"📊 Showing {len(sorted_insts)} institutions")
    
    # Display institutions
    for inst_name, data in sorted_insts:
        papers = data['papers']
        
        # Filter papers if paper ID search is active
        if search_paper_id:
            if ',' in search_paper_id:
                paper_ids = [int(x.strip()) for x in search_paper_id.split(',') if x.strip().isdigit()]
                papers = {k: v for k, v in papers.items() if k in paper_ids}
            else:
                search_id = int(search_paper_id) if search_paper_id.isdigit() else None
                if search_id:
                    papers = {k: v for k, v in papers.items() if k == search_id}
        
        # Create badges
        badge_html = ""
        for pid, pdata in papers.items():
            decision_class = f"badge-{pdata['decision'].lower()}" if pdata['decision'] else "badge-pending"
            badge_html += f'<span class="{decision_class}" style="margin-right: 0.5rem; cursor: pointer;">{pid}</span>'
        
        with st.expander(f"**{inst_name}** — {len(papers)} paper(s)", expanded=False):
            st.markdown(badge_html, unsafe_allow_html=True)
            st.write("")
            st.write("**📄 Papers:**")
            for pid, pdata in papers.items():
                decision_badge = get_decision_badge(pdata['decision'])
                st.markdown(f"• Paper **{pid}**: {pdata['title']} {decision_badge}", unsafe_allow_html=True)

# ============================================
# COUNTRIES TAB
# ============================================
def show_countries_tab(papers_data):
    """Countries tab"""
    country_stats = {}
    for paper in papers_data:
        for author in paper['authors']:
            country = author.get('Country', 'Unknown')
            if country not in country_stats:
                country_stats[country] = set()
            country_stats[country].add(paper['paper_id'])
    
    sorted_countries = sorted(country_stats.items(), 
                             key=lambda x: len(x[1]), 
                             reverse=True)
    
    cols = st.columns(3)
    for idx, (country, papers) in enumerate(sorted_countries):
        with cols[idx % 3]:
            st.markdown(f'<div class="stat-card"><h3 style="margin:0;">{country}</h3><p style="margin:0.5rem 0 0 0;">{len(papers)} papers</p></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
