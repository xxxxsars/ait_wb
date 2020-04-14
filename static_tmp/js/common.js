/**
 * Created by Andy on 2020/1/10.
 */


//auto close alert  after 4 seconds.
$(".alert").delay(4000).slideUp(200, function () {
    $(this).alert('close');

});


$(function () {
    $('[data-toggle="tooltip"]').tooltip()
});

function ajax_download(url) {

                $.ajax({
                    "consumes": [],
                    "produces": [
                        "application/octet-stream"
                    ],
                    url: url,
                    xhrFields: {
                        // keep binary file
                        responseType: "blob"
                    }
                }).done((response, status, xhr) => {
                    // 這邊一定要用原生的 document.createElement
                    // jQuery 沒辦法真的模擬原生的 click event

                    const a = document.createElement("a");
                    // 給下載回來的資料產生一個網址
                    const url = URL.createObjectURL(response);
                    a.style = "display: none";

                    //get original filename
                    var f = (xhr.getResponseHeader('Content-Disposition').split("=")[1]);

                    var dt = new Date();
                    a.download = dt.toISOString() +".zip";
                    a.href = url;

                    a.click();
                    setTimeout(() => URL.revokeObjectURL(url), 5000)
                });

}

function ajax_loading(content) {
    $(document).ajaxStart(function () {
        $("body").hide();

        $(".load_panel").each(function () {
            $(this).remove()
        });

        $("html").append(
            '<div class="load_panel" style="width: 100%; height: 100%;">' +
            '  <div class="ui active inverted dimmer">' +
            '    <div class="ui text loader">'+ content +'</div>' +
            '  </div>' +
            '</div>');


    });

    $(document).ajaxComplete(function () {
        $(".load_panel").each(function () {
            $(this).remove()
        });

        // remove load.css
        $("#load_css").remove();
        $("body").show()
    });
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}