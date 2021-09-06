from odoo import models, fields


class BlogType(models.Model):
    _name = "blog.type"
    _description = "Blog Type"
    _rec_name = "name"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    export_id = fields.Many2one(comodel_name="export.settings", string="Export Settings", required=True)
    description = fields.Text(string="Description")

    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'Blog Type must be unique !')
    ]