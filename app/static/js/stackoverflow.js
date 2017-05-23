      function myFunction () {
        var title_val = $('#q_title').val();
        var body_val = $('#q_body').val();
      $.ajax({
       type: "POST",
       contentType: "application/json; charset=utf-8",
       url: "/projects/stackoverflow",
       dataType: "json",
       async: true,
       data: '{"title": "'+title_val+'", "body": "'+body_val+'"}',
       success: function (data) {
        console.log(data);

        $('#pred-type').text(data.pred);
        $('#pred-prob').text('Probability: '.concat(data.prob_str));

        },
        error: function (result) {
       }
      })
      }; 