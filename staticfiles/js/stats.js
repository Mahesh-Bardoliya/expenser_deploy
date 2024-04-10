var type = 'doughnut';
var myChart;

function myNewFunction(s) {
    switch(s) {
        case 1:
            type='doughnut';
            break;
        case 2:
            type='bar';
            break;
        case 3:
            type='line';
            break;
        case 4:
            type='bubble';
            break;    
        
    }

    myChart.config.type = type;
    myChart.update();
}

const renderChart = (data, labels) => {
    var ctx = document.getElementById("myChart").getContext("2d");
    if (window.myChart) {
        window.myChart.destroy();
    }
    
    window. myChart = new Chart(ctx, {
        type: type,
        data: {
            labels: labels,
            datasets: [
                {
                    
                    data: data,
                    backgroundColor: [
                        "rgba(255, 99, 132, 0.2)",
                        "rgba(54, 162, 235, 0.2)",
                        "rgba(255, 206, 86, 0.2)",
                        "rgba(75, 192, 192, 0.2)",
                        "rgba(153, 102, 255, 0.2)",
                        "rgba(255, 159, 64, 0.2)",
                    ],
                    borderColor: [
                        "rgba(255, 99, 132, 1)",
                        "rgba(54, 162, 235, 1)",
                        "rgba(255, 206, 86, 1)",
                        "rgba(75, 192, 192, 1)",
                        "rgba(153, 102, 255, 1)",
                        "rgba(255, 159, 64, 1)",
                    ],
                    borderWidth: 1,
                },
            ],
        },
        options: {
            title: {
                display: true,
                text: "Income per category",
            },
        },
    });
};

const getChartData = () => {
    const fromDate = document.getElementById("from_date").value;
    const toDate = document.getElementById("to_date").value;
    const url = `/expense_category_summary?from_date=${fromDate}&to_date=${toDate}`;
    console.log("fetching");
    fetch(url)
        .then((res) => res.json())
        .then((results) => {
            console.log("results", results);
            const category_data = results.expense_category_data;
            const [labels, data] = [
                Object.keys(category_data),
                Object.values(category_data),
            ];
            renderChart(data, labels);
        });
};
