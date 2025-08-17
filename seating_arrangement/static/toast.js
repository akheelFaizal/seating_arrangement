document.addEventListener("DOMContentLoaded", function () {
        var toastElList = [].slice.call(document.querySelectorAll(".toast"));
        var toastList = toastElList.map(function (toastEl) {
          var toast = new bootstrap.Toast(toastEl, { delay: 3000 }); // 3 seconds
          toast.show();
          return toast;
        });
      });