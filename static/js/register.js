const usrnm= document.querySelector('#username-field');
const usernameSuccessOutput = document.querySelector(".usernameSuccessOutput");
const feedBackArea = document.querySelector(".invalid_feedback");
const submitBtn = document.querySelector(".btn");
const emailField = document.querySelector("#email-field");
const pwdField = document.querySelector("#passwd-field");
const emailFeedBackArea = document.querySelector(".emailFeedBackArea");
const showPasswdToggle=document.querySelector(".showPasswdToggle");


emailField.addEventListener("keyup", (e) => {
  const emailVal = e.target.value;

  emailField.classList.remove("is-invalid");
  emailFeedBackArea.style.display = "none";

  if (emailVal.length > 0) {
    fetch("/auth/validate-email", {
      body: JSON.stringify({ email: emailVal }),
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("data", data);
        if (data.email_error) {
          submitBtn.disabled = true;
          emailField.classList.add("is-invalid");
          emailFeedBackArea.style.display = "block";
          emailFeedBackArea.innerHTML = `<p>${data.email_error}</p>`;
        } else {
          submitBtn.removeAttribute("disabled");
        }
      });
  }
});


usrnm.addEventListener("keyup" , (e)=>{
    const usernameVal = e.target.value;
    usernameSuccessOutput.style.display = "block";
    usernameSuccessOutput.textContent = `Checking  ${usernameVal}`;
    usrnm.classList.remove("is-invalid");
    feedBackArea.style.display = "none";
    if (usernameVal.length > 0) {
      fetch("/auth/validate-username", {
        body: JSON.stringify({username: usernameVal}),
        method: "POST",
      })
      .then((res) => res.json()).then((data) => {
        usernameSuccessOutput.style.display = "none";
        
          if (data.username_error) {
            usrnm.classList.add("is-invalid");
            feedBackArea.style.display = "block";
            feedBackArea.innerHTML = `<p>${data.username_error}</p>`;
            submitBtn.disabled = true;
          } else {
            submitBtn.removeAttribute("disabled");
          }

          console.log(data)
        });
    }
})