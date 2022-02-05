document.addEventListener('DOMContentLoaded',() =>{
  
    // Use buttons to toggle between views  
    document.querySelector('#menu-all').addEventListener('click', () => view_postlist('all',0));
    document.querySelector('#menu-profile').addEventListener('click', () => view_postlist('by_user',0));
    document.querySelector('#menu-following').addEventListener('click', () => view_postlist('by_followed',0));
    
    document.querySelector('#menu-newPost').addEventListener('click', view_newpost);

    view_postlist('all',0)
});

// VIEW: new post (vnp)
function view_newpost() {
    // Show and hide views
    document.querySelector('#view-NewPost').style.display = 'block';
    document.querySelector('#view-PostsList').style.display = 'none';

    // Clear out fields
    document.querySelector('#vnpTxt_PostText').value = ''; 
    
    // Clean button div
    document.querySelector('#vnpDiv_Save').innerHTML=""
    document.querySelector('#vnpDiv_Save').innerHTML=`<input id="vnpBtn_Save" class="btn btn-primary" value = "Post" type="button" />`

    //Set up save button as a save NEW post
    document.querySelector('#vnpBtn_Save').addEventListener('click', () => save_post(true,0,0));
};

// VIEW: edit post (vep)
function view_editpost(post_id, text,page) {
    // Show and hide views
    document.querySelector('#view-NewPost').style.display = 'block';
    document.querySelector('#view-PostsList').style.display = 'none';

    // Populate fields
    document.querySelector('#vnpTxt_PostText').value = text;   

    // Clean button div
    document.querySelector('#vnpDiv_Save').innerHTML=""
    document.querySelector('#vnpDiv_Save').innerHTML=`<input id="vnpBtn_Save" class="btn btn-primary" value = "Post" type="button" />`

    //Set up save button as a save EDITED EXISTING post    
    document.querySelector('#vnpBtn_Save').addEventListener('click', () => save_post(false,post_id,page));

};

// Function save post
function save_post(newPost,post_id,page) {
    // If it's a new post: newPost==true and post_id doesn't matter
    // If it's a edited post: newPost==false and post_id is de post's id
    if (newPost){
        // API route to save a new post
        console.log('---------> Fetching to save new post')
        fetch('/newpost', {
            method: 'POST',
            body: JSON.stringify({
              text: document.querySelector('#vnpTxt_PostText').value,
            })
        })
        .then(response => response.json())
        .then(result => {
            // Print result
            console.log(result);
            if(result.error){
                alert(result.error)
            }; 
            view_postlist('all',page);
        });
        
    }else{
        // API route to save an edited post
        fetch('/editpost/'+String(post_id), {
            method: 'POST',
            body: JSON.stringify({
              text: document.querySelector('#vnpTxt_PostText').value,
            })
        })
        .then(response => response.json())
        .then(result => {
            // Print result
            console.log(result);
            if(result.error){
                alert(result.error)
            }; 
            view_postlist('by_user',page);
        });        
    };    
};

// Function like/Unlike
function like_post(like,post_id,listType,page) {
    //API route to Like or unlike post
    let url = '/like/' + String(post_id)
    fetch(url, {
        method: 'PUT',
        body: JSON.stringify({
            like: like
        })
    })
    .then(response => view_postlist(listType,page)) ;
};

// Get all users to follow or unfollow
function follow_user(page) {
    // Users listed in a Dropdown list
    userDropdown = document.querySelector('#vplSel_users');
    action = userDropdown.options[userDropdown.selectedIndex].dataset.action;
    
    //API route to Follow or unfollow users
    let url = '/follow' 
    fetch(url, {
       method: 'PUT',
       body: JSON.stringify({
           action: action,
           user: userDropdown.value
       })
    })
    .then(response => view_postlist('by_user',page)) ;
};

