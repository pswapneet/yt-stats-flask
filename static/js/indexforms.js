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