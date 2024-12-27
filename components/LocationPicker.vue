<script>

export default {
    data() {
        return {
            selected_location: { lat: 0.0, lng: 0.0},
            selected_address : "",
            selected_details : {},
            rules: [
                value => !!value || 'Required.', //required
                value => { //double float 
                    if(!value.includes(',')){
                        return 'Invalid Location, must be in format "LAT, LONG"'
                    }
                    try {
                        const [lat, lon] = value.split(',').map(coord => parseFloat(coord.trim()))
                        if (isNaN(lat) || isNaN(lon) || lat == null || lon == null || lat < -90 || lat > 90 || lon < -180 || lon > 180) {
                            return 'Invalid Location, must be in format "LAT, LONG"'
                        }
                    } catch (error) {
                        return 'Invalid Location, must be in format "LAT, LONG" both must be decimal numbers.'
                    }
                }
            ],
            location: '',
        };
    },
    methods: {
        emitLocation() {
            if (this.location.includes(',')) {
                const [lat, lon] = this.location.split(',').map(coord => parseFloat(coord.trim()))
                this.selected_location = {lat, lon}
                this.selected_address = this.location //potentially get the real address from the coordinates
                this.selected_details = {}
            }
            this.$emit('location-selected', this.selected_location)
        },
    },
    emits: ['location-selected'],
};

</script>

<template>
    <v-card class="my-1 location-picker d-flex flex-column align-center" style="width: fit-content;">
        <v-card-title class="text-body">Location Picker</v-card-title>
        <v-card-text class="text-body-1" style="width:fit-content;"> 
            <v-text-field 
                label="Longitude, Latitude" 
                placeholder="-42.1337, 66.99" 
                clearable
                :rules="rules"
                v-model="location"
                style="width: 300px;"
                append-icon="mdi-arrow-right"
                @click:append="emitLocation">
            </v-text-field>
        </v-card-text>
    </v-card>            
</template>