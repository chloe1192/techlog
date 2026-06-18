

    function setUsedFuel() {
        document.querySelectorAll(".fuel-tank-single").forEach(tank => {
            const tankId = tank.dataset.tankId;
            const departure = document.getElementById(`fuel_departure_${tankId}`);
            const arrival = document.getElementById(`fuel_arrival_${tankId}`);
            const usage = document.getElementById(`fuel_usage_${tankId}`)
            console.log(usage)

            usage.value = departure.value - arrival.value;
        });        
    }