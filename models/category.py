from odoo import models, fields


class BlogCategory(models.Model):
    _name = "blog.category"
    _description = "Blog Category"
    _rec_name = "name"

    name = fields.Char(string="Name", required=True)
    url = fields.Char(string="URL", required=True)
    code = fields.Char(string="Code", required=True)
    description = fields.Text(string="Description")

    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'Category must be unique !')
    ]