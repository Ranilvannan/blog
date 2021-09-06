from odoo import models, fields, api
from datetime import datetime
import random


class BlogArticle(models.Model):
    _name = "blog.article"
    _description = "Blog Article"
    _rec_name = "name"

    date = fields.Date(string="Date", default=datetime.now())
    name = fields.Char(string="Name", readonly=True)
    url = fields.Text(string="URL", required=True)
    title = fields.Text(string="Title", required=True)
    preview = fields.Text(string="Preview")
    category_id = fields.Many2one(comodel_name="blog.category", string="Category", required=True)
    sub_category_id = fields.Many2one(comodel_name="blog.sub.category", string="Sub Category")
    content = fields.Text(string="Content", required=True)
    gallery_id = fields.Many2one(comodel_name="blog.gallery", string="Gallery")
    gallery_ids = fields.Many2many(comodel_name="blog.gallery", string="Galleries")
    published_on = fields.Date(string="Published On")
    primary_tag_id = fields.Many2one(comodel_name="blog.tag", string="Primary Tag", required=True)
    secondary_tag_id = fields.Many2one(comodel_name="blog.tag", string="secondary Tag", required=True)
    other_tag_ids = fields.Many2many(comodel_name="blog.tag", string="Other Tags")
    is_completed = fields.Boolean(string="Is Completed", default=False)
    is_exported = fields.Boolean(string="Is Exported", default=False)

    def get_tags(self):
        data = []

        if self.primary_tag_id:
            data.append({
                "tag_id": self.primary_tag_id.id,
                "tag_name": self.primary_tag_id.name,
                "tag_url": self.primary_tag_id.url,
                "tag_code": self.primary_tag_id.code,
                "tag_description": self.primary_tag_id.description,
            })

        if self.secondary_tag_id:
            data.append({
                "tag_id": self.secondary_tag_id.id,
                "tag_name": self.secondary_tag_id.name,
                "tag_url": self.secondary_tag_id.url,
                "tag_code": self.secondary_tag_id.code,
                "tag_description": self.secondary_tag_id.description,
            })

        for rec in self.other_tag_ids:
            data.append({
                "tag_id": rec.id,
                "tag_name": rec.name,
                "tag_url": rec.url,
                "tag_code": rec.code,
                "tag_description": rec.description,
            })

        return data

    def get_related(self):
        related = []
        obj = self.env["blog.article"].search([("primary_tag_id", "=", self.primary_tag_id.id),
                                               ("id", "!=", self.id)])

        if not obj:
            return False

        if len(obj) >= 3:
            related = random.sample(obj, 3)
        else:
            related = obj

        return [{"url": rec.url, "name": rec.name} for rec in related]

    def get_previous(self):
        filter = [("secondary_tag_id", "=", self.secondary_tag_id.id)]

        previous_rec = filter + [("id", "<", self.id)]
        previous_obj = self.env["blog.article"].search(previous_rec)

        if previous_obj:
            return {"url": previous_obj[-1].url, "title": previous_obj[-1].title}

        last_rec = filter + [("id", ">", self.id)]
        last_obj = self.env["blog.article"].search(last_rec)

        if last_obj:
            return {"url": last_obj[-1].url, "title": last_obj[-1].title}

        return False

    def get_next(self):
        filter = [("secondary_tag_id", "=", self.secondary_tag_id.id)]

        next_rec = filter + [("id", ">", self.id)]
        next_obj = self.env["blog.article"].search(next_rec)

        if next_obj:
            return {"url": next_obj[0].url, "title": next_obj[0].title}

        first_rec = filter + [("id", "<", self.id)]
        first_obj = self.env["blog.article"].search(first_rec)

        if first_obj:
            return {"url": first_obj[0].url, "title": first_obj[0].title}

        return False

    @api.model
    def create(self, vals):
        vals["name"] = self.env['ir.sequence'].next_by_code("blog.article")
        return super(BlogArticle, self).create(vals)
