Root Tags
=========

{% for tag in load("tags/tag") %}
* [{{tag.name}}](/tags/{{tag.path}})
{% endfor %}

[All Tags](/tags)

[Sign Out]({{ sign_out_url }})

----

Raw Data
--------
{{ json(load("tags/tag"))|indent(4, true) }}


