update_profile_photo_div = document.querySelector('.profile_photo_div');
photo_base_64 = document.querySelector('input[type="file"]');
profile_photo_base64_hidden_inp = document.querySelector('#profile_photo_base64');
personal_profile_photo = document.querySelector('.profile_photo_edit');
body = document.querySelector('body');
profile_photo_letter_p = document.querySelector('form .profile_photo_div .profile_photo_letter');

update_profile_photo_div.addEventListener('click', ()=>{
    photo_base_64.click();
});


function getBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = error => reject(error);
    });
};

photo_base_64.addEventListener('change', ()=>{
    if (photo_base_64.value == '') return;
    getBase64(photo_base_64.files[0]).then((base64) =>{
        profile_photo_base64_hidden_inp.value = base64;
        if (personal_profile_photo == null) {
            personal_profile_photo = document.createElement('img');
            personal_profile_photo.classList.add('profile_photo_edit');
            profile_photo_letter_p.remove()
            update_profile_photo_div.appendChild(personal_profile_photo);
        }
        personal_profile_photo.src = base64;
        set_image_dimensions(personal_profile_photo);
    }).catch((error)=>{
        // What should i do here?
        error_paragraph = document.createElement('p');
        error_paragraph.innerHTML = error;
        body.appendChild(error_paragraph);
})});

function set_image_dimensions(image) {
    if (image.height > image.width) {
        image.classList.remove('profile_photo_width_larger');
        image.classList.add('profile_photo_height_larger');
    } else {
        image.classList.remove('profile_photo_height_larger');
        image.classList.add('profile_photo_width_larger');
    }
};

if (personal_profile_photo != null) {
    set_image_dimensions(personal_profile_photo);
};