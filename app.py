import streamlit as st
from docxtpl import DocxTemplate
import io
import os
import subprocess
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from num2words import num2words

# --- Helper Functions ---
def format_indian_number(num_str):
    """Formats a number string with Indian commas (e.g., 1,00,000)"""
    num_str = str(num_str).replace(",", "").strip()
    if not num_str.isdigit(): 
        return num_str
    
    s = num_str
    if len(s) <= 3: 
        return s
    
    res = s[-3:]
    s = s[:-3]
    while len(s) > 0:
        res = s[-2:] + "," + res
        s = s[:-2]
    return res

def get_indian_words(num_str):
    """Converts a number string to Indian English words"""
    num_str = str(num_str).replace(",", "").strip()
    if not num_str.isdigit(): 
        return ""
    
    # Convert to words, replace hyphens with spaces, and Capitalize Each Word
    words = num2words(int(num_str), lang='en_IN').replace("-", " ").title()
    return words

# --- UI Setup ---
st.set_page_config(page_title="Rent Agreement Generator", page_icon="📄")
st.title("📄 Rent Agreement Generator")
st.write("Fill in the details below to instantly generate a formatted rent agreement.")

# Create the input form
with st.form("rent_form"):
    st.subheader("Landlord & Tenant Details")
    landlord_details = st.text_input("Landlord Full Details", placeholder="e.g., JATINDER GUPTA S/O...")
    landlord_name = st.text_input("Landlord Name (For Signature)", placeholder="e.g., JATINDER GUPTA")
    tenant_details = st.text_input("Tenant Full Details", placeholder="e.g., NIDHI BHARGAVA R/O...")
    tenant_name = st.text_input("Tenant Name (For Signature)", placeholder="e.g., NIDHI BHARGAVA")
    
    st.subheader("Property Details")
    rented_address = st.text_input("Rented Address", placeholder="e.g., H. NO. 4106, SECTOR 46D, CHANDIGARH")
    
    col_prop1, col_prop2 = st.columns(2)
    with col_prop1:
        floor = st.selectbox("Floor Rented", ["Ground Floor", "First Floor", "Second Floor", "Third Floor", "Entire Property"])
    with col_prop2:
        room_desc = st.text_input("Room Description", value="3 BHK Semi-Furnished, with 3 Washroom Attached along with Dining Hall")
    
    include_annexure = st.radio("Include Annexure clause?", ["Yes", "No"])
    
    st.subheader("Tenancy Dates")
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        start_date = st.date_input("Tenancy Start Date")
    with col_date2:
        duration_months = st.number_input("Duration (Months)", value=11, min_value=1)
        # Automatically calculate end date (Start Date + Months)
        end_date = start_date + relativedelta(months=duration_months)
        st.info(f"Auto-Calculated End Date: **{end_date.strftime('%d-%m-%Y')}**")
        
    st.subheader("Financial Details")
    col_fin1, col_fin2 = st.columns(2)
    with col_fin1:
        rent_input = st.text_input("Rent Amount", value="42000")
        security_input = st.text_input("Security Amount", value="84000")
        percent_inc = st.text_input("Percentage Increase (%)", value="7")
    with col_fin2:
        charge_type = st.selectbox("Water/Garbage Charges are:", ["excluding", "including"])
        
        # Format numbers and generate words automatically
        rent_formatted = format_indian_number(rent_input)
        rent_words = get_indian_words(rent_input)
        
        security_formatted = format_indian_number(security_input)
        security_words = get_indian_words(security_input)
        
        # Display the calculated words to the user as confirmation
        st.caption(f"**Rent in words:** {rent_words}")
        st.caption(f"**Security in words:** {security_words}")

    # New Toggle for the Security Clause
    include_non_refundable = st.radio("Include 6-Month Non-Refundable Security Clause?", ["Yes", "No"])

    st.subheader("Export Options")
    export_format = st.radio("Choose download format:", ["Word Document (.docx)", "PDF (.pdf)"])

    # Submit button
    submitted = st.form_submit_button("Generate Agreement")

# --- Generation Logic ---
if submitted:
    try:
        # Load the Word template
        doc = DocxTemplate("Rent_Template.docx")
        
        # Logic for conditional annexure text
        annexure_text = ", with Annexure enclosed therein" if include_annexure == "Yes" else ""
        
        # Logic for conditional non-refundable security text
        if include_non_refundable == "Yes":
            non_refundable_text = "The Security amount so given will be NON-REFUNDABLE IF VACATED WITHIN SIX MONTHS from commencement of the tenancy period."
        else:
            non_refundable_text = ""
            
        # Format dates as DD-MM-YYYY
        formatted_start = start_date.strftime("%d-%m-%Y")
        formatted_end = end_date.strftime("%d-%m-%Y")
        
        # Dictionary of replacements
        context = {
            "LANDLORD_DETAILS": landlord_details,
            "TENANT_DETAILS": tenant_details,
            "RENTED_ADDRESS": rented_address,
            "FLOOR": floor,
            "ROOM_DESC": room_desc,
            "ANNEXURE_TEXT": annexure_text,
            "START_DATE": formatted_start,
            "END_DATE": formatted_end,
            "CHARGE_TYPE": charge_type,
            "RENT_NUM": rent_formatted, 
            "RENT_WORDS": rent_words,   
            "SECURITY_NUM": security_formatted,
            "SECURITY_WORDS": security_words,
            "PERCENT_INC": percent_inc,
            "LANDLORD_NAME": landlord_name,
            "TENANT_NAME": tenant_name,
            "NON_REFUNDABLE_SECURITY": non_refundable_text # New tag added here
        }
        
        # Render the template
        doc.render(context)
        
        st.success("✅ Agreement generated successfully!")
        
        # Handle Word Download
        if export_format == "Word Document (.docx)":
            bio = io.BytesIO()
            doc.save(bio)
            st.download_button(
                label="⬇️ Download Word Document",
                data=bio.getvalue(),
                file_name=f"Rent_Agreement_{tenant_name.replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
        # Handle PDF Download (Requires LibreOffice on the server)
        elif export_format == "PDF (.pdf)":
            with st.spinner("Converting to PDF... this might take a few seconds."):
                temp_docx = "temp_agreement.docx"
                doc.save(temp_docx)
                
                subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', temp_docx])
                
                temp_pdf = "temp_agreement.pdf"
                
                if os.path.exists(temp_pdf):
                    with open(temp_pdf, "rb") as pdf_file:
                        pdf_bytes = pdf_file.read()
                        
                    st.download_button(
                        label="⬇️ Download PDF Document",
                        data=pdf_bytes,
                        file_name=f"Rent_Agreement_{tenant_name.replace(' ', '_')}.pdf",
                        mime="application/pdf"
                    )
                    os.remove(temp_pdf)
                else:
                    st.error("PDF conversion failed. Please try downloading as a Word document instead.")
                
                if os.path.exists(temp_docx):
                    os.remove(temp_docx)
                    
    except Exception as e:
        st.error(f"An error occurred: {e}")
