function validateUsernameForm() {
  const input = document.querySelector("#username_input");
  if (input.value.length < 3) {
    alert("Error: Please enter a minimum of 3 characters");
    return false;
  }
  return true;
}

function validateIdForm() {
  const input = document.querySelector("#channel_id_input");
  if (input.value.length !== 24) {
    alert(`Error: ID length invalid. Your input has ${input.value.length} characters. YouTube Channel IDs are exactly 24 characters.`);
    return false;
  }
  return true;
}

function submitUsernameForm() {
  const form = document.querySelector("#usernameSelected form");
  const input = document.querySelector("#username_input");
  form.action = "/";
  form.method = "post";
  input.value = input.value;
  form.submit();
}

function submitIdForm() {
  const form = document.querySelector("#idFormSelected form");
  const input = document.querySelector("#channel_id_input");  
  form.action = "/";
  form.method = "post";
  input.value = input.value;
  form.submit();
}