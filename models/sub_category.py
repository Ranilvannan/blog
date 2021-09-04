from odoo import models, fields


class BlogSubCategory(models.Model):
    _name = "blog.sub.category"
    _description = "Blog Sub Category"
    _rec_name = "name"

    name = fields.Char(string="Name", required=True)
    url = fields.Char(string="URL", required=True)
    code = fields.Char(string="Code", required=True)
    description = fields.Text(string="Description")
    category_id = fields.Many2one(comodel_name="blog.category", string="Sub Category", required=True)

    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'Sub Category must be unique !')
    ]
