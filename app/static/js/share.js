// Define global functions so that onclick events in HTML can access them
function copyShareLink() {
    const shareLink = document.getElementById('share-link');
    shareLink.select();
    document.execCommand('copy');

    const copyMessage = document.getElementById('copy-message');
    copyMessage.classList.remove('d-none');
    setTimeout(() => {
        copyMessage.classList.add('d-none');
    }, 2000);
}

function copyLinkedInText() {
    const tempInput = document.createElement('textarea');
    const shareLink = document.getElementById('share-link').value;
    tempInput.value = "Check out my fitness progress! " + shareLink;
    document.body.appendChild(tempInput);
    tempInput.select();
    document.execCommand('copy');
    document.body.removeChild(tempInput);
    alert('Text copied to clipboard! Just paste it in the LinkedIn post editor.');
}

function downloadQRCode() {
    const qrImage = document.querySelector('#qrcode img');
    const qrUrl = qrImage.src.replace('size=200x200', 'size=400x400');
    fetch(qrUrl)
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'fitness-progress-qrcode.png';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        })
        .catch(err => console.error('Error downloading QR code:', err));
}

function downloadAllCharts() {
    const chartIds = [
        'DailyExerciseDurationChart',
        'ExerciseIntensityLevelsChart',
        'CaloriesBurnedperSessionChart',
        'WeeklyExerciseFrequencyChart',
        'DailyCaloricIntakeChart',
        'MacronutrientBreakdownChart',
        'WaterConsumptionChart',
        'WeeklyMealFrequencyChart',
        'DailySleepDurationChart',
        'SleepQualityScoresChart',
        'SleepTypeDistributionChart',
        'SleepWakeupsChart'
    ];

    chartIds.forEach((chartId, index) => {
        setTimeout(() => {
            downloadChart(chartId);
        }, index * 200); // Stagger downloads to ensure rendering
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.remove('show');
            alert.classList.add('fade');
        }, 2000);
    });
});

// Initialize the chart when the page loads
window.onload = function () {
    // Calculate macronutrient values
    const macronutrientValues = [
        chartData.diet_protein.reduce((a, b) => a + b, 0),
        chartData.diet_carbs.reduce((a, b) => a + b, 0),
        chartData.diet_fats.reduce((a, b) => a + b, 0)
    ];

    // Chart configurations
    const chartConfigs = {
        DailyExerciseDurationChart: {
            type: 'line',
            data: {
                labels: chartData.exercise_dates,
                datasets: [{
                    label: 'Duration (minutes)',
                    data: chartData.exercise_durations,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        },
        ExerciseIntensityLevelsChart: {
            type: 'bar',
            data: {
                labels: chartData.exercise_intensity_labels,
                datasets: [{
                    label: 'Intensity Counts',
                    data: chartData.exercise_intensity_counts,
                    backgroundColor: 'rgba(153, 102, 255, 0.6)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        },
        CaloriesBurnedperSessionChart: {
            type: 'line',
            data: {
                labels: chartData.exercise_dates,
                datasets: [{
                    label: 'Calories Burned',
                    data: chartData.exercise_calories,
                    borderColor: 'rgba(255, 159, 64, 1)',
                    backgroundColor: 'rgba(255, 159, 64, 0.2)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        },
        WeeklyExerciseFrequencyChart: {
            type: 'bar',
            data: {
                labels: chartData.exercise_frequency_labels,
                datasets: [{
                    label: 'Frequency',
                    data: chartData.exercise_frequency_values,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        },
        DailyCaloricIntakeChart: {
            type: 'line',
            data: {
                labels: chartData.diet_dates,
                datasets: [{
                    label: 'Calories Consumed',
                    data: chartData.diet_calories,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        },
        MacronutrientBreakdownChart: {
            type: 'doughnut',
            data: {
                labels: ["Protein", "Carbs", "Fats"],
                datasets: [{
                    label: 'Macronutrients',
                    data: macronutrientValues,
                    backgroundColor: ['#36a2eb', '#ff6384', '#ffcd56']
                }]
            },
            options: {
                responsive: true,
                aspectRatio: 1.4,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        },
        WaterConsumptionChart: {
            type: 'line',
            data: {
                labels: chartData.diet_dates,
                datasets: [{
                    label: 'Water Intake (ml)',
                    data: chartData.diet_water,
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        },
        WeeklyMealFrequencyChart: {
            type: 'bar',
            data: {
                labels: chartData.meal_labels,
                datasets: [{
                    label: 'Meal Values',
                    data: chartData.meal_values,
                    backgroundColor: 'rgba(255, 206, 86, 0.6)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        },
        DailySleepDurationChart: {
            type: 'line',
            data: {
                labels: chartData.sleep_dates,
                datasets: [{
                    label: 'Sleep Duration (hours)',
                    data: chartData.sleep_duration,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        },
        SleepQualityScoresChart: {
            type: 'line',
            data: {
                labels: chartData.sleep_dates,
                datasets: [{
                    label: 'Sleep Quality Scores',
                    data: chartData.sleep_efficiency,
                    borderColor: 'rgba(153, 102, 255, 1)',
                    backgroundColor: 'rgba(153, 102, 255, 0.2)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        },
        SleepTypeDistributionChart: {
            type: 'doughnut',
            data: {
                labels: chartData.sleep_stage_labels,
                datasets: [{
                    label: 'Sleep Stages',
                    data: chartData.sleep_stage_counts,
                    backgroundColor: ['#4bc0c0', '#ff9f40', '#9966ff', '#ff6384']
                }]
            },
            options: {
                responsive: true,
                aspectRatio: 1.4,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        },
        SleepWakeupsChart: {
            type: 'bar',
            data: {
                labels: chartData.sleep_wake_ups_dates,
                datasets: [{
                    label: 'Daily Wake-up Count',
                    data: chartData.sleep_wake_ups,
                    backgroundColor: 'rgba(255, 99, 132, 0.6)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        }
    };

    // Create all charts
    const charts = {};
    for (const [chartId, config] of Object.entries(chartConfigs)) {
        const ctx = document.getElementById(chartId)?.getContext("2d");
        if (ctx) {
            charts[chartId] = new Chart(ctx, config);
        } else {
            console.error(`Canvas element for ${chartId} not found`);
        }
    }

    // Download individual chart function - Make it available globally
    window.downloadChart = function(chartId) {
        const chart = charts[chartId];
        if (chart) {
            // Ensure the chart is fully rendered
            chart.update();
            setTimeout(() => {
                const url = chart.toBase64Image();
                const a = document.createElement('a');
                a.href = url;
                a.download = `${chartId}.png`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            }, 100);
        } else {
            console.error(`Chart ${chartId} not found`);
        }
    };

    // Map downloadChart to the global scope as well
    downloadChart = window.downloadChart;

    // Initialization alert disappears automatically
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.remove('show');
            alert.classList.add('fade');
        }, 2000); // 2 seconds
    });
};