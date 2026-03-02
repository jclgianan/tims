/* IMTS Login Logic 
    Simplified version: Handled only Success and Incorrect Credentials
*/

// 1. Handle Form Submission UI
document.getElementById('loginForm').onsubmit = function () {
  const btn = document.getElementById('loginBtn');
  const txt = document.getElementById('btnText');

  btn.disabled = true;
  txt.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Verifying...';
};

// 2. Handle Status Alerts
(function () {
  const errorStatus = document.body.getAttribute('data-error');

  // SUCCESS: Redirect to home
  if (errorStatus === 'no') {
    window.location.href = '/dashboard/';
  }
  // ERROR: Show SweetAlert for incorrect credentials
  else if (errorStatus === 'yes') {
    // Check if swal actually exists before calling it
    if (typeof swal !== 'undefined') {
      swal({
        title: 'Access Denied',
        text: 'Incorrect Email or Password.',
        icon: 'error',
        buttons: {
          confirm: {
            text: 'Try Again',
            className: 'btn btn-primary',
          },
        },
      });
    } else {
      // Fallback if the plugin didn't load
      alert('Access Denied: Incorrect Email or Password.');
    }
  }
})();
