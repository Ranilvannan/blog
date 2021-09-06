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
                "article_id": rec.id,
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
                "related_ids": rec.get_related(),
                "tags": rec.get_tags()
            }

            if rec.category_id:
                category_data = {
                    "category_id": rec.category_id.id,
                    "category_name": rec.category_id.name,
                    "category_code": rec.category_id.code,
                    "category_url": rec.category_id.url,
                    "category_description": rec.category_id.description,
                }
                data.update(category_data)

            if rec.sub_category_id:
                sub_category_data = {
                    "sub_category_id": rec.sub_category_id.id,
                    "sub_category_name": rec.sub_category_id.name,
                    "sub_category_code": rec.sub_category_id.code,
                    "sub_category_url": rec.sub_category_id.url,
                    "sub_category_description": rec.sub_category_id.description,
                }
                data.update(sub_category_data)

            if rec.gallery_ids:
                data["galleries"] = [{
                    "gallery_id": gallery.id,
                    "gallery_name": gallery.name,
                    "gallery_path": gallery.path,
                    "gallery_description": gallery.description} for gallery in rec.gallery_ids]

            if rec.gallery_id:
                gallery_data = {
                    "gallery_id": rec.gallery_id.id,
                    "gallery_name": rec.gallery_id.name,
                    "gallery_path": rec.gallery_id.path,
                    "gallery_description": rec.gallery_id.description,
                }
                data.update(gallery_data)

            article.append(data)

        return article

    def generate_tmp_json_file(self, json_data, suffix):
        prefix = datetime.now().strftime('%s')
        tmp_file = tempfile.NamedTemporaryFile(prefix=prefix, suffix=suffix, delete=False, mode="w+")
        json.dump(json_data, tmp_file)
        tmp_file.flush()

        return tmp_file

    def move_tmp_file(self, tmp_file):
        settings = self.type_id.export_id
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
