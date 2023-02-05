nav_profile_photo = document.querySelector('nav .profile_photo_display img');

function insert_profile_photo_dimensions(image) {
    if (image.height > image.width) {
        image.classList.remove('profile_photo_width_larger');
        image.classList.add('profile_photo_height_larger');
    } else {
        image.classList.remove('profile_photo_height_larger');
        image.classList.add('profile_photo_width_larger');
    }
};

if (nav_profile_photo != null) {
    insert_profile_photo_dimensions(nav_profile_photo);
}
