import streamlit as st
import ollama
from fpdf import FPDF
import tempfile
import os
from PyPDF2 import PdfReader
import json

# Function to extract text from a PDF file
def extract_text_from_pdf(file):
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Failed to extract text from PDF: {e}")
        print("HI Aniket")
        return ""

# Function to parse the resume using DeepSeek model
def parse_resume(resume_text):
    prompt = f"""
    Parse the following resume and extract the following details in **valid JSON format**:
    {{
        "Name": "Full Name",
        "ContactInformation": {{
            "Phone": "Phone Number",
            "Email": "Email Address",
            "LinkedIn": "LinkedIn Profile",
            "GitHub": "GitHub Profile",
            "Location": "Location"
        }},
        "ProfessionalSummary": "Summary text",
        "TechnicalSkills": ["Skill 1", "Skill 2", "Skill 3"],
        "Education": [
            {{
                "Institution": "Institution Name",
                "Degree": "Degree",
                "StartDate": "Start Date",
                "EndDate": "End Date",
                "GPA": "GPA"
            }}
        ],
        "ProfessionalExperience": [
            {{
                "Company": "Company Name",
                "Role": "Role Title",
                "StartDate": "Start Date",
                "EndDate": "End Date",
                "Location": "Location",
                "BulletPoints": ["Bullet Point 1", "Bullet Point 2"]
            }}
        ],
        "Publications": {{
            "Title": "Publication Title",
            "Journal": "Journal Name",
            "Volume": "Volume",
            "Issue": "Issue"
        }},
        "Certifications": [
            {{
                "Name": "Certification Name",
                "Issuer": "Issuer Name",
                "Date": "Certification Date"
            }}
        ]
    }}

    Resume:
    {resume_text}
    """
    
    try:
        # Use Ollama to generate the response
        response = ollama.generate(model='llama3.2', prompt=prompt)
        st.write("Model Response:", response['response'])  # Debug: Print the raw response
        
        # Clean the response to ensure it is valid JSON
        response_text = response['response'].strip()
        
        # Remove any non-JSON content (e.g., "Here is the extracted data in valid JSON format:")
        if response_text.startswith("Here is the extracted data in valid JSON format:"):
            response_text = response_text.replace("Here is the extracted data in valid JSON format:", "").strip()
        
        # Parse the cleaned response as JSON
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse the response from the model. The response is not valid JSON: {e}")
        st.write("Raw Response:", response['response'])  # Debug: Print the raw response
        return {}
    except Exception as e:
        st.error(f"An error occurred while parsing the resume: {e}")
        return {}

