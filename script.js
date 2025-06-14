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
  let currentDate = new Date(2025, 5, 2); // Mai 2025 (les mois sont 0-indexés)
  
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
                update_BarChart(data); // met à jour le graphique
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
                console.log("pie pie:", data);  // AJOUTE CECI
                update_pie(data); // met à jour le graphique
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
                  update_Line(data); // met à jour le graphique
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
                  update_Line_deux(data); // met à jour le graphique
              } else {
                  console.error("Erreur de récupération des données pour", selectedDateStr);
              }
          }
      };
      httpRequest5.send();


      const httpRequest6 = new XMLHttpRequest();
      httpRequest6.open('GET', `/api/data6?date=${selectedDateStr}`);
      httpRequest6.onreadystatechange = function () {
          if (httpRequest6.readyState === 4) {
              if (httpRequest6.status === 200) {
                  const data = JSON.parse(httpRequest6.responseText);
                  updatebare(data); // met à jour le graphique
              } else {
                  console.error("Erreur de récupération des données pour", selectedDateStr);
              }
          }
      };
      httpRequest6.send();


}
//----------------------------------------------------------------------------------------------------------------------------------------------
  updateCalendars();
});
//------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------my charts: chart.js---------------------------------------------------------------------------------------------------
let myBarChart;

function updatebare(data) {
   const zones = data.map(item => item.zone);
                const maxChariots = data.map(item => item.max_chariots);
                const minChariots = data.map(item => item.min_chariots);

                const ctx = document.getElementById('chariotChart').getContext('2d');
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: zones,
                        datasets: [
                            {
                                label: 'Max chariots',
                                data: maxChariots,
                                backgroundColor: '#f84d54'
                            },
                            {
                                label: 'Min chariots',
                                data: minChariots,
                                backgroundColor: '#5d5ded'
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'top'
                            },
                            title: {
                                display: true,
                                text: 'Max vs Min des chariots détectés par zone'
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: 'Nombre de chariots'
                                }
                            },
                            x: {
                                title: {
                                    display: true,
                                    text: 'Zone'
                                }
                            }
                        }
                    }
                });
                }



//------------------------------------------------------------------------------------------------------------------------------------------------------

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


function update_BarChart(data_JSON) {
    // Extraire les labels (zones) et les valeurs (taux d'alertes)
    var labels = data_JSON.map(item => item.zone);
    var values = data_JSON.map(item => item.alerte_rate || 0); // Utiliser 0 si alerte_rate est undefined

    // Définir les couleurs
    var colors = [
        '#f84d54',   // Rouge
        '#5d5ded',   // Bleu
        'rgba(255, 206, 86, 0.7)',   // Jaune
        '#2fce4d',   // Vert menthe
        'rgba(153, 102, 255, 0.7)',  // Violet
        '#ffa707'    // Orange
    ];

    // Récupérer le contexte du canvas
    var ctx = document.getElementById("bar-chart");
    if (!ctx) {
        console.error("Canvas 'doughnut-chart2' non trouvé.");
        return;
    }

    // Détruire l'ancien graphique s'il existe
    if (window.barChart) {
        window.barChart.destroy();
    }

    // Créer un nouveau graphique en barres
    window.barChart = new Chart(ctx, {
        type: 'bar', // Type changé en bar chart
        data: {
            labels: labels,
            datasets: [{
                label: 'Taux d\'alertes (%)', // Légende pour les barres
                data: values,
                backgroundColor: colors.slice(0, labels.length), // Limiter les couleurs au nombre de zones
                borderColor: colors.slice(0, labels.length).map(color => color.replace('0.7', '1')), // Bordures plus opaques
                borderWidth: 1,
                borderRadius: 5 // Coins arrondis pour les barres
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: "Taux d'alertes par zone (%)",
                    font: {
                        size: 16
                    }
                },
                legend: {
                    display: true // Légende affichée pour identifier les barres
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            let value = context.raw || 0;
                            return `${label}: ${value.toFixed(2)}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Taux d\'alertes (%)'
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

function update_pie(data_JSON) {
    // Vérifier les données reçues
    console.log("Données JSON:", data_JSON);

    // Extraire labels et valeurs
    var labels = data_JSON.map(item => item.zone);
    var values = data_JSON.map(item => {
        const value = Number(item.nombre_alertes);
        if (isNaN(value)) {
            console.warn("Valeur non numérique pour", item.zone, ": ", item.nombre_alertes);
            return 0; // Remplacer par 0 si non numérique
        }
        return value;
    });

    console.log("Labels:", labels);
    console.log("Values:", values);

    // Vérifier et obtenir le contexte du canvas
    const canvas = document.getElementById("pie-chart");
    if (!canvas) {
        console.error("Canvas avec ID 'pie-chart' non trouvé dans le DOM.");
        return;
    }

    const ctx = canvas.getContext('2d');
    if (!ctx) {
        console.error("Impossible d'obtenir le contexte 2D pour 'pie-chart'.");
        return;
    }

    // Détruire l'ancien graphique s'il existe
    if (window.alertesZoneChart) {
        window.alertesZoneChart.destroy();
    }

    // Créer le nouveau graphique
    window.alertesZoneChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                label: 'Alertes par Zone',
                data: values,
                backgroundColor: [
                    '#f84d54',   // Rouge
                    '#5d5ded',   // Bleu
                    'rgba(255, 206, 86, 0.7)', // Jaune
                    '#2fce4d',   // Vert menthe
                    'rgba(153, 102, 255, 0.7)', // Violet
                    '#ffa707'    // Orange
                ],
                borderWidth: 1,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Nombre d\'alertes par zone'
                },
                legend: {
                    display: true,
                    position: 'bottom'
                }
            }
        }
    });

    // Vérifier si le graphique a été créé
    if (!window.alertesZoneChart) {
        console.error("Échec de la création du graphique.");
    }
}

function update_Line(data_JSON) {
  console.log(data_JSON)
  const labels = data_JSON.map(item => item.date);
  const values = data_JSON.map(item => item.alerte_rate);
  console.log("Labels:", labels);
  console.log("Values:", values);
  const ctx = document.getElementById("line-chart");
  if (window.alertesZoneChart2) {
    window.alertesZoneChart2.destroy();
  }

  window.alertesZoneChart2 = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Correlation d\'alertes',
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
            text: 'correlation d\'alertes (%)'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Dates'
          }
        }
      }
    }
  });


}



//-----------------------------------------------------------------------------------------------------------------------------------------------------

function update_Line_deux(data_JSON) {
  console.log(data_JSON);
  var labels = data_JSON.map(item => item.date);
  var values = data_JSON.map(item => item.max_alertes);

  const ctx = document.getElementById("line-chart_deux");
  if (window.alertesZoneChart3) {
    window.alertesZoneChart3.destroy();
  }

  window.alertesZoneChart3 = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Alertes maximales par jour',
        data: values,
        borderColor: '#5d5ded',
        
        tension: 0.3,
        pointBackgroundColor: '#5d5ded',
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
          text: 'Zone avec le plus d\'alertes par jour'
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const index = context.dataIndex;
              const zone = data_JSON[index].zone_max_alertes;
              const value = context.formattedValue;
              return `Zone: ${zone} — Alertes: ${value}`;
            }
          }
        },
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Nombre d\'alertes'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Dates'
          }
        }
      }
    }
  });
}
//------------------------------------------------------------------------------------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
  const cards = document.querySelectorAll('.card');
  const modal = document.querySelector('.modal');
  const modalImg = document.getElementById("annotated-stream");
  const modalTitle = document.getElementById('modal-title');
  const modalDescription = document.getElementById('modal-description');
  const detectionsList = document.getElementById('detections-list');
  const closeBtn = document.querySelector('.close2');

  cards.forEach(card => {
    card.addEventListener('click', async () => {
      const cameraId = card.getAttribute('data-camera-id');
      const title = card.querySelector('h3').textContent;
      const description = card.querySelector('.description').textContent;

      modalImg.src = `/static/video/video${cameraId}.mp4`;
      modalTitle.textContent = title;
      modalDescription.textContent = description;

      await fetchDetections(cameraId); // Appelle correctement
      modal.style.display = 'flex';
    });
  });

  closeBtn.addEventListener('click', () => {
    modal.style.display = 'none';
    modalImg.src = '';
  });

  window.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.style.display = 'none';
      modalImg.src = '';
    }
  });
});

async function fetchDetections(cameraId) {
  const response = await fetch('/predict_video', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ video_path: `/static/video/video${cameraId}.mp4` })
  });

  const data = await response.json();
  const list = document.getElementById("detections-list");
  list.innerHTML = '';
  for (const className in data.class_counts) {
    const li = document.createElement("li");
    li.textContent = `${className}: ${data.class_counts[className]}`;
    list.appendChild(li);
  }
}



function redirectToZone(zoneName) {
    window.location.href = `/zone/${zoneName.toLowerCase().replace(' ', '')}`;
}