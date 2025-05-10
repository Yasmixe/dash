//----------------------------------------------------------sidebar--------------------------------------------------------------------

const toggleButton = document.getElementById('toggle-btn')
const sidebar = document.getElementById('sidebar')

function toggleSidebar(){
  sidebar.classList.toggle('close')
  toggleButton.classList.toggle('rotate')

  closeAllSubMenus()
}

function toggleSubMenu(button){

  if(!button.nextElementSibling.classList.contains('show')){
    closeAllSubMenus()
  }

  button.nextElementSibling.classList.toggle('show')
  button.classList.toggle('rotate')

  if(sidebar.classList.contains('close')){
    sidebar.classList.toggle('close')
    toggleButton.classList.toggle('rotate')
  }
}

function closeAllSubMenus(){
  Array.from(sidebar.getElementsByClassName('show')).forEach(ul => {
    ul.classList.remove('show')
    ul.previousElementSibling.classList.remove('rotate')
  })
}
//--------------------------------------------------------------------------------------------------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", function() {
  // Variables d'état
  let currentDate = new Date(2025, 4, 8); // Mai 2025 (les mois sont 0-indexés)
  
  // Éléments DOM
  const miniCalendarMonth = document.getElementById('mini-calendar-month');
  const miniCalendarBody = document.querySelector('#mini-calendar tbody');
  const mainCalendarMonth = document.getElementById('main-calendar-month');
  const daysRow = document.getElementById('days-row');
  
  // Boutons de navigation
  document.querySelector('.prev-month').addEventListener('click', () => {
    currentDate.setMonth(currentDate.getMonth() - 1);
    updateCalendars();
  });
  
  document.querySelector('.next-month').addEventListener('click', () => {
    currentDate.setMonth(currentDate.getMonth() + 1);
    updateCalendars();
  });
  
  document.querySelector('.prev-main').addEventListener('click', () => {
    currentDate.setDate(currentDate.getDate() - 7);
    updateCalendars();
  });
  
  document.querySelector('.next-main').addEventListener('click', () => {
    currentDate.setDate(currentDate.getDate() + 7);
    updateCalendars();
  });
// -------------------------------------Gestion du sélecteur de date---------------------------------------------------------------
  const dateInput = document.getElementById('custom-date-input');
  const goToDateBtn = document.getElementById('go-to-date-btn');
  
  goToDateBtn.addEventListener('click', function() {
    const selectedDate = new Date(dateInput.value);
    if (!isNaN(selectedDate.getTime())) {
      currentDate = selectedDate;
      updateCalendars();
    } else {
      alert('Veuillez sélectionner une date valide');
    }
  });
  
