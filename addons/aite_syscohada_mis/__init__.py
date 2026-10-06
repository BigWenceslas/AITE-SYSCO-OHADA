from . import models


def post_init_hook(env):
    env["mis.report"]._aite_syscohada_build()
