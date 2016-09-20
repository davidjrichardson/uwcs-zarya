OLD_APPS = [
    'cms',
    'events',
    'memberinfo'
]


class MigrateRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label in OLD_APPS:
            return 'old_data'
        return None
