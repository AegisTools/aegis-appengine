{% import 'templates/macros/forms.md' as forms %}

{% set task = load("tasks/task", keys.task) %}
{{ task.name }}
==================

{% if task.parent %}**parent:** [{{ task.parent.name }}](/tasks/{{ task.parent.path }}){% endif %}
**active:** {{ task.active }}  
**created:** {{ task.created }}  
**created_by:** [{{ task.created_by }}](/users/{{ task.created_by }})

{% for child in task.children %}
* [{{ child.name }}](/tasks/{{ child.path }})
{% endfor %}

[Root Tasks](/tasks)

Create New Task
---------------

{{ forms.form("/tasks/" + task.path + "/{path}",
    [ { "id": "path", "name": "Path" },
      { "id": "name", "name": "Name" } ],
    "PUT") }}

----

[Sign Out]({{ sign_out_url }})

----

Raw Data
--------
{{ json(load("tasks/task", keys.task))|indent(4, true) }}


