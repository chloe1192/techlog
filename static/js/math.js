
function setUsedFluid() {
    document.querySelectorAll(".fuel-tank-single").forEach(tank => {
        const tankId = tank.dataset.tankId;
        const departure = document.getElementById(`fluid_departure_${tankId}`);
        const arrival = document.getElementById(`fluid_arrival_${tankId}`);
        const usage = document.getElementById(`fluid_usage_${tankId}`)

        if (arrival.value != ""){
            usage.value = departure.value - arrival.value;
        }

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
        console.log(arrival)
        console.log(preFuel)
        console.log(tankId)
        
        preFuel.value = arrival.value;
        preFuel_total.value = arrival_total.value;
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
        required_fuel_in_weight.value = required_fuel - fuel_pre_total
        required_fuel_in_volume.value = Math.round((required_fuel - fuel_pre_total) / specific_gravity)

        if (departure_fob_in_kg) {
            required_uplift_in_lt.value = Math.round((departure_fob_in_kg - fuel_pre_total) / specific_gravity)
            calculated_uplift_in_lt.textContent = Math.round((departure_fob_in_kg - fuel_pre_total) / specific_gravity)
        }
    } else {
        required_fuel_in_weight.value = ""
        required_fuel_in_volume.value = ""
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
            console.log("total_departure_fuel")
            console.log(total_departure_fuel)
        }
    });

    const departure_fob_in_kg = document.getElementById("departure_fob_in_kg");

    if (departure_fob_in_kg) {
        departure_fob_in_kg.value = total_departure_fuel;
    }

    calculateFuelVolume();
}

function calculateFluidDifference(uplift_or_usage) 
{
    document.querySelectorAll(".fuel-tank-single").forEach(tank => {
        const tankId = tank.dataset.tankId;
        const arrival = document.getElementById(`fluid_arrival_${tankId}`);
        const departure = document.getElementById(`fluid_departure_${tankId}`);
        if (uplift_or_usage == 'uplift' && departure.value) {
            const uplift = document.getElementById(`fluid_uplift_${tankId}`)
            uplift.value = departure.value - arrival.value
        } else if (uplift_or_usage == 'usage' && arrival.value) {            
            const usage = document.getElementById(`fluid_usage_${tankId}`)
            usage.value = departure.value - arrival.value
        }
    });

}

function diversionAirportId() {
    const aiportIdInput = document.getElementById('actual_arrival_airport');
    const input = document.getElementById('actual_arrival_airport_datalist');
    const datalist = document.getElementById('airportDatalistOptions');
    const option = [...datalist.options].find(
        opt => opt.value === input.value
    );

    if (option) {
        console.log(option.dataset.actualArrivalAirport)
        aiportIdInput.value = option.dataset.actualArrivalAirport
        console.log(aiportIdInput)
        console.log('Matched option:', option.dataset);
    }
}
