import PyPDF2,json
import docx2txt
from odoo import api, fields, models, tools
from odoo.exceptions import AccessError, UserError
from pdfminer.high_level import extract_text
import openai
import ast,re  
class OpenAIKey(models.Model):
    _name = 'ai.openai.key'
    _description = 'set up the open ai key'

    open_ai_key = fields.Char(string='openai key')
        
    @api.model
    def create(self, vals):
        existing_record = self.search([], limit=1)
        if existing_record:
            existing_record.write(vals)
            return existing_record
        else:
            return super(OpenAIKey, self).create(vals)

    def write(self, vals):
        existing_record = self.search([], limit=1)
        if existing_record:
            return super(OpenAIKey, existing_record).write(vals)
        return False

    @api.model
    def default_get(self, fields_list):
        res = super(OpenAIKey, self).default_get(fields_list)
        existing_record = self.search([], limit=1)
        if existing_record:
            res.update({
                'open_ai_key': existing_record.open_ai_key,
            })
        return res
    
    