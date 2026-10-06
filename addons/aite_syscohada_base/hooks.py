import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Applique le paramétrage SYSCOHADA aux sociétés déjà équipées d'un plan OHADA."""
    companies = env["res.company"].search([])
    targets = companies.filtered(lambda c: c._aite_is_syscohada())
    _logger.info("AITE SYSCOHADA : paramétrage de %s société(s)", len(targets))
    targets._aite_syscohada_setup()
