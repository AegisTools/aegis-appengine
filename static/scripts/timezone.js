var timezone_cookie = "timezoneoffset";

// if the timezone cookie not exists create one.
if (!$.cookie(timezone_cookie)) { 

    // create a new cookie 
    $.cookie(timezone_cookie, new Date().getTimezoneOffset());

    // re-load the page
    location.reload(); 
}

// if the current timezone and the one stored in cookie are different
// then store the new timezone in the cookie and refresh the page.
else {         

    var storedOffset = parseInt($.cookie(timezone_cookie));
    var currentOffset = new Date().getTimezoneOffset();

    // user may have changed the timezone
    if (storedOffset !== currentOffset) { 
        $.cookie(timezone_cookie, new Date().getTimezoneOffset());
        location.reload();
    }
}