// VIEW: posts list (vpl)
function view_postlist(listType,page) {

    // Show and hide views
    document.querySelector('#view-NewPost').style.display = 'none';
    document.querySelector('#view-PostsList').style.display = 'block';
  
    // Clean View
    document.querySelector('#view-PostsList').innerHTML=""
 
    // Get current user
    currentUser = document.getElementById("currentUser").value
    
    
    // Show the postlist name
    let title = ''
    if(listType === 'all'){
        title = 'All Posts'
    }else if(listType === 'by_user'){
        title = 'Profile Page'
    }else{
        title = 'Following Posts'
    }
    document.querySelector('#view-PostsList').innerHTML = `<h3> ${title}</h3>`; 
    
    // Only for profile view - Follow counts and follow/unfollow actions
    if (listType === 'by_user'){
        let follower = 0;
        let followed = 0;
        var url =''

        // API route to get Follow counters
        url = '/followcounts'
        console.log(url)
    
        fetch(url)
        .then(response => response.json())
        .then(followcounts => {
            follower = followcounts.follower;
            followed = followcounts.followed;

            // main div for follow counts
            let vplDiv_follow = document.createElement('div');
            vplDiv_follow.className = 'vplDiv_follow';   

            // Containers for data
            let vplCon_follow = document.createElement('div');
            vplCon_follow.className = 'vplCon_follow'; 
            
            //Put data inside containers
            vplCon_follow.innerHTML = `Following ${followed} users and followed by ${follower}. `;
            
            //Nesting boxes
            vplDiv_follow.append(vplCon_follow);
            document.querySelector('#view-PostsList').append(vplDiv_follow); //DOM

            // API ROUTE to get User list (excluding current user and adding flag indicator of follow state) 
            url = '/followlist';
            console.log(url);

             fetch(url)
            .then(response => response.json())
            .then(follow_list => {

                // main div for user selector
                let vplDiv_users = document.createElement('div');
                vplDiv_users.className = 'vplDiv_users';
                let vplDiv_selectLabel = document.createElement('div');
                vplDiv_selectLabel.className = 'vplDiv_selectLabel';
                let vplDiv_selectUser = document.createElement('div');
                vplDiv_selectUser.className = 'vplDiv_selectUser';
                let vplDiv_btnFollow = document.createElement('div');
                vplDiv_btnFollow.className = 'vplDiv_btnFollow';

                // Select users by drop down list
                vplDiv_selectLabel.innerHTML='List of users: '
                let vplSel_users = document.createElement('select');
                vplSel_users.className = 'vplSel_users';
                vplSel_users.id = 'vplSel_users';

                vplDiv_users.append(vplDiv_selectLabel);
                vplDiv_selectUser.append(vplSel_users);
                vplDiv_users.append(vplDiv_selectUser);
                
                // Button
                let vplbtn_follow = document.createElement('button');
                vplbtn_follow.className = 'btn btn-primary'; //Boostrap
                vplbtn_follow.innerHTML = 'Follow / Unfollow'
                vplDiv_btnFollow.append(vplbtn_follow);
                vplDiv_users.append(vplDiv_btnFollow);

                // click event handler for vplbtn_follow
                vplbtn_follow.onclick = () => follow_user(page);

                follow_list.forEach(user => {
                    var option = document.createElement("option");
                    option.value = user.id;
                    option.text = user.user + " " +user.follow;
                    if(user.follow===''){
                        option.dataset.action = 'follow'
                    }else{
                        option.dataset.action = 'unfollow'
                    }
                    vplSel_users.appendChild(option);          
                });
                // DOM
                document.querySelector('#view-PostsList').append(vplDiv_users);
                post_list(listType,page)
            });            
        });
    }else{
        post_list(listType,page)
    }
};