//----------------------------------------------------------------------------------------------------------------------------------------------
  dateInput.value = formatDateForInput(currentDate);
  
  function formatDateForInput(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
//-----------------------------------------Fonction pour mettre à jour les deux calendriers-------------------------------------------------------------------------------
  function updateCalendars() {
    updateMiniCalendar();
    updateMainCalendar();
  }

  // Mini calendrier (sidebar)
  function updateMiniCalendar() {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    miniCalendarMonth.textContent = `${new Date(year, month).toLocaleString('default', { month: 'long' })} ${year}`;
    
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDay = firstDay.getDay() === 0 ? 6 : firstDay.getDay() - 1; // Lundi=0
    
    let html = '';
    let day = 1;
    
    for (let i = 0; i < 6; i++) {
      html += '<tr>';
      
      for (let j = 0; j < 7; j++) {
        if (i === 0 && j < startingDay) {
          html += '<td></td>';
        } else if (day > daysInMonth) {
          html += '<td></td>';
        } else {
          const isToday = day === currentDate.getDate() && month === currentDate.getMonth() && year === currentDate.getFullYear();
          html += `<td${isToday ? ' class="today"' : ''}>${day}</td>`;
          day++;
        }
      }
      
      html += '</tr>';
      if (day > daysInMonth) break;
    }
    
    miniCalendarBody.innerHTML = html;
    
    // Ajouter les événements de clic sur les jours
    document.querySelectorAll('#mini-calendar td').forEach(td => {
      if (td.textContent) {
        td.addEventListener('click', () => {
          currentDate = new Date(year, month, parseInt(td.textContent));
          updateCalendars();
        });
      }
    });
  }

  // Calendrier principal (vue semaine)
  function updateMainCalendar() {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const date = currentDate.getDate();
    const dayOfWeek = currentDate.getDay();
    
    mainCalendarMonth.textContent = `${new Date(year, month).toLocaleString('default', { month: 'long' })}, ${year}`;
    
    const weekStart = new Date(year, month, date - dayOfWeek);
    
    // Générer les 7 jours de la semaine
    let html = '';
    for (let i = 0; i < 7; i++) {
      const dayDate = new Date(weekStart);
      dayDate.setDate(weekStart.getDate() + i);
      
      const isActive = dayDate.toDateString() === currentDate.toDateString();
      const dayName = dayDate.toLocaleString('default', { weekday: 'short' });
      const dayNum = dayDate.getDate();
      
      html += `<div class="day${isActive ? ' active' : ''}">${dayName} ${dayNum}</div>`;
    }
    
    daysRow.innerHTML = html;
    
    updateCalendarContent();
  }

  function updateCalendarContent() {
    const selectedDateStr = currentDate.toISOString().split('T')[0]; // format YYYY-MM-DD
// ------------------------------------------AJAX code ta3 bob----------------------------------------------------------------------------------------------------------
    const httpRequest = new XMLHttpRequest();
    httpRequest.open('GET', `/api/data1?date=${selectedDateStr}`);
    httpRequest.onreadystatechange = function () {
        if (httpRequest.readyState === 4) {
            if (httpRequest.status === 200) {
                const data = JSON.parse(httpRequest.responseText);
                update_Doughnut(data); // met à jour le graphique
            } else {
                console.error("Erreur de récupération des données pour", selectedDateStr);
            }
        }
    };
    httpRequest.send();
//----------------------------------------------------------------------------------------------------------------------------------------------
    const httpRequest2 = new XMLHttpRequest();
    httpRequest2.open('GET', `/api/data2?date=${selectedDateStr}`);
    httpRequest2.onreadystatechange = function () {
        if (httpRequest2.readyState === 4) {
            if (httpRequest2.status === 200) {
                const data = JSON.parse(httpRequest2.responseText);
                updateBarChart(data); // met à jour le graphique
            } else {
                console.error("Erreur de récupération des données pour", selectedDateStr);
            }
        }
    };
    httpRequest2.send();
//----------------------------------------------------------------------------------------------------------------------------------------------
    const httpRequest3 = new XMLHttpRequest();
    httpRequest3.open('GET', `/api/data3?date=${selectedDateStr}`);
    httpRequest3.onreadystatechange = function () {
        if (httpRequest3.readyState === 4) {
            if (httpRequest3.status === 200) {
                const data = JSON.parse(httpRequest3.responseText);
                console.log("Data brute reçue :", data);  // AJOUTE CECI
                update_LineAlertesParZone(data); // met à jour le graphique
            } else {
                console.error("Erreur de récupération des données pour", selectedDateStr);
            }
        }
    };
    httpRequest3.send();
//----------------------------------------------------------------------------------------------------------------------------------------------
      const httpRequest4 = new XMLHttpRequest();
      httpRequest4.open('GET', `/api/data4?date=${selectedDateStr}`);
      httpRequest4.onreadystatechange = function () {
          if (httpRequest4.readyState === 4) {
              if (httpRequest4.status === 200) {
                  const data = JSON.parse(httpRequest4.responseText);
                 
                  updateBarChart2(data); // met à jour le graphique
              } else {
                  console.error("Erreur de récupération des données pour", selectedDateStr);
              }
          }
      };
      httpRequest4.send();
//----------------------------------------------------------------------------------------------------------------------------------------------
      const httpRequest5 = new XMLHttpRequest();
      httpRequest5.open('GET', `/api/data5?date=${selectedDateStr}`);
      httpRequest5.onreadystatechange = function () {
      if (httpRequest5.readyState === 4) {
        if (httpRequest5.status === 200) {
            const data = JSON.parse(httpRequest5.responseText);

            if (data.length > 0) {
                const topZone = data[0];
                const text = `<p><strong>Zone avec le plus de chariots vides :</strong> ${topZone.zone} (${topZone.nombre_vide} chariots vides)</p>`;
                document.getElementById("top-zone-vide-info").innerHTML = text;
            } else {
                document.getElementById("top-zone-vide-info").innerHTML = "Aucune donnée disponible.";
            }
        } else {
            console.error("Erreur de récupération des données pour", selectedDateStr);
        }
    }
};
httpRequest5.send();
}
//----------------------------------------------------------------------------------------------------------------------------------------------
  updateCalendars();
});
//------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------my charts: chart.js---------------------------------------------------------------------------------------------------
let myBarChart;

