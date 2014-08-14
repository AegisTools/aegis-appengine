dependencies = ['users']

templates = { "{id}" : "view",
              "{id}/edit" : None }


def get_template(path):
    return "view", None

def load_user(id):
    return { 'id' : id }

def load_user_list(user_id):
    return { 'user' : user_id }


types = { 'user' : load_user,
          'user_list' : load_user_list }

