// The content for one post request goes here 
// ScanContent holds all entities for one destination
class ScanContent {

    // record fields
    destination;
    recipients = null;
    bons = [];
    amounts = [];
    units = [];

    // server feedback state 
    postSuccess = false;

    constructor(destination) {
        this.destination = destination;
    }

    addBon(bon) {
        this.bons.push(bon);
    }

    setRecipients(recipients) {
        this.recipients = recipients;
    }

    addAmount(amount) {
        this.amounts.push(amount);
    }

    addUnit(unit) {
        this.units.push(unit);
    }

    json() {
        return JSON.stringify(this);
    }

    sendPost(callback) {

        // content of the post request
        const content = {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: this.json()
        };

        // send post request to server and display result as popup
        const response = fetch("/barcode/bookings/", content) 
            .then(resp => {
                if (resp.ok) {
                    this.postSuccess = true;
                }
                else {
                    this.postSuccess = false;
                }
                callback();
            }
        );

    }

}

// Scenes that hold forms 
// Each scene points to the following one 

class Scene {

    id; // id of the surrounding div 
    anchor; // id of the element to focus 

    constructor(id, anchor) {
        this.id = id;
        this.anchor = anchor;
    }

    disable() {
        document.getElementById(this.id).style.display = "none";
    }

    enable() {
        document.getElementById(this.id).style.display = "table-cell";
        this.focus();
    }

    focus() {
        document.getElementById(this.anchor).focus();
    }

    nextScene(scene) {
        this.disable();
        scene.enable();
    }
}


// Helper functions

function focus(id) {
    // TODO: implement
}

function clearText(id) {
    document.getElementById(id).value = "";
}
