# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class Users(models.Model):
    _inherit = "res.users"

    # Archive contact when archive user
    def write(self, vals):
        res = super(Users, self).write(vals)
        for user in self:
            if vals.get('active') is not None:
                user.sudo().partner_id.write({'active': vals.get('active')})
        return res

    def unlink(self):
        partner = self.mapped('partner_id')
        res = super(Users, self).unlink()
        self.env['res.partner'].sudo().browse(partner.id).write({'active': False})
        return res


class Partner(models.Model):
    _inherit = "res.partner"

    def write(self, vals):
        res = super(Partner, self).write(vals)
        for partner in self:
            # Archive childs partner when archive parent
            if vals.get('active') is False:
                self.child_ids.active = False
            # Unarchive childs partner when unarchive parent
            elif vals.get('active') is True:
                childs = self.env['res.partner'].search([('parent_id', '=', partner.id), ('active', '=', False)])
                for child in childs:
                    self.env['res.partner'].sudo().browse(child.id).write({'active': True})
        return res


class ApplicantGetRefuseReason(models.TransientModel):
    _inherit = 'applicant.get.refuse.reason'

    def action_refuse_reason_apply(self):
        res = super(ApplicantGetRefuseReason, self).action_refuse_reason_apply()
        for refuse in self:
            refuse = refuse.sudo()
            applicants = refuse.applicant_ids

            # Archive contact
            partners = applicants.mapped('partner_id')
            partners.sudo().write({'active': False})

        return res


# class Applicant(models.Model):
#     _inherit = "hr.applicant"
#
#     # Unarchive contact when restore applicant
#     def write(self, vals):
#         res = super(Applicant, self).write(vals)
#         if not self.env.context.get('delay_archive_partner'):
#             for applicant in self:
#                 if vals.get('active') is not None and applicant.sudo().partner_id:
#                     applicant.sudo().partner_id.write({'active': vals.get('active')})
#         return res


