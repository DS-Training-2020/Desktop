import streamlit as st
from auth import check_auth, get_current_user
from database import get_all_appointments
from datetime import datetime

st.set_page_config(page_title="Admin", page_icon="🔒")

check_auth()
user = get_current_user()

if user["role"] != "admin":
    st.error("You don't have permission to access this page.")
    st.stop()

st.title("Admin Dashboard")

# Display all appointments with patient names
st.header("All Booked Appointments")
appointments = get_all_appointments()

if not appointments:
    st.info("No appointments found.")
else:
    for appt in appointments:
        appointment_date = datetime.fromisoformat(appt['date'])
        created_at = datetime.fromisoformat(appt['created_at'])
        
        with st.expander(f"👤 {appt['name']} - {appt['sub_type']}"):
            st.write(f"**Patient Name:** {appt['name']}")
            st.write(f"**Appointment Type:** {appt['appointment_type']}")
            st.write(f"**Service:** {appt['sub_type']}")
            st.write(f"**When:** {appointment_date.strftime('%A, %B %d, %Y at %I:%M %p')}")
            st.write(f"**Status:** {appt['status']}")
            st.write(f"**Booked On:** {created_at.strftime('%Y-%m-%d %H:%M')}")
            
            if st.button("Cancel Appointment", key=f"cancel_{appt['id']}"):
                # Add cancellation logic here
                st.warning(f"Appointment for {appt['name']} would be cancelled")

# Export functionality with name
st.header("Export Data")
if st.button("Export All Appointments to CSV"):
    import pandas as pd
    from io import StringIO
    
    data = []
    for appt in appointments:
        appointment_date = datetime.fromisoformat(appt['date'])
        
        data.append({
            "Patient Name": appt["name"],
            "Appointment Type": appt["appointment_type"],
            "Service": appt["sub_type"],
            "Date": appointment_date.strftime('%Y-%m-%d'),
            "Time": appointment_date.strftime('%H:%M'),
            "Status": appt["status"],
            "Booked On": datetime.fromisoformat(appt['created_at']).strftime('%Y-%m-%d %H:%M')
        })
    
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False)
    
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="appointments_export.csv",
        mime="text/csv"
    )