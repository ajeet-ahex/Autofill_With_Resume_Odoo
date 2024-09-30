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


# Get the current date in the required format
current_date = datetime.now().strftime("%B %Y")

def extract_text_from_pdf(pdf_path,openai_key):
    if not pdf_path or not isinstance(pdf_path, str) or not os.path.exists(pdf_path):
        # Skip the current file and return None
        print(f"Skipping invalid file path: {pdf_path}")
        return None
    else:
        try:
            text = extract_text(pdf_path)
            print("full text:",text)
            single_line_text = ' '.join(text.split())
            print('single_line_text:::',single_line_text)
            result = gpt_model(single_line_text,openai_key)
            # print('result:',result)
            # print('result type:',type(result))
            return result
        except Exception as e:
            try:
                # Load the DOCX file
                doc = docx.Document(pdf_path)
                
                # Initialize a list to hold all the text
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
                    # else:
                    #     raise ValidationError("Please upload the PDF's or Docx file only")
                    elif element.tag.endswith('picture'):
                        # Extract text from the image within the picture element
                        image_path = element.get('src')
                        if image_path:
                            # Extract text from the image
                            text = pytesseract.image_to_string(image_path)
                            print("image text:",text)
                            full_text.append(text)

                # Combine all the content with newlines in between
                print("full text: ", full_text)
                text= '\n'.join(full_text)
                single_line_text = ' '.join(text.split())
                print('single_line_text:::',single_line_text)
                result = gpt_model(single_line_text,openai_key)
                # print('result:',result)
                # print('result type:',type(result))
                return result
            except:
                raise ValidationError("File supported only PDF and docx.")
                # print("file unable to process !!! ")
    
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



        # print("Prompt : ", initial_prompt)

    prompt = initial_prompt.format(text=text)
    print('prompt:',prompt)
    # openai api key here
    openai.api_key = openai_key
    # response = openai.chat.completions.create(
        # openai.ChatCompletion.create(
    # try:
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        # model="gpt-4o",
        # model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0
    )
    final_result= response.choices[0].message['content']
    # print('Response:', final_result)
    # print('Response:', response.choices[0].message.content)
    
        
        # return response.choices[0].message.content 
    # except openai.error.OpenAIError as e:
    #     print(f"An error occurred: {e}")
    #     final_result='no data'
        
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
    # Email configuration
    port = 587
    smtp_server = "smtp.gmail.com"
    sender_email = "demo.ahex@gmail.com"
    password = "rguf afay knuw kjeq"
    # receiver_email = "openaiahex@gmail.com"

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Interview Invitation"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    # Attach HTML content to the email
    html_part = MIMEText(email_html_content, 'html')
    msg.attach(html_part)

    # Connect to SMTP server
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Secure the connection
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent successfully!")
        
    return "Email sent successfully!"


# apply the UI design for the the skill priority  of resume or of jobs.
def skill_priority_UI(priority):
    colored_priorities = []
    # Extract the dictionary part from the HTML string using a regex
    match = re.search(r'\{.*\}', str(priority))
    print("match job priority:",match.group(0))
    if match:
        priority_dict_str = match.group(0)
        try:
            # Safely parse the dictionary string using ast.literal_eval
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
    
        # Join the colored priorities into a single HTML string
        skills_level= '<br/>'.join(colored_priorities)
    return skills_level

class AttachmentSkillScore(models.Model):
    _name = 'auto.fill.resume'
    _description = 'Attachment Skill Score'

    applicant_id = fields.Many2one('hr.applicant', string="Applicant",  ondelete='cascade', required=True)
    attachment_id = fields.Many2one('ir.attachment', string="Attachment",  ondelete='cascade', required=True)
    # resume_text = fields.Html(string='Resume Text')
    resume_name = fields.Char(string='Resume Name')
    
    resume_exp = fields.Text(string='Experience')
    resume_loc = fields.Text(string='Location')
    # resume_summary = fields.Text(string='Resume Summary')
    resume_phone = fields.Text(string='Phone')
    resume_email = fields.Text(string='Email')
    resume_linkedin = fields.Text(string='LinkedIn')
    resume_github = fields.Char(string='Github')
    resume_degree = fields.Char(string='Degree')
    # Hobbies , Strength , Date_Of_Birth , Gender , Nationality
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
    
    

