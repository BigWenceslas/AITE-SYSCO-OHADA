from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Lot 2 : comptes de retenues et taxes de retenue à la source pour les sociétés existantes."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["res.company"].search([])._aite_syscohada_setup()
