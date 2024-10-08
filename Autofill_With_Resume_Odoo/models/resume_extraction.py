import PyPDF2,json
import docx2txt
from odoo import api, fields, models, tools
from odoo.exceptions import AccessError, UserError, ValidationError
from pdfminer.high_level import extract_text
import openai
import ast,re
import pytesseract
import docx,os
import logging
from datetime import datetime
_logger = logging.getLogger(__name__)

current_date = datetime.now().strftime("%B %Y")

def extract_text_from_pdf(pdf_path,openai_key):
    if not pdf_path or not isinstance(pdf_path, str) or not os.path.exists(pdf_path):
        return None
    else:
        try:
            text = extract_text(pdf_path)
            single_line_text = ' '.join(text.split())
            result = gpt_model(single_line_text,openai_key)
            return result
        except Exception as e:
            try:
                doc = docx.Document(pdf_path)
                full_text = []
                for element in doc.element.body:
                    if element.tag.endswith('p'):
                        paragraph = docx.text.paragraph.Paragraph(element, doc)
                        full_text.append(paragraph.text)
                    elif element.tag.endswith('tbl'):
                        table = docx.table.Table(element, doc)
                        for row in table.rows:
                            row_data = []
                            for cell in row.cells:
                                row_data.append(cell.text)
                            full_text.append('\t'.join(row_data))
                    elif element.tag.endswith('picture'):
                        image_path = element.get('src')
                        if image_path:
                            text = pytesseract.image_to_string(image_path)
                            full_text.append(text)
                text= '\n'.join(full_text)
                single_line_text = ' '.join(text.split())
                result = gpt_model(single_line_text,openai_key)
                return result
            except:
                raise ValidationError("File supported only PDF and docx.")

def gpt_model(text,openai_key):

    initial_prompt = f"""

        Your task is to extract relevant data from the provided resume text and return it in a specific JSON format.

        ### Instructions:

        Extract the following information from the resume text: "{text}"

       
        1. **Experience**: Calculate total experience based on the following guidelines:
            - First, check for an "Experience" section or similar headings such as "Work History" or "Professional Experience."
            - If no explicit experience periods are mentioned, derive experience from any work-related descriptions. If no such information exists, set experience to **0**.
            - If specific date ranges are found (e.g., "Jan 2022 to Present," "Jan 2022 to Till Now"), calculate the total experience from the start date up to **{current_date}**.
            - Handle date formats like:
                - "Month Year - Present" (e.g., "Jan 2020 - Present" = X years and Y months)
                - "Year-Month to Year-Month" (e.g., "2020-Jan to 2022-Jan" = 2 years).
                - For partial date formats (e.g., "2020 to 2022"), treat them as yearly ranges.
        2. **Location**: Extract the candidate's location or address.
       
        3. **Name**: Extract the candidate’s name.
        4. **Email**: Extract the candidate’s correct email address.
        5. **Phone_Number**: Extract the candidate’s phone number.
        6. **LinkedIn**: Extract the LinkedIn profile URL.
        7. **Degree**: Extract the highest qualification or degree.
        8. **Github**: Extract the GitHub profile URL.
        9. **Certificates**: Extract any certificates mentioned.
        10. **Known_Languages**: Extract list of languages spoken by the candidate.
        11. **Achievements**: Extract list of key achievements.
        12. **Project_Names**: Extract list of full project names, especially combined entities (e.g., "L&T (finance) & Mahindra (finance)").
        13. **Hobbies**: Extract list of hobbies mentioned.
        14. **Strength**: Extract list of key strengths.
        15. **Date_Of_Birth**: Extract the date of birth.
        16. **Gender**: Extract the gender.
        17. **Nationality**: Extract nationality.
        28. **Soft_Skill**: Extract list of soft skills or personal skills (e.g., communication, leadership).
        19. **Marital_Status**: Extract list of marital status.
        20. **Weakness**: Extract list of any weaknesses mentioned.
       
        ### Notes:
        - Do not return with ``` at the start and of the json result.
        - Return the information in the specified format without using json at the start of the response.
        - If the project name has any special symbol do not split the project name read as it is.
        - For project names like "L&T (finance) & Mahindra (finance)," extract them as single entities without splitting.
        - If a value is not found for any field, return 'None.'
        - When experience headings or dates are missing, rely on descriptions of roles and responsibilities to estimate the time span.
        - **Experience**: Prioritize the experience section if it exists. Avoid calculating experience based on generic summaries.
        - Always handle 'Till Now,' 'Upto Date,' and 'Present' as dynamic date references, updating them to **{current_date}** for accurate calculations.

        ### Output Format:
        Return the following keys:  Experience, Location, Name, Email, Phone_Number, LinkedIn, Degree, Github, Certificates, Known_Languages, Achievements, Project_Names, Hobbies, Strength, Date_Of_Birth, Gender, Nationality, Soft_Skill, Marital_Status, Weakness,.
        """

    prompt = initial_prompt.format(text=text)
    openai.api_key = openai_key
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0
    )
    final_result= response.choices[0].message['content']
    return final_result

