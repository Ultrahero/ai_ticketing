<template>
    <v-card class="d-flex flex-column">
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
            <nuxt-link :to="'/events/' + ticket.id"><v-btn>View</v-btn></nuxt-link>
            <v-spacer></v-spacer>
            <v-btn @click="$emit('add-to-cart', ticket)">Add to Cart</v-btn>
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
}
</script>

<style scoped>
/* Add any styles you need here */
</style>