# attach_data = fields.Many2one('ir.attachment', string="Attachment Data")
# mydatas1 = fields.Char(related='attach_data.store_fname', string="mydatas1", readonly=False,)
# print("######"*10)
# # print("attachment_ids: ",mydatas)
# print("origin: ",mydatas1) 
   

class Applicant(models.Model):
    _inherit ='hr.applicant'

    
    
    print("######"*10)
    
    mydatas = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'hr.applicant')], string='Attachments')

    
    print("######"*10)
    print("mydatas: ",mydatas)
    
    resume_name = fields.Char(string='Resume Name', compute='_compute_attachment_read_pdf',store='true')
    
    resume_exp = fields.Text(string='Experience', compute='_compute_attachment_read_pdf',store='true')
    resume_loc = fields.Text(string='Location', compute='_compute_attachment_read_pdf',store='true') 
    # resume_summary = fields.Text(string='Resume Summary', compute='_compute_attachment_read_pdf')
    resume_phone = fields.Text(string='Phone', compute='_compute_attachment_read_pdf',store='true')
    resume_email = fields.Text(string='Email', compute='_compute_attachment_read_pdf',store='true')
    resume_linkedin = fields.Text(string='LinkedIn', compute='_compute_attachment_read_pdf',store='true')
    resume_github = fields.Char(string='Github', compute='_compute_attachment_read_pdf',store='true')
    resume_degree = fields.Char(string='Degree', compute='_compute_attachment_read_pdf',store='true')
    # Hobbies , Strength , Date_Of_Birth , Gender , Nationality
    resume_hobbies = fields.Char(string='Hobbies', compute='_compute_attachment_read_pdf',store='true')
    resume_strength = fields.Char(string='Strength', compute='_compute_attachment_read_pdf',store='true')
    resume_dob = fields.Char(string='Date Of Birth', compute='_compute_attachment_read_pdf',store='true')
    resume_gender = fields.Char(string='Gender', compute='_compute_attachment_read_pdf',store='true')
    resume_nationality = fields.Char(string='Nationality', compute='_compute_attachment_read_pdf',store='true')
    # Soft_Skill, Marital_Status, Weakness => resume_soft_skill, resume_marital_status, resume_Weakness
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
    # resume_known_languages = fields.Char(string='Known Languages', compute='_compute_attachment_read_pdf')
    
    # Hobbies , Strength , Date_Of_Birth , Gender , Nationality
    show_resume_hobbies = fields.Boolean(string='Show Hobbies')
    show_resume_strength = fields.Boolean(string='Show Strength')
    show_resume_dob = fields.Boolean(string='Show Date_Of_Birth')
    show_resume_gender = fields.Boolean(string='Show Gender')
    show_resume_nationality = fields.Boolean(string='Show Nationality')
    # select_all = fields.Boolean(string="Select All")
    # fetch_info = fields.Selection([
    #     ('basic_info', 'Basic Info'),
    #     ('extra_info', 'Extra Info'),
    # ], string="Fetch Information")
    
    


    
    @api.depends('attachment_ids')
    def _compute_attachment_read_pdf(self):
        for record in self:
            if len(record.attachment_ids) == 0:
                # Set a flag or field to indicate that the attachments are empty
                record.attachment_empty = True
            else:
                record.attachment_empty = False

    attachment_empty = fields.Boolean('Attachment Empty', compute='_compute_attachment_read_pdf',store='true')
        
    def action_add_extra_info(self):
        return {
        # 'type': 'ir.actions.client',
        # 'tag': 'reload',
        'type': 'ir.actions.act_window',
        'name': 'Extra Information',
        'view_mode': 'form',
        'res_model': 'hr.applicant.extra.info.wizard',
        # 'view_id': self.env.ref('Entity_Extraction.view_hr_applicant_extra_info_wizard').id,
        'view_id': False,
        # 'type': 'ir.actions.client',
        # 'tag': 'reload',
        # 'type': 'ir.actions.act_window',
        'target': 'new',
    }
    # def action_refresh_page(self):
    #     # Check if 'attachment_empty' field is True in the hr.applicant model
    #     if self.attachment_empty==True:
    #         return {
    #             'type': 'ir.actions.client',
    #             'tag': 'reload',
    #         }
    
    
    # @api.onchange('fetch_info')
    # def _onchange_info_type(self):
    #     if self.fetch_info == 'basic_info':
    #         return self.action_add_extra_info(basic=True)
    #     elif self.fetch_info == 'extra_info':
    #         return self.action_add_extra_info(extra_all=True)

    # def action_add_extra_info(self, basic=False, extra_all=False):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Extra Information',
    #         'view_mode': 'form',
    #         'res_model': 'hr.applicant.extra.info.wizard',
    #         'view_id': False,
    #         'target': 'new',
    #         'context': {
    #             'default_basic_info': basic,
    #             'default_extra_info': extra_all,
    #         },
    #     }
    


    
    # @api.depends('attachment_ids.store_fname')
    @api.depends('attachment_ids')
    def _compute_attachment_read_pdf(self):
        for record in self:
            print("attachments:  ",  record.attachment_ids)
            print("message_main_attachment_id.store_fname:  ",  record.message_main_attachment_id.store_fname)
            if len(record.attachment_ids)==0:
                # record.resume_text = ''
                record.resume_name = ''
                record.resume_exp = ''
                record.resume_loc = ''
                # record.resume_summary = ''
                record.resume_phone = ''
                record.resume_email = ''
                record.resume_linkedin = ''
                record.resume_degree = ''
                record.resume_github = ''
                record.resume_certificates = ''
                record.resume_known_languages='',
                record.resume_achievements='',
                record.resume_project_names='', 
                record.resume_hobbies = '',
                record.resume_strength = '',
                record.resume_dob = '',
                record.resume_gender = '',
                record.resume_nationality = '',
                record.resume_soft_skill = '',
                record.resume_marital_status = '',
                record.resume_Weakness = '',
                
                break
            
            attachment = record.attachment_ids[0]
            print("attachment id :",attachment.id)
            existing_record = record.env['auto.fill.resume'].search([
                        ('attachment_id', '=', attachment.id)], limit=1)
            # try:
            # existing_record = record.env['hr.applicant'].search([
            #             ('attachment_id', '=', attachment.id)], limit=1)

            if  existing_record:
                # print("existing_record  :",  existing_record.skill_score)
                # record.skill_score = existing_record.skill_score
                # record.resume_text = existing_record.resume_text
                record.resume_name = existing_record.resume_name
                record.resume_exp = existing_record.resume_exp
                record.resume_loc = existing_record.resume_loc
                # record.resume_summary = existing_record.resume_summary
                record.resume_phone = existing_record.resume_phone
                record.resume_email = existing_record.resume_email
                record.resume_linkedin = existing_record.resume_linkedin
                record.resume_degree = existing_record.resume_degree
                record.resume_github = existing_record.resume_github
                record.resume_certificates = existing_record.resume_certificates
                record.resume_known_languages= existing_record.resume_known_languages
                record.resume_achievements= existing_record.resume_achievements
                record.resume_project_names= existing_record.resume_project_names 
                record.resume_hobbies = existing_record.resume_hobbies
                record.resume_strength = existing_record.resume_strength
                record.resume_dob = existing_record.resume_dob
                record.resume_gender = existing_record.resume_gender
                record.resume_nationality = existing_record.resume_nationality
                record.resume_soft_skill = existing_record.resume_soft_skill
                record.resume_marital_status = existing_record.resume_marital_status
                record.resume_Weakness = existing_record.resume_Weakness
            # except:
                
            else:
            
                # openai api key here
                openai_key_record = record.env['ai.openai.key'].search([], limit=1)
                print("="*19)
                print("job open ai key: ", openai_key_record.open_ai_key)
                print("job openai key type   :", type(openai_key_record.open_ai_key))
                # Check if the key exists
                if not openai_key_record or not openai_key_record.open_ai_key:
                    # Raise a ValidationError if no key is found
                    # raise ValidationError("The OpenAI API key doesn't exist.")
                    continue

                # If the key exists, assign it to a variable
                openai_key = openai_key_record.open_ai_key

                # Continue processing with the valid API key
                _logger.info("Using OpenAI key: %s", openai_key)
                print("job open ai key: ", openai_key_record.open_ai_key)
                # openai_key = openai_key_record.open_ai_key
                
                if record.attachment_ids:
                    attachment = record.attachment_ids[0]
                    file_path = attachment._full_path(attachment.store_fname)
                    
        
                    result = extract_text_from_pdf(file_path,openai_key)
                    print("="*19)
                    print("resume result :", result)
                    print("="*19)
                    dict_data = json.loads(result)
                    

                    record.resume_name = dict_data["Name"]
                    record.resume_exp = dict_data["Experience"]
                    loc_data = dict_data["Location"]
                    if loc_data and loc_data != 'None':
                        record.resume_loc = dict_data["Location"]
                    else:
                        record.resume_loc = ''
                    # record.resume_summary = dict_data["Summary"]
                    phone_data = dict_data["Phone_Number"]
                    if phone_data and phone_data != 'None':
                        record.resume_phone = dict_data["Phone_Number"]
                    else:
                        record.resume_phone = ''
                    email_data = dict_data["Email"]
                    if email_data and email_data != 'None':
                        record.resume_email = dict_data["Email"]
                    else:
                        record.resume_email = ''
                    linkedin_data = dict_data["LinkedIn"]
                    if linkedin_data and linkedin_data != 'None':
                        record.resume_linkedin = dict_data["LinkedIn"]
                    else:
                        record.resume_linkedin = ''
                    
                    degree_data = dict_data["Degree"]
                    if degree_data and degree_data != 'None':
                        record.resume_degree = dict_data["Degree"]
                    else:
                        record.resume_degree = ''
                    github_data = dict_data["Github"]
                    if github_data and github_data != 'None':
                        record.resume_github = dict_data["Github"]
                    else:
                        record.resume_github = ''
                    marital_data = dict_data["Marital_Status"]
                    if marital_data and marital_data != 'None':
                        record.resume_marital_status = dict_data["Marital_Status"]
                    else:
                        record.resume_marital_status = ''
                    certificates = dict_data.get('Certificates', [])
                    if certificates and certificates != 'None':
                        if isinstance(certificates, list):
                            record.resume_certificates = ', \n'.join([f"{i+1}. {certificate}" for i, certificate in enumerate(certificates)])
                            get_certificates = ', \n'.join([f"{i+1}. {certificate}" for i, certificate in enumerate(certificates)])
                        elif isinstance(certificates, str):
                            items = [item.strip() for item in certificates.split(',')]

                            # Combine items into a numbered list
                            record.resume_certificates = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))
                            get_certificates = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))
                            
                        else:
                            # Handle the case where 'Certificates' is not a list
                            record.resume_certificates = str(certificates)
                            get_certificates = str(certificates)
                    else:
                            # Handle the case where 'Certificates' is not a list
                            record.resume_certificates = ''
                            get_certificates = ''
                    Known_Languages = dict_data.get('Known_Languages', [])
                    if Known_Languages and Known_Languages != 'None':
                        if isinstance(Known_Languages, list):
                            record.resume_known_languages = ', \n'.join([f"{i+1}. {language}" for i, language in enumerate(Known_Languages)])
                            get_resume_known_languages = ', \n'.join([f"{i+1}. {language}" for i, language in enumerate(Known_Languages)])
                        elif isinstance(Known_Languages, str):
                            items = [item.strip() for item in Known_Languages.split(',')]

                            # Combine items into a numbered list
                            record.resume_known_languages = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))
                            get_resume_known_languages = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))
                        else:
                            # Handle the case where 'Certificates' is not a list
                            record.resume_known_languages = str(Known_Languages)
                            get_resume_known_languages = str(Known_Languages)
                    else:
                        # Handle the case where 'Certificates' is not a list
                        record.resume_known_languages = ''
                        get_resume_known_languages = ''
                    Achievements = dict_data.get('Achievements', [])
                    if Achievements and Achievements != 'None':
                        if isinstance(Achievements, list):
                            record.resume_achievements = ', \n'.join([f"{i+1}. {achievement}" for i, achievement in enumerate(Achievements)])
                            get_resume_achievements = ', \n'.join([f"{i+1}. {achievement}" for i, achievement in enumerate(Achievements)])
                        elif isinstance(Achievements, str):
                            items = [item.strip() for item in Achievements.split(',')]

                            # Combine items into a numbered list
                            record.resume_achievements = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))
                            get_resume_achievements = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))
                            
                        else:
                            # Handle the case where 'Certificates' is not a list
                            record.resume_achievements = str(Achievements)
                            get_resume_achievements = str(Achievements)
                    else:
                        # Handle the case where 'Certificates' is not a list
                        record.resume_achievements = ''
                        get_resume_achievements = ''
                    Project_Names = dict_data.get('Project_Names', [])
                    if Project_Names and Project_Names != 'None':
                        if isinstance(Project_Names, list):
                            record.resume_project_names = ', \n'.join([f"{i+1}. {project}" for i, project in enumerate(Project_Names)])
                            get_resume_project_names = ', \n'.join([f"{i+1}. {project}" for i, project in enumerate(Project_Names)])
                        elif isinstance(Project_Names, str):
                            items = [item.strip() for item in Project_Names.split(',')]

                            # Combine items into a numbered list
                            record.resume_project_names = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))
                            get_resume_project_names = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))
                            
                        else:
                            # Handle the case where 'Certificates' is not a list
                            record.resume_project_names = str(Project_Names)
                            get_resume_project_names = str(Project_Names)
                    else:
                        # Handle the case where 'Certificates' is not a list
                        record.resume_project_names = str(Project_Names)
                        get_resume_project_names = str(Project_Names)
                    # Soft_Skill, Marital_Status, Weakness => resume_soft_skill, resume_marital_status, resume_Weakness
                    
                    Soft_Skill = dict_data.get('Soft_Skill', [])
                    if Soft_Skill and Soft_Skill != 'None':
                        if isinstance(Soft_Skill, list):
                            record.resume_soft_skill = ', \n'.join([f"{i+1}. {project}" for i, project in enumerate(Soft_Skill)])
                            get_resume_soft_skill = ', \n'.join([f"{i+1}. {project}" for i, project in enumerate(Soft_Skill)])
                        elif isinstance(Soft_Skill, str):
                            items = [item.strip() for item in Soft_Skill.split(',')]

                            # Combine items into a numbered list
                            record.resume_soft_skill = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))
                            get_resume_soft_skill = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))
                            
                        else:
                            # Handle the case where 'Certificates' is not a list
                            record.resume_soft_skill = str(Soft_Skill)
                            get_resume_soft_skill = str(Soft_Skill)
                    else:
                        # Handle the case where 'Certificates' is not a list
                        record.resume_soft_skill = ''
                        get_resume_soft_skill = ''
                    Weakness = dict_data.get('Weakness', [])
                    if Weakness and Weakness != 'None':
                        if isinstance(Weakness, list):
                            record.resume_Weakness = ', \n'.join([f"{i+1}. {project}" for i, project in enumerate(Weakness)])
                            get_resume_Weakness = ', \n'.join([f"{i+1}. {project}" for i, project in enumerate(Weakness)])
                        elif isinstance(Weakness, str):
                            items = [item.strip() for item in Weakness.split(',')]

                            # Combine items into a numbered list
                            record.resume_soft_skill = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))
                            get_resume_Weakness = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))
                            
                        else:
                            # Handle the case where 'Certificates' is not a list
                            record.resume_soft_skill = str(Weakness)
                            get_resume_Weakness = str(Weakness)
                    else:
                        # Handle the case where 'Certificates' is not a list
                        record.resume_soft_skill = ''
                        get_resume_Weakness = ''
                    hobbies =dict_data["Hobbies"]
                    if hobbies and hobbies != 'None':
                        if isinstance(hobbies, list):
                            record.resume_hobbies = ', \n'.join([f"{i+1}. {hobby}" for i, hobby in enumerate(hobbies)])
                            get_resume_hobbies = ', \n'.join([f"{i+1}. {hobby}" for i, hobby in enumerate(hobbies)])
                        elif isinstance(hobbies, str):
                            items = [item.strip() for item in hobbies.split(',')]

                            # Combine items into a numbered list
                            record.resume_hobbies = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))
                            get_resume_hobbies = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))
                            
                        else:
                            # Handle the case where 'Certificates' is not a list
                            record.resume_hobbies = str(hobbies)
                            get_resume_hobbies = str(hobbies)
                    else:
                        # Handle the case where 'Certificates' is not a list
                        record.resume_hobbies = ''
                        get_resume_hobbies = ''
                    Strength =dict_data["Strength"]
                    if hobbies and hobbies != 'None':
                        if isinstance(Strength, list):
                            record.resume_strength = ', \n'.join([f"{i+1}. {strength}" for i, strength in enumerate(Strength)])
                            get_resume_strength = ', \n'.join([f"{i+1}. {strength}" for i, strength in enumerate(Strength)])
                        elif isinstance(Strength, str):
                            items = [item.strip() for item in Strength.split(',')]

                            # Combine items into a numbered list
                            record.resume_strength = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))
                            get_resume_strength = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))
                            
                        else:
                            # Handle the case where 'Certificates' is not a list
                            record.resume_strength = str(Strength)
                            get_resume_strength = str(Strength)
                    else:
                        # Handle the case where 'Certificates' is not a list
                        record.resume_strength = ''
                        get_resume_strength = ''
                    DoB =dict_data["Date_Of_Birth"]
                    if DoB and DoB != 'None':
                        if isinstance(DoB, list):
                            record.resume_dob = ', '.join(DoB)
                        else:
                            # Handle the case where 'Certificates' is not a list
                            record.resume_dob = str(DoB)
                    else:
                        # Handle the case where 'Certificates' is not a list
                        record.resume_dob = ''
                    gender =dict_data["Gender"]
                    if gender and gender != 'None':
                        if isinstance(gender, list):
                            record.resume_gender = ', '.join(gender)
                        else:
                            # Handle the case where 'Certificates' is not a list
                            record.resume_gender = str(gender)
                    else:
                        # Handle the case where 'Certificates' is not a list
                        record.resume_gender = ''
                    nationality =dict_data["Nationality"]
                    if nationality and nationality != 'None':
                        if isinstance(nationality, list):
                            record.resume_nationality = ', '.join(nationality)
                        else:
                            # Handle the case where 'Certificates' is not a list
                            record.resume_nationality = str(nationality)
                    else:
                        # Handle the case where 'Certificates' is not a list
                        record.resume_nationality = ''
                    self.env.cr.commit()
                    print('saved data')
                    # record.invalidate_cache()  # Ensures that Odoo's cache is cleared and refetched
                    
                        # record.env['hr.applicant'].create({
                    record.env['auto.fill.resume'].create({
                    
                            'applicant_id': record.id,
                            'attachment_id': attachment.id,
                            # 'resume_text' : record.resume_text,
                            'resume_name' : record.resume_name,
                            'resume_exp' : record.resume_exp,
                            'resume_loc' : record.resume_loc,
                            # 'resume_summary' : record.resume_summary,
                            'resume_phone' : record.resume_phone,
                            'resume_email' : record.resume_email,
                            'resume_linkedin' : record.resume_linkedin,
                            'resume_degree' : record.resume_degree,
                            'resume_github' : record.resume_github,
                            'resume_certificates' : get_certificates,
                            'resume_known_languages' : get_resume_known_languages,
                            'resume_achievements' : get_resume_achievements,
                            'resume_project_names' : get_resume_project_names ,
                            'resume_hobbies' : get_resume_hobbies,
                            'resume_strength' : get_resume_strength,
                            'resume_dob' : record.resume_dob,
                            'resume_gender' : record.resume_gender,
                            'resume_nationality' : record.resume_nationality,
                            'resume_soft_skill' : get_resume_soft_skill,
                            'resume_Weakness' : get_resume_Weakness,
                            'resume_marital_status' : record.resume_marital_status,
                            
                            
                            
                        })
                    record.attachment_empty = True
                    
                    # return {
                    #     'type': 'ir.actions.client',
                    #     'tag': 'reload',
                    # }
                    
                    
                else:
                    # Set default values if no attachment is found
                    # record.resume_text = ''
                    record.resume_name = ''
                    record.resume_exp = ''
                    record.resume_loc = ''
                    # record.resume_summary = ''
                    record.resume_phone = ''
                    record.resume_email = ''
                    record.resume_linkedin = ''
                    record.resume_degree = ''
                    record.resume_github = ''
                    record.resume_certificates = ''
                    record.resume_known_languages='',
                    record.resume_achievements='',
                    record.resume_project_names='', 
                    record.resume_hobbies = '',
                    record.resume_strength = '',
                    record.resume_dob = '',
                    record.resume_gender = '',
                    record.resume_nationality = '',
                    record.resume_soft_skill = '',
                    record.resume_Weakness = '',
                    record.resume_marital_status = '',
        # return {
        #                 'type': 'ir.actions.client',
        #                 'tag': 'reload',
        #             }
