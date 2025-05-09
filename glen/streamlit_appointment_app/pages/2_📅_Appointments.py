import streamlit as st
from datetime import datetime, time, date
from auth import check_auth, get_current_user
from database import (
    create_appointment,
    get_user_appointments,
    update_appointment,
    delete_appointment
)
import pytz

st.set_page_config(page_title="Appointments", page_icon="📅")

check_auth()
user = get_current_user()

# Appointment options
APPOINTMENT_TYPES = {
    "Consultation": [
        "Eye consult",
        "Dental consult",
        "General consult",
        "Physician specialist",
        "Gynecological consult",
        "Antenatal consult"
    ],
    "Medical screening": [
        "Full body checkup",
        "Cardiac screening",
        "Diabetes screening",
        "Cancer screening",
        "Vision screening",
        "Hearing screening"
    ]
}

def appointment_form(key_suffix=""):
    with st.form(key=f"appointment_form_{key_suffix}"):
        appointment_type = st.selectbox(
            "Appointment Type",
            list(APPOINTMENT_TYPES.keys()),
            key=f"type_{key_suffix}"
        )
        
        sub_type = st.selectbox(
            "Specific Service",
            APPOINTMENT_TYPES[appointment_type],
            key=f"sub_type_{key_suffix}"
        )
        
        appointment_date = st.date_input(
            "Date",
            min_value=date.today(),
            key=f"date_{key_suffix}"
        )
        
        appointment_time = st.time_input(
            "Time",
            time(9, 0),
            key=f"time_{key_suffix}"
        )
        
        submitted = st.form_submit_button("Book Appointment")
        
        if submitted:
            appointment_datetime = datetime.combine(
                appointment_date,
                appointment_time
            ).astimezone(pytz.utc)
            
            return {
                "type": appointment_type,
                "sub_type": sub_type,
                "datetime": appointment_datetime
            }
    return None

def display_appointments():
    st.header("Your Appointments")
    appointments = get_user_appointments(user["username"])
    
    if not appointments:
        st.info("You have no upcoming appointments.")
        return
    
    for i, appt in enumerate(appointments):
        appointment_date = datetime.fromisoformat(appt['date'])
        
        with st.expander(f"{appt['sub_type']} - {appointment_date.strftime('%Y-%m-%d %I:%M %p')}"):
            st.write(f"**Type:** {appt['appointment_type']}")
            st.write(f"**Service:** {appt['sub_type']}")
            st.write(f"**When:** {appointment_date.strftime('%A, %B %d, %Y at %I:%M %p')}")
            st.write(f"**Status:** {appt['status']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Edit ✏️", key=f"edit_{i}"):
                    st.session_state["editing"] = appt["id"]
            
            with col2:
                if st.button(f"Cancel ❌", key=f"cancel_{i}"):
                    delete_appointment(appt["id"])
                    st.success("Appointment cancelled successfully!")
                    st.rerun()

def edit_appointment(appointment_id):
    st.header("Edit Appointment")
    appointment = next(
        (a for a in get_user_appointments(user["username"]) if a["id"] == appointment_id),
        None
    )
    
    if not appointment:
        st.error("Appointment not found")
        return
    
    if st.button("Back to appointments"):
        del st.session_state["editing"]
        st.rerun()
    
    result = appointment_form("edit")
    if result:
        update_appointment(
            appointment_id,
            result["type"],
            result["sub_type"],
            result["datetime"]
        )
        del st.session_state["editing"]
        st.success("Appointment updated successfully!")
        st.rerun()

def main():
    st.title("Book an Appointment")
    
    if "editing" in st.session_state:
        edit_appointment(st.session_state["editing"])
        return
    
    # Create new appointment
    st.header("New Appointment")
    result = appointment_form()
    if result:
        create_appointment(
            user["username"],
            result["type"],
            result["sub_type"],
            result["datetime"]
        )
        st.success("Appointment booked successfully!")
        st.rerun()
    
    display_appointments()

if __name__ == "__main__":
    main()