body = document.querySelector('body');
personal_profile_photos = document.getElementsByClassName('personal_profile_photo');
arrow_src = document.querySelector('.arrow').src;
my_profile_photo = document.querySelector('.profile_view .personal_photo_display img');


function insert_profile_photo_dimensions(image) {
    if (image.height > image.width) {
        image.classList.remove('profile_photo_width_larger');
        image.classList.add('profile_photo_height_larger');
    } else {
        image.classList.remove('profile_photo_height_larger');
        image.classList.add('profile_photo_width_larger');
    }
};

function set_tweet_div_profile_dimensions() {
    for (photo of personal_profile_photos) {
        insert_profile_photo_dimensions(photo);
    }
};

set_tweet_div_profile_dimensions();
