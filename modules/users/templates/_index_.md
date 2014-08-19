{% import 'templates/macros/forms.md' as forms %}

User List
=========

{% for user in load("users/user_list") %}
* [{{user.user}}](/users/{{user.user}})
    * **active:** {{user.active}}
    * **notes:** {{user.notes}}
    * **created_by:** [{{user.created_by}}](/users/{{user.created_by}})
    * **created:** {{user.created}}
    * **updated:** {{ user.updated}}
{% endfor %}

Create New User
---------------

{{ forms.form("/users/{user}", 
    [ { "id": "user",       "name": "Username" },
      { "id": "first_name", "name": "First Name" },
      { "id": "last_name",  "name": "Last Name" } ], 
    "PUT") }}

----

[Sign Out]({{ sign_out_url }})

Raw Data
--------
{{ json(load("users/user_list"))|indent(4, true) }}

