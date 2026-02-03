function addLocation() {
    fetch("/add-location", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_name: document.getElementById("name").value,
            city: document.getElementById("city").value,
            state: document.getElementById("state").value,
            latitude: document.getElementById("lat").value,
            longitude: document.getElementById("lon").value
        })
    })
    .then(res => res.json())
    .then(data => alert(data.message));
}

function makePayment() {
    fetch("/add-payment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_name: document.getElementById("pname").value,
            amount: document.getElementById("amount").value,
            payment_method: document.getElementById("method").value
        })
    })
    .then(res => res.json())
    .then(data => alert(data.message));
}
