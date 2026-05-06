import streamlit as st
from docxtpl import DocxTemplate
import io

# Set up the page layout
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
    
    # Radio button for Annexure
    include_annexure = st.radio("Include Annexure clause?", ["Yes", "No"])
    
    st.subheader("Tenancy & Financial Details")
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        start_date = st.date_input("Tenancy Start Date")
    with col_date2:
        end_date = st.date_input("Tenancy End Date")
        
    col_fin1, col_fin2 = st.columns(2)
    with col_fin1:
        rent_num = st.text_input("Rent Amount (Numbers)", value="42000")
        security_num = st.text_input("Security Amount (Numbers)", value="84000")
        percent_inc = st.text_input("Percentage Increase", value="7")
    with col_fin2:
        rent_words = st.text_input("Rent Amount (Words)", value="Forty Two Thousand")
        security_words = st.text_input("Security Amount (Words)", value="Eighty Four Thousand")
        charge_type = st.selectbox("Water/Garbage Charges are:", ["excluding", "including"])

    # Submit button
    submitted = st.form_submit_button("Generate Agreement")

# Logic to run when the form is submitted
if submitted:
    try:
        # Load the Word template using docxtpl
        doc = DocxTemplate("Rent_Template.docx")
        
        # Logic for conditional annexure text
        if include_annexure == "Yes":
            annexure_text = ", with Annexure enclosed therein"
        else:
            annexure_text = ""
            
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
            "RENT_NUM": rent_num,
            "RENT_WORDS": rent_words,
            "SECURITY_NUM": security_num,
            "SECURITY_WORDS": security_words,
            "PERCENT_INC": percent_inc,
            "LANDLORD_NAME": landlord_name,
            "TENANT_NAME": tenant_name
        }
        
        # Render the template with the dictionary
        doc.render(context)
        
        # Save the generated document into memory
        bio = io.BytesIO()
        doc.save(bio)
        
        st.success("✅ Agreement generated successfully!")
        
        # Provide the download button
        st.download_button(
            label="⬇️ Download Rent Agreement",
            data=bio.getvalue(),
            file_name=f"Rent_Agreement_{tenant_name.replace(' ', '_')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        st.error(f"An error occurred: {e}. Please ensure 'Rent_Template.docx' is in the same folder.")