

profile_view_img = document.querySelector('.profile_view .profile_photo_display img');

if (profile_view_img != null) {
    insert_profile_photo_dimensions(profile_view_img);
}

function insert_profile_photo_dimensions(image) {
    if (image.height > image.width) {
        image.classList.remove('profile_photo_width_larger');
        image.classList.add('profile_photo_height_larger');
    } else {
        image.classList.remove('profile_photo_height_larger');
        image.classList.add('profile_photo_width_larger');
    }
};