def send_email_link(name,receiver_email):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    # Email content
    email_html_content = """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google Meeting Link Notification</title>
   
</head>
<body style=            "font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;">

        <h1 style="color: #333333;">Interview Meeting Invitation</h1>
        <p style="color: #666666;">Hello, {name}</p>
        <p>You have been qualified for the first round of the interview.</p>
        
        <p>Please be available for the interview.</p>

        <p>Thank you!</p>
   
</body>
</html>
    """.format(name = name)
    port = 587
    smtp_server = "smtp.gmail.com"
    sender_email = "demo.ahex@gmail.com"
    password = "rguf afay knuw kjeq"
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Interview Invitation"
    msg['From'] = sender_email
    msg['To'] = receiver_email
    html_part = MIMEText(email_html_content, 'html')
    msg.attach(html_part)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Secure the connection
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
    return "Email sent successfully!"

# apply the UI design for the the skill priority  of resume or of jobs.
def skill_priority_UI(priority):
    colored_priorities = []
    # Extract the dictionary part from the HTML string using a regex
    match = re.search(r'\{.*\}', str(priority))
    if match:
        priority_dict_str = match.group(0)
        try:
            priority_dict = ast.literal_eval(priority_dict_str)

            color_mapping = {
                'high_priority': 'red',
                'moderate_priority': 'orange',
                'low_priority': 'green'
            }
            for key, value in priority_dict.items():
                color = color_mapping.get(key, 'black')
                colored_priority = f'<span style="color:{color}">{key.replace("_", " ").title()}: {value}</span>'
                colored_priorities.append(colored_priority)

        except (SyntaxError, ValueError):
            pass
        skills_level= '<br/>'.join(colored_priorities)
    return skills_level

class AttachmentSkillScore(models.Model):
    _name = 'auto.fill.resume'
    _description = 'Attachment Skill Score'

    applicant_id = fields.Many2one('hr.applicant', string="Applicant",  ondelete='cascade', required=True)
    attachment_id = fields.Many2one('ir.attachment', string="Attachment",  ondelete='cascade', required=True)
    resume_name = fields.Char(string='Resume Name')
    resume_exp = fields.Text(string='Experience')
    resume_loc = fields.Text(string='Location')
    resume_phone = fields.Text(string='Phone')
    resume_email = fields.Text(string='Email')
    resume_linkedin = fields.Text(string='LinkedIn')
    resume_github = fields.Char(string='Github')
    resume_degree = fields.Char(string='Degree')
    resume_hobbies = fields.Char(string='Hobbies')
    resume_strength = fields.Char(string='Strength')
    resume_dob = fields.Char(string='Date Of Birth')
    resume_gender = fields.Char(string='Gender')
    resume_nationality = fields.Char(string='Nationality')

    resume_certificates = fields.Char(string='Certificates')
    resume_known_languages = fields.Char(string='Known Languages')
    resume_achievements = fields.Char(string='Achievements')
    resume_project_names = fields.Char(string='Project Names')
    resume_soft_skill = fields.Char(string='Soft Skill')
    resume_marital_status = fields.Char(string='Marital Status')
    resume_Weakness = fields.Char(string='Weakness')

