from odoo import models, fields, api
from datetime import datetime


class BlogArticle(models.Model):
    _name = "blog.article"
    _description = "Blog Article"
    _rec_name = "name"

    date = fields.Date(string="Date", default=datetime.now())
    name = fields.Char(string="Name", readonly=True)
    url = fields.Text(string="URL", required=True)
    title = fields.Text(string="Title", required=True)
    preview = fields.Text(string="Preview")
    category_id = fields.Many2one(comodel_name="blog.category", string="Category")
    sub_category_id = fields.Many2one(comodel_name="blog.sub.category", string="Category")
    content = fields.Text(string="Content", required=True)
    gallery_id = fields.Many2one(comodel_name="blog.gallery", string="Gallery")
    gallery_ids = fields.Many2many(comodel_name="blog.gallery", string="Galleries")
    published_on = fields.Date(string="Published On")
    primary_tag_id = fields.Many2one(comodel_name="blog.tag", string="Primary Tag")
    secondary_tag_id = fields.Many2one(comodel_name="blog.tag", string="secondary Tag")
    other_tag_ids = fields.Many2many(comodel_name="blog.tag", string="Other Tags")
    is_completed = fields.Boolean(string="Is Completed", default=False)
    is_exported = fields.Boolean(string="Is Exported", default=False)

    @api.model
    def create(self, vals):
        vals["name"] = self.env['ir.sequence'].next_by_code("blog.article")
        return super(BlogArticle, self).create(vals)
