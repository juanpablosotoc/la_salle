profile_photos = document.getElementsByClassName('profile_photo_groups_a') // live collection of users_profile_photos

function insert_profile_photo_dimensions(image) {
    if (image.height > image.width) {
        image.classList.remove('profile_photo_width_larger');
        image.classList.add('profile_photo_height_larger');
    } else {
        image.classList.remove('profile_photo_height_larger');
        image.classList.add('profile_photo_width_larger');
    }
};

for (const profile_photo of Array(...profile_photos)) {
    insert_profile_photo_dimensions(profile_photo);
}