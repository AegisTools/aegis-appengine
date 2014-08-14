dependencies = ['users']

templates = { "{id}" : "view",
              "{id}/edit" : None,
              "{id}/edit/{item}" : None }

def load_permission(id):
    return { 'id' : id }

def load_permission_list(user_id):
    return { 'user' : user_id }

def action(verb, path, data):
    return None

types = { 'permission' : load_permission,
          'permission_list' : load_permission_list }

