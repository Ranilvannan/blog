from odoo import models, fields


class BlogCategory(models.Model):
    _name = "blog.category"
    _description = "Blog Category"
    _rec_name = "name"

    name = fields.Char(string="Name", required=True)
    url = fields.Char(string="URL", required=True)
    code = fields.Char(string="Code", required=True)
    type_id = fields.Many2one(comodel_name="blog.type", string="Type")
    description = fields.Text(string="Description")
    sub_category_ids = fields.One2many(comodel_name="blog.sub.category", inverse_name="category_id")

    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'Category must be unique !')
    ]