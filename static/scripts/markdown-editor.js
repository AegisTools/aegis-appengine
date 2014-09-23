
$(function() {
  $(".markdown-editor[data-markdown-preview]").each(function(index, element) {
    var e = $(element);
    e.on('change keyup paste', function() {
      $(e.attr('data-markdown-preview')).html(marked(e.context.value));
    }).trigger('change');
  });
});

