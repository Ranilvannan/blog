from odoo import models, fields
import os
import json
from datetime import datetime
import tempfile
from paramiko import SSHClient, AutoAddPolicy


class ExportService(models.TransientModel):
    _name = "export.service"
    _description = "Export Service"

    type_id = fields.Many2one(comodel_name="blog.type", string="Type")

    def reset_gallery(self):
        """Reset Gallery called from scheduler no UI for triggering reset"""
        recs = self.env["blog.gallery"].search([("is_exported", "=", True)])[:100]

        for rec in recs:
            rec.is_exported = False

    def reset_article(self):
        """Reset Article called from scheduler no UI for triggering reset"""
        recs = self.env["blog.article"].search([("is_exported", "=", True),
                                                ("category_id.type_id", "=", self.type_id.id)])[:100]

        for rec in recs:
            rec.is_exported = False

    def trigger_article_export(self):
        recs = self.env["blog.article"].search([("is_exported", "=", False),
                                                ("is_completed", "=", True),
                                                ("category_id.type_id", "=", self.type_id.id)])[:10]

        if recs:
            filename = "_{0}_{1}".format(self.type_id.code, "blog.json")
            blog_list = self.generate_article_json(recs)
            tmp_file = self.generate_tmp_json_file(blog_list, filename)
            self.move_tmp_file(tmp_file)

        for rec in recs:
            rec.is_exported = True

    def generate_article_json(self, recs):
        article = []

        for rec in recs:
            data = {
                "id": rec.id,
                "date": rec.date.strftime("%d-%m-%Y"),
                "published_on": rec.published_on.strftime("%d-%m-%Y"),
                "blog_type": rec.category_id.type_id.code,
                "name": rec.name,
                "url": rec.url,
                "title": rec.title,
                "preview": rec.preview,
                "content": rec.content,
                "previous": rec.get_previous(),
                "next": rec.get_next(),
                "related_ids": rec.get_related()
            }

            if rec.category_id:
                data["category"] = {
                    "id": rec.category_id.id,
                    "name": rec.category_id.name,
                    "code": rec.category_id.code,
                    "url": rec.category_id.url,
                    "description": rec.category_id.description,
                }

            if rec.sub_category_id:
                data["sub_category"] = {
                    "id": rec.sub_category_id.id,
                    "name": rec.sub_category_id.name,
                    "code": rec.sub_category_id.code,
                    "url": rec.sub_category_id.url,
                    "description": rec.sub_category_id.description,
                }

            if rec.gallery_ids:
                data["galleries"] = [{
                    "id": gallery.id,
                    "name": gallery.name,
                    "path": gallery.path,
                    "description": gallery.description} for gallery in rec.gallery_ids]

            if rec.gallery_id:
                data["image"] = {
                    "id": rec.gallery_id.id,
                    "name": rec.gallery_id.name,
                    "path": rec.gallery_id.path,
                    "description": rec.gallery_id.description,
                }

            article.append(data)

        return article

    def generate_tmp_json_file(self, json_data, suffix):
        prefix = datetime.now().strftime('%s')
        tmp_file = tempfile.NamedTemporaryFile(prefix=prefix, suffix=suffix, delete=False, mode="w+")
        json.dump(json_data, tmp_file)
        tmp_file.flush()

        return tmp_file

    def move_tmp_file(self, tmp_file):
        settings = self.env["export.settings"].search([("type_id", "=", self.type_id.id)])
        filename = os.path.basename(tmp_file.name)
        source = tmp_file.name
        destination = os.path.join(settings.path, filename)

        ssh_client = SSHClient()
        ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        ssh_client.connect(hostname=settings.host,
                           username=settings.username,
                           key_filename=settings.key_file)
        sftp_client = ssh_client.open_sftp()
        sftp_client.put(source, destination)
        sftp_client.close()
        tmp_file.close()

        return True
