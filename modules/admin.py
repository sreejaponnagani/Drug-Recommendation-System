# admin.py
import streamlit as st
from mongodb_utils import get_db_collection
from datetime import datetime
from bson.objectid import ObjectId

def admin_dashboard():
    # Initialize session state for admin login
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
    if "admin_username" not in st.session_state:
        st.session_state.admin_username = ""

    # Show login form if not logged in
    if not st.session_state.admin_logged_in:
        render_admin_login()
    else:
        render_admin_panel()

def render_admin_login():
    st.title("🔐 Admin Login")
    
    with st.form("admin_login_form"):
        st.subheader("Administrator Access")
        
        username = st.text_input("👤 Username", placeholder="Enter admin username")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter admin password")
        
        login_button = st.form_submit_button("🚀 Login", use_container_width=True)
        
        if login_button:
            if authenticate_admin(username, password):
                st.session_state.admin_logged_in = True
                st.session_state.admin_username = username
                st.success("✅ Login successful! Redirecting...")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

def authenticate_admin(username, password):
    """Authenticate admin against MongoDB"""
    try:
        # Connect to MongoDB admin collection
        from pymongo import MongoClient
        client = MongoClient("mongodb+srv://sreejaponnagani:Sreeja0410@cluster0.q0xku.mongodb.net/")
        db = client["drug_recommender_db"]
        admins_col = db["admins"]
        
        # Check if admin exists
        admin = admins_col.find_one({"username": username, "password": password})
        return admin is not None
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return False

def render_admin_panel():
    # Header with logout option
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"🔐 Admin Dashboard")
    with col2:
        st.write(f"**Logged in as:** {st.session_state.admin_username}")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.admin_logged_in = False
            st.session_state.admin_username = ""
            st.rerun()
    
    st.markdown("---")
    
    # Connect to MongoDB
    try:
        users_col = get_db_collection()
        
        # Admin Stats
        st.subheader("📊 Dashboard Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_users = users_col.count_documents({})
            st.metric("Total Users", total_users)
        
        with col2:
            # You can add more metrics here
            st.metric("Active Today", "N/A")
        
        with col3:
            st.metric("New This Week", "N/A")
        
        with col4:
            st.metric("System Status", "✅ Online")
        
        st.markdown("---")
        
        # User Management Section
        st.subheader("👥 User Management")
        
        # Add New User Form
        with st.expander("➕ Add New User", expanded=False):
            with st.form("add_user_form"):
                st.write("**Create New User Account**")
                
                col1, col2 = st.columns(2)
                with col1:
                    new_name = st.text_input("Full Name", placeholder="John Doe")
                    new_email = st.text_input("Email Address", placeholder="john@example.com")
                with col2:
                    new_password = st.text_input("Password", type="password", placeholder="Secure password")
                    new_age = st.number_input("Age", min_value=1, max_value=120, value=30)
                
                new_allergies = st.text_area("Allergies", placeholder="List any allergies (comma separated)")
                
                add_button = st.form_submit_button("👤 Add User", use_container_width=True)
                
                if add_button:
                    if new_name and new_email and new_password:
                        # Check if email already exists
                        existing_user = users_col.find_one({"email": new_email})
                        if existing_user:
                            st.error("❌ User with this email already exists!")
                        else:
                            # Insert new user
                            users_col.insert_one({
                                "full_name": new_name,
                                "email": new_email,
                                "password": new_password,
                                "age": new_age,
                                "allergies": new_allergies,
                                "created_at": datetime.now(),
                                "is_active": True
                            })
                            st.success(f"✅ User {new_name} added successfully!")
                            st.rerun()
                    else:
                        st.error("❌ Please fill in all required fields (Name, Email, Password)")
        
        st.markdown("---")
        
        # Display Existing Users
        st.write(f"**📋 Registered Users ({total_users})**")
        
        # Search and filter options
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input("🔍 Search users by name or email", placeholder="Type to search...")
        with col2:
            items_per_page = st.selectbox("Users per page", [5, 10, 20, 50], index=1)
        
        # Fetch users with optional search
        query = {}
        if search_term:
            query = {
                "$or": [
                    {"full_name": {"$regex": search_term, "$options": "i"}},
                    {"email": {"$regex": search_term, "$options": "i"}}
                ]
            }
        
        users = list(users_col.find(query))
        
        if users:
            # Pagination
            total_users = len(users)
            page_number = st.number_input("Page", min_value=1, value=1, step=1)
            start_idx = (page_number - 1) * items_per_page
            end_idx = start_idx + items_per_page
            users_to_display = users[start_idx:end_idx]
            
            st.write(f"Showing {len(users_to_display)} of {total_users} users")
            
            for user in users_to_display:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"""
                        **👤 Name:** {user.get('full_name', 'N/A')}  
                        **📧 Email:** {user.get('email', 'N/A')}  
                        **🎂 Age:** {user.get('age', 'N/A')}  
                        **⚠️ Allergies:** {user.get('allergies', 'None')}  
                        **📅 Joined:** {user.get('created_at', 'Unknown').strftime('%Y-%m-%d') if user.get('created_at') else 'Unknown'}
                        """)
                    
                    with col2:
                        if st.button(f"✏️ Edit", key=f"edit_{user.get('_id')}"):
                            st.session_state.editing_user = user.get('_id')
                            st.rerun()
                    
                    with col3:
                        if st.button(f"🗑️ Delete", key=f"delete_{user.get('_id')}"):
                            users_col.delete_one({"_id": user.get('_id')})
                            st.success(f"✅ User {user.get('full_name')} deleted successfully")
                            st.rerun()
                    
                    st.markdown("---")
            
            # Pagination controls
            total_pages = (total_users + items_per_page - 1) // items_per_page
            if total_pages > 1:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.write(f"Page {page_number} of {total_pages}")
                    prev_col, next_col = st.columns(2)
                    with prev_col:
                        if page_number > 1 and st.button("⬅️ Previous"):
                            st.rerun()
                    with next_col:
                        if page_number < total_pages and st.button("Next ➡️"):
                            st.rerun()
        
        else:
            st.info("ℹ️ No users found matching your search criteria.")
            
    except Exception as e:
        st.error(f"❌ Database connection error: {e}")
        st.info("ℹ️ Please check your MongoDB connection and try again.")

# Edit User Functionality (optional enhancement)
def edit_user_form(user_id, users_col):
    """Form to edit user details"""
    user = users_col.find_one({"_id": user_id})
    if user:
        with st.form(f"edit_user_{user_id}"):
            st.subheader(f"✏️ Edit User: {user.get('full_name')}")
            
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Full Name", value=user.get('full_name', ''))
                new_email = st.text_input("Email", value=user.get('email', ''))
            with col2:
                new_age = st.number_input("Age", min_value=1, max_value=120, value=user.get('age', 30))
                new_password = st.text_input("Password", type="password", placeholder="Leave blank to keep current")
            
            new_allergies = st.text_area("Allergies", value=user.get('allergies', ''))
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Save Changes"):
                    update_data = {
                        "full_name": new_name,
                        "email": new_email,
                        "age": new_age,
                        "allergies": new_allergies
                    }
                    if new_password:
                        update_data["password"] = new_password
                    
                    users_col.update_one({"_id": user_id}, {"$set": update_data})
                    st.success("✅ User updated successfully!")
                    del st.session_state.editing_user
                    st.rerun()
            
            with col2:
                if st.form_submit_button("❌ Cancel"):
                    del st.session_state.editing_user
                    st.rerun()