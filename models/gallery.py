from odoo import models, fields
from datetime import datetime


class BlogGallery(models.Model):
    _name = "blog.gallery"
    _description = "Blog Galleries"
    _rec_name = "name"

    date = fields.Date(string="Date", default=datetime.now())
    name = fields.Char(string="File Name", required=True)
    path = fields.Char(string="File Path", required=True)
    description = fields.Char(string="Description")
    is_exported = fields.Boolean(string="Is Exported")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Gallery must be unique !')
    ]
