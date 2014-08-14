templates = { "{id}" : "view",
              "{id}/edit" : None }


def load_user(user, id):
    return { 'user': user, 'id' : id }

def load_user_list(user, ignored):
    return { 'user' : user }


types = { 'user' : load_user,
          'user_list' : load_user_list }