function updateBarChart(data) {
    const zones = [...new Set(data.map(item => item.zone))];
    const classes = ["chariot vide", "chariot rempli"];

    const datasetByClasse = classes.map((classe, index) => {
        const color = classe === "chariot vide" ? "#5d5ded" : "#ffa707";

        return {
            label: classe,
            data: zones.map(zone => {
                const entry = data.find(d => d.zone === zone && d.classe === classe);
                return entry ? entry.nombre_de_chariots : 0;
            }),
            backgroundColor: color
        };
    });

    if (myBarChart) {
        myBarChart.destroy();
    }

    const ctx = document.getElementById('bar-chart');
    myBarChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: zones,
            datasets: datasetByClasse
        },
        options: {
            responsive: true,
           
            plugins: {
                title: {
                    display: true,
                    text: 'Nombre de chariots (vides/remplis) par zone'
                },
                legend: {
                    display: false,
                }
            },
            scales: {
                x: {
                    stacked: true
                },
                y: {
                    beginAtZero: true,
                    stacked: true
                }
            }
        }
    });
}

let myBarChart2
//------------------------------------------------------------------------------------------------------------------------------------------------------
function updateBarChart2(data) {
  const zones = [...new Set(data.map(item => item.zone))];
  const alertes = [...new Set(data.map(item => item.alerte))];

  const colors = {
      "pile presque vide": "#5d5ded",
      "chariot abandonné": "#ffa707",
      "chariot defectueux": "#ff4d4d"
  };

  const datasets = alertes.map(alerte => ({
      label: alerte,
      data: zones.map(zone => {
          const match = data.find(d => d.zone === zone && d.alerte === alerte);
          return match ? match.nombre : 0;
      }),
      backgroundColor: colors[alerte] || '#999999'
  }));

  if (myBarChart2) {
      myBarChart2.destroy();
  }

  const ctx = document.getElementById('bar-chart2');
  myBarChart2 = new Chart(ctx, {
      type: 'bar',
      data: {
          labels: zones,
          datasets: datasets
      },
      options: {
          responsive: true,
          plugins: {
              title: {
                  display: true,
                  text: 'Nombre d’alertes par type et par zone'
              },
              legend: {
                  display:false
              }
          },
          scales: {
              x: {
                  stacked: true
              },
              y: {
                  beginAtZero: true,
                  stacked: true
              }
          }
      }
  });
}

//------------------------------------------------------------------------------------------------------------------------------------------------------

function update_Doughnut(data_JSON) {
  var labels = data_JSON.map(item => item.zone);
  var values = data_JSON.map(item => item.nombre_de_chariots);

  var colors = [
    '#f84d54',   // Rouge
    '#5d5ded',   // Bleu
    'rgba(255, 206, 86, 0.7)',   // Jaune
    '#2fce4d',   // Vert menthe
    'rgba(153, 102, 255, 0.7)',  // Violet
    '#ffa707'    // Orange
  ];

  var ctx = document.getElementById("doughnut-chart");
  if (window.zoneChart) {
    window.zoneChart.destroy();
}

window.zoneChart = new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: labels,
    datasets: [{
      data: values,
      backgroundColor: colors.slice(0, labels.length),
      borderWidth: 1,
      borderRadius: 10
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: "Nombre de chariots par zone",
        font: {
          size: 16 
        }
      },
      legend: {
        display: false
      }
    }
  }
});
}
//------------------------------------------------------------------------------------------------------------------------------------------------------

function update_LineAlertesParZone(data_JSON) {
  console.log(data_JSON)
  const labels = data_JSON.map(item => item.zone);
  const values = data_JSON.map(item => Number(item.nombre_alertes));
  console.log("Labels:", labels);
  console.log("Values:", values);
  const ctx = document.getElementById("line-chart");
  if (window.alertesZoneChart) {
    window.alertesZoneChart.destroy();
  }

  window.alertesZoneChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Alertes par Zone',
        data: values,
        borderColor: '#f84d54',
        backgroundColor: 'rgba(248, 77, 84, 0.2)',
        tension: 0.3,
        pointBackgroundColor: '#f84d54',
        pointRadius: 5,
        fill: true
      }]
    },
    options: {
      animations: {
        tension: {
          duration: 1000,
          easing: 'linear',
          from: 1,
          to: 0,
          loop: true
        }
      },
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        title: {
          display: true,
          text: 'Nombre dalertes par zone'
        },
        legend: {
          display: true
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Nombre dalertes'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Zones'
          }
        }
      }
    }
  });


}
//------------------------------------------------------------------------------------------------------------------------------------------------------