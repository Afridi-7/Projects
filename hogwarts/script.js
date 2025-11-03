document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("hogwartsForm");
  const sortingHat = document.getElementById("sortingHat");
  const houseSelection = document.getElementById("houseSelection");
  const password = document.getElementById("password");
  const confirmPassword = document.getElementById("confirmPassword");

  // Disable/enable house selection
  sortingHat.addEventListener("change", () => {
    houseSelection.querySelectorAll("input").forEach(radio => {
      radio.disabled = sortingHat.checked;
    });
  });

  // Validate passwords match + age
  form.addEventListener("submit", (e) => {
    const dob = new Date(form.dob.value);
    const today = new Date();
    const age = today.getFullYear() - dob.getFullYear() -
      (today < new Date(today.getFullYear(), dob.getMonth(), dob.getDate()) ? 1 : 0);

    if (age < 11) {
      e.preventDefault();
      alert("You are too young for Hogwarts, the lower age limit is 11 years.");
      return;
    }

    if (password.value !== confirmPassword.value) {
      e.preventDefault();
      alert("Passwords do not match!");
    }
  });
});
