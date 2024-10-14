from odoo import models, fields, api
from odoo.exceptions import AccessError, MissingError, ValidationError, UserError


class HrApplicantExtraInfoWizard(models.TransientModel):
    _name = 'hr.applicant.extra.info.wizard'
    _description = 'Extra Information Wizard for HR Applicant'

    basic = fields.Boolean(string='Basic Details')
    extra_all = fields.Boolean(string='Extra All Info')
    resume_linkedin = fields.Boolean(string='Show LinkedIn')
    resume_name = fields.Boolean(string='Show Name')
    resume_email = fields.Boolean(string='Show Email')
    resume_phone = fields.Boolean(string='Show Phone')
    resume_github = fields.Boolean(string='Show Github')
    resume_loc = fields.Boolean(string='Show Location')
    resume_degree = fields.Boolean(string='Show Degree')
    resume_exp = fields.Boolean(string='Show Experience')
    resume_certificates = fields.Boolean(string='Show Certificates')
    resume_known_languages = fields.Boolean(string='Show Known Language')
    resume_achievements = fields.Boolean(string='Show Achievements')
    resume_project_names = fields.Boolean(string='Show Project Names')
    resume_hobbies = fields.Boolean(string='Show Hobbies')
    resume_strength = fields.Boolean(string='Show Strength')
    resume_dob = fields.Boolean(string='Show Date_Of_Birth')
    resume_gender = fields.Boolean(string='Show Gender')
    resume_nationality = fields.Boolean(string='Show Nationality')
    resume_soft_skill = fields.Boolean(string='Show Soft Skill')
    resume_marital_status = fields.Boolean(string='Show Marital Status')
    resume_Weakness = fields.Boolean(string='Show Weakness')
    select_all = fields.Boolean(string="Select All")
    resume_name_val = fields.Text(string='Applicant Name')
    resume_linkedin_val = fields.Text(string='LinkedIn')
    resume_email_val = fields.Text(string='Email')
    resume_phone_val = fields.Text(string='Phone')
    resume_github_val = fields.Text(string='Github')
    resume_loc_val = fields.Text(string='Location')
    resume_exp_val = fields.Text(string='Experience')
    resume_degree_val = fields.Text(string='Degree')
    resume_certificates_val = fields.Text(string='Certificates')
    resume_known_languages_val = fields.Text(string='Known Languages')
    resume_achievements_val = fields.Text(string='Achievements')
    resume_project_names_val = fields.Text(string='Project Names')
    resume_hobbies_val = fields.Text(string='Hobbies')
    resume_strength_val = fields.Text(string='Strength')
    resume_dob_val = fields.Char(string='Date_Of_Birth')
    resume_gender_val = fields.Text(string='Gender')
    resume_nationality_val = fields.Text(string='Nationality')
    resume_soft_skill_val = fields.Text(string='Soft Skill')
    resume_marital_status_val = fields.Char(string='Marital Status')
    resume_Weakness_val = fields.Text(string='Weakness')
    show_header = fields.Boolean(compute='_compute_show_header')

    def default_get(self, fields):
        """Initialize the wizard with current applicant status."""
        res = super(HrApplicantExtraInfoWizard, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        if active_id:
            applicant = self.env['hr.applicant'].browse(active_id)
            res.update({
                'resume_linkedin': applicant.show_resume_linkedin,
                'resume_name': applicant.show_resume_name,
                'resume_email': applicant.show_resume_email,
                'resume_phone': applicant.show_resume_phone,
                'resume_github': applicant.show_resume_github,
                'resume_degree': applicant.show_resume_degree,
                'resume_loc': applicant.show_resume_loc,
                'resume_exp': applicant.show_resume_exp,
                'resume_certificates': applicant.show_resume_certificates,
                'resume_known_languages': applicant.show_resume_known_languages,
                'resume_achievements': applicant.show_resume_achievements,
                'resume_project_names': applicant.show_resume_project_names,
                'resume_hobbies': applicant.show_resume_hobbies,
                'resume_strength': applicant.show_resume_strength,
                'resume_dob': applicant.show_resume_dob,
                'resume_gender': applicant.show_resume_gender,
                'resume_nationality': applicant.show_resume_nationality,
                'resume_soft_skill': applicant.show_resume_soft_skill,
                'resume_marital_status': applicant.show_resume_marital_status,
                'resume_Weakness': applicant.show_resume_Weakness,
                'resume_linkedin_val': applicant.resume_linkedin,
                'resume_name_val': applicant.resume_name,
                'resume_email_val': applicant.resume_email,
                'resume_phone_val': applicant.resume_phone,
                'resume_github_val': applicant.resume_github,
                'resume_loc_val': applicant.resume_loc,
                'resume_exp_val': applicant.resume_exp,
                'resume_degree_val': applicant.resume_degree,
                'resume_certificates_val': applicant.resume_certificates,
                'resume_known_languages_val': applicant.resume_known_languages,
                'resume_achievements_val': applicant.resume_achievements,
                'resume_project_names_val': applicant.resume_project_names,
                'resume_hobbies_val': applicant.resume_hobbies,
                'resume_strength_val': applicant.resume_strength,
                'resume_dob_val': applicant.resume_dob,
                'resume_gender_val': applicant.resume_gender,
                'resume_nationality_val': applicant.resume_nationality,
                'resume_soft_skill_val': applicant.resume_soft_skill,
                'resume_marital_status_val': applicant.resume_marital_status,
                'resume_Weakness_val': applicant.resume_Weakness,
            })
        return res

    def apply_changes(self):
        """Apply the changes made in the wizard to the hr.applicant."""
        self.ensure_one()
        applicant = self.env['hr.applicant'].browse(self._context.get('active_id'))
        if not applicant:
            raise UserError("The applicant record does not exist or has been deleted.")
        applicant.write({
            'show_resume_github': self.resume_github,
            'show_resume_linkedin': self.resume_linkedin,
            'show_resume_name': self.resume_name,
            'show_resume_email': self.resume_email,
            'show_resume_phone': self.resume_phone,
            'show_resume_degree': self.resume_degree,
            'show_resume_loc': self.resume_loc,
            'show_resume_exp': self.resume_exp,
            'show_resume_certificates': self.resume_certificates,
            'show_resume_known_languages': self.resume_known_languages,
            'show_resume_achievements': self.resume_achievements,
            'show_resume_project_names': self.resume_project_names,
            'show_resume_hobbies': self.resume_hobbies,
            'show_resume_strength': self.resume_strength,
            'show_resume_dob': self.resume_dob,
            'show_resume_gender': self.resume_gender,
            'show_resume_nationality': self.resume_nationality,
            'show_resume_soft_skill': self.resume_soft_skill,
            'show_resume_marital_status': self.resume_marital_status,
            'show_resume_Weakness': self.resume_Weakness,
        })

        return {'type': 'ir.actions.act_window_close'}

    @api.onchange('select_all')
    def action_select_all(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            applicant = self.env['hr.applicant'].browse(active_id)
            field_mapping = {
                'basic': ['resume_name', 'resume_email', 'resume_phone'],
                'extra_all': [
                    'resume_linkedin', 'resume_github', 'resume_degree', 'resume_loc', 'resume_exp',
                    'resume_certificates', 'resume_known_languages', 'resume_achievements',
                    'resume_project_names', 'resume_hobbies', 'resume_strength', 'resume_dob',
                    'resume_gender', 'resume_nationality', 'resume_soft_skill', 'resume_marital_status',
                    'resume_Weakness'
                ]
            }
            for record in self:
                updates = {}
                if record.select_all:
                    if record.basic:
                        updates.update({field: True for field in field_mapping['basic']})
                    if record.extra_all:
                        updates.update({field: True for field in field_mapping['extra_all']})
                else:
                    for field in field_mapping['basic'] + field_mapping['extra_all']:
                        updates[field] = getattr(applicant, f'show_{field}', True)
                record.update(updates)

    @api.depends('basic', 'extra_all')
    def _compute_show_header(self):
        for record in self:
            record.show_header = record.basic or record.extra_all
