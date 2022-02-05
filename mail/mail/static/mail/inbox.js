  
document.addEventListener('DOMContentLoaded',() =>{
  
  // Use buttons to toggle between views  
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  // Other listeners
  document.querySelector('#form-submit').addEventListener('click', send_email);
  

  // By default, load the inbox
  load_mailbox('inbox');  
});


// Compose a new email function
function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}


// Compose a existing email (Reply) function
function reply_email(email) {

  // Show compose view and hide other views
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Pre-fill composition fields
  document.querySelector('#compose-recipients').value = email.sender;
  if(email.subject.slice(0,4)!='Re: '){
    document.querySelector('#compose-subject').value = 'Re: '+ email.subject;
  }else{
    document.querySelector('#compose-subject').value = email.subject;
  }
  document.querySelector('#compose-body').value = 'On '+ email.timestamp + ' ' + email.sender + ' wrote:';
}

// Send email function
function send_email() {
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: document.querySelector('#compose-recipients').value,
      subject: document.querySelector('#compose-subject').value,
      body: document.querySelector('#compose-body').value,
      read: false, 
      archived: false
    })
  })
  .then(response => response.json())
  .then(result => {
    // Print result
    console.log(result);
    if(result.error){
      alert(result.error)
    }
    load_mailbox('sent');
  });
}

// VIEW: Load mailbox (Vlm)
function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Clean View
  document.querySelector('#emails-view').innerHTML=""
  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3> ${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`; 

  const url = '/emails/' + mailbox
  console.log(url)
  fetch(url)
  .then(response => response.json())
  .then(emails => {
    // Print emails
    emails.forEach(email => {
      // main div for entire email structure
      let emailBox_div = document.createElement('div');
      emailBox_div.className = 'emailBox';

      if (email.read && (mailbox === 'inbox' || mailbox === 'archive')){
        emailBox_div.style.backgroundColor = 'lightgrey';
      }  
      // click event handler for emailBox_div
      emailBox_div.onclick = () => load_email(email.id,mailbox);   

      // boxes for: address and subject (to the left) and timestamp to the right
      let leftBox_div = document.createElement('div');
      leftBox_div.className = 'leftBox';   
      let rightBox_div = document.createElement('div');
      rightBox_div.className = 'rightBox';
      // Containers for data
      let addressCon_div = document.createElement('div');
      addressCon_div.className = 'addressCon';  
      let subjectCon_div = document.createElement('div');
      subjectCon_div.className = 'subjectCon';  
      let timestampCon_div = document.createElement('div');
      timestampCon_div.className = 'timestampCon';  

      //Put data inside containers
            
      if (mailbox === 'archive' || mailbox === 'inbox'){
        addressCon_div.innerHTML = email.sender;
      } else{
        addressCon_div.innerHTML = email.recipients[0] + '(+)';
      }
      subjectCon_div.innerHTML = email.subject;
      timestampCon_div.innerHTML = email.timestamp;
      
      //Nesting boxes
      leftBox_div.append(addressCon_div);
      leftBox_div.append(subjectCon_div);
      rightBox_div.append(timestampCon_div);

      emailBox_div.append(leftBox_div);
      emailBox_div.append(rightBox_div);

      //Update the DOM        
      document.querySelector('#emails-view').append(emailBox_div)
        
    });

    console.log(emails);
    // ... do something else with emails ...
  });
}
    
// VIEW: Individual email (Vle)
function load_email(mailId, mailbox) {
  // Show the mailview and hide other views
  document.querySelector('#email-view').style.display = 'block';
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  let url = '/emails/' + String(mailId)
  
  //Mark this email as read
  fetch(url, {
    method: 'PUT',
    body: JSON.stringify({
        read: true
    })
  })

  fetch(url)
  .then(response => response.json())
  .then(email => {

    // Archiving and unarchivig functions     
    let archiveVle_btn = document.createElement('button');
    if (mailbox === 'inbox'){
      archiveVle_btn.innerHTML = 'Archive'
      archiveVle_btn.onclick = () => archive_email(mailId,'a');   
    }else if(mailbox === 'archive'){
      archiveVle_btn.innerHTML = 'Unarchive'
      archiveVle_btn.onclick = () => archive_email(mailId,'u');   
    }else{
      archiveVle_btn.style.visibility = 'hidden';
    }

    // Reply function  
    let replyVle_btn = document.createElement('button');
    if (mailbox === 'inbox' || mailbox === 'archive'){
      replyVle_btn.innerHTML = 'Reply'
      replyVle_btn.onclick = () => reply_email(email);    
    }else{
      replyVle_btn.style.visibility = 'hidden';
    }

    // Box structure
    let mainVle_div = document.createElement('div');
    mainVle_div.className = 'mainVle';
    let buttonsVle_div = document.createElement('div');
    buttonsVle_div.className = 'buttonsVle';
    
    // Data containers
    let timestampVle_con = document.createElement('div');
    timestampVle_con.className = 'timestampVle';
    let senderVle_con = document.createElement('div');
    senderVle_con.className = 'senderVle';
    let recipientsVle_con = document.createElement('div');
    recipientsVle_con.className = 'recipientsVle';
    let subjetVle_con = document.createElement('div');
    subjetVle_con.className = 'subjetVle';
    let bodyVle_con = document.createElement('div');
    bodyVle_con.className = 'bodyVle_con';
    let archiveBtnVle_con = document.createElement('div');
    archiveBtnVle_con.className = 'BtnVle_con';
    let replyBtnVle_con = document.createElement('div');
    replyBtnVle_con.className = 'BtnVle_con';

    // Container populating
    timestampVle_con.innerHTML = email.timestamp;
    senderVle_con.innerHTML = 'From: ' + email.sender;
    recipientTxt = ''
    email.recipients.forEach(recipient => {
      recipientTxt = recipientTxt + recipient +', '
    })
    recipientTxt=recipientTxt.slice(0,(recipientTxt.length-2))
    subjetVle_con.innerHTML = 'Subject: ' + email.subject;
    recipientsVle_con.innerHTML = 'To: ' + recipientTxt;      
    bodyVle_con.innerHTML = email.body;
    archiveBtnVle_con.append(archiveVle_btn)
    replyBtnVle_con.append(replyVle_btn)

    // Nesting boxes
    mainVle_div.append(timestampVle_con);
    mainVle_div.append(senderVle_con);
    mainVle_div.append(subjetVle_con);
    mainVle_div.append(recipientsVle_con);  
    //Put buttons before body
    buttonsVle_div.append(archiveBtnVle_con);
    buttonsVle_div.append(replyBtnVle_con);
    mainVle_div.append(buttonsVle_div);  
    mainVle_div.append(bodyVle_con);

    // Update the DOM
    document.querySelector('#email-view').innerHTML="";
    document.querySelector('#email-view').append(mainVle_div);
    console.log(email);

    // ... do something else with email ...
  });
}

// Archive email function
function archive_email(mailId, action){
  //Mark this email as archived or unarchived
  let archived = false;
  if(action === 'a'){
    archived = true;
  }
  
  let url = '/emails/' + String(mailId)

  fetch(url, {
    method: 'PUT',
    body: JSON.stringify({
        archived: archived
    })
  })
  .then(response => load_mailbox('inbox'))  
}
