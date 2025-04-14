from django.apps import apps

def load_shared_models():
    for app_config in apps.get_app_configs():
        if app_config.name == 'shared_models':
            return list(app_config.get_models())
    return []
