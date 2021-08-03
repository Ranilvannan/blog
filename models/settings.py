from odoo import models, fields


class ExportSettings(models.Model):
    _name = "export.settings"
    _description = "Export Settings"
    _rec_name = "name"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    host = fields.Char(string="Host", required=True)
    username = fields.Char(string="username", required=True)
    key_file = fields.Char(string="Key File", required=True)
    path = fields.Char(string="Export Path", required=True)

    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'Export Settings must be unique !')
    ]