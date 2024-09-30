from odoo import models, fields, api
from odoo.exceptions import AccessError, MissingError, ValidationError, UserError


class HrApplicantExtraInfoWizard(models.TransientModel):
    _name = 'hr.applicant.extra.info.wizard'
    _description = 'Extra Information Wizard for HR Applicant'

    basic = fields.Boolean(string='Basic Details')
    # def toggle_is_basic(self):
    #     for record in self:
    #         # record.basic = not record.basic
    #         record.basic = True
    #         record.extra_all = False
    #     return {
    #     'type': 'ir.actions.act_window',
    #     'view_mode': 'form',
    #     'res_model': self._name,
    #     'res_id': self.id,
    #     'target': 'new',  # Keep the pop-up open
    # }
      
    extra_all = fields.Boolean(string='Extra All Info')
    # def toggle_is_extra(self):
    #     for record in self:
    #         record.extra_all = True
    #         record.basic = False
    #     return {
    #     'type': 'ir.actions.act_window',
    #     'view_mode': 'form',
    #     'res_model': self._name,
    #     'res_id': self.id,
    #     'target': 'new',  # Keep the pop-up open
    # }
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
    # Soft_Skill, Marital_Status, Weakness => resume_soft_skill, resume_marital_status, resume_Weakness
    
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
    
    def default_get(self, fields):
        """Initialize the wizard with current applicant status."""
        res = super(HrApplicantExtraInfoWizard, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        if active_id:
            applicant = self.env['hr.applicant'].browse(active_id)
            # applicant = self.env['auto.fill.resume'].browse(active_id)
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


    # def apply_changes(self):
    #     """Apply the changes made in the wizard to the hr.applicant."""
    #     self.ensure_one()
    #     applicant = self.env['hr.applicant'].browse(self._context.get('active_id'))
        
    #     if self.resume_github== True:
    #         applicant.write({'show_resume_github': True})
    #     else:
    #         applicant.write({'show_resume_github': False})
    #     if self.resume_linkedin== True:
    #         applicant.write({'show_resume_linkedin': True})
    #     else:
    #         applicant.write({'show_resume_linkedin': False})
    #     if self.resume_name== True:
    #         applicant.write({'show_resume_name': True})
    #     else:
    #         applicant.write({'show_resume_name': False})
    #     if self.resume_email== True:
    #         applicant.write({'show_resume_email': True})
    #     else:
    #         applicant.write({'show_resume_email': False})
    #     if self.resume_phone== True:
    #         applicant.write({'show_resume_phone': True})
    #     else:
    #         applicant.write({'show_resume_phone': False})
    #     if self.resume_degree== True:
    #         applicant.write({'show_resume_degree': True})
    #     else:
    #         applicant.write({'show_resume_degree': False})
    #     if self.resume_loc== True:
    #         applicant.write({'show_resume_loc': True})
    #     else:
    #         applicant.write({'show_resume_loc': False})
    #     if self.resume_exp== True:
    #         applicant.write({'show_resume_exp': True})
    #     else:
    #         applicant.write({'show_resume_exp': False})
    #     if self.resume_certificates== True:
    #         applicant.write({'show_resume_certificates': True})
    #     else:
    #         applicant.write({'show_resume_certificates': False})
    #     if self.resume_known_languages== True:
    #         applicant.write({'show_resume_known_languages': True})
    #     else:
    #         applicant.write({'show_resume_known_languages': False})
    #     if self.resume_achievements== True:
    #         applicant.write({'show_resume_achievements': True})
    #     else:
    #         applicant.write({'show_resume_achievements': False})
    #     if self.resume_project_names== True:
    #         applicant.write({'show_resume_project_names': True})
    #     else:
    #         applicant.write({'show_resume_project_names': False})
    #     if self.resume_hobbies== True:
    #         applicant.write({'show_resume_hobbies': True})
    #     else:
    #         applicant.write({'show_resume_hobbies': False})
    #     if self.resume_strength== True:
    #         applicant.write({'show_resume_strength': True})
    #     else:
    #         applicant.write({'show_resume_strength': False})
    #     if self.resume_dob== True:
    #         applicant.write({'show_resume_dob': True})
    #     else:
    #         applicant.write({'show_resume_dob': False})
    #     if self.resume_gender== True:
    #         applicant.write({'show_resume_gender': True})
    #     else:
    #         applicant.write({'show_resume_gender': False})
    #     if self.resume_nationality== True:
    #         applicant.write({'show_resume_nationality': True})
    #     else:
    #         applicant.write({'show_resume_nationality': False})
    #     if self.resume_soft_skill== True:
    #         applicant.write({'show_resume_soft_skill': True})
    #     else:
    #         applicant.write({'show_resume_soft_skill': False})
    #     if self.resume_marital_status== True:
    #         applicant.write({'show_resume_marital_status': True})
    #     else:
    #         applicant.write({'show_resume_marital_status': False})
    #     if self.resume_Weakness== True:
    #         applicant.write({'show_resume_Weakness': True})
    #     else:
    #         applicant.write({'show_resume_Weakness': False})
        
    #     return {'type': 'ir.actions.act_window_close'}
    
    def apply_changes(self):
        """Apply the changes made in the wizard to the hr.applicant."""
        self.ensure_one()
        applicant = self.env['hr.applicant'].browse(self._context.get('active_id'))

        if not applicant:
            raise UserError("The applicant record does not exist or has been deleted.")

        # Update fields based on wizard selections
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
        # Assuming `active_id` is the current applicant's ID passed in context
        active_id = self.env.context.get('active_id')
        
        if active_id:
            # Fetch the hr.applicant record based on active_id
            applicant = self.env['hr.applicant'].browse(active_id)

            for record in self:
                if record.select_all:
                    # When select_all is True, set all fields to True
                    record.update({
                        'resume_linkedin': True,
                        'resume_name': True,
                        'resume_email': True,
                        'resume_phone': True,
                        'resume_github': True,
                        'resume_degree': True,
                        'resume_loc': True,
                        'resume_exp': True,
                        'resume_certificates': True,
                        'resume_known_languages': True,
                        'resume_achievements': True,
                        'resume_project_names': True,
                        'resume_hobbies': True,
                        'resume_strength': True,
                        'resume_dob': True,
                        'resume_gender': True,
                        'resume_nationality': True,
                        'resume_soft_skill': True,
                        'resume_marital_status': True,
                        'resume_Weakness': True,
                    })
                else:
                    # When select_all is False, only deselect fields that are not True in the hr.applicant model
                    record.update({
                        'resume_linkedin': False if not applicant.show_resume_linkedin else True,
                        'resume_name': False if not applicant.show_resume_name else True,
                        'resume_email': False if not applicant.show_resume_email else True,
                        'resume_phone': False if not applicant.show_resume_phone else True,
                        'resume_github': False if not applicant.show_resume_github else True,
                        'resume_degree': False if not applicant.show_resume_degree else True,
                        'resume_loc': False if not applicant.show_resume_loc else True,
                        'resume_exp': False if not applicant.show_resume_exp else True,
                        'resume_certificates': False if not applicant.show_resume_certificates else True,
                        'resume_known_languages': False if not applicant.show_resume_known_languages else True,
                        'resume_achievements': False if not applicant.show_resume_achievements else True,
                        'resume_project_names': False if not applicant.show_resume_project_names else True,
                        'resume_hobbies': False if not applicant.show_resume_hobbies else True,
                        'resume_strength': False if not applicant.show_resume_strength else True,
                        'resume_dob': False if not applicant.show_resume_dob else True,
                        'resume_gender': False if not applicant.show_resume_gender else True,
                        'resume_nationality': False if not applicant.show_resume_nationality else True,  # Keep nationality unchanged
                        'resume_soft_skill': False if not applicant.show_resume_soft_skill else True,  # Keep nationality unchanged
                        'resume_marital_status': False if not applicant.show_resume_marital_status else True,  # Keep nationality unchanged
                        'resume_Weakness': False if not applicant.show_resume_Weakness else True,  # Keep nationality unchanged
                    })