# Function to generate a PDF resume
def generate_pdf_resume(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add Name
    pdf.cell(200, 10, txt=f"Name: {data['Name']}", ln=True)

    # Add Contact Information
    pdf.cell(200, 10, txt="Contact Information:", ln=True)
    pdf.cell(200, 10, txt=f"- Phone: {data['ContactInformation']['Phone']}", ln=True)
    pdf.cell(200, 10, txt=f"- Email: {data['ContactInformation']['Email']}", ln=True)
    pdf.cell(200, 10, txt=f"- LinkedIn: {data['ContactInformation']['LinkedIn']}", ln=True)
    pdf.cell(200, 10, txt=f"- GitHub: {data['ContactInformation']['GitHub']}", ln=True)
    pdf.cell(200, 10, txt=f"- Location: {data['ContactInformation']['Location']}", ln=True)

    # Add Professional Summary
    pdf.cell(200, 10, txt="Professional Summary:", ln=True)
    pdf.multi_cell(0, 10, txt=data['ProfessionalSummary'])

    # Add Technical Skills
    pdf.cell(200, 10, txt="Technical Skills:", ln=True)
    pdf.multi_cell(0, 10, txt=", ".join(data['TechnicalSkills']))

    # Add Education
    pdf.cell(200, 10, txt="Education:", ln=True)
    for edu in data['Education']:
        pdf.multi_cell(0, 10, txt=f"- {edu['Degree']} at {edu['Institution']} ({edu['StartDate']} - {edu['EndDate']})")

    # Add Professional Experience
    pdf.cell(200, 10, txt="Professional Experience:", ln=True)
    for exp in data['ProfessionalExperience']:
        pdf.multi_cell(0, 10, txt=f"- {exp['Role']} at {exp['Company']} ({exp['StartDate']} - {exp['EndDate']}), {exp['Location']}")
        for bullet in exp['BulletPoints']:
            pdf.multi_cell(0, 10, txt=f"  • {bullet}")

    # Add Publications
    pdf.cell(200, 10, txt="Publications:", ln=True)
    pdf.multi_cell(0, 10, txt=f"- {data['Publications']['Title']} ({data['Publications']['Journal']}, {data['Publications']['Volume']}, {data['Publications']['Issue']})")

    # Add Certifications
    pdf.cell(200, 10, txt="Certifications:", ln=True)
    for cert in data['Certifications']:
        pdf.multi_cell(0, 10, txt=f"- {cert['Name']} ({cert['Issuer']}, {cert['Date']})")

    # Save the PDF to a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name

# Streamlit App
def main():
    st.title("Resume Parser and Generator")

    # Upload resume
    uploaded_file = st.file_uploader("Upload your resume (PDF or text)", type=["pdf", "txt"])
    if uploaded_file is not None:
        # Read the file content
        if uploaded_file.type == "application/pdf":
            file_content = extract_text_from_pdf(uploaded_file)
        else:
            file_content = uploaded_file.read().decode("utf-8")

        # Parse the resume
        parsed_data = parse_resume(file_content)

        # Display parsed data in editable sections
        st.header("Parsed Resume Data")

        # Name
        name = st.text_input("Name", value=parsed_data.get("Name", ""))

        # Contact Information
        st.subheader("Contact Information")
        phone = st.text_input("Phone", value=parsed_data.get("ContactInformation", {}).get("Phone", ""))
        email = st.text_input("Email", value=parsed_data.get("ContactInformation", {}).get("Email", ""))
        linkedin = st.text_input("LinkedIn", value=parsed_data.get("ContactInformation", {}).get("LinkedIn", ""))
        github = st.text_input("GitHub", value=parsed_data.get("ContactInformation", {}).get("GitHub", ""))
        location = st.text_input("Location", value=parsed_data.get("ContactInformation", {}).get("Location", ""))

        # Professional Summary
        st.subheader("Professional Summary")
        professional_summary = st.text_area("Professional Summary", value=parsed_data.get("ProfessionalSummary", ""))

        # Technical Skills
        st.subheader("Technical Skills")
        technical_skills = st.text_area("Technical Skills", value=", ".join(parsed_data.get("TechnicalSkills", [])))

        # Education
        st.subheader("Education")
        education_data = parsed_data.get("Education", [])
        for i, edu in enumerate(education_data):
            st.text_input(f"Institution {i+1}", value=edu.get("Institution", ""), key=f"edu_institution_{i}")
            st.text_input(f"Degree {i+1}", value=edu.get("Degree", ""), key=f"edu_degree_{i}")
            st.text_input(f"Start Date {i+1}", value=edu.get("StartDate", ""), key=f"edu_start_date_{i}")
            st.text_input(f"End Date {i+1}", value=edu.get("EndDate", ""), key=f"edu_end_date_{i}")

        # Professional Experience
        st.subheader("Professional Experience")
        professional_experience = st.text_area("Professional Experience", value="\n".join([
            f"- {exp['Role']} at {exp['Company']} ({exp['StartDate']} - {exp['EndDate']}), {exp['Location']}\n" +
            "\n".join([f"  • {bullet}" for bullet in exp['BulletPoints']])
            for exp in parsed_data.get("ProfessionalExperience", [])
        ]))

        # Publications
        st.subheader("Publications")
        publications = st.text_area("Publications", value=f"- {parsed_data.get('Publications', {}).get('Title', '')} ({parsed_data.get('Publications', {}).get('Journal', '')}, {parsed_data.get('Publications', {}).get('Volume', '')}, {parsed_data.get('Publications', {}).get('Issue', '')})")

        # Certifications
        st.subheader("Certifications")
        certifications = st.text_area("Certifications", value="\n".join([
            f"- {cert['Name']} ({cert['Issuer']}, {cert['Date']})"
            for cert in parsed_data.get("Certifications", [])
        ]))

        # Generate PDF button
        if st.button("Generate PDF Resume"):
            # Prepare data for PDF generation
            data = {
                "Name": name,
                "ContactInformation": {
                    "Phone": phone,
                    "Email": email,
                    "LinkedIn": linkedin,
                    "GitHub": github,
                    "Location": location
                },
                "ProfessionalSummary": professional_summary,
                "TechnicalSkills": technical_skills.split(", "),
                "Education": [
                    {
                        "Institution": st.session_state[f"edu_institution_{i}"],
                        "Degree": st.session_state[f"edu_degree_{i}"],
                        "StartDate": st.session_state[f"edu_start_date_{i}"],
                        "EndDate": st.session_state[f"edu_end_date_{i}"]
                    }
                    for i in range(len(education_data))
                ],
                "ProfessionalExperience": [
                    {
                        "Company": exp.split(" at ")[1].split(" (")[0],
                        "Role": exp.split(" at ")[0].strip("- "),
                        "StartDate": exp.split(" (")[1].split(" - ")[0],
                        "EndDate": exp.split(" - ")[1].split("), ")[0],
                        "Location": exp.split("), ")[1],
                        "BulletPoints": [bullet.strip("• ") for bullet in exp.split("\n")[1:]]
                    }
                    for exp in professional_experience.split("\n\n")
                ],
                "Publications": {
                    "Title": publications.split(" (")[0].strip("- "),
                    "Journal": publications.split(" (")[1].split(", ")[0],
                    "Volume": publications.split(", ")[1],
                    "Issue": publications.split(", ")[2].strip(")")
                },
                "Certifications": [
                    {
                        "Name": cert.split(" (")[0].strip("- "),
                        "Issuer": cert.split(" (")[1].split(", ")[0],
                        "Date": cert.split(", ")[1].strip(")")
                    }
                    for cert in certifications.split("\n")
                ]
            }

            # Generate PDF
            pdf_file = generate_pdf_resume(data)

            # Provide download link
            with open(pdf_file, "rb") as f:
                st.download_button("Download PDF Resume", f, file_name="resume.pdf")

            # Clean up temporary file
            os.unlink(pdf_file)

# Run the Streamlit app
if __name__ == "__main__":
    main()