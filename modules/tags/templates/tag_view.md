{% import 'templates/macros/forms.md' as forms %}

{% set tag = load("tags/tag", keys.tag) %}
{{ tag.name }}
==============

{% if tag.parent %}**parent:** [{{ tag.parent.name }}](/tags/{{ tag.parent.path }}){% endif %}  
**created:** {{ tag.created }}  
**created_by:** [{{ tag.created_by }}](/users/{{ tag.created_by }})

{% for child in tag.children %}
* [{{ child.name }}](/tags/{{ child.path }})
{% endfor %}

[Root Tags](/tags)

Create New Tag
--------------

{{ forms.form("/tags/" + tag.path + "/{path}",
    [ { "id": "path", "name": "Path" },
      { "id": "name", "name": "Name" } ],
    "PUT") }}

----

[Sign Out]({{ sign_out_url }})

----

Raw Data
--------
{{ json(load("tags/tag", keys.tag))|indent(4, true) }}


