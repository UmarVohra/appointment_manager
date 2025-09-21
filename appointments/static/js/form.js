// Mobile Navigation Toggle
document.addEventListener("DOMContentLoaded", function () {
  const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
  const navDesktop = document.querySelector('.nav-desktop');
  
  // Create mobile menu if it doesn't exist
  let mobileMenu = document.querySelector('.nav-mobile');
  if (!mobileMenu) {
    mobileMenu = document.createElement('nav');
    mobileMenu.className = 'nav-mobile';
    mobileMenu.innerHTML = `
      <a href="#" class="nav-link">Home</a>
      <a href="#" class="nav-link active">Book Appointment</a>
    `;
    navDesktop.parentNode.insertBefore(mobileMenu, navDesktop.nextSibling);
  }

  // Toggle mobile menu
  if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', function() {
      mobileMenu.classList.toggle('show');
      const icon = this.querySelector('i');
      
      if (mobileMenu.classList.contains('show')) {
        icon.className = 'fas fa-times';
      } else {
        icon.className = 'fas fa-bars';
      }
    });
  }

  // Close mobile menu when clicking outside
  document.addEventListener('click', function(e) {
    if (!mobileMenuBtn.contains(e.target) && !mobileMenu.contains(e.target)) {
      mobileMenu.classList.remove('show');
      const icon = mobileMenuBtn.querySelector('i');
      if (icon) {
        icon.className = 'fas fa-bars';
      }
    }
  });
  
  //Collecting data of all selected slots
  const bookedSlots = JSON.parse(document.getElementById('booked-data').textContent);

  //Custom date picker functionality
  const today = new Date().toISOString().split('T')[0];
  const dateInput = document.getElementById('id_date');
  const slotSelect = document.getElementById("id_slot");
  dateInput.setAttribute('min', today);
  //console.log(today)//2025-09-17

  //Disabled Slots if the time has passed
  function to24hrs(hour){
    if (hour === 12) return 12;
    if (hour < 8) return hour + 12;
    return hour;
  }

  function disablePastSlots(){
    //console.log(document.getElementById('id_date').value)//2025-09-18
    const now = new Date();
    const selectedDate = dateInput.value;
    const currentHour = now.getHours();
    const currentMinutes = now.getMinutes();
    
    slotSelect.querySelectorAll('option').forEach(opt => opt.disabled = false);

    // disable past slots for today
    if (selectedDate === today) {
      slotSelect.querySelectorAll("option").forEach(option => {
        if (!option.value) return;
        const endTime = option.value.split("-")[1];
        let [endHour, endMinute] = endTime.split(":").map(Number);
        endHour = to24hrs(endHour);
        if (currentHour > endHour || (currentHour === endHour && currentMinutes >= endMinute)) {
          option.disabled = true;
        }
      });

    }
    // --- Disable booked slots for the selected date ---
    bookedSlots.forEach(([date, slot]) => {
      if (date === selectedDate) {
        const opt = slotSelect.querySelector(`option[value="${slot}"]`);
        if (opt) opt.disabled = true;
      }
    });

    slotSelect.value = "";
  }
  disablePastSlots();
  setInterval(disablePastSlots, 60000)
  dateInput.addEventListener('change', ()=> disablePastSlots())

  // Improve mobile date input UX: preserve placeholder and open native date picker on first pointer
  const datePlaceholders = document.querySelectorAll('input[data-behavior="show-date"]');
  datePlaceholders.forEach((input) => {
    // Ensure we only convert once
    let converted = false;

    const onPointerDown = (e) => {
      // On some mobile browsers, changing type on focus prevents immediate picker open.
      // Switch type on pointerdown and then focus+click to trigger native picker once.
      if (converted) return;
      converted = true;
      input.type = 'date';
      // Give browser a tick to apply the type change, then focus and click
      setTimeout(() => {
        try {
          input.focus();
          input.click();
        } catch (err) {
          // ignore; best-effort
        }
      }, 0);
      // Remove this handler after conversion to avoid repeated work
      input.removeEventListener('pointerdown', onPointerDown);
    };

    input.addEventListener('pointerdown', onPointerDown, {passive: true});
    // If user focuses via keyboard, also convert
    input.addEventListener('focus', () => {
      if (!converted) {
        converted = true;
        input.type = 'date';
      }
    });
  });

  // Modal functionality
  window.showModal = function() {
    const modal = document.getElementById('success-modal');
    if (modal) {
      modal.classList.add('show');
    }
  };

  window.closeModal = function() {
    const modal = document.getElementById('success-modal');
    if (modal) {
      modal.classList.remove('show');
    }
  };

  // Close modal when clicking outside
  const modal = document.getElementById('success-modal');
  if (modal) {
    modal.addEventListener('click', function(e) {
      if (e.target === modal) {
        closeModal();
      }
    });
  }
});