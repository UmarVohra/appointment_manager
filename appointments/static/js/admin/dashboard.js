document.addEventListener("DOMContentLoaded", function () {
  //Edit Modal functionality for desktop
  const table = document.getElementById("appointmentsTable");
  const modal = document.getElementById("editModal");
  const addModal = document.getElementById("addModal");
  const addBtn = document.getElementById("addAppointmentBtn");
  const closeAddBtn = document.getElementById("closeAddBtn");
  const cancelAddBtn = document.getElementById("cancelAddBtn");
  const closeBtn = document.getElementById("closeBtn");
  const cancelBtn = document.getElementById("cancelBtn");

  table.addEventListener("click", function (e) {
    const row = e.target.closest("tr");
    if (!row || !row.dataset.id) return;
    //console.log("Selected ID:", row.dataset.id);
    //console.log("Hidden input:", document.getElementById("appointment_id"));
    document.getElementById("appointment_id").value = row.dataset.id;
    document.getElementById("id_fullname").value = row.dataset.fullname;
    document.getElementById("id_age").value = row.dataset.age;
    document.getElementById("id_enroll_no").value = row.dataset.enroll_no;
    document.getElementById("id_department").value = row.dataset.department;
    document.getElementById("id_phone").value = row.dataset.phone;
    document.getElementById("id_email").value = row.dataset.email;
    document.getElementById("id_slot").value = row.dataset.slot;
    document.getElementById("id_status").value = row.dataset.status;
    document.getElementById("id_remarks").value = row.dataset.remarks;

    // Populate date input without triggering timezone shifts
    const dateInput = document.getElementById("id_date");
    if (row.dataset.date && dateInput) {
      const raw = row.dataset.date;
      // If already in YYYY-MM-DD, assign directly (no timezone conversion)
      if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) {
        dateInput.value = raw;
      } else {
        // Try to parse and build a local YYYY-MM-DD value to avoid UTC offset issues
        try {
          const d = new Date(raw);
          if (!isNaN(d.getTime())) {
            const y = d.getFullYear();
            const m = String(d.getMonth() + 1).padStart(2, "0");
            const dd = String(d.getDate()).padStart(2, "0");
            dateInput.value = `${y}-${m}-${dd}`;
          } else {
            // fallback: use raw string
            dateInput.value = raw;
          }
        } catch (err) {
          dateInput.value = raw;
        }
      }
    }
    // Radio buttons
    document.querySelectorAll("input[name=reason]").forEach((radio) => {
      radio.checked = radio.value === row.dataset.reason;
    });
    modal.style.display = "block";
  });

  //Edit Modal functionality for desktop
  const cards = document.querySelectorAll(".appointment-card");
  cards.forEach((card) => {
    card.addEventListener("click", function (e) {
      const card = e.currentTarget;
      if (!card || !card.dataset.id) return;
      //console.log("Selected ID:", card.dataset.id);
      document.getElementById("appointment_id").value = card.dataset.id;
      document.getElementById("id_fullname").value = card.dataset.fullname;
      document.getElementById("id_age").value = card.dataset.age;
      document.getElementById("id_enroll_no").value = card.dataset.enroll_no;
      document.getElementById("id_department").value = card.dataset.department;
      document.getElementById("id_phone").value = card.dataset.phone;
      document.getElementById("id_email").value = card.dataset.email;
      document.getElementById("id_slot").value = card.dataset.slot;
      document.getElementById("id_status").value = card.dataset.status;
      document.getElementById("id_remarks").value = card.dataset.remarks;

      // Populate date input without triggering timezone shifts
      const dateInput = document.getElementById("id_date");
      if (card.dataset.date && dateInput) {
        const raw = card.dataset.date;
        // If already in YYYY-MM-DD, assign directly (no timezone conversion)
        if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) {
          dateInput.value = raw;
        } else {
          // Try to parse and build a local YYYY-MM-DD value to avoid UTC offset issues
          try {
            const d = new Date(raw);
            if (!isNaN(d.getTime())) {
              const y = d.getFullYear();
              const m = String(d.getMonth() + 1).padStart(2, "0");
              const dd = String(d.getDate()).padStart(2, "0");
              dateInput.value = `${y}-${m}-${dd}`;
            } else {
              // fallback: use raw string
              dateInput.value = raw;
            }
          } catch (err) {
            dateInput.value = raw;
          }
        }
      }
      // Radio buttons
      document.querySelectorAll("input[name=reason]").forEach((radio) => {
        radio.checked = radio.value === card.dataset.reason;
      });
      modal.style.display = "block";
    });
  });
  addBtn.addEventListener("click", openAddAppointmentModal);
  function openAddAppointmentModal() {
    addModal.style.display = "block";
  }

  // close Modal
  closeBtn.addEventListener("click", function () {
    modal.style.display = "none";
  });
  closeAddBtn.addEventListener("click", function () {
    addModal.style.display = "none";
  });
  cancelBtn.addEventListener("click", function () {
    modal.style.display = "none";
  });
  cancelAddBtn.addEventListener("click", function () {
    addModal.style.display = "none";
  });
  window.addEventListener("click", function (e) {
    if (e.target === modal) {
      modal.style.display = "none";
    } else if (e.target === addModal) {
      addModal.style.display = "none";
    }
  });

  // Delete confirmation
  const deleteBtn = document.getElementById("deleteBtn");
  if (deleteBtn) {
    deleteBtn.addEventListener("click", function (e) {
      const ok = confirm(
        "Are you sure you want to delete this appointment? This action cannot be undone."
      );
      if (!ok) {
        e.preventDefault();
        return false;
      }
    });
  }
});
