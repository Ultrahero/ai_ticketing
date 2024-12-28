<template>
    <v-card class="d-flex flex-column ticket-card">
        <div>
        <v-card-title>{{ ticket.name }}</v-card-title>
        
        <v-card-text>
            <span>{{ ticket.short_description }}</span>
        </v-card-text>
        </div>
        <v-spacer></v-spacer>
        <div>
        <v-card-text>
            <div>Time: {{ times }}</div>
            <div>Location: {{ ticket.location }}</div>
            <div>Price: from {{ min_price }}</div>
        </v-card-text>
        <v-card-actions class="d-flex flex-row align-center">
            <nuxt-link :to="'/events/' + ticket.id"><v-btn tonal color="rgb(var(--v-theme-accent))" outlined>View</v-btn></nuxt-link>
            <v-spacer></v-spacer>
            <v-menu :close-on-content-click="false" v-model="menu">
        <template v-slot:activator="{ props }">
            <v-btn v-bind="props">
                Add to Cart
            </v-btn>
        </template>
        <v-container class="bg-white rounded-lg pa-0">
        <v-form @submit.prevent="addToCart" >
        <v-row>
            <v-col cols="11" class="mx-auto px-2 mt-2">
                <v-select
                    v-model="selectedDate"
                    :items="ticket.dates"
                    label="Date"
                    placeholder="Select Date"
                    required
                    class="pb-0"
                    :hint="dateMessage"
                ></v-select>
                <v-select
                    v-model="selectedSeats"
                    :items="Array.from({ length: Math.min(ticket.seat_count[ticket.dates.indexOf(selectedDate)], ticket.number_of_tickets_per_buyer || 42) }, (_, i) => i + 1)"
                    label="Seats"
                    placeholder="Select Seats"
                    required
                    class="pb-0"
                    :hint="seatMessage"
                ></v-select>
            </v-col>
        </v-row>
        <v-row class="mt-0 pb-2 mx-0">
            <v-col cols="6" class="ma-0 pa-0">
                <v-btn text @click="selectedSeats = 0; selectedDate = null; menu=false" block class="rounded-be-0 rounded-te-0 rounded-ts-0">Dismiss</v-btn>
            </v-col>
            <v-col cols="6" class="ma-0 pa-0">
                <v-btn text color="primary" type="submit" block class="rounded-bs-0 rounded-te-0 rounded-ts-0">Add to Cart</v-btn>
            </v-col>
        </v-row>
    </v-form>
    </v-container>
            </v-menu>
        </v-card-actions>
        </div>
    </v-card>
</template>

<script>
export default {
    name: 'TicketCard',
    emits: ['add-to-cart'],
    props: {
        ticket: {
            type: Object,
            required: true,
            default: () => ({
                name: '',
                price: '',
                id: '',
                dates: '',
                location: '',
                short_description: ''
            })
        },
    },
    data() {
        return {
            selectedSeats: 0,
            selectedDate: null,
            menu: false,
            dateMessage: "",
            seatMessage: ""
        }
    },
    computed: {
        times() {
            return (this.ticket.dates[0].split(";")[0] + " - " + this.ticket.dates[this.ticket.dates.length-1].split(";")[0]).toString()
            // return "Monday"
        },
        min_price() {
            return Math.min(parseFloat(...this.ticket.price));
        }
    },
    methods: {
        async addToCart(){
            if (!this.selectedDate){
                this.dateMessage = "Please select a Date";
                return;
            }
            if (!this.selectedSeats){
                this.seatMessage = "Please select Seats";
                return;
            }
            this.$emit('add-to-cart', {
                event : this.ticket,
                dateIndex : this.ticket.dates.indexOf(this.selectedDate),
                quantity : this.selectedSeats
            });
            this.selectedSeats = 0;
            this.selectedDate = null;
            this.menu = false;
        }
    }
}
</script>

<style scoped>
/* Add any styles you need here */
/* ticket card should be elevated and slightly shifted up/right on hover */
.ticket-card {
    transition: transform 0.2s;
    transition: box-shadow 0.2s;
    transition: outline 0.05s;
    cursor: pointer;
    box-shadow: none;
    outline: none;
}
.ticket-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 8px rgba(0, 214, 199,0.3);
    outline: 1px solid rgba(0, 214, 199,0.5);
}
</style>