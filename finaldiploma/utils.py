def get_env_variable(env_instance, var_name, default=None, cast=None):
    try:
        if cast:
            return env_instance(var_name, cast=cast)
        return env_instance(var_name)
    except Exception:
        if default is None:
            raise Exception(f"The {var_name} environment variable is missing!")
        return default
