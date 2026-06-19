
function setUsedFuel() {
    document.querySelectorAll(".fuel-tank-single").forEach(tank => {
        const tankId = tank.dataset.tankId;
        const departure = document.getElementById(`fuel_departure_${tankId}`);
        const arrival = document.getElementById(`level${tankId}`);
        const usage = document.getElementById(`fuel_usage_${tankId}`)
        console.log(usage)

        usage.value = departure.value - arrival.value;
    });        
}

function copyArrivalFuel() {
    event.preventDefault()
    document.querySelectorAll(".fuel-tank-single").forEach(tank => {
        const tankId = tank.dataset.tankId;
        const arrival = document.getElementById(`fluid_arrival_${tankId}`);
        const preFuel = document.getElementById(`pre_refuel_in_kg_${tankId}`);
        const arrival_total = document.getElementById("fluid_arrival_total")
        const preFuel_total = document.getElementById("pre_refuel_in_kg")
        
        preFuel.value = arrival.value;
        preFuel_total.value = arrival_total.textContent.trim();
        calculateFuelVolume()
    });
}

function calculateFuelVolume(){
    const required_fuel = document.getElementById("planned_dep_fuel_in_kg").value
    const specific_gravity = document.getElementById("specific_gravity").value
    const fuel_pre_total = document.getElementById("pre_refuel_in_kg").value
    const departure_fob_in_kg = document.getElementById("departure_fob_in_kg").value
    const required_uplift_in_lt = document.getElementById("required_uplift_in_lt")
    const calculated_uplift_in_lt = document.getElementById("calculated_uplift_in_lt")
    const required_fuel_in_volume = document.getElementById("required_fuel_in_volume")
    const required_fuel_in_weight = document.getElementById("required_fuel_in_weight")

    if (fuel_pre_total && specific_gravity && required_fuel) {
        required_fuel_in_weight.textContent = required_fuel - fuel_pre_total
        required_fuel_in_volume.textContent = Math.round((required_fuel - fuel_pre_total) / specific_gravity)

        if (departure_fob_in_kg) {
            console.log("departure_fob_in_kg")
            console.log(departure_fob_in_kg)
            required_uplift_in_lt.value = Math.round((departure_fob_in_kg - fuel_pre_total) / specific_gravity)
            calculated_uplift_in_lt.textContent = Math.round((departure_fob_in_kg - fuel_pre_total) / specific_gravity)
        }
    } else {
        required_fuel_in_weight.textContent = ""
        required_fuel_in_volume.textContent = ""
    }
}

function setDepartureFuel(event) {
    event.preventDefault();

    let total_departure_fuel = 0;

    document.querySelectorAll(".fuel-tank-single").forEach(tank => {
        const tankId = tank.dataset.tankId;

        const input = document.getElementById(`fluid_departure_${tankId}`);
        console.log("input")
        console.log(input)

        if (input && input.value) {
            total_departure_fuel += Number(input.value) || 0;
        }
    });

    const departure_fob_in_kg = document.getElementById("departure_fob_in_kg");

    if (departure_fob_in_kg) {
        departure_fob_in_kg.value = total_departure_fuel;
    }

    calculateFuelVolume();
}
