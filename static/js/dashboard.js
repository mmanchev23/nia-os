const cpuCtx = document.getElementById("cpuChart").getContext("2d");

new Chart(cpuCtx, {
    type: "line",
    data: {
        labels: [...Array(12).keys()].map(i => `${i * 5}m`),
        datasets: [{
            label: "CPU %",
            data: [12, 19, 14, 22, 30, 25, 27, 35, 32, 40, 38, 45],
            borderColor: "#42A5F5",
            backgroundColor: "rgba(66,165,245,0.2)",
            tension: 0.4,
            fill: true
        }]
    },
    options: {
        responsive: true,
    }
});

const memoryCtx = document.getElementById("memoryChart").getContext("2d");

new Chart(memoryCtx, {
    type: "line",
    data: {
        labels: [...Array(12).keys()].map(i => `${i * 5}m`),
        datasets: [{
            label: "Memory %",
            data: [45, 50, 48, 52, 55, 60, 58, 62, 65, 70, 68, 72],
            borderColor: "#16A34A",
            backgroundColor: "rgba(22,163,74,0.2)",
            tension: 0.4,
            fill: true
        }]
    },
    options: {
        responsive: true,
    }
});

const statusCtx = document.getElementById("deviceStatusChart").getContext("2d");

new Chart(statusCtx, {
    type: "doughnut",
    data: {
        labels: ["Online", "Offline", "Error"],
        datasets: [{
            data: [9, 2, 1],
            backgroundColor: [
                "#22C55E",
                "#FACC15",
                "#EF4444"
            ]
        }]
    },
    options: {
        responsive: true
    }
});
