# -*- coding: utf-8 -*-


def post_init_hook(env):
    """Génère la société de services informatiques et ses 21 mois d'opérations à l'installation du module."""
    env["aite.syscohada.demo.services"]._aite_generate()
