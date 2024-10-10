# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import datetime

from odoo import _, fields, models, api


class ProjectProject(models.Model):
    _inherit = "project.project"

    sprint_ids = fields.Many2many("project.sprint", string="Sprints", compute="_compute_sprint_ids")
    is_scrum_project = fields.Boolean("Uses Scrum")

    @api.depends("task_ids.sprint_id")
    def _compute_sprint_ids(self):
        for project in self:
            if project.task_ids:
                for task in project.task_ids:
                    if task.sprint_id and task.sprint_id not in project.sprint_ids:
                        project.sprint_ids = [(4, task.sprint_id.id)]

    def action_view_sprints(self):
        self.ensure_one()
        return {
            "name": self.name + _(" Sprints"),
            "type": "ir.actions.act_window",
            "res_model": "project.sprint",
            "view_mode": "tree,form",
            "domain": [("project_ids", "in", self.id)],
            "context": {
                "default_project_ids": [(6, 0, [self.id])],
                "default_date_start": datetime.today(),
            },
        }

    def action_view_project_backlog(self):
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

    @api.model
    def default_get(self, fields_list):
        defaults = super(ProjecTask, self).default_get(fields_list)
        if 'project_id' in defaults:
            project = self.env['project.project'].browse(defaults['project_id'])
            defaults['is_scrum_task'] = project.is_scrum_project
        return defaults


class ProjectSprint(models.Model):
    _name = "project.sprint"
    _description = "Project Sprints"

    name = fields.Char("Sprint name", required=True)
    project_ids = fields.Many2many("project.project", "sprint_ids", string="Projects", compute="_compute_project_ids")
    task_ids = fields.One2many("project.task", "sprint_id", string="Tasks")
    date_start = fields.Date("Date Start")
    date_stop = fields.Date("Date End")
    state = fields.Selection(
        [("draft", "Sprint Planning"), ("active", "Sprint Execution"), ("review", "Sprint Review"), ("done", "Sprint Retrospective"), ("cancel", "Cancelled")],
        string="Sprint Stage",
        default="draft",
        required=True,
    )

    @api.depends("task_ids")
    def _compute_project_ids(self):
        for sprint in self:
            if sprint.task_ids:
                for task in sprint.task_ids:
                    if task.project_id and task.project_id not in sprint.project_ids:
                        sprint.project_ids = [(4, task.project_id.id)]

    def action_draft(self):
        self.ensure_one()
        self.state = "draft"

    def action_start(self):
        self.ensure_one()
        self.state = "active"

    def action_review(self):
        self.ensure_one()
        self.state = "review"

    def action_done(self):
        self.ensure_one()
        self.state = "done"

    def action_cancel(self):
        self.ensure_one()
        self.state = "cancel"
