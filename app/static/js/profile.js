document.addEventListener("DOMContentLoaded", () => {
    const profileForm = document.getElementById("profileForm");
    const passwordForm = document.getElementById("passwordForm");
    const alertBox = document.getElementById("profileAlert");
  
    function showAlert(type, message) {
      alertBox.innerHTML = `<div class="alert alert-${type}" role="alert">${message}</div>`;
    }
  
    profileForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(profileForm);
      const res = await fetch("/profile/update", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      showAlert(data.status === "success" ? "success" : "danger", data.message);
    });
  
    passwordForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(passwordForm);
      const res = await fetch("/profile/password", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      showAlert(data.status === "success" ? "success" : "danger", data.message);
      if (data.status === "success") passwordForm.reset();
    });
  });
  