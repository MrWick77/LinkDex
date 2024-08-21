from flask import Flask, render_template, request, send_file
import requests
from fpdf import FPDF
import os

app = Flask(__name__)

API_ENDPOINT = 'https://nubela.co/proxycurl/api/v2/linkedin'
API_KEY = 'Add your api key'
HEADERS = {'Authorization': f'Bearer {API_KEY}'}

def is_valid_linkedin_url(url):
    return url.startswith("https://www.linkedin.com/in/")

def remove_unsupported_characters(text):
    try:
        text.encode('latin-1')
        return text
    except UnicodeEncodeError:
        return text.encode('latin-1', 'replace').decode('latin-1')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        linkedin_url = request.form.get('profile_url')
        if not linkedin_url or not is_valid_linkedin_url(linkedin_url):
            return 'Error: Invalid LinkedIn URL', 400
        
        profile_data = fetch_profile_data(linkedin_url)
        if profile_data:
            try:
                pdf_path = generate_resume_pdf(profile_data)
                return send_file(pdf_path, as_attachment=True)
            except Exception as e:
                return f'Error generating PDF: {e}', 500
        else:
            return 'Error fetching profile data', 500
    return render_template('index.html')

def fetch_profile_data(profile_url):
    params = {'url': profile_url}
    response = requests.get(API_ENDPOINT, headers=HEADERS, params=params)
    
    if response.status_code == 200:
        profile_data = response.json()
        
        # Ensure default values to prevent template errors
        profile_data.setdefault('full_name', 'N/A')
        profile_data.setdefault('headline', 'N/A')
        profile_data.setdefault('summary', 'No summary available.')
        profile_data.setdefault('education', [])
        profile_data.setdefault('experiences', [])
        profile_data.setdefault('skills', [])
        profile_data.setdefault('accomplished_courses', [])
        profile_data.setdefault('accomplished_projects', [])
        profile_data.setdefault('certifications', [])

        return profile_data
    
    return None

def generate_resume_pdf(profile_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add profile details
    pdf.set_fill_color(173, 216, 230)
    pdf.cell(200, 10, txt=remove_unsupported_characters(profile_data.get('full_name', 'N/A')), ln=True, align='C')
    pdf.cell(200, 10, txt=remove_unsupported_characters(profile_data.get('headline', 'N/A')), ln=True, align='C')
    
    pdf.ln(10)

    # Summary section
    pdf.set_fill_color(173, 216, 230)
    pdf.set_font("Arial", size=12, style='B')
    pdf.cell(200, 10, txt="Summary", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=remove_unsupported_characters(profile_data.get('summary', 'No summary available.')))

    pdf.ln(10)

    # Education section
    pdf.set_fill_color(173, 216, 230)
    pdf.set_font("Arial", size=12, style='B')
    pdf.cell(200, 10, txt="Education", ln=True)
    pdf.set_font("Arial", size=12)
    for education in profile_data.get('education', []):
        pdf.multi_cell(0, 10, txt=remove_unsupported_characters(f"{education.get('degree_name', 'N/A')} in {education.get('field_of_study', 'N/A')} - {education.get('school', 'N/A')} ({education.get('starts_at', {}).get('year', 'N/A')} - {education.get('ends_at', {}).get('year', 'N/A')})"))

    pdf.ln(10)

    # Experience section
    pdf.set_fill_color(173, 216, 230)
    pdf.set_font("Arial", size=12, style='B')
    pdf.cell(200, 10, txt="Experience", ln=True)
    pdf.set_font("Arial", size=12)
    for experience in profile_data.get('experiences', []):
        title = experience.get('title', 'N/A')
        company = experience.get('company', 'N/A')
        start_month = experience.get('starts_at', {}).get('month', 'N/A')
        start_year = experience.get('starts_at', {}).get('year', 'N/A')
        end_month = experience.get('ends_at', {}).get('month', 'N/A')
        end_year = experience.get('ends_at', {}).get('year', 'N/A')
        pdf.multi_cell(0, 10, txt=remove_unsupported_characters(f"{title} at {company} ({start_month} {start_year} - {end_month} {end_year})"))

    pdf.ln(10)

    # Accomplished Courses section
    pdf.set_fill_color(173, 216, 230)
    pdf.set_font("Arial", size=12, style='B')
    pdf.cell(200, 10, txt="Accomplished Courses", ln=True)
    pdf.set_font("Arial", size=12)
    for course in profile_data.get('accomplishment_courses', []):
        pdf.cell(0, 10, txt=remove_unsupported_characters(f"{course.get('name', 'N/A')} - {course.get('number', 'N/A')}"), ln=True)

    pdf.ln(10)

    # Accomplished Projects section
    pdf.set_fill_color(173, 216, 230)
    pdf.set_font("Arial", size=12, style='B')
    pdf.cell(200, 10, txt="Accomplished Projects", ln=True)
    pdf.set_font("Arial", size=12)
    for project in profile_data.get('accomplishment_projects', []):
        pdf.cell(0, 10, txt=remove_unsupported_characters(f"{project.get('title', 'N/A')} - {project.get('description', 'N/A')}"), ln=True)

    pdf.ln(10)

    # Certifications section
    pdf.set_fill_color(173, 216, 230)
    pdf.set_font("Arial", size=12, style='B')
    pdf.cell(200, 10, txt="Certifications", ln=True)
    pdf.set_font("Arial", size=12)
    for certification in profile_data.get('certifications', []):
        pdf.cell(0, 10, txt=remove_unsupported_characters(f"{certification.get('name', 'N/A')} - {certification.get('license_number', 'N/A')} "), ln=True)

    # Ensure the directory exists
    if not os.path.exists('static'):
        os.makedirs('static')

    pdf_path = os.path.join('static', 'resume.pdf')
    pdf.output(pdf_path)
    return pdf_path

if __name__ == '__main__':
    app.run(debug=True)
