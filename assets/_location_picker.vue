<!-- <script>
import { VueOpenMap } from "vue3-openstreet-map" 
export default {
    components: {
        VueOpenMap
    },
    data() {
        return {
            selected_location: { lat: 0.0, lng: 0.0, zoom: 1 },
            selected_address : "",
            selected_details : {},
        }
    },
    props: {
        position: {
            type: Object,
            default: () => ({ lat: 40.689247, lng: -74.044502 })
        },
        width: {
            type: String,
            default: '600px'
        },
        height: {
            type: String,
            default: '400px'
        },
    },
    methods: {
        handleLocationSelect(event) {
            /*event = {
                address_name: json.display_name,
                address_details: json,
                origin: {
                    lat: lat,
                    lon: lon
                },
                coordinates: {
                    lat: json.lat,
                    lon: json.lon
                }
            }*/
            this.selected_address = event.address_name
            this.selected_details = event.address_details

            //emit the selected location to the parent component
            this.$emit('location-selected', {lat: event.coordinates.lat, lon: event.coordinates.lon})

            //do after some time: set the position to the new location for new search around that location
            setTimeout(() => {
                this.selected_location = {lat: event.coordinates.lat, lon: event.coordinates.lon, zoom: 4}
            }, 5000)
        },
        emitLocation() {
            this.$emit('location-selected', this.selected_location)
        }
    },
    onLoad() {
        this.selected_location = {lat: this.position.lat, lon: this.position.lng, zoom: 2}
    },
    emits: ['location-selected']
}
</script>

<template>
  <v-container id="location-picker" class="d-flex flex-column align-center">
    <v-card>
        <v-card-title>{{ selected_address }}</v-card-title>
         <v-card-text>
            <v-row>
            <v-col cols="12">
                <v-text-field label="Search Location" v-model="search_location"></v-text-field>
            </v-col>
            </v-row>
        </v-card-text>
        <VueOpenMap :position="selected_location" @onChange="handleLocationSelect"></VueOpenMap>
        <v-btn @click="emitLocation()" style="width:100%">Select Location</v-btn>
    </v-card>
  </v-container>

</template> -->