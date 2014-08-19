{% macro form(target, inputs, method="POST") %}

<script>
  function replaceFormAction() {
    var action = '{{ target }}';
    var regex = /{(.+?)}/g;
    var match = regex.exec(action)

    while (match != null) {
      action = action.substr(0, match.index) + 
          document['{{ target }}'][match[1]].value + 
          action.substr(match.index + match[0].length);
      match = regex.exec(action);
    }

    document['{{ target }}'].action=action;
  }
</script>

<form name="{{ target }}" method="post" onsubmit="try { return replaceFormAction(); } catch(err) { console.log(err); } return false;">
  <input type="hidden" name="_method_" value="{{ method }}">
  <table border="0">
    {% for input in inputs %}
      {% if input.type == "hidden" %}
        <input type="hidden" name="{{input.id}} value="{{input.value}}">
      {% else %}
        <tr>
          <td>{% if input.name %}{{input.name}}{% else %}{{input.id}}{% endif %}:</td>
          <td>
            {% if input.type == "radio" %}
              Radio buttons not supported yet
            {% else %}
              <input type="{% if input.type %}{{input.type}}{% else %}text{% endif %}" name="{{input.id}}" value="{{input.value}}">
            {% endif %}
          </td>
        </tr>
      {% endif %}
    {% endfor %}
    <tr>
      <td></td>
      <td><input type="Submit"></td>
    </tr>
  </table>
</form>

{% endmacro %}
