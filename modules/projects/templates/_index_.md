{% import 'templates/macros/forms.md' as forms %}

Project List
============

{% for project in load("projects/project") %}
* [{{ project.name }}](/projects/{{ project.path }})
{% endfor %}

Create New Project
------------------

{{ forms.form("/projects/{path}",
    [ { "id": "path", "name": "Path" },
      { "id": "name", "name": "Name" } ],
    "PUT") }}

----

[Sign Out]({{ sign_out_url }})

Raw Data
--------
{{ json(load("projects/project"))|indent(4, true) }}

