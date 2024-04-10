const username=document.querySelector('#username');
const feedback=document.querySelector('.invalid_feedback');
const emailFeedBackArea=document.querySelector('.emailFeedBackArea');
const email=document.querySelector('#email');
const submitBtn=document.querySelector('.submit-btn');

email.addEventListener("keyup", (e) => {
    const emailVal = e.target.value;
  
    email.classList.remove("is-invalid");
    emailFeedBackArea.style.display = "none";
  
    if (emailVal.length > 0) {
      fetch("/authentication/validate-email", {
        body: JSON.stringify({ email: emailVal }),
        method: "POST",
      })
        .then((res) => res.json())
        .then((data) => {
          console.log("data", data);
          if (data.email_error) {
            submitBtn.disabled = true;           
            email.classList.add('is-invalid');
            emailFeedBackArea.style.display = 'block';
            emailFeedBackArea.innerHTML=`<p>${data.email_error}</p>`;
          } else {
            submitBtn.removeAttribute("disabled");
          }
          
        });
    }
  });
  
username.addEventListener('keyup',(e)=>{
    const usernameVal = e.target.value;
    if(usernameVal.length>0){
     fetch("authentication/validate-username",{
         body: JSON.stringify({username: usernameVal}),
         method: 'POST',
        } ).then(res=>res.json()).then(data=>{
         console.log("data",data);
         username.classList.remove('is-invalid');
         feedback.style.display = 'none';
         if(data.username_error){
              submitBtn.disabled=true;
             username.classList.add('is-invalid');
             feedback.style.display = 'block';
             feedback.innerHTML=`<p>${data.username_error}</p>`;
         } else {
          submitBtn.removeAttribute("disabled");
        }
        });
    }
    
 });
