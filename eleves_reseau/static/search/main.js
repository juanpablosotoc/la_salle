search_username_input = document.querySelector('#search_username');
search_user_button = document.querySelector('.search_user_button');
recent_searches_div = document.querySelector('.recent_searches_div');
searches_by_word_div = document.querySelector('.searches_by_word_div');
delete_all_searches_button = document.querySelector('.delete_all_searches_button');
body = document.querySelector('body');
recent_profiles_photos = document.getElementsByClassName('profile_photo'); // live collection of profile photos
no_previous_searches_p = document.querySelector('.no_previous_searches');

root_url = (function x() {
    url = '';
    n = 0;
    for (char of window.location.href) {
        if (char == '/') n++;
        url += char;
        if (n == 3) break;
    }
    return url;    
})();

search_username_input.value = '';

function delete_visual_recent_searches() {
    no_previous_searches_p.classList.remove('invisible');
    while (true) {
        first_recent_search = document.querySelector('.recent_search');
        if (first_recent_search == null) return;
        first_recent_search.remove();
    }
}

function set_image_dimensions(image) {
    if (image.height > image.width) {
        image.classList.remove('profile_photo_width_larger');
        image.classList.add('profile_photo_height_larger');
    } else {
        image.classList.remove('profile_photo_height_larger');
        image.classList.add('profile_photo_width_larger');
    }
};

for (recent_profile_photo of recent_profiles_photos) {
    set_image_dimensions(recent_profile_photo);
}

function create_profile_preview(data) {
    profile_preview_a = document.createElement('a');
    profile_preview_a.classList.add('search_profile_a');
    profile_preview_a.href = '/search/' + data['username'];
    profile_photo_div = document.createElement('div');
    profile_photo_div.classList.add('profile_photo_display');
    username_name_div = document.createElement('div');
    username_name_div.classList.add('username_name_div');
    profile_preview_a.appendChild(username_name_div);
    if (data['profile_photo'] == null){
        p_tag = document.createElement('p');
        p_tag.innerHTML = data['username'][0].toUpperCase();
        p_tag.classList.add('first_letter');
        profile_photo_div.appendChild(p_tag);
    } else {
        profile_photo = document.createElement('img');
        profile_photo.src = data['profile_photo'];
        profile_photo.classList.add('profile_photo');
        set_image_dimensions(profile_photo);
        profile_photo_div.appendChild(profile_photo);
    }
    profile_preview_a.appendChild(profile_photo_div);
    profile_preview_a.appendChild(username_name_div);
    username_p_tag = document.createElement('p');
    username_p_tag.classList.add('search_username');
    username_p_tag.innerHTML = data['username'];
    username_name_div.appendChild(username_p_tag);
    name_p_tag = document.createElement('p');
    name_p_tag.classList.add('search_name');
    name_p_tag.innerHTML = data['name'];
    username_name_div.appendChild(name_p_tag);
    return profile_preview_a;
}

function search_user(){
    search_word = {'search_word': search_username_input.value};
    fetch(root_url+ '/search', {
        method: 'POST', 
        mode: 'same-origin',
        credentials: 'include',
        headers: {
        'Content-Type': 'application/json'
        },
        redirect: 'follow',
        body: JSON.stringify(search_word) 
    }).then((response)=>{
        return response.json()
    }).then((data)=>{
        recent_searches_div.classList.add('invisible');
        searches_by_word_div.innerHTML = '';
        if (data.length === 0) {
            p_tag = document.createElement('p');
            p_tag.innerHTML = 'No users found';
            p_tag.classList.add('no_user_found');
            searches_by_word_div.appendChild(p_tag);
            return
        }
        for (user of data) {
            profile_preview_div = create_profile_preview(user);
            searches_by_word_div.appendChild(profile_preview_div);
        }
    }).catch((e)=>{
        console.log(e);
    });
}

function delete_user_recent_searches(delete_all_searches, delete_specific_searches, recent_search_div) {
    options = {'delete_all_searches': delete_all_searches, 'delete_specific_searches': delete_specific_searches}
    fetch(root_url+ '/search', {
        method: 'DELETE', 
        mode: 'same-origin',
        credentials: 'include',
        headers: {
        'Content-Type': 'application/json'
        },
        redirect: 'follow',
        body: JSON.stringify(options) 
    }).then((response)=>{
        return response.json()
    }).then((data)=>{
        if (data['error'] == false) {
            if (delete_all_searches) {
                delete_visual_recent_searches()
                return;
            };
            recent_search_div.remove();
            first_recent_search = document.querySelector('.recent_search');
            if (first_recent_search == null) delete_visual_recent_searches();
        }
        console.log(data)
    }).catch((e)=>{
        console.log(e);
    });
}

search_user_button.addEventListener('click', ()=>{
    search_user()
});

if (delete_all_searches_button != null) {
    delete_all_searches_button.addEventListener('click', ()=>{
        delete_user_recent_searches(true, null);
    })
    body.addEventListener('click', (event)=>{
        path = event.path;
        for (element of path) {
            if (element.nodeName == 'HTML') return;
            if (element.classList.contains('delete_specific_searches_button')) {
                recent_search_div = element.parentNode;
                 search_a = recent_search_div.children[0];
                recent_search_usermame = search_a.children[1].children[0].innerHTML;
                delete_user_recent_searches(false, recent_search_usermame, recent_search_div);
            }
        }
    })
}