class Applicant(models.Model):
    _inherit ='hr.applicant'
    
    mydatas = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'hr.applicant')], string='Attachments')
    resume_name = fields.Char(string='Resume Name', compute='_compute_attachment_read_pdf',store='true')
    resume_exp = fields.Text(string='Experience', compute='_compute_attachment_read_pdf',store='true')
    resume_loc = fields.Text(string='Location', compute='_compute_attachment_read_pdf',store='true') 
    resume_phone = fields.Text(string='Phone', compute='_compute_attachment_read_pdf',store='true')
    resume_email = fields.Text(string='Email', compute='_compute_attachment_read_pdf',store='true')
    resume_linkedin = fields.Text(string='LinkedIn', compute='_compute_attachment_read_pdf',store='true')
    resume_github = fields.Char(string='Github', compute='_compute_attachment_read_pdf',store='true')
    resume_degree = fields.Char(string='Degree', compute='_compute_attachment_read_pdf',store='true')
    resume_hobbies = fields.Char(string='Hobbies', compute='_compute_attachment_read_pdf',store='true')
    resume_strength = fields.Char(string='Strength', compute='_compute_attachment_read_pdf',store='true')
    resume_dob = fields.Char(string='Date Of Birth', compute='_compute_attachment_read_pdf',store='true')
    resume_gender = fields.Char(string='Gender', compute='_compute_attachment_read_pdf',store='true')
    resume_nationality = fields.Char(string='Nationality', compute='_compute_attachment_read_pdf',store='true')
    resume_soft_skill = fields.Char(string='Soft Skill', compute='_compute_attachment_read_pdf',store='true')
    resume_marital_status = fields.Char(string='Marital Status', compute='_compute_attachment_read_pdf',store='true')
    resume_Weakness = fields.Char(string='Weakness', compute='_compute_attachment_read_pdf',store='true')
    resume_certificates = fields.Char(string='Certificates', compute='_compute_attachment_read_pdf',store='true')
    resume_known_languages = fields.Char(string='Known Languages', compute='_compute_attachment_read_pdf',store='true')
    resume_achievements = fields.Char(string='Achievements', compute='_compute_attachment_read_pdf',store='true')
    resume_project_names = fields.Char(string='Project Names', compute='_compute_attachment_read_pdf',store='true')
    show_resume_linkedin = fields.Boolean(string='Show LinkedIn')
    show_resume_name = fields.Boolean(string='Show Name')
    show_resume_email = fields.Boolean(string='Show Email')
    show_resume_phone = fields.Boolean(string='Show Phone')
    show_resume_degree = fields.Boolean(string='Show Degree')
    show_resume_loc = fields.Boolean(string='Show Location')
    show_resume_exp = fields.Boolean(string='Show Experience')
    show_resume_github = fields.Boolean(string='Show Github')
    show_resume_certificates = fields.Boolean(string='Show Certificates')
    show_resume_known_languages = fields.Boolean(string='Show Know Languages')
    show_resume_achievements = fields.Boolean(string='Show Achievements')
    show_resume_project_names = fields.Boolean(string='Show Project Name')
    show_resume_soft_skill = fields.Boolean(string='Show Soft Skill')
    show_resume_marital_status = fields.Boolean(string='Show Marital Status')
    show_resume_Weakness = fields.Boolean(string='Show Weakness')
    show_resume_hobbies = fields.Boolean(string='Show Hobbies')
    show_resume_strength = fields.Boolean(string='Show Strength')
    show_resume_dob = fields.Boolean(string='Show Date_Of_Birth')
    show_resume_gender = fields.Boolean(string='Show Gender')
    show_resume_nationality = fields.Boolean(string='Show Nationality')
    attachment_empty = fields.Boolean('Attachment Empty', compute='_compute_attachment_read_pdf',store='true')
    @api.depends('attachment_ids')
    def _compute_attachment_read_pdf(self):
        for record in self:
            if len(record.attachment_ids) == 0:
                record.attachment_empty = True
            else:
                record.attachment_empty = False

    def action_add_basic_info(self):
        return {
            'name': 'Basic/Extra Info',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.applicant.extra.info.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_basic': self.env.context.get('basic', False),
                'default_extra_all': self.env.context.get('extra_all', False),
            }
        }

    def action_add_extra_info(self):
        return self.action_add_basic_info()

    @api.depends('attachment_ids')
    def _compute_attachment_read_pdf(self):
        for record in self:
            if len(record.attachment_ids) == 0:
                # Clear all fields if no attachment
                record.resume_name = ''
                record.resume_exp = ''
                record.resume_loc = ''
                record.resume_phone = ''
                record.resume_email = ''
                record.resume_linkedin = ''
                record.resume_degree = ''
                record.resume_github = ''
                record.resume_certificates = ''
                record.resume_known_languages = ''
                record.resume_achievements = ''
                record.resume_project_names = ''
                record.resume_hobbies = ''
                record.resume_strength = ''
                record.resume_dob = ''
                record.resume_gender = ''
                record.resume_nationality = ''
                record.resume_soft_skill = ''
                record.resume_marital_status = ''
                record.resume_Weakness = ''
                break

            attachment = record.attachment_ids[0]
            existing_record = record.env['auto.fill.resume'].search([
                ('attachment_id', '=', attachment.id)], limit=1)
            if existing_record:
                # Populate fields from existing record, ensuring no `None` is stored
                record.resume_name = existing_record.resume_name or ''
                record.resume_exp = existing_record.resume_exp or ''
                record.resume_loc = existing_record.resume_loc or ''
                record.resume_phone = existing_record.resume_phone or ''
                record.resume_email = existing_record.resume_email or ''
                record.resume_linkedin = existing_record.resume_linkedin or ''
                record.resume_degree = existing_record.resume_degree or ''
                record.resume_github = existing_record.resume_github or ''
                record.resume_certificates = existing_record.resume_certificates or ''
                record.resume_known_languages = existing_record.resume_known_languages or ''
                record.resume_achievements = existing_record.resume_achievements or ''
                record.resume_project_names = existing_record.resume_project_names or ''
                record.resume_hobbies = existing_record.resume_hobbies or ''
                record.resume_strength = existing_record.resume_strength or ''
                record.resume_dob = existing_record.resume_dob or ''
                record.resume_gender = existing_record.resume_gender or ''
                record.resume_nationality = existing_record.resume_nationality or ''
                record.resume_soft_skill = existing_record.resume_soft_skill or ''
                record.resume_marital_status = existing_record.resume_marital_status or ''
                record.resume_Weakness = existing_record.resume_Weakness or ''
            else:
                # Use a savepoint for safety
                with record.env.cr.savepoint():
                    openai_key_record = record.env['ai.openai.key'].search([], limit=1)
                    if not openai_key_record or not openai_key_record.open_ai_key:
                        continue
                    openai_key = openai_key_record.open_ai_key
                    _logger.info("Using OpenAI key: %s", openai_key)

                    if record.attachment_ids:
                        attachment = record.attachment_ids[0]
                        file_path = attachment._full_path(attachment.store_fname)
                        result = extract_text_from_pdf(file_path, openai_key)
                        dict_data = json.loads(result)

                        # Extracting data and populating fields, ensuring no `None`
                        record.resume_name = dict_data.get("Name", "") or ''
                        record.resume_exp = dict_data.get("Experience", "") or ''
                        record.resume_loc = dict_data.get("Location", "") or ''
                        record.resume_phone = dict_data.get("Phone_Number", "") or ''
                        record.resume_email = dict_data.get("Email", "") or ''
                        record.resume_linkedin = dict_data.get("LinkedIn", "") or ''
                        record.resume_degree = dict_data.get("Degree", "") or ''
                        record.resume_github = dict_data.get("Github", "") or ''
                        record.resume_certificates = dict_data.get("Certificates", "") or ''
                        record.resume_known_languages = dict_data.get("Known_Languages", "") or ''
                        record.resume_achievements = dict_data.get("Achievements", "") or ''
                        record.resume_project_names = dict_data.get("Project_Names", "") or ''
                        record.resume_hobbies = dict_data.get("Hobbies", "") or ''
                        record.resume_strength = dict_data.get("Strength", "") or ''
                        record.resume_dob = dict_data.get("Date_of_Birth", "") or ''
                        record.resume_gender = dict_data.get("Gender", "") or ''
                        record.resume_nationality = dict_data.get("Nationality", "") or ''
                        record.resume_soft_skill = dict_data.get("Soft_Skills", "") or ''
                        record.resume_marital_status = dict_data.get("Marital_Status", "") or ''
                        record.resume_Weakness = dict_data.get("Weakness", "") or ''

                        # Create new record in auto.fill.resume
                        record.env['auto.fill.resume'].create({
                            'applicant_id': record.id,
                            'attachment_id': attachment.id,
                            'resume_name': record.resume_name,
                            'resume_exp': record.resume_exp,
                            'resume_loc': record.resume_loc,
                            'resume_phone': record.resume_phone,
                            'resume_email': record.resume_email,
                            'resume_linkedin': record.resume_linkedin,
                            'resume_degree': record.resume_degree,
                            'resume_github': record.resume_github,
                            'resume_certificates': record.resume_certificates,
                            'resume_known_languages': record.resume_known_languages,
                            'resume_achievements': record.resume_achievements,
                            'resume_project_names': record.resume_project_names,
                            'resume_hobbies': record.resume_hobbies,
                            'resume_strength': record.resume_strength,
                            'resume_dob': record.resume_dob,
                            'resume_gender': record.resume_gender,
                            'resume_nationality': record.resume_nationality,
                            'resume_soft_skill': record.resume_soft_skill,
                            'resume_Weakness': record.resume_Weakness,
                            'resume_marital_status': record.resume_marital_status,
                        })
                        record.attachment_empty = True
                    else:
                        # Clear all fields if no valid attachment
                        record.resume_name = ''
                        record.resume_exp = ''
                        record.resume_loc = ''
                        record.resume_phone = ''
                        record.resume_email = ''
                        record.resume_linkedin = ''
                        record.resume_degree = ''
                        record.resume_github = ''
                        record.resume_certificates = ''
                        record.resume_known_languages = ''
                        record.resume_achievements = ''
                        record.resume_project_names = ''
                        record.resume_hobbies = ''
                        record.resume_strength = ''
                        record.resume_dob = ''
                        record.resume_gender = ''
                        record.resume_nationality = ''
                        record.resume_soft_skill = ''
                        record.resume_Weakness = ''
                        record.resume_marital_status = ''