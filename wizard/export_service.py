from odoo import models, fields, api, exceptions
from odoo.tools import config
import os
import json
from datetime import datetime
import tempfile
from paramiko import SSHClient, AutoAddPolicy

BLOG_FILENAME = "_blog.json"
CATEGORY_FILENAME = "_category.json"
GALLERY_FILENAME = "_gallery.json"


class ExportService(models.TransientModel):
    _name = "export.service"
    _description = "Export Service"

    def reset_gallery(self):
        recs = self.env["blog.gallery"].search([("is_exported", "=", True)])[:500]

        for rec in recs:
            rec.is_exported = False

    def reset_article(self):
        recs = self.env["blog.article"].search([("is_exported", "=", True)])[:500]

        for rec in recs:
            rec.is_exported = False

    def trigger_article_export(self):
        recs = self.env["blog.article"].search([("is_exported", "=", False),
                                                ("published_on", "!=", False),
                                                ("is_finished", "=", True)])[:100]

        if recs:
            blog_list = self.generate_article_json(recs)
            tmp_file = self.generate_tmp_json_file(blog_list, BLOG_FILENAME)
            self.move_tmp_file(tmp_file)

        for rec in recs:
            rec.is_exported = True

    def trigger_category_export(self):
        recs = self.env["blog.category"].search([("id", ">", 0)])

        if recs:
            category_list = self.generate_category_json(recs)
            tmp_file = self.generate_tmp_json_file(category_list, CATEGORY_FILENAME)
            self.move_tmp_file(tmp_file)

    def trigger_gallery_export(self):
        recs = self.env["blog.gallery"].search([("is_exported", "=", False)])[:500]

        if recs:
            gallery_list = self.generate_gallery_json(recs)
            tmp_file = self.generate_tmp_json_file(gallery_list, GALLERY_FILENAME)
            self.move_tmp_file(tmp_file)

        for rec in recs:
            rec.is_exported = True

    def generate_article_json(self, recs):
        story = []

        for rec in recs:
            data = {
                "blog_id": rec.id,
                "name": rec.name,
                "url": rec.url,
                "title": rec.title,
                "preview": rec.preview,
                "image_filename": rec.gallery_id.name,
                "image_filepath": rec.gallery_id.path,
                "image_description": rec.gallery_id.description,
                "galleries": [{"image_filename": gallery.name,
                               "image_filepath": gallery.path,
                               "image_description": gallery.description} for gallery in rec.gallery_ids],
                "previous_title": rec.prev_id.title,
                "previous_url": rec.prev_id.url,
                "next_title": rec.next_id.title,
                "next_url": rec.next_id.url,
                "category_name": rec.category_id.name,
                "category_url": rec.category_id.url,
                "content_ids": rec.content.split("|#|"),
                "published_on": rec.published_on.strftime("%d-%m-%Y") if rec.published_on else None,
                "date": rec.published_on.isoformat() if rec.published_on else None
            }

            story.append(data)

        return story

    def generate_category_json(self, recs):
        category = []

        for rec in recs:
            data = {
                "category_id": rec.id,
                "name": rec.name,
                "code": rec.code,
                "url": rec.url,
                "description": rec.description
            }
            category.append(data)

        return category

    def generate_gallery_json(self, recs):
        galleries = []

        for rec in recs:
            image = {
                "gallery_id": rec.id,
                "name": rec.name,
                "path": rec.path,
                "description": rec.description
            }
            galleries.append(image)

        return galleries

    def generate_tmp_json_file(self, json_data, suffix):
        prefix = datetime.now().strftime('%s')
        tmp_file = tempfile.NamedTemporaryFile(prefix=prefix, suffix=suffix, delete=False, mode="w+")
        json.dump(json_data, tmp_file)
        tmp_file.flush()

        return tmp_file

    def move_tmp_file(self, tmp_file):
        settings = self.env["export.settings"].search([("code", "=", "EXP")])
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
