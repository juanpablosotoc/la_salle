profile_photo_input = document.querySelector('.profile_photo_input');
first_letter = document.querySelector('.first_letter');
profile_photo_display = document.querySelector('.profile_photo_display');
profile_photo = document.querySelector('.profile_photo');
body = document.querySelector('body');
profile_photo_base64_input = document.querySelector('#profile_photo_base64');


profile_photo_display.addEventListener('click', ()=>{
    profile_photo_input.click();
});

function getBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = error => reject(error);
    });
};

profile_photo_input.addEventListener('change', ()=>{
    if (profile_photo_input.value == '') return;
    getBase64(profile_photo_input.files[0]).then((base64) =>{
        profile_photo_base64_input.value = base64;
        css_grey_var = getComputedStyle(document.documentElement).getPropertyValue('--grey');
        profile_photo_display.style.backgroundColor = css_grey_var;
        first_letter.classList.add('invisible');
        profile_photo.src = base64;
        if (profile_photo.height > profile_photo.width) {
            profile_photo.classList.remove('profile_photo_width_larger');
            profile_photo.classList.add('profile_photo_height_larger');
        } else {
            profile_photo.classList.remove('profile_photo_height_larger');
            profile_photo.classList.add('profile_photo_width_larger');
        }
        profile_photo.classList.remove('invisible');
    }).catch((error)=>{
        // What should i do here?
        error_paragraph = document.createElement('p');
        error_paragraph.innerHTML = error;
        body.appendChild(error_paragraph);
})});
