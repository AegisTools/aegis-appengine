{% set user = load("users/user", keys.user) %}
{{user.user}}
=============

* **active:** {{user.active}}
* **notes:** {{user.notes}}
* **created_by:** [{{user.created_by}}](/users/{{user.created_by}})
* **created:** {{user.created}}
* **updated:** {{ user.updated}}

[Sign Out]({{ sign_out_url }})

----

Raw Data
--------
{{ json(load("users/user", keys.user))|indent(4, true) }}


