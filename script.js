document.addEventListener("DOMContentLoaded", function () {
    const provinceSelect = document.getElementById("province");

    const provinces = [
        "Aceh", "Sumatera Utara", "Sumatera Barat", "Riau", "Jambi", "Sumatera Selatan", "Bengkulu", "Lampung",
        "Bangka Belitung", "Kepulauan Riau", "DKI Jakarta", "Jawa Barat", "Jawa Tengah", "DI Yogyakarta", "Jawa Timur", "Banten",
        "Bali", "Nusa Tenggara Barat", "Nusa Tenggara Timur", "Kalimantan Barat", "Kalimantan Tengah", "Kalimantan Selatan",
        "Kalimantan Timur", "Kalimantan Utara", "Sulawesi Utara", "Sulawesi Tengah", "Sulawesi Selatan", "Sulawesi Tenggara",
        "Gorontalo", "Sulawesi Barat", "Maluku", "Maluku Utara", "Papua", "Papua Barat", "Papua Selatan", "Papua Tengah", "Papua Pegunungan"
    ];

    provinces.forEach(province => {
        const option = document.createElement("option");
        option.value = province.toLowerCase();
        option.textContent = province;
        provinceSelect.appendChild(option);
    });
});

function goToProvince() {
    document.getElementById("home").style.display = "none";
    document.getElementById("provinceSelection").style.display = "block";
}

function fetchInfrastructure() {
    const province = document.getElementById("province").value;
    const result = document.getElementById("result");

    if (!province) {
        result.innerHTML = "<p>Please select a province!</p>";
        return;
    }

    fetch(`http://127.0.0.1:8000/get-infrastructure/${encodeURIComponent(province)}`)
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            result.innerHTML = "<p>Invalid province selected.</p>";
            return;
        }

        result.innerHTML = `
            <h3>Results for ${data.province}</h3>
            <p><strong>Green Infrastructure:</strong> ${data.infrastructure}</p>
            <p><strong>Renewable Energy:</strong> ${data.renewable_energy}</p>
            <p><strong>Poverty Index:</strong> ${data.poverty_index}</p>
            <p><strong>EVI Index:</strong> ${data.evi}</p>
            <p><strong>Average Precipitation:</strong> ${data.precipitation} mm</p>
            <p><strong>Sentinel-1 Data:</strong> ${data.sentinel} db</p>
        `;
    })
    .catch(error => {
        result.innerHTML = "<p>Failed to fetch data!</p>";
    });
}

