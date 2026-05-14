// ChartJS - données statiques (remplacer plus tard si tu veux)

fetch('/api/stats-globales/')
.then(response => response.json())
.then(data => {
    poubelles_pleines = data.pleines
    poubelles_vides = data.videes
    const pieCtx = document.getElementById('pieChart').getContext('2d');
    new Chart(pieCtx, {
        type: 'pie',
        data: {
        labels: ['Poubelles Pleines', 'Poubelles Vidées'],
        datasets: [{
            data: [poubelles_pleines, poubelles_vides],
            backgroundColor: ['#dc3545', '#28a745']
        }]
        }
    });
});


fetch('/histogrammes_uploads/')
.then(response => response.json())
.then(data => {
    console.log(data)
    let days = []
    let nombres = []

    data.forEach(element => {
    days.push(element["jour"])
    nombres.push(element["nb_images"])
    })

    const barCtx = document.getElementById('barChart').getContext('2d');
    new Chart(barCtx, {
    type: 'bar',
    data: {
        labels: days,
        datasets: [
        {
            label: 'Poubelles Pleines',
            data: nombres,
            backgroundColor: /*'#dc3545'*/ '#28a745'
        },
        // {
        //   label: 'Poubelles Vidées',
        //   data: [15, 29, 5, 5, 2, 3, 10],
        //   backgroundColor: '#28a745'
        // }
        ]
    },
    options: { responsive: true }
    });
});



fetch('http://127.0.0.1:8000/zone_5/')
.then(response => response.json())
.then(data => {
    console.log(data)
    let adresses = []
    let nombres = []

    data.forEach(({ lat, long, occur, adresse })  => {
        if (occur >= 5) {
            adresses.push(adresse)
            nombres.push(occur)
        }
            
    })
    document.querySelector(".status-orange p ").textContent = adresses.length

    const barCtx = document.getElementById('barChartVertical').getContext('2d');
    new Chart(barCtx, {
    type: 'bar',
    data: {
        labels: adresses,
        datasets: [
        {
            label: 'Zones critiques',
            data: nombres,
            backgroundColor: '#dc3545'
        },
        ]
    },
    options: { responsive: true }
    });
});
























fetch('/histogrammes_hours/')
.then(response => response.json())
.then(data => {
    console.log(data)
    let hours = []
    let nombres = []

    data.forEach(element => {
    hours.push( element["heure"]+"h")
    nombres.push(element["nb_signalements"])
    })
    console.log(hours)
    const lineCtx = document.getElementById('lineChart').getContext('2d');
    new Chart(lineCtx, {
    type: 'line',
    data: {
        labels: hours,
        datasets: [{
        label: 'Fréquence',
        data: nombres,
        borderColor: '#007bff',
        fill: false
        }]
    },
    options: { responsive: true }
    });


});





// Données dynamiques depuis ton API Django
fetch('/api/stats-globales/')
    .then(response => response.json())
    .then(data => {
    poubelles_pleines = data.pleines
    poubelles_vides = data.videes
    
    document.querySelector('.status-blue p').textContent = data.total;
    document.querySelector('.status-red p').textContent = data.pleines;
    document.querySelector('.status-green p').textContent = data.videes;
    });

// fetch('/api/risques/')
//   .then(res => res.json())
//   .then(data => {
//     const ul = document.querySelector('.card ul');
//     ul.innerHTML = "";
//     if (data.length === 0) {
//       ul.innerHTML = "<li>Aucune donnée disponible</li>";
//     } else {
//       data.forEach(p => {
//         ul.innerHTML += `<li><strong>${p.quartier_nom}</strong> - <span class="badge badge-${p.risque.toLowerCase()}">${p.risque}</span> (${p.raison})</li>`;
//       });
//     }
//   });
