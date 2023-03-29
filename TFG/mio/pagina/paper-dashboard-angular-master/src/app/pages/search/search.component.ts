import { Component, OnInit } from '@angular/core';

declare interface SearchData {
    headerRow: string[];
    dataRows: string[][];
}

@Component({
    selector: 'search-cmp',
    moduleId: module.id,
    templateUrl: 'search.component.html'
})

export class SearchComponent implements OnInit{
    public searchData1: SearchData;
    public searchData2: SearchData;
    ngOnInit(){
        interface ProvinceData {
            [key: string]: string[];
          }
      
          const provinces: ProvinceData = {
                  andalucia: [
                    "Almería",
                    "Cádiz",
                    "Córdoba",
                    "Granada",
                    "Huelva",
                    "Jaén",
                    "Málaga",
                    "Sevilla",
                  ],
                  aragon: ["Huesca", "Teruel", "Zaragoza"],
                  asturias: ["Asturias"],
                  baleares: ["Baleares"],
                  canarias: ["Palmas", "Santa Cruz de Tenerife"],
                  cantabria: ["Cantabria"],
                  castilla_la_mancha: [
                    "Albacete",
                    "Ciudad Real",
                    "Cuenca",
                    "Guadalajara",
                    "Toledo",
                  ],
                  castilla_y_leon: [
                    "Ávila",
                    "Burgos",
                    "León",
                    "Palencia",
                    "Salamanca",
                    "Segovia",
                    "Soria",
                    "Valladolid",
                    "Zamora",
                  ],
                  cataluna: ["Barcelona", "Girona", "Lleida", "Tarragona"],
                  ceuta: ["Ceuta"],
                  comunidad_valenciana: ["Alicante", "Castellón", "Valencia"],
                  extremadura: ["Badajoz", "Cáceres"],
                  galicia: ["A Coruña", "Lugo", "Ourense", "Pontevedra"],
                  madrid: ["Madrid"],
                  melilla: ["Melilla"],
                  murcia: ["Murcia"],
                  navarra: ["Navarra"],
                  pais_vasco: ["Álava", "Guipúzcoa", "Vizcaya"],
                  rioja: ["La Rioja"],
              };
      
          const community = document.getElementById("community") as HTMLElement;
          const provinceSelect = document.getElementById("province") as HTMLSelectElement;
              
          function updateProvinceList(communityValue: string) {
              provinceSelect.innerHTML = '<option value="">Seleccione una provincia</option>';
              console.log(provinces[communityValue]);
              if (communityValue && provinces[communityValue]) {
                  provinces[communityValue].forEach((province) => {
                  const option = document.createElement("option");
                  option.value = province.toLowerCase();
                  option.textContent = province;
                  provinceSelect.appendChild(option);
                  });
              }
          }
      
          community.addEventListener("change", function () {
              updateProvinceList((community as HTMLSelectElement).value);
            });
    }
        // Send request to get data from server at port 
        /*this.searchData1 = {
            headerRow: [ 'ID', 'Name', 'Country', 'City', 'Salary'],
            dataRows: [
                ['1', 'Dakota Rice', 'Niger', 'Oud-Turnhout', '$36,738'],
                ['2', 'Minerva Hooper', 'Curaçao', 'Sinaai-Waas', '$23,789'],
                ['3', 'Sage Rodriguez', 'Netherlands', 'Baileux', '$56,142'],
                ['4', 'Philip Chaney', 'Korea, South', 'Overland Park', '$38,735'],
                ['5', 'Doris Greene', 'Malawi', 'Feldkirchen in Kärnten', '$63,542'],
                ['6', 'Mason Porter', 'Chile', 'Gloucester', '$78,615']
            ]
        };
        this.searchData2 = {
            headerRow: [ 'ID', 'Name',  'Salary', 'Country', 'City' ],
            dataRows: [
                ['1', 'Dakota Rice','$36,738', 'Niger', 'Oud-Turnhout' ],
                ['2', 'Minerva Hooper', '$23,789', 'Curaçao', 'Sinaai-Waas'],
                ['3', 'Sage Rodriguez', '$56,142', 'Netherlands', 'Baileux' ],
                ['4', 'Philip Chaney', '$38,735', 'Korea, South', 'Overland Park' ],
                ['5', 'Doris Greene', '$63,542', 'Malawi', 'Feldkirchen in Kärnten', ],
                ['6', 'Mason Porter', '$78,615', 'Chile', 'Gloucester' ]
            ]
        };*/
}

