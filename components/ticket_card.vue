<template>
    <v-card>
        <v-card-title>{{ ticket.title }}</v-card-title>
        <v-card-subtitle>ID: {{ ticket.id }}</v-card-subtitle>
        <v-card-text>
            <div>Price: {{ ticket.price }}</div>
            <div>Time: {{ ticket.time }}</div>
            <div>Place: {{ ticket.place }}</div>
            <div>{{ ticket.short_description }}</div>
        </v-card-text>
        <v-card-actions>
            <nuxt-link :to="'/ticket/' + ticket.id"><v-btn>View</v-btn></nuxt-link>
            <v-btn @click="$emit('add-to-cart', ticket)">Add to Cart</v-btn>
        </v-card-actions>
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
                title: '',
                price: '',
                id: '',
                time: '',
                place: '',
                short_description: ''
            })
        }
    },
}
</script>

<style scoped>
/* Add any styles you need here */
</style>