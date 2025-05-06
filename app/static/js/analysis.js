window.onload = function () {
  const macronutrientValues = [
    chartData.diet_protein.reduce((a, b) => a + b, 0),
    chartData.diet_carbs.reduce((a, b) => a + b, 0),
    chartData.diet_fats.reduce((a, b) => a + b, 0)
  ];

  const chartConfigs = {
    // Exercise Charts
    exerciseChart1: {
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
          legend: {
            position: 'bottom'
          }
        }
      }
    },
    exerciseChart2: {
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
          legend: {
            position: 'bottom'
          }
        }
      }
    },
    exerciseChart3: {
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
          legend: {
            position: 'bottom'
          }
        }
      }
    },
    exerciseChart4: {
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
          legend: {
            position: 'bottom'
          }
        }
      }
    },

    // Diet Charts
    dietChart1: {
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
          legend: {
            position: 'bottom'
          }
        }
      }
    },
    dietChart2: {
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
          legend: {
            position: 'bottom'
          }
        }
      }
    },
    dietChart3: {
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
          legend: {
            position: 'bottom'
          }
        }
      }
    },
    dietChart4: {
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
          legend: {
            position: 'bottom'
          }
        }
      }
    },

    // Sleep Charts
    sleepChart1: {
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
          legend: {
            position: 'bottom'
          }
        }
      }
    },
    sleepChart2: {
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
          legend: {
            position: 'bottom'
          }
        }
      }
    },
    sleepChart3: {
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
          legend: {
            position: 'bottom'
          }
        }
      }
    },
    sleepChart4: {
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
          legend: {
            position: 'bottom'
          }
        }
      }
    }
  };

  const charts = {};
  for (const [chartId, config] of Object.entries(chartConfigs)) {
    const ctx = document.getElementById(chartId)?.getContext("2d");
    if (ctx) {
      charts[chartId] = new Chart(ctx, config);
    }
  }
};