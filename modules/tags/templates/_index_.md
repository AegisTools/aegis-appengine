{% import 'templates/macros/forms.md' as forms %}

Root Tags
=========

{% for tag in load("tags/tag") %}
* [{{tag.name}}](/tags/{{tag.path}})
{% endfor %}

Create New Tag
--------------

{{ forms.form("/tags/{path}",
    [ { "id": "path", "name": "Path" },
      { "id": "name", "name": "Name" } ],
    "PUT") }}

----

[Sign Out]({{ sign_out_url }})

Raw Data
--------
{{ json(load("tags/tag"))|indent(4, true) }}


