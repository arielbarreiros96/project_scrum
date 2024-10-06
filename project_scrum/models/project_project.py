# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import datetime

from odoo import _, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    sprint_ids = fields.One2many("project.sprint", "project_id", string="Sprints")
    is_scrum_project = fields.Boolean("Uses Scrum")

    def action_view_sprints(self):
        self.ensure_one()
        return {
            "name": self.name + _(" Sprints"),
            "type": "ir.actions.act_window",
            "res_model": "project.sprint",
            "view_mode": "tree,form",
            "domain": [("project_id", "=", self.id)],
            "context": {
                "default_project_id": self.id,
                "default_date_start": datetime.today(),
            },
        }

    def action_view_backlog(self):
        self.ensure_one()
        return {
            "name": self.name + _(" Backlog"),
            "type": "ir.actions.act_window",
            "res_model": "project.task",
            "view_mode": "tree,form",
            "domain": [
                "&",
                ("project_id", "=", self.id),
                "&",
                ("is_scrum_task", "=", True),
                "&",
                ("sprint_id", "=", False),
                ("stage_id.fold", "!=", True),
            ],
        }


class ProjecTask(models.Model):
    _inherit = "project.task"

    sprint_id = fields.Many2one("project.sprint", string="Sprint")
    is_scrum_task = fields.Boolean("Uses Scrum")


class ProjectSprint(models.Model):
    _name = "project.sprint"
    _description = "Project Sprints"

    name = fields.Char("Sprint name", required=True)
    project_id = fields.Many2one("project.project", string="Project", required=True)
    task_ids = fields.One2many("project.task", "sprint_id", string="Tasks")
    date_start = fields.Date("Date Start")
    date_stop = fields.Date("Date End")
