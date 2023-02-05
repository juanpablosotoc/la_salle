profile_view_photo = document.querySelector('.profile_view .personal_profile_photo');
profile_view_display = document.querySelector('.profile_view .personal_photo_display');
root_url_input = document.querySelector('#root_url');
personal_photo_display = document.querySelector('.personal_photo_display');
personal_profile_photo = document.querySelector('.personal_profile_photo');

photo_display_background_color = css_grey_var = getComputedStyle(document.documentElement).getPropertyValue('--grey');

url = '';
n = 0;
for (char of window.location.href) {
    if (char == '/') n++;
    url += char;
    if (n == 3) break;
}
root_url_input.value = url;




function set_profile_photo_display_bk_color(profile_photo_display) {
    profile_photo_display.style.backgroundColor = photo_display_background_color;
}
function set_profile_photo_classes(profile_photo_display, profile_photo) {
    if (profile_photo.height > profile_photo.width) {
        profile_photo.classList.remove('profile_photo_width_larger');
        profile_photo.classList.add('profile_photo_height_larger');
    } else {
        profile_photo.classList.remove('profile_photo_height_larger');
        profile_photo.classList.add('profile_photo_width_larger');
    }
    set_profile_photo_display_bk_color(profile_photo_display);
}

if (personal_profile_photo != undefined) {
    set_profile_photo_classes(personal_photo_display, personal_profile_photo);
} else {
    set_profile_photo_display_bk_color(personal_photo_display);
}


if (profile_view_photo != undefined) {
    set_profile_photo_classes(profile_view_display, profile_view_photo);
} else {
    set_profile_photo_display_bk_color(profile_view_display);
}
