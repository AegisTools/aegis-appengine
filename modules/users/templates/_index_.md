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

[Sign Out]({{ sign_out_url }})

----

Raw Data
--------
{{ json(load("users/user_list"))|indent(4, true) }}

