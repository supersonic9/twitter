// function to hide one div and display another when 'Edit Post' is selected
// define function with a section as input
function dismiss(deleteThis) {
    // hide the section that was passed into the function
    deleteThis.style.display = 'none';
    // show the div with id '#edit_post_form_div' which is a child of the parent of the function that was passed into the function
    deleteThis.parentNode.querySelector('.edit_post_form_div').style.display = 'block';
    // initiate animation associated with this div now being displayed
    deleteThis.parentNode.querySelector('.edit_post_form_div').style.animationPlayState = 'running';
}


// required function to get cookie details for csrftoken in AJAX fetch request
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


// wait for page to load
document.addEventListener('DOMContentLoaded', function() {

    // event delegation to listen for clicks throughout the DOM
    document.addEventListener('click', function(event){

        // handle initial click on 'Edit Post' button - display Edit form with existing post in <textarea>
        if (event.target.className == 'btn btn-primary edit') {

            // call the dismiss function with the parentNode of the button clicked
            dismiss(event.target.parentNode);
        }

        // handle saving and updating post via 'Save' button from edit form that pops up following initial 'Edit Post' click
        if (event.target.className == 'btn btn-primary edit_button') {

            // stop form from submitting by default (refreshes the page)
            event.preventDefault();

            // variable to hold textarea data in form
            updated_content = event.target.parentNode.querySelector('#edit_post_textarea').value;

            // variable from getCookie function for fetch request below
            const csrftoken = getCookie('csrftoken');

            // get id of the post to send back to Django as part of AJAX request below
            const post_id = JSON.parse(event.target.parentNode.querySelector('#post-id-data').textContent);

            // POST request via fetch to edit route - AJAX request so page doesn't refresh
            fetch("/edit", {
                method: 'POST',
                credentials: 'same-origin',
                headers:{
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({
                    "updated_content": updated_content,
                    "post_id": post_id
                })
            })
            .then(response => {
                return response.json();
            })
            .then(data => {
                // hide editing div (parent of the parent of the edit button (event.target))
                event.target.parentNode.parentNode.style.display = 'none';
                // update value of div displaying comment section with data.post_content
                event.target.parentNode.parentNode.parentNode.querySelector('#post_content').innerHTML = data.post_content;
                // re-display normal 'display_block' div
                event.target.parentNode.parentNode.parentNode.querySelector('.display_block').style.display = 'block';
                // run re-display animation
                event.target.parentNode.parentNode.parentNode.querySelector('.display_block').style.animationPlayState = 'running';
            })
        }

        // if user clicks on a heart to LIKE a post
        if (event.target.className == 'far fa-heart heart_like') {

            // get id of post being liked to pass to AJAX request
            const liked_post_id = JSON.parse(event.target.parentNode.parentNode.parentNode.querySelector('#post-id-data').textContent);

            // variable from getCookie function for fetch request below
            const csrftoken = getCookie('csrftoken');

            // POST request via fetch to like route
            fetch("like", {
                method: 'POST',
                credentials: 'same-origin',
                headers:{
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({
                    "liked_post_id": liked_post_id
                })
            })
            .then(response => {
                return response.json();
            })
            .then(data => {

                // variable that holds div to update
                sectionToUpdate = event.target.parentNode.parentNode;

                // HTML to update section  with as a single string, including updated like count from data
                updatedHTML = "<p><i class='fas fa-heart heart_unlike'></i>  "+data.likes+"</p>";

                // update section with HTML string
                sectionToUpdate.innerHTML = updatedHTML;

                // trigger CSS animation
                sectionToUpdate.querySelector('.fa-heart').style.animationPlayState = 'running';
            })
        }

        // if user clicks on a heart to UNLIKE a post
        if (event.target.className == 'fas fa-heart heart_unlike') {

            // get id of post being unliked to send via AJAX request
            const unliked_post_id = JSON.parse(event.target.parentNode.parentNode.parentNode.querySelector('#post-id-data').textContent);

            // variable from getCookie function for fetch request below
            const csrftoken = getCookie('csrftoken');

            // POST request via fetch to unlike
            fetch("unlike", {
                method: 'POST',
                credentials: 'same-origin',
                headers:{
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({
                    "unliked_post_id": unliked_post_id
                })
            })
            .then(response => {
                return response.json();
            })
            .then(data => {

                // variable that holds div to update
                sectionToUpdate = event.target.parentNode.parentNode;

                // HTML to update section  with as a single string, including updated like count from data
                updatedHTML = "<p><i class='far fa-heart heart_like'></i>  "+data.likes+"</p>";

                // update section with HTML string
                sectionToUpdate.innerHTML = updatedHTML;

                // trigger CSS animation
                sectionToUpdate.querySelector('.fa-heart').style.animationPlayState = 'running';
            })
        }
    })
});