# class IrAttachment(models.Model):
#     _inherit = 'ir.attachment'

#     @api.model
#     def create(self, vals):
#         # Call the original create method to create the attachment
#         attachment = super(IrAttachment, self).create(vals)
#         print("attachment:",attachment)
#         return {
#                 'type': 'ir.actions.client',
#                 'tag': 'reload',
#             }
        # Check if the attachment is for 'hr.applicant' model
    #     if vals.get('res_model') == 'hr.applicant' and vals.get('res_id'):
    #         # Reload the page after the attachment is created
    #         return {
    #             'type': 'ir.actions.client',
    #             'tag': 'reload',
    #         }
    #     return attachment

    # def write(self, vals):
    #     # Call the original write method to handle updates
    #     result = super(IrAttachment, self).write(vals)
    #     print("result:",result)
    #     # Check if the attachment is updated for 'hr.applicant' model
    #     if self.res_model == 'hr.applicant' and self.res_id:
    #         # Reload the page after the attachment is updated
    #         return {
    #             'type': 'ir.actions.client',
    #             'tag': 'reload',
    #         }
    #     return result

    # @api.model
    # def create(self, vals):
    #     res = super(Applicant, self).create(vals)
    #     if 'attachment_ids' in vals:
    #         # Your logic after attachment is uploaded
    #         self.env.cr.commit()
    #         res._trigger_refresh_action()
    #     return res

    # def _trigger_refresh_action(self):
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'reload',
    #     }

    # @api.depends('attachment_ids')
    # def generate_data(self):
    #     # Fetch the applicant record(s) you want to check
    #     applicants = self.env['hr.applicant'].search('attachment_ids')
    #     print("applicant:  ",  applicants.attachment_empty)
    #     print("applicant:  ",  applicants)
        
    #     if applicants.attachment_empty:
    #         print("inside applicant")
    #         # If there are any records where attachment_empty is True, refresh the page
    #         return {
    #             'type': 'ir.actions.client',
    #             'tag': 'reload',
    #         }




    

           
                    