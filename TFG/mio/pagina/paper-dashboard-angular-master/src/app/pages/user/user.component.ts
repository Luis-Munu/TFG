import { Component, OnInit } from '@angular/core';
import { ToastrService } from "ngx-toastr";

@Component({
  selector: 'user-cmp',
  moduleId: module.id,
  templateUrl: 'user.component.html'
})
export class UserComponent implements OnInit {
  ngOnInit() {
    document
      .getElementById("addCustomBank")
      .addEventListener("click", function () {
        const customBankFields = document.getElementById("customBankFields") as HTMLElement;
        if (customBankFields.style.display === "none") {
          customBankFields.style.display = "block";
        } else {
          customBankFields.style.display = "none";
        }
      });
    }
    constructor(private toastr: ToastrService) {}
    showNotification(from, align) {
        const color = Math.floor(Math.random() * 5 + 1);
        this.toastr.success(
            '<span data-notify="icon" class="nc-icon nc-bell-55"></span><span data-notify="message">Información actualizada.</span>',
            "",
            {
              timeOut: 4000,
              closeButton: true,
              enableHtml: true,
              toastClass: "alert alert-success alert-with-icon",
              positionClass: "toast-" + from + "-" + align
            }
          );
        }
}

  
