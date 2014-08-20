{% import 'templates/macros/forms.md' as forms %}

{% set project = load("projects/project", keys.project) %}
{{ project.name }}
==================

{% if project.parent %}**parent:** [{{ project.parent.name }}](/projects/{{ project.parent.path }}){% endif %}
**created:** {{ project.created }}  
**created_by:** [{{ project.created_by }}](/users/{{ project.created_by }})

{% for child in project.children %}
* [{{ child.name }}](/projects/{{ child.path }})
{% endfor %}

[Root Projects](/projects)

Create New Project
------------------

{{ forms.form("/projects/" + project.path + "/{path}",
    [ { "id": "path", "name": "Path" },
      { "id": "name", "name": "Name" } ],
    "PUT") }}

----

[Sign Out]({{ sign_out_url }})

----

Raw Data
--------
{{ json(load("projects/project", keys.project))|indent(4, true) }}