function post_list(listType,page){
    // API route for get list of posts
    url = '/posts/' + listType
    console.log(url)
    fetch(url)
    .then(response => response.json())
    .then(posts => {
        // How many post?
        postCount = posts.length;

        // Pagination control variables
        let firstPage = false;
        let lastPage = false;        
        if(page === 0){
            firstPage = true; 
        }

        // does page make sense?
        if( page*10 >= postCount ){ //not sense
            page= Math.trunc(postCount/10.1)
        }
        // Fix last post in case of last page
        if(postCount <= 10*(page+1)){ // Last page!!
            lastPost = postCount;
            lastPage = true; 
        }else{
            lastPost = 10*(page+1);
        }
        for(let i=10*page  ; i < lastPost  ; i++ ){
            let post = posts[i];
        
            //posts.forEach(post => {
            
        // main div for entire posts list structure
            let vplDiv_post = document.createElement('div');
            vplDiv_post.className = "vplDiv_post";
    
            // Containers for data
            let vplCon_poster = document.createElement('div');
            vplCon_poster.className = 'vplCon_poster'; 

            let vplCon_text = document.createElement('div');
            vplCon_text.className = "vplCon_text";

            let vplCon_firstTimeStamp = document.createElement('div');
            vplCon_firstTimeStamp.className = 'vplCon_firstTimeStamp'; 

            let vplCon_likeCount = document.createElement('div');
            vplCon_likeCount.className = 'vplCon_likeCount';  

            let vplCon_likeBtn = document.createElement('div');
            vplCon_likeBtn.className = 'vplCon_likeBtn'; 
            
            let vplCon_editBtn = document.createElement('div');
            vplCon_editBtn.className = 'vplCon_editBtn'; 
            

            //Put data inside containers
            vplCon_poster.innerHTML = post.user;
            vplCon_text.innerHTML = post.text;
            vplCon_firstTimeStamp.innerHTML = post.firstTimeStamp;
            vplCon_likeCount.innerHTML = 'Likes: ' + String(post.likeCount);

            //Like button (Only for non own post)
            if(currentUser!=post.userId){
                let vplBtn_likeBtn = document.createElement('button');
                vplBtn_likeBtn.className = 'btn btn-primary'; //Boostrap
                if (post.like){
                    vplBtn_likeBtn.innerHTML = "Unlike"
                    // click event handler for vplBtn_likeBtn
                    vplBtn_likeBtn.onclick = () => like_post(false,post.id,listType,page);  
                }else{
                    vplBtn_likeBtn.innerHTML = "Like"
                    // click event handler for vplBtn_likeBtn
                    vplBtn_likeBtn.onclick = () => like_post(true,post.id,listType,page); 
                }
                vplCon_likeBtn.append(vplBtn_likeBtn);
            }
 
            // Edit button -  only for profile view            
            if (listType === 'by_user'){
                let vplBtn_editBtn = document.createElement('button');
                vplBtn_editBtn.className = 'btn btn-primary'; //Boostrap
                vplBtn_editBtn.innerHTML = "Edit"
                // click event handler for vplBtn_editBtn
                vplBtn_editBtn.onclick = () => view_editpost(post.id, post.text,page);  
                vplCon_editBtn.append(vplBtn_editBtn);
            };            
            
            //Nesting boxes
            vplDiv_post.append(vplCon_poster);
            vplDiv_post.append(vplCon_text);
            vplDiv_post.append(vplCon_firstTimeStamp);     
            vplDiv_post.append(vplCon_likeCount);
            vplDiv_post.append(vplCon_likeBtn);
            if (listType === 'by_user'){ vplDiv_post.append(vplCon_editBtn)};
    
            // Update DOM
            document.querySelector('#view-PostsList').append(vplDiv_post);
        };

        // Pagination
        let vplDiv_pagination = document.createElement('div');
        vplDiv_pagination.className = 'vplDiv_pagination';
        let vplNav_pagination = document.createElement('nav');
        let vplNav_paginationUl = document.createElement('ul');
        vplNav_paginationUl.className = "pagination";


        if (!firstPage ){            
            let vplNav_paginationLiPrev = document.createElement('li');  
            vplNav_paginationLiPrev.className = "page-item"
            
            let vplNav_paginationAPrev = document.createElement('a');
            vplNav_paginationAPrev.innerHTML='Previous'
            vplNav_paginationAPrev.className = "page-link"  
            vplNav_paginationAPrev.href = "#";
            vplNav_paginationAPrev.onclick = () => view_postlist(listType,page-1); 
            

            // nesting
            vplNav_paginationLiPrev.append(vplNav_paginationAPrev);
            vplNav_paginationUl.append(vplNav_paginationLiPrev);
  
        }

        if (!lastPage ){            
            let vplNav_paginationLiNext = document.createElement('li');
            vplNav_paginationLiNext.className = "page-item"
            let vplNav_paginationANext = document.createElement('a');
            vplNav_paginationANext.innerHTML='Next'  
            vplNav_paginationANext.className = "page-link"
            vplNav_paginationANext.href = "#";
            vplNav_paginationANext.onclick = () => view_postlist(listType,page+1); 
            // nesting
            vplNav_paginationLiNext.append(vplNav_paginationANext);
            vplNav_paginationUl.append(vplNav_paginationLiNext);
        }
        vplNav_pagination.append(vplNav_paginationUl);
        vplDiv_pagination.append(vplNav_pagination)
        // Update DOM
        document.querySelector('#view-PostsList').append(vplDiv_pagination);
    });
};