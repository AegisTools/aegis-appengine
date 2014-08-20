{% import 'templates/macros/forms.md' as forms %}

Task List
=========

{% for task in load("tasks/task") %}
* [{{ task.name }}](/tasks/{{ task.path }})
{% endfor %}

Create New Task
---------------

{{ forms.form("/tasks/{path}",
    [ { "id": "path", "name": "Path" },
      { "id": "name", "name": "Name" } ],
    "PUT") }}

----

[Sign Out]({{ sign_out_url }})

Raw Data
--------
{{ json(load("tasks/task"))|indent(4, true) }